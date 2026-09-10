# Spec: VTA RelayToTIR

Module id: `vta-relay-to-tir`

Status: Approved by the user on 2026-09-09

## Objective

Replace GraphPack and the classic per-function `relay.ext.vta` callback with a
model-independent Relay partition pass and the `vta` TargetKind's modern
IRModule-at-a-time `RelayToTIR` hook.

The module accepts Relay produced by the repository's pinned TVM quantization
flow, identifies only operations supported by the active build-bound VTA
configuration, outlines one quantized convolution composite per VTA function,
and lowers every outlined VTA function to scheduled VTA PrimFuncs. Unsupported
Relay remains unchanged and compilable by the LLVM host target.

## Public Contract

### Partition API

Applications explicitly invoke partitioning after TVM quantization and before
standard `relay.build`:

```python
with tvm.transform.PassContext(opt_level=3):
    with relay.quantize.qconfig(calibrate_mode="global_scale"):
        quantized = relay.quantize.quantize(mod, params=params)

partitioned = vta.relay.partition_for_vta(
    quantized,
    mod_name="mlperf_resnet",
)
```

`partition_for_vta(mod, params=None, mod_name="default")` remains the public
entry point and must:

- accept a typed or untyped `IRModule` and return a typed `IRModule`;
- optionally bind parameters before capability matching;
- deterministically derive external symbols from `mod_name`;
- be idempotent when invoked repeatedly on an already partitioned module;
- perform capability-based matching without model-specific operator names,
  indices, start/stop ranges, or GraphPack annotations;
- outline exactly one VTA convolution composite per external Relay function;
- leave every unsupported or ambiguous expression available to LLVM;
- avoid registering or invoking `relay.ext.vta`.

Merely including `Target("vta")` in the target collection does not partition an
otherwise unannotated Relay module. The explicit partition call is required.

### Supported composite

One VTA region contains exactly this quantized structure:

```text
nn.conv2d
  -> optional nn.bias_add or add with a constant bias
  -> right_shift by a scalar constant
  -> clip to the active VTA output dtype range
  -> cast to the active VTA output dtype
```

The capability predicate accepts a candidate only when all of the following
hold:

- input and output tensor shapes are static and rank four;
- weights are compile-time constants;
- input, weight, accumulator, and output dtypes match the active
  `VTA_CONFIG_FILE`;
- input channels are divisible by `BLOCK_IN` and output channels by
  `BLOCK_OUT`;
- batch is divisible by `BATCH`;
- kernel is `1x1` or `3x3`;
- stride is one or two in both spatial dimensions;
- dilation is one and groups is one;
- padding is statically valid for the selected layout, kernel, and output
  shape;
- the right shift is a non-negative scalar smaller than accumulator width;
- clip bounds fit the configured output dtype.

The RGB first layer and any other near miss remain on LLVM. This release does
not insert channel padding to make an unsupported shape appear supported.

### Layout contract

The partitioner and RelayToTIR hook support both standard layout pairs:

- `NHWC` data with `HWIO` kernels;
- `NCHW` data with `OIHW` kernels.

The hook converts constant weights and region-local input/output tensors to and
from the active VTA packed layouts. Packed layouts never cross a VTA function
boundary, so the surrounding LLVM graph observes the same layout and tensor
type as before partitioning. Applications do not call `ConvertLayout` or
GraphPack to prepare VTA regions.

### RelayToTIR hook

The `vta` TargetKind supplies a typed `FTVMRelayToTIR` module pass. For every
outlined function with `Compiler="vta"`, it must:

1. Validate the complete function and composite contract before lowering.
2. Perform region-local layout legalization and constant packing.
3. Lower the legalized convolution through the repository's existing VTA TOPI,
   TE schedule, tensorization, and VTA TIR passes.
4. Emit scheduled PrimFuncs with deterministic symbols and the target/runtime
   attributes required by the downstream `TIRToRuntime` hook.
5. Preserve non-VTA Relay functions and unrelated IRModule contents.
6. Remove or replace handled VTA Relay functions according to the pinned TVM
   target-hook contract, without routing through TECompiler's legacy external
   callback.

The replacement semantics must strictly follow the pinned TVM Ethos-U
implementation. The native TargetKind hook may call one private,
module-at-a-time lowering bridge. That bridge must inspect all outlined VTA
functions and update each existing GlobalVar binding in place from a Relay
Function carrying `Compiler="vta"` to a target-annotated `tir.PrimFunc`. It
must return the fully updated IRModule before ordinary `LowerTE` runs, without
leaving, copying, or recreating any global or nested Relay Function carrying
`Compiler="vta"`.

As with Ethos-U, a qualified private bridge name is permitted, but the classic
exact-name callback `relay.ext.vta` is forbidden. No no-op sentinel or cache
compatibility callback may be registered under that exact name.

The hook processes all VTA regions in one IRModule invocation. It must not rely
on global mutable model state or on the order in which Relay functions happen
to be visited.

## Tech Stack

- Repository-pinned TVM Relay, dataflow-pattern, target-hook, TE, TOPI, and TIR
  APIs.
- Existing VTA environment/configuration, intrinsic, schedule, and lowering
  passes.
- Python for the public partition pipeline and capability predicate.
- C++17 inside `libtvm-vta-ext` for the registered target hook and any native
  IRModule-level integration required by the pinned TVM API.
- NumPy only where needed for compile-time constant packing; no new dependency.

## Commands

Focused validation follows the repository's existing environment convention:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/tests/python/unittest/test_byoc_partition.py \
  vta/tests/python/unittest/test_byoc_lowering.py
