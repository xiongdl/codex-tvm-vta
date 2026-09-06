# Spec: VTA BYOC Contract

## Objective

Define the stable boundary for a complete VTA Relay BYOC compiler extension.
This module establishes names, types, configuration, supported-capability
rules, error behavior, and an end-to-end fixture before partitioning or
external-codegen implementation begins.

The contract deliberately separates the Relay external compiler identity from
the existing VTA execution target:

```text
BYOC compiler tag:       vta
Registry entry:          relay.ext.vta
Execution target:        ext_dev -device=vta -keys=vta,cpu ...
Runtime device type:     kDLExtDev
Host target:             Environment.target_host
```

This preserves the established VTA device/runtime behavior while allowing TVM
to discover and invoke VTA through its standard BYOC compiler hook.

## Public API Contract

### Partitioning entry point

```python
from vta.relay import partition_for_vta

partitioned = partition_for_vta(
    mod,
    params=params,
    mod_name="default",
)
```

```python
def partition_for_vta(
    mod: tvm.IRModule,
    params: Optional[Dict[str, tvm.runtime.NDArray]] = None,
    mod_name: str = "default",
) -> tvm.IRModule:
    ...
```

- The input and output are `IRModule` objects.
- Parameters are bound before capability matching.
- Supported regions become primitive global Relay functions carrying
  `Compiler="vta"`, `Primitive=1`, `Inline=1`, and a deterministic
  `global_symbol` generated through `PartitionGraph(mod_name=mod_name)`.
- Unsupported expressions remain in the host `main` function.
- Calling the function repeatedly on a module that has already been
  partitioned must not duplicate VTA regions.

The API lives in `vta.relay`, not `vta.top`: graph partitioning is a Relay
compiler integration boundary rather than a TOPI operator implementation.

### Backend registration

```python
import vta

vta.register_byoc()
```

```python
def register_byoc() -> None:
    """Register VTA BYOC hooks idempotently in the current TVM process."""
```

- Registration installs the pattern table and `relay.ext.vta` compiler hook.
- Repeated registration is a no-op and does not replace a foreign registry
  entry silently.
- Importing `vta` may register the backend automatically only if registration
  has no hardware access, compilation, filesystem writes, or process-global
  configuration changes beyond TVM registries.
- Tests must also be able to call the explicit entry point so registration
  behavior is observable and independently verifiable.

### Build contract

After partitioning, users build a heterogeneous module with the existing VTA
execution target and host target:

```python
env = vta.get_env()
target = tvm.target.Target(env.target, host=env.target_host)

with tvm.transform.PassContext(opt_level=3):
    factory = relay.build(partitioned, target=target, params=params)
```

The VTA external compiler consumes one outlined, typed Relay function and
returns a `tvm.runtime.Module` whose exported symbol exactly matches the Relay
function's `global_symbol`. The resulting Relay build artifact contains both
host code and the imported VTA module.

## Compiler Configuration Contract

The initial version derives hardware-dependent values from the active
`vta.Environment`:

```text
batch factor       Environment.BATCH
input block        Environment.BLOCK_IN
output block       Environment.BLOCK_OUT
input dtype        Environment.inp_dtype
weight dtype       Environment.wgt_dtype
accumulator dtype  Environment.acc_dtype
output dtype       Environment.out_dtype
execution target   Environment.target
host target        Environment.target_host
```

No second independent set of PassContext options is introduced in the first
increment. A function partitioned under one active VTA configuration must be
compiled under an equivalent configuration; the external compiler validates
the relevant attributes and fails before lowering when they disagree.

Future compiler options, if needed, use the namespace
`relay.ext.vta.options`. They must be additive and must not duplicate hardware
configuration already owned by `vta.Environment`.

## Initial Capability Contract

The first end-to-end composite is named `vta.qnn_conv2d` and covers the
smallest useful quantized convolution region accepted by VTA:

```text
input
  -> nn.conv2d(constant_weight, out_dtype=Environment.acc_dtype)
  -> [nn.bias_add or add(constant)]
  -> [right_shift / clip / cast sequence supported by existing VTA TOPI]
  -> output
```

Capability predicates must reject a candidate unless all of the following are
statically known and supported:

- Input and weight tensor ranks and shapes required by VTA packing.
- Batch/channel divisibility or a documented padding transformation.
- Constant convolution weights.
- Supported input, weight, accumulator, and output dtypes.
- Supported `groups`, strides, dilation, padding, data layout, kernel layout,
  and output layout.
- A static result type.
- A configuration compatible with the active `vta.Environment`.

Predicates return `False` for unsupported graphs; they do not raise for normal
capability misses. Malformed internal composite functions reaching the
external compiler are contract violations and raise `ValueError` containing
the composite name and rejected attribute.

The exact accepted layouts, padding rules, and fused post-ops are specified in
`SPEC-vta-pattern-partition.md`; this contract requires that the predicate and
lowering accept exactly the same domain.

## External Compiler Contract

TVM discovers the backend using:

```text
relay.ext.vta : relay.Function -> tvm.runtime.Module
```

The hook must:

1. Validate `Compiler`, `Composite`, `global_symbol`, types, and active VTA
   configuration.
2. Lower only the supplied outlined function; it must not recursively invoke
   BYOC partitioning.
3. Use the existing VTA TE/TIR schedules, intrinsic lowering passes, and
   `ext_dev` target path where applicable.
4. Return a runtime module exporting exactly the requested symbol and owning
   all code/data needed by that partition.
