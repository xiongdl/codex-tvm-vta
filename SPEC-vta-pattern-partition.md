# Spec: VTA Capability-Based Relay Partitioning

## Objective

Implement the Relay-facing half of the VTA BYOC extension. The module exposes
`partition_for_vta`, recognizes the first supported quantized convolution
region through a dataflow pattern plus a capability predicate, and outlines
accepted regions as `Compiler="vta"` functions through TVM's standard BYOC
Pass sequence.

This replaces model-specific start/stop selection with local, intrinsic
capability decisions. It ends at a correctly partitioned `IRModule`; Relay to
VTA TIR lowering and `relay.ext.vta` artifact creation belong to later modules.

## Initial Pattern Contract

The first composite is named `vta.qnn_conv2d`:

```text
wildcard input
  -> nn.conv2d(constant weight, out_dtype=Environment.acc_dtype)
  -> [nn.bias_add(constant) | add(constant)]
  -> right_shift(constant scalar)
  -> clip
  -> cast(Environment.out_dtype)
```

The bias/add stage is optional. The requantization-like
`right_shift -> clip -> cast` tail is required in this first slice so outlined
functions have the established VTA int8 output contract. More general
requantization and accumulator-output composites are later pattern-table
extensions, not implicit matches in this module.

The pattern starts at `nn.conv2d`; producer operations such as the contract
fixture's `abs` remain on the host. It ends at `cast`; consumer operations such
as `transpose` also remain on the host.

## Capability Predicate

`check_qnn_conv2d(call) -> bool` validates the root call matched by the
pattern. Ordinary capability misses return `False` and do not raise.

An accepted candidate must satisfy all conditions below against a
`VTACompilerConfig` snapshot from the active environment.

### Types and constants

- All participating calls have inferred static tensor types.
- Input dtype equals `input_dtype`.
- Convolution weight is a Relay `Constant` with `weight_dtype`.
- Convolution `out_dtype` and inferred output dtype equal
  `accumulator_dtype`.
- Optional bias/add constant dtype equals `accumulator_dtype` and is
  broadcast-compatible with the convolution output.
- Right-shift amount is a scalar integer Relay `Constant`, is non-negative,
  and is less than the accumulator bit width.
- Clip bounds fit within the signed or unsigned range of `output_dtype`.
- Final cast and composite result dtype equal `output_dtype`.

### Shapes and layouts

- Input and convolution output are static rank-4 tensors.
- Data layout is exactly `NCHW`; kernel layout is exactly `OIHW`.
- `out_layout` is empty or `NCHW`.
- Batch is positive and divisible by `batch`.
- Input channels are positive and divisible by `block_in`.
- Output channels and `attrs.channels` are positive and divisible by
  `block_out`.
- Weight shape is statically consistent with output channels, input channels,
  and the declared kernel size.

The first slice accepts a `3x3` kernel, stride `(1, 1)`, dilation `(1, 1)`,
groups `1`, and symmetric padding equivalent to `(1, 1, 1, 1)`. Broader
values require their own lowering and runtime evidence before the predicate is
expanded.

### Optional post-convolution constant

- `nn.bias_add` uses the output-channel axis of the NCHW result.
- `add` accepts a constant only on the right-hand side in this first pattern.
- The constant is scalar, channel-only, or otherwise statically
  broadcast-compatible with the NCHW convolution output.

Predicate traversal must identify operators by `tvm.ir.Op` and their names,
not by positional assumptions that would confuse the optional bias/add forms.

## Pattern Table Contract

```python
def pattern_table(config=None):
    """Return VTA patterns ordered from most specific to least specific."""
```

- With no argument, the function snapshots `vta.get_env()` at call time.
- Passing an explicit immutable `VTACompilerConfig` supports deterministic
  tests and later compiler validation.
- It returns a new list on each call containing:

```python
[("vta.qnn_conv2d", qnn_conv2d_pattern(), predicate)]
```

- Pattern tables are not registered as an import side effect.
- `register_byoc()` will own process-global registration in the external
  codegen module. `partition_for_vta` uses the table directly, as CMSIS-NN
  does, so partitioning remains usable and testable before codegen exists.
- Registering the table later uses TVM's
  `tvm.relay.op.contrib.register_pattern_table` under compiler name `vta`.

## Public Partitioning API

```python
def partition_for_vta(
    mod: tvm.IRModule,
    params: Optional[Dict[str, tvm.runtime.NDArray]] = None,
    mod_name: str = "default",
) -> tvm.IRModule:
    ...
```

Boundary validation follows `SPEC-vta-byoc-contract.md`:

- Non-`IRModule` input raises `TypeError`.
- `params` must be `None` or a mapping accepted by
  `bind_params_by_name`; invalid values raise `TypeError` or `ValueError`
  before Pass execution.
- `mod_name` must be a non-empty string without control characters.
- Parameters are bound into `main` before type inference and matching.

The function assembles one `tvm.transform.Sequential`:

```text
InferType
  -> MergeComposite(pattern_table(config))
  -> AnnotateTarget("vta")
  -> MergeCompilerRegions
  -> PartitionGraph(mod_name=mod_name)
  -> InferType
```