```

The extension build remains:

```bash
./scripts/build_vta_lib.sh --target libtvm-vta-ext
```

The final integration gate remains `./scripts/test_vta_byoc.sh` after the
initiative updates that existing script. Planning may refine focused test file
names but must reuse these build and environment entry points.

## Project Structure

```text
vta/python/vta/relay/patterns.py
    Composite patterns and side-effect-free capability predicates.

vta/python/vta/relay/partition.py
    Public, deterministic, idempotent partition pipeline.

vta/python/vta/relay/transform.py
    Region validation, layout legalization, constant packing, and reusable
    VTA lowering logic.

vta/src/compiler/
    Native IRModule-at-a-time RelayToTIR hook integrated into
    libtvm-vta-ext.

vta/tests/python/unittest/
    Pattern, partition, legalization, hook, and lowering contract tests.
```

Tests may extend existing BYOC-named files during migration, but new production
code and public documentation must use the modern target-hook terminology.

## Code Style

Capability checks return false for unsupported Relay; lowering validates again
and raises a precise error only for malformed functions already marked VTA:

```python
def check_quantized_conv2d(call, config):
    shape = static_conv_shape(call)
    if shape is None:
        return False
    return (
        shape.kernel in {(1, 1), (3, 3)}
        and shape.stride in {(1, 1), (2, 2)}
        and shape.input_channels % config.block_in == 0
        and shape.output_channels % config.block_out == 0
    )
```

Predicates must not mutate IR, consult model names, catch broad exceptions, or
duplicate hardware constants outside `VTACompilerConfig`. Legalization helpers
must have explicit input/output contracts and deterministic constant transforms.

## Testing Strategy

### Capability matrix

Parameterized tests cover the Cartesian boundary of:

- `1x1` and `3x3` kernels;
- stride one and two;
- both supported layout pairs;
- optional constant bias;
- aligned versus unaligned input/output channels;
- valid and invalid dtype, batch, group, dilation, padding, shift, clip, static
  shape, and constant-weight conditions.

Every rejection test asserts that the candidate stays on LLVM and does not fail
later in VTA lowering.

### Partition contracts

- One supported composite produces one external VTA function.
- Two adjacent supported composites produce two VTA functions, never a merged
  multi-convolution region.
- Mixed supported and unsupported graphs preserve topology, types, and host
  expressions.
- Repeated partitioning is structurally stable and symbol names are
  deterministic for the same `mod_name`.
- Binding params before matching produces the same partition as an equivalent
  module containing constants.
- No test or implementation requires GraphPack or `relay.ext.vta`.

### Legalization and lowering

- NHWC/HWIO and NCHW/OIHW candidates legalize to the same configured VTA packed
  compute semantics.
- Constant weights and optional bias are packed at compile time.
- Region output is unpacked to its original layout and checked type.
- All outlined functions in a multi-region IRModule become scheduled VTA
  PrimFuncs in one hook invocation.
- Emitted TIR contains the expected VTA tensorization/instruction structure and
  deterministic target/runtime attributes.
- Malformed pre-annotated VTA functions fail before partial mutation or codegen.

### Regression

- Existing VTA TOPI/TE unit tests remain green.
- The pinned TVM checkout remains clean.
- `python -m compileall`, `git diff --check`, and the scoped GraphPack retirement
  check pass.

## Boundaries

### Always

- Treat capability rejection as host fallback, not a compilation error.
- Validate outlined VTA functions again at the lowering boundary.
- Use the active build-bound VTA configuration as the only hardware capability
  source.
- Preserve original region boundary layouts and types.
- Process every VTA region in an IRModule deterministically.
- Keep the partition call explicit in application code.

### Ask first

- Add channel padding, dynamic shapes, a new dtype, kernel, stride, dilation, or
  grouped/depthwise convolution capability.
- Fuse multiple convolution composites into one VTA function.
- Put residual add, pooling, dense, softmax, or another standalone operator in a
  VTA region.
- Require applications to perform layout conversion or GraphPack-like graph
  rewriting.
- Change the public `partition_for_vta()` signature.

### Never

- Select regions by MLPerf operator name, ordinal, or source-model metadata.
- Allow packed VTA layouts to leak into LLVM regions.
- Claim support in the predicate and then fail on the same valid candidate in
  RelayToTIR.
- Restore or call the classic `relay.ext.vta` compiler callback.
- Modify the pinned TVM source tree.

## Success Criteria

1. `partition_for_vta()` outlines every and only supported candidate in the
   approved capability matrix, with one convolution composite per VTA function.
2. TFLite-style NHWC/HWIO and TVM-style NCHW/OIHW inputs both work without an
   application-level layout pass.
3. The registered `RelayToTIR` hook lowers every VTA function in a mixed
   IRModule to scheduled, tensorized VTA PrimFuncs while preserving LLVM Relay.
4. Unsupported candidates, including the RGB first layer and channel alignment
   near misses, remain compilable by LLVM.
5. Partitioning and lowering are deterministic, idempotent where applicable,
   independent of GraphPack, and independent of `relay.ext.vta`.
6. Focused structural and lowering tests pass against the active default VTA
   configuration with no changes in the pinned TVM checkout.

## Dependencies And Deferred Work

- Depends on the `vta-target-extension` target identity and registration
  boundary.
- Provides scheduled VTA PrimFuncs to `vta-tir-to-runtime`; runtime module
  generation and host FSIM execution are not implemented here.
- Full TFLite import, `global_scale` quantization orchestration, ten PNG inputs,
  pure-LLVM comparison, and end-to-end execution belong to
  `mlperf-resnet-host-deployment`.
- Multi-convolution fusion, AutoTVM, performance targets, hardware changes,
  CMSIS-NN, and FVP are out of scope.

## Open Questions

None.

## Approval Gate

The user must approve this spec before planning begins. Approval does not
authorize implementation.
