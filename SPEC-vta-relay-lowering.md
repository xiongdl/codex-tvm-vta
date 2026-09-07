# Spec: VTA Relay Lowering

## Objective

Implement the `vta-relay-lowering` module from `CAPABILITY_MAP-vta-byoc.md`.
The module consumes one typed Relay function outlined with `Compiler="vta"`,
legalizes its supported composite into VTA packed layouts, applies the existing
VTA TOPI schedule, and produces a VTA-compatible TIR `PrimFunc`.

This module replaces graph-wide marker/range packing with function-local
lowering. It does not register `relay.ext.vta`, build a runtime module, access
hardware, migrate applications, or delete `graph_pack`.

`SPEC-vta-graph-pack-pipeline.md` describes an earlier compatibility approach
that retained start/stop selection. The later approved architecture and this
spec supersede that approach for new BYOC compilation.

## Input Contract

The primary internal entry point is:

```python
def lower_vta_function(func, config=None):
    """Lower one outlined VTA Relay function to a scheduled TIR PrimFunc."""
```

`func` must be a typed `relay.Function` with:

- `Compiler="vta"`, `Primitive=1`, and a non-empty `global_symbol`;
- exactly one supported `Composite="vta.qnn_conv2d"` call;
- the static shapes, dtypes, constants, layouts, and attributes accepted by
  `check_qnn_conv2d`;
- tensor input/output types matching the unpacked NCHW host ABI.

`config` defaults to `VTACompilerConfig.from_env(get_env())`. Supplying an
explicit config makes tests deterministic and prevents lowering decisions from
silently consulting model/operator names.

Ordinary unsupported graphs are rejected before outlining. A malformed or
unsupported outlined function is a contract violation and raises `ValueError`
that names the rejected compiler/composite/operator or attribute. Wrong public
Python types raise `TypeError`.

## Relay Legalization Contract

Legalization operates only inside the supplied VTA function. It must not scan
the host module or use graph-global mutable state.

For the initial convolution slice it performs these local transformations:

1. Pack the NCHW input into `NCHW{BATCH}n{BLOCK_IN}c` using reshape and
   transpose.
2. Pack the constant OIHW weight into
   `OIHW{BLOCK_OUT}o{BLOCK_IN}i` using reshape and transpose.
3. Rewrite `nn.conv2d` with the packed data/kernel layouts and preserve the
   approved stride, padding, dilation, groups, channels, kernel size, and
   accumulator dtype.
4. Pack an optional constant `nn.bias_add` or right-hand `add` operand into the
   packed output layout and normalize `nn.bias_add` to `add`.
5. Preserve the scalar right shift, clip bounds, and final cast in packed form.
6. Unpack the result back to the original NCHW output shape at the external
   function boundary.

No bit packing is introduced in the first slice because the approved contract
currently requires the environment's int8 weight dtype. Padding unsupported
channels is also forbidden: divisibility is established by the partition
predicate and revalidated during lowering.

Legalization is assembled from named Relay passes so each responsibility is
testable independently:

```text
InferType
  -> ValidateVTAExternalFunction
  -> LegalizeVTAQnnConv2D
  -> InferType
  -> ValidatePackedVTAFunction
```

The transformed function retains its external `global_symbol` and compiler
identity until converted to TIR. Its parameter and return ABI remains unpacked
NCHW; packed tensors are local expressions.

## TE and TIR Lowering Contract

The pinned TVM checkout provides `relay.backend.te_compiler.get().lower`, which
lowers a primitive Relay function for an explicit target and invokes the TOPI
schedule selected by the reduction anchor. VTA uses this interface with the
full `ext_dev -device=vta` target so `schedule_conv2d_packed` is selected. The
generic UMA pattern of calling the target-less `relay.backend.LowerToTE` and
then `te.create_prim_func` is not sufficient because it loses the VTA target
key and bypasses VTA scheduling and GEMM tensorization.

The lowering sequence is:

```text
legalized Relay Function
  -> strip BYOC dispatch attrs from an internal packed-core Relay function
  -> relay.backend.te_compiler.get().lower(full VTA target)
  -> existing VTA TOPI schedule_conv2d_packed selected by the conv anchor
  -> verify one GEMM-tensorized packed-convolution TE schedule
  -> tvm.lower under existing vta.build_config passes
  -> scheduled VTA TIR PrimFunc
```

The resulting `PrimFunc` must:

- preserve the Relay `global_symbol`;
- carry the configured VTA/ext_dev target and original Relay attributes needed
  by downstream codegen;
- expose host-visible input/output buffers with deterministic ordering;
- contain evidence of the VTA tensorized GEMM/intrinsic path after the
  appropriate lowering stage;
- contain no Relay functions, composite wrappers, graphpack markers, or
  start/stop selection state.

Constants discovered by the TE compiler remain explicit lowering artifacts;
the exact runtime ownership/serialization policy belongs to
`vta-external-codegen` and `vta-runtime-integration`.

## Public Surface

The lowering entry point is internal to the backend and is not added to
`vta.relay.__all__`. The only public user entry point remains
`partition_for_vta`. The next module imports `lower_vta_function` directly
from `vta.relay.transform` when implementing `relay.ext.vta`.

No global compiler hook is registered on import. Existing VTA TOPI strategy
registration remains unchanged.

## Tech Stack and Version Baseline

