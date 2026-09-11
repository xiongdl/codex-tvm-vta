# Verification Evidence

Status: Complete on 2026-09-11

## Verified candidate identity

The final verification matrix ran against these exact repository states:

- Parent repository: `bfd679df7ddd1bfd10d3f19d44115cb253320445`
- VTA submodule: `e6443ae67fa28877476e5af954f652a4c2dfeccc`
- Pinned TVM submodule: `eeebcfa0ad4a6e9d49cce3ee6718ecbef0ee018f`

The parent repository, VTA, and TVM had no staged or unstaged tracked changes
after verification. TVM remained at its pinned commit and was not modified.
Only pre-existing untracked local environment, editor, full CIFAR-10, and
upstream MLPerf source files remained; none were added to the candidate.

## Target extension foundation

The VTA-owned compiler extension was built separately from the simulator with:

```text
./scripts/build_vta_lib.sh --target libtvm-vta-ext --jobs 2
```

Result: `vta/build/libtvm-vta-ext.dylib` was produced successfully on macOS.
With `PYTHONPATH=tvm/python:vta/python` and the default VTA configuration,
`import vta` loaded the extension and `Target("vta")` reported typed, non-null
`RelayToTIR` and `TIRToRuntime` target attributes. Loading was idempotent, and
runtime-only TVM imports did not search for or load the compiler extension.
Missing, unloadable, incomplete, and incorrectly typed extension cases retained
actionable diagnostics naming the rebuild command.

The target reports TVM's `kDLExtDev` device identity (12), keeping modern VTA
compilation distinct from the LLVM host/fallback target. The native hook uses
the private `vta.relay._relay_to_tir` IRModule bridge. Full `import vta`
registers that bridge, while runtime-only imports bypass it.

## Relay partitioning and lowering

The supported and rejected capability matrix covered 1x1 and 3x3 kernels,
stride 1 and 2, aligned static shapes, constant weights, supported bias forms,
and both NCHW/OIHW and NHWC/HWIO layouts. Supported adjacent candidates formed
separate deterministic one-convolution functions; near misses stayed on LLVM,
and repeated partitioning was structurally stable.

Previously recorded focused verification remained:

```text
pytest -q vta/tests/python/unittest/test_byoc_partition.py   # 42 passed
pytest -q vta/tests/python/unittest/test_byoc_lowering.py    # 43 passed
```

Lowering produced GEMM-tensorized PrimFuncs with packed tensors and constants
internal to each VTA region and restored the original external layout. The
module-level RelayToTIR tests covered zero, one, and multiple regions, in-place
GlobalVar replacement, nested outlining, non-VTA preservation, and validation
before mutation. No VTA-owned Relay function reached ordinary `LowerTE`.

## ABI fingerprint and runtime artifact

The canonical ABI fingerprint tests covered deterministic normalization and
sensitivity to every ABI-relevant definition and schema version. Compiler and
FSIM builds consumed the same generated fingerprint. Repeated matching checks
were side-effect free; mismatch diagnostics reported expected and actual values
and failed before allocation, command, or profiler activity.

Native TIRToRuntime verification covered one and multiple VTA PrimFuncs,
complete exported symbols, invalid-module rejection before code generation,
and direct LLVM host code generation without recursive public `tvm.build` use.
Compilation and export did not require FSIM to be loaded. Reloaded artifacts
resolved the VTA runtime ABI, matched pure LLVM output exactly, and produced
positive GEMM, load, and store activity when executed with FSIM.

## MLPerf ResNet HOST deployment

The committed model hash, model provenance/license material, ten deterministic
PNG hashes, and sample manifest were checked. The sample provenance records the
official CIFAR-10 source and its lack of a declared open-source license without
claiming one. When the local `test_batch` was available, all PNG pixels matched
the selected first occurrence of labels 0 through 9. The full CIFAR-10 dataset
and local `tiny-v1.4` source remained untracked.

The application imported the asserted floating ResNet-8 topology, quantized
the shared Relay module once with `global_scale=8.0` and
`skip_conv_layers=[0]`, and forked pure LLVM and mixed builds from that exact
module. Structural validation found exactly eight one-convolution VTA
partitions with the skipped first convolution and unsupported operators left on
LLVM. No TensorFlow, TFLite Runtime, GraphPack, AutoTVM execution, calibration,
FVP, CMSIS-NN, TVM `c` target, AOT, or CRT path was used.

The documented HOST command exported and reloaded both standard Graph Executor
artifacts. All 10 committed samples produced elementwise-identical output
tensors and matching top-1 indices. The eight expected VTA symbols were present,
and all required GEMM, weight-load, and output-store counters were positive.

## Modern cutover

The active ResNet exporter, Darknet detection tutorial, MLPerf application, and
documentation use full `import vta`, one explicit capability partition, and
`Target("vta", host=...)` for mixed Relay compilation with LLVM fallback. The
documentation distinguishes that target from preserved low-level
`tvm.target.vta()` and `ext_dev -device=vta` workflows.

The public classic registration entry, external-compiler constant, callback
registration, callback backend module, and callback-only tests were removed.
The permanent aggregate source scan found zero active legacy callback or
GraphPack/range references. Its exclusions remain limited to the dedicated
absence test, build/third-party content, and the local untracked MLPerf source
and full CIFAR-10 data allowed by the approved specification.

Representative low-level `vta.build_config()`, `vta.build()`, `vta.lower()`,
TE/TIR, instruction, FSIM, TSIM, `tvm.target.vta()`, and `ext_dev` workflows
remained available and green.

## Final verification matrix

The independent final run reported:

```text
Aggregate structural suites: 247 passed
FSIM suite:                    24 passed
TSIM suite:                    12 passed
Python compileall:             passed
Permanent zero-reference scan: passed
Scoped repository checks:      passed
Documented MLPerf HOST/FSIM:    passed
```

The aggregate's modern Relay execution path used FSIM; TSIM was exercised only
as a preserved low-level regression. `git diff --check` passed, all three
tracked worktrees were clean, and inspection found no unapproved dependency,
target, model, generated tracked artifact, or TVM source change.

All Tasks 1-15 and Checkpoints A-E have passing evidence. The implementation
is ready for independent review. No merge, push, pull-request mutation, tag,
release, deployment, or other Ship action was performed.