5. Avoid hardware access during compilation.
6. Support serialization/export and reloading through the same artifact path
   used by Relay build output.

For multiple VTA partitions, each invocation produces a uniquely named module
function; symbol generation must be deterministic for the same partitioned
module and `mod_name`.

## Error Semantics

- Wrong public input type: `TypeError`.
- Invalid public option or empty `mod_name`: `ValueError`.
- Ordinary unsupported Relay pattern: leave it on the host without warning.
- Missing VTA runtime/compiler registration at build time: `RuntimeError`
  naming `relay.ext.vta` and the registration action.
- Inconsistent environment or outlined function contract: `ValueError` before
  code generation.
- Unsupported node that bypassed capability checking: `ValueError` naming the
  composite and operator.

Errors must not be converted to assertions at public boundaries because
assertions may be disabled and provide unstable diagnostics.

## Tech Stack and Version Baseline

- Python 3.11 from `scripts/setup_tvm_vta_env.sh`.
- The TVM source and libraries pinned in this workspace.
- Relay BYOC passes: `InferType`, `MergeComposite`, `AnnotateTarget`,
  `MergeCompilerRegions`, and `PartitionGraph`.
- TVM external compiler registry contract documented in
  `tvm/docs/dev/how_to/relay_bring_your_own_codegen.rst` and implemented by
  `tvm/src/relay/backend/te_compiler.cc`.
- Existing VTA TOPI, schedules, TIR transforms, runtime, FSIM, and TSIM.

UMA is a reference for Relay-to-TIR staging, but its dynamic target
registration is not used directly in the first version: this TVM baseline's
UMA target registration assigns `kDLCPU`, while existing VTA execution uses
`kDLExtDev` through the `ext_dev` target kind.

## Commands

Use existing repository scripts rather than adding one-off helpers:

```bash
./scripts/build_vta_lib.sh --target libvta_fsim
./scripts/test_vta_fsim.sh
./scripts/test_vta_fsim.sh --integration

.envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py -q

git -C tvm status --short
git -C vta status --short
```

The focused test path is introduced by later implementation modules. The
existing FSIM scripts remain the canonical build/runtime verification entry
points and may be minimally extended when BYOC tests become runnable.

## Project Structure

```text
vta/python/vta/relay/
├── __init__.py       # public partitioning API
├── backend.py        # idempotent BYOC registration and compiler hook
├── patterns.py       # pattern definitions and capability predicates
└── transform.py      # Relay legalization/layout passes

vta/python/vta/top/   # existing compute/schedule implementations reused by lowering
vta/python/vta/transform.py  # existing VTA TIR lowering passes
vta/src/runtime/      # existing runtime/device integration
vta/tests/python/unittest/test_byoc_contract.py
```

Files are created only by their owning implementation module. This contract
does not require all proposed files to exist immediately.

## Code Style

Interfaces are typed and validation is performed at public boundaries:

```python
def partition_for_vta(mod, params=None, mod_name="default"):
    if not isinstance(mod, tvm.IRModule):
        raise TypeError("mod must be a tvm.IRModule")
    if not isinstance(mod_name, str) or not mod_name:
        raise ValueError("mod_name must be a non-empty string")
    return _partition_pipeline(mod_name)(bind_params(mod, params))
```

Pattern names use `vta.<capability>`. Registry names use `relay.ext.vta` and
future configuration uses `relay.ext.vta.options`.

## Testing Strategy

The contract fixture defines a small Relay module containing:

```text
host-supported pre-op -> supported quantized convolution -> host-only post-op
```

Contract tests, initially written to fail, verify:

1. Compiler registration is idempotent and discoverable.
2. Partitioning produces one `Compiler="vta"` function with deterministic
   symbol and leaves unsupported operators on the host.
3. A near-miss graph remains entirely on the host.
4. Public argument and configuration errors follow the specified exception
   types.
5. Later modules progressively make lowering, runtime-module creation,
   export/reload, and FSIM numerical execution assertions pass using the same
   fixture.

Each downstream spec adds tests to this fixture without weakening or skipping
earlier assertions.

## Boundaries

- Always:
  - Keep compiler identity and execution target distinct.
  - Keep the pinned `tvm/` checkout unmodified.
  - Reject unsupported candidates during capability matching.
  - Preserve deterministic symbols and host fallback.
  - Reuse existing repository build/test scripts.
- Ask first:
  - Change the `vta` compiler tag or `relay.ext.vta` registry name.
  - Change VTA from `kDLExtDev` to another runtime device type.
  - Introduce a new artifact format or runtime executor.
  - Add TVM patches or new dependencies.
- Never:
  - Use model-specific operator indices or start/stop node names.
  - Access hardware while partitioning or compiling.
  - Accept a graph in the pattern predicate that lowering cannot compile.
  - Fall back silently after a graph has been outlined as VTA.

## Success Criteria

- Compiler tag, registry hook, execution target, device type, and host target
  have one unambiguous definition.
- Public partitioning and registration signatures are documented and additive.
- Initial supported and rejected graph domains are testable.
- Error behavior is consistent across partitioning and external compilation.
- The end-to-end fixture can be reused from partition tests through FSIM.
- The contract does not require modifying upstream TVM.
- Human review approves this spec before planning or implementation begins.

## Open Questions

None. The user confirmed a complete VTA BYOC/external-codegen implementation,
ARM-style `partition_for_vta` naming, capability/pattern-based selection, and
removal of the start/stop mechanism.