- TVM source revision: `eeebcfa0a`.
- VTA source baseline: `7a9ad28` plus the committed BYOC partition series.
- Python 3.11 from `.envs/tvm-vta-env`.
- Relay `DFPatternCallback`/`rewrite` for composite-local legalization.
- `relay.backend.te_compiler.get().lower` from the pinned TVM TE compiler.
- Existing `vta.top.vta_conv2d.schedule_conv2d_packed`.
- Existing `vta.build_config` and `vta.transform` TIR passes.

Primary repository sources:

- `tvm/src/relay/backend/te_compiler_cache.cc` defines `ScheduleBuilder` and
  confirms that `TECompiler.lower` selects the anchor TOPI schedule for the
  supplied target; it also confirms target-less `LowerToTE` is unscheduled.
- `tvm/python/tvm/relay/backend/contrib/uma/api/lower.py` provides the closest
  official Relay-to-TIR staging reference, but its unscheduled
  `te.create_prim_func` step is intentionally not copied for VTA.
- `tvm/python/tvm/relay/backend/contrib/ethosu/legalize.py` demonstrates
  composite-function rewriting with typed `DFPatternCallback` objects.
- `vta/python/vta/top/graphpack.py` is behavioral evidence for packed layout
  permutations only; the new implementation must not import it.
- `vta/python/vta/top/op.py` and `vta/python/vta/top/vta_conv2d.py` define the
  packed convolution strategy, compute, schedule, and tensorization path.
- `vta/python/vta/build_module.py` defines the required VTA TIR pass pipeline.

## Commands

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_lowering.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py \
  vta/tests/python/unittest/test_byoc_partition.py \
  vta/tests/python/unittest/test_byoc_lowering.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta/relay

./scripts/test_vta_fsim.sh
git -C tvm status --short
git -C vta diff --check
```

## Project Structure

```text
vta/python/vta/relay/
├── contract.py       # compiler/environment contract
├── patterns.py       # eligibility domain; source of accepted composite name
├── partition.py      # BYOC region selection and outlining
└── transform.py      # local Relay legalization and scheduled TIR lowering

vta/tests/python/unittest/
├── byoc_utils.py
├── test_byoc_partition.py
└── test_byoc_lowering.py
```

The module should remain focused. A second production file is justified only
if Relay legalization and TE/TIR orchestration cannot remain reviewable in one
file without circular imports.

## Code Style

Validation uses guards and stable diagnostics; capability failures never rely
on assertions:

```python
def lower_vta_function(func, config=None):
    if not isinstance(func, relay.Function):
        raise TypeError("func must be a tvm.relay.Function")
    config = config or VTACompilerConfig.from_env(get_env())
    validated = validate_vta_external_function(func, config)
    legalized = legalize_vta_function(validated, config)
    return lower_legalized_vta_function(legalized, config)
```

Private helpers name the transformation they perform. Layout strings and the
composite name are derived from the compiler config/constants rather than
duplicated at call sites.

## Testing Strategy

Tests use the existing supported/near-miss fixture and inspect each stage:

1. Contract tests reject wrong Python types, missing/mismatched attributes,
   malformed composite bodies, and explicit config mismatches.
2. Relay tests lock input/weight/bias packing permutations, packed layouts,
   unpacked external ABI, preserved quantization tail, typing, and structural
   determinism.
3. TE/TIR tests prove VTA's packed convolution implementation and schedule are
   selected. Merely obtaining any `PrimFunc` is insufficient.
4. Lowering tests inspect symbol/target/attribute propagation and required VTA
   intrinsic or coprocessor evidence at the agreed stage.
5. Existing contract, partition, Python compilation, and FSIM suites form the
   regression gate.

Tests must not register `relay.ext.vta`, touch hardware, use network access,
or modify the pinned TVM checkout.

## Boundaries

- Always:
  - Revalidate outlined functions before lowering.
  - Keep the host ABI unpacked and packing local to a VTA function.
  - Apply the existing VTA TOPI schedule and TIR build passes.
  - Keep predicate and lowering domains exactly aligned.
  - Preserve deterministic symbols and explicit configuration behavior.
- Ask first:
  - Broaden the supported composite/operator/attribute domain.
  - Change the host/VTA ABI or constant ownership model.
  - Add a TVM patch, dependency, artifact format, or new runtime entry point.
- Never:
  - Import or call `graph_pack`, `get_subgraph`, or marker-based helpers.
  - Select regions using operator names, indices, models, or start/stop state.
  - Register `relay.ext.vta` in this module.
  - Accept a function whose packed schedule cannot be produced.
  - Access VTA hardware during legalization or lowering.

## Success Criteria

- The approved `vta.qnn_conv2d` partition legalizes to a typed packed Relay
  function with the same unpacked external ABI.
- Optional bias forms and quantization tail retain their specified semantics.
- Lowering deterministically produces a scheduled VTA `PrimFunc` with the
  required symbol, target, attributes, and VTA tensorization/intrinsic evidence.
- Every malformed or unsupported outlined-function boundary has a stable
  `TypeError` or `ValueError` test.
- No graphpack marker/range mechanism or external compiler registration is
  introduced.
- Contract, partition, lowering, compilation, and FSIM regression gates pass;
  the TVM checkout remains clean.

## Open Questions

None. The Task 4 spike established `TECompiler.lower` as the target-aware
scheduling bridge and verified `TensorIntrin(name=GEMM)` on the convolution
stage without modifying TVM.