`AnnotateTarget` uses TVM's default `include_non_call_ops=True`, matching the
standard BYOC flow. `MergeCompilerRegions` is explicit so adjacent accepted
composites can later become one VTA compiler region without changing this
public pipeline.

If the module already contains a global function with `Compiler="vta"`, the
function treats it as already partitioned: after public validation and
`InferType`, it returns a structurally equivalent module without applying the
partition sequence again. This makes repeated calls idempotent and avoids
nested or duplicate VTA regions.

## Output Invariants

For the approved supported fixture:

- Exactly one outlined global function has `Compiler="vta"`.
- That function has `Composite="vta.qnn_conv2d"` within its body and carries
  `Primitive=1`, `Inline=1`, and a deterministic `global_symbol` prefixed by
  `mod_name`.
- Constant convolution weight and optional constant bias/add belong to the
  outlined function according to `PartitionGraph` constant-binding behavior.
- `abs` and `transpose` remain in host `main`.
- The host/VTA call boundary has typed int8 tensors.

For the approved near-miss fixture, no `Compiler="vta"` global function is
created because its convolution weight is not constant.

## Tech Stack and Sources

- TVM version pinned by this workspace.
- Relay dataflow patterns from `tvm.relay.dataflow_pattern`.
- Pattern-table registration contract from
  `tvm/python/tvm/relay/op/contrib/register.py`.
- CMSIS-NN reference pipeline in
  `tvm/python/tvm/relay/op/contrib/cmsisnn.py`.
- Ethos-U capability-predicate and partition reference in
  `tvm/python/tvm/relay/op/contrib/ethosu.py`.
- VTA packed convolution constraints in
  `vta/python/vta/top/op.py`, `vta/python/vta/top/vta_conv2d.py`, and the
  existing graph-pack rewrite.

## Commands

Use the existing repository environment and scripts:

```bash
.envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_partition.py -q

.envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py \
  vta/tests/python/unittest/test_byoc_partition.py -q

.envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta/relay

./scripts/test_vta_fsim.sh

git -C tvm status --short
git -C vta status --short
```

No new script is required for this module.

## Project Structure

```text
vta/python/vta/relay/
├── __init__.py       # add partition_for_vta export
├── contract.py       # existing immutable compiler configuration
├── patterns.py       # qnn_conv2d pattern and capability predicate
└── partition.py      # public validation and standard BYOC Pass pipeline

vta/tests/python/unittest/
├── byoc_utils.py             # approved shared fixture
├── test_byoc_contract.py     # existing contract tests
└── test_byoc_partition.py    # pattern predicate and partition tests
```

## Code Style

Keep parsing separate from policy so unsupported shapes return `False` from
one readable predicate:

```python
def check_qnn_conv2d(call, config=None):
    config = config or VTACompilerConfig.from_env(vta.get_env())
    candidate = QnnConv2DCandidate.from_call(call)
    return candidate is not None and candidate.is_supported(config)
```

`QnnConv2DCandidate` may be a private immutable helper only if it removes
repeated optional-chain traversal. It must not become a second public
configuration model. Prefer small named validation helpers over nested
conditionals or assertions.

## Testing Strategy

Use TDD and the shared contract fixtures.

1. Pattern-shape tests verify supported, optional-bias, optional-add, and
   near-miss forms through `MergeComposite` outcomes.
2. Parameterized predicate tests independently vary each accepted attribute at
   its boundary and confirm unsupported values return `False` without raising.
3. Public API tests cover argument validation, parameter binding, deterministic
   symbols, and idempotence.
4. Structural partition tests verify exactly one VTA global, host fallback,
   constant ownership, attributes, and typed call boundaries.
5. Existing contract and FSIM tests guard against environment/runtime
   regressions. Numerical VTA execution remains out of scope until lowering
   and external codegen exist.

## Boundaries

- Always:
  - Match by local graph capability, never node name position or model name.
  - Keep predicate acceptance identical to the domain promised to lowering.
  - Return `False` for ordinary unsupported candidates.
  - Preserve host fallback and typed boundaries.
  - Keep upstream `tvm/` read-only.
- Ask first:
  - Add another composite or broaden kernel/stride/dilation/group support.
  - Change constant binding or compiler-region merging behavior.
  - Add a TVM patch, dependency, or build-system change.
- Never:
  - Call `graph_pack`, `get_subgraph`, or bitpack start/stop markers.
  - Register `relay.ext.vta` in this module.
  - Silently accept dynamic shapes or unsupported layouts.
  - Perform VTA compilation or hardware access during partitioning.

## Success Criteria

- `partition_for_vta` follows the documented standard BYOC Pass sequence.
- The supported fixture produces exactly one deterministic VTA partition with
  host operations outside it.
- The non-constant-weight near-miss produces no VTA partition.
- Every initial capability constraint has an accepted or rejected test.
- Repeated partitioning is structurally idempotent.
- Focused tests, contract tests, Python compilation, and FSIM regression pass.
- No external compiler stub exists and upstream TVM remains clean.
- Human review approves this spec before planning or implementation.

## Open Questions

None. The first capability slice intentionally accepts only the documented
3x3 stride-1 symmetric-padding quantized convolution domain; expansion follows
successful Relay-to-TIR and FSIM evidence.
