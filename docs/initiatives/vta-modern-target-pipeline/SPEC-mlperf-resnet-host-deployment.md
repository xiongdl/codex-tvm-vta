# Spec: MLPerf ResNet HOST Deployment

Module id: `mlperf-resnet-host-deployment`

Status: Approved by the user on 2026-09-09

## Objective

Provide a self-contained HOST deployment example for the MLPerf Tiny v1.4
Image Classification ResNet-8 model. The example imports the committed
floating-point `pretrainedResnet.tflite` model with the pinned TVM frontend,
quantizes it through the approved deterministic VTA quantization flow, builds a
pure-LLVM reference and a mixed `VTA + LLVM` artifact from the exact same
quantized Relay module, exports and reloads both, and verifies identical results
on ten committed CIFAR-10 PNG samples while FSIM proves accelerator activity.

The example demonstrates the independent `libtvm-vta-ext` compiler pipeline on
a real model. It is not an accuracy benchmark, performance benchmark, training
workflow, general compiler CLI, FVP deployment, or TVM `c` target example.

## Application Contract

### Fixed compilation flow

The application performs these stages in order:

```text
pretrainedResnet.tflite
  -> pinned TVM TFLite frontend
  -> bind model parameters
  -> relay.quantize(global_scale=8.0, skip_conv_layers=[0])
  -> retain one immutable quantized IRModule as the common source
      |-> relay.build for pure LLVM
      `-> partition_for_vta -> relay.build for VTA + LLVM
  -> export both artifacts
  -> reload both artifacts
  -> execute ten PNG inputs
  -> compare tensors and classifications
  -> verify VTA routing and FSIM activity
```

The approved quantization configuration is:

```python
with relay.quantize.qconfig(
    calibrate_mode="global_scale",
    global_scale=8.0,
    skip_conv_layers=[0],
):
    quantized = relay.quantize.quantize(mod, params=params)
```

CIFAR-10 is not calibration input. The two build branches must derive from the
same quantized IRModule; neither branch may rerun quantization or mutate the
other branch's reference module.

The application explicitly calls `vta.relay.partition_for_vta()` once for the
mixed branch and then invokes standard `relay.build`. Graph Executor is the only
executor in scope. LLVM is the only host and fallback target in scope.

### Model contract

The committed source artifact is:

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v1/
  model/pretrainedResnet.tflite
```

It is copied byte-for-byte from:

```text
vta/apps/mlperf_tiny_benchmark/tiny-v1.4/
  benchmark/training/image_classification/trained_models/
  pretrainedResnet.tflite
```

The local `tiny-v1.4` tree is a source reference only and is not committed.
`model/README.md` records the MLPerf Tiny v1.4 provenance, source-relative path,
original SHA-256, unchanged status, and TVM-side quantization policy. The app
also carries the applicable MLPerf Tiny Apache-2.0 license text.

Import validation must assert the actual model contract rather than infer it
from the current training script:

- one `float32` input with static shape `[1, 32, 32, 3]`;
- one classification output with final dimension 10;
- nine convolution layers in the imported reference topology;
- channel progression compatible with the expected 16/32/64-channel ResNet-8
  artifact after the RGB input layer;
- only operators supported by the pinned TVM TFLite frontend.

Unexpected model bytes, shape, dtype, channel structure, or operator topology is
an actionable failure. The application must not switch to another model, pad
channels, edit the graph, or weaken routing expectations automatically.

### Partition routing contract

After quantization and VTA partitioning:

- the skipped RGB first convolution remains on LLVM;
- the eight subsequent eligible `1x1` or `3x3`, stride-one or stride-two
  convolutions become eight separate VTA functions;
- every VTA function contains exactly one approved convolution composite;
- residual add, activation not fused into the approved composite, pooling,
  flatten, dense, softmax, and other unsupported work remains on LLVM;
- symbols are deterministic for the fixed module name;
- no GraphPack annotation, operator range, `relay.ext.vta`, Collage, AutoTVM, or
  runtime cost search participates.

The application reports the partition count, symbols, supported composite
summary, and LLVM fallback presence before building. A count or structure
mismatch is a failed deployment validation, not a warning.

### HOST artifacts

The application produces two non-committed host artifacts in its ignored build
output directory:

- pure LLVM reference;
- mixed `VTA + LLVM`.

Both follow the mandatory lifecycle:

```text
relay.build -> factory.export_library -> tvm.runtime.load_module
  -> GraphExecutor
```

The mixed artifact contains all expected VTA region symbols and the approved
configuration fingerprint checks. Export/reload must not require
`relay.ext.vta` or retain Python compiler callbacks. `libvta_fsim` is loaded
explicitly by importing `vta.testing.simulator` before mixed execution, not by
`import vta` or by compiler hooks.

### Input and result contract

Exactly ten committed PNGs are used, one for each CIFAR-10 class. They are
selected from the official CIFAR-10 `test_batch` by scanning its original order
and taking the first occurrence of labels 0 through 9.

Each PNG is lossless RGB, `32x32`, and 8-bit per channel. A committed manifest
records:

- PNG filename;
- original zero-based test index;
- numeric label and class name;
- original CIFAR filename;
- PNG SHA-256;
- dataset source, version, attribution, and license.

At runtime, decoding produces `float32` NHWC `[1, 32, 32, 3]` with pixel values
unchanged in `[0, 255]`. There is no resize, crop, channel swap, division by 255,
mean subtraction, or standardization.

For every input:

- the pure-LLVM and `VTA + LLVM` output tensors have identical shape and dtype;
- their values are elementwise equal;
- their top-1 class indices are equal.

The pure-LLVM result of the same quantized Relay module is the sole numerical
reference. This module does not compare with the floating-point TFLite runtime,
evaluate quantization accuracy, require correct ground-truth classification, or
calculate official MLPerf metrics.

FSIM profiler state is cleared before mixed execution. After running the sample
set, GEMM count, weight-load bytes, and output-store bytes must all be positive.
Pure-LLVM execution must not cause VTA profiler activity.

## User-Facing Entry Point

The deliverable contains one documented Python application entry point with
fixed repository-relative defaults. Running it performs the complete build,
export, reload, execution, and comparison workflow and exits nonzero on any
contract failure.

This entry point is an application example, not a general VTA CLI or TVMC
integration. Planning may choose its filename and a small number of operational
flags such as an output directory, but must not expose hardware capability,
operator-range, tuning, or partition-policy controls.

## Tech Stack And Dependencies

- Repository-pinned TVM Python and native libraries with LLVM enabled.
- `libtvm-vta-ext` and `libvta_fsim` built from the same `VTA_CONFIG_FILE`.
- Python 3.11 environment from existing repository setup automation.
- `tflite` FlatBuffer schema package for `relay.frontend.from_tflite`.
- Pillow for deterministic PNG decoding and validation.
- NumPy and pytest already present in the repository environment.

TensorFlow, TFLite Runtime, scikit-learn, h5py, MLPerf training requirements,
CMSIS-NN, FVP, Docker FVP wrappers, and AutoTVM are not dependencies.

Compatible `tflite` and Pillow versions must be verified against the pinned TVM
and then pinned in the existing `scripts/setup_tvm_vta_env.sh`; implementation
must not silently install dependencies at application runtime.

## Commands

Prerequisite builds reuse existing automation:

```bash
./scripts/build_vta_lib.sh --target libtvm-vta-ext
./scripts/build_vta_lib.sh --target libvta_fsim
```

The application command will follow this fixed shape, with the exact script name
confirmed by planning:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py
```

Focused automated validation uses pytest under the same environment. The final
initiative gate remains `./scripts/test_vta_byoc.sh` after it is migrated to the
modern, FSIM-only scope.

## Project Structure

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v1/
  README.md                 Deployment prerequisites, command, and expected output
  run.py                    Fixed-purpose HOST deployment entry point
  model/
    pretrainedResnet.tflite Unmodified MLPerf Tiny v1.4 floating model
    README.md               Model provenance, checksum, and quantization policy
  samples/
    manifest.json           Deterministic indices, labels, filenames, hashes
    *.png                   Ten committed lossless CIFAR-10 inputs
  LICENSE.mlperf-tiny       Applicable upstream Apache-2.0 license
  tests/
    ...                     Import, preprocessing, routing, and integration tests
  build/                    Ignored generated artifacts and intermediate output
```

Reusable sample extraction, if required during implementation, belongs in a
focused documented script under repository `scripts/` after existing automation
is rechecked. The full CIFAR-10 dataset and local `tiny-v1.4` source tree remain
untracked and outside runtime requirements.

## Code Style

Stages expose explicit inputs and outputs rather than communicate through
mutable globals:

```python
quantized = import_and_quantize(model_path)
reference = build_export_reload(quantized, target="llvm", output_path=reference_path)
partitioned = vta.relay.partition_for_vta(quantized, mod_name="mlperf_resnet")
mixed = build_export_reload(partitioned, target=vta_llvm_targets, output_path=mixed_path)
compare_samples(reference, mixed, sample_manifest)
```

The snippet describes structure, not final function names. Paths use
`pathlib.Path`, validation failures name the artifact/sample/stage, and no broad
exception handler turns a contract failure into a warning. Model and sample
metadata are data, not executable input.

## Testing Strategy

### Fast tests

- Model and PNG SHA-256 values match committed provenance.
- Manifest contains exactly labels 0 through 9 once each with unique source
  indices and files.
- Every PNG decodes losslessly to the expected shape, dtype, RGB ordering, and
  raw CIFAR bytes when the optional full dataset is present.
- Preprocessing produces exact `float32 [1,32,32,3]` values in `[0,255]`.
- TFLite import validates input/output, operator, convolution, and channel
  contracts.
- Quantization is invoked once with the exact approved qconfig and yields a
  reusable typed IRModule.
- Partition inspection finds exactly eight single-convolution VTA functions and
  required LLVM fallback work.

### End-to-end HOST FSIM test

- Build and reload both Graph Executor artifacts.
- Run all ten PNGs through both artifacts.
- Require elementwise output equality and equal top-1 indices per sample.
- Require every expected VTA symbol in the reloaded mixed artifact.
- Require matching configuration fingerprints.
- Require positive FSIM GEMM, weight-load, and output-store activity.
- Require no AutoTVM execution, tuning-log access, GraphPack, legacy external
  callback, FVP, CMSIS-NN, or full CIFAR-10 dependency.

### Repository checks

- `python -m compileall` succeeds for the app and VTA package.
- `git diff --check` passes.
- `git -C tvm status --short` remains empty.
- Generated build artifacts, local source benchmark, and full CIFAR-10 remain
  untracked/ignored as appropriate.

## Boundaries

### Always

- Use the committed unmodified floating TFLite model as the source artifact.
- Produce both builds from one quantized Relay module.
- Export and reload both artifacts before comparing them.
- Validate exact routing, output equality, and real FSIM activity.
- Preserve deterministic model/sample provenance and preprocessing.
- Fail loudly when dependencies, artifact structure, symbols, fingerprints, or
  results violate the contract.

### Ask first

- Change model bytes, qconfig, global scale, skipped layers, sample indices,
  preprocessing, partition count, executor, host target, or comparison rule.
- Add an application option beyond operational path/output controls.
- Add or upgrade a Python dependency after compatible versions are pinned.
- Copy another upstream MLPerf source file into the committed app.

### Never

- Train, retrain, calibrate from CIFAR-10, or use the supplied quantized TFLite
  artifact.
- Select samples based on prediction quality.
- Download CIFAR-10 or MLPerf assets at runtime or during tests.
- Compare separately quantized graphs.
- Claim MLPerf accuracy, performance, energy, or submission compliance.
- Fall back silently when no VTA region executes or when results differ.
- Use TVM `Target("c")`, AOT, CRT, CMSIS-NN, FVP, TSIM, Collage, or AutoTVM.

## Success Criteria

1. The committed app is runnable without the local `tiny-v1.4` tree, full
   CIFAR-10 dataset, TensorFlow, TFLite Runtime, FVP, or CMSIS-NN.
2. The unmodified committed float model imports and quantizes once using
   `global_scale=8.0` and `skip_conv_layers=[0]`.
3. Partition inspection produces exactly eight deterministic, single-convolution
   VTA functions and preserves the expected LLVM fallback.
4. Pure LLVM and `VTA + LLVM` Graph Executor artifacts both export and reload
   through standard TVM APIs.
5. All ten deterministic PNG inputs produce elementwise-equal output tensors
   and equal top-1 indices between the two reloaded artifacts.
6. The mixed artifact passes its configuration fingerprint check and produces
   positive FSIM GEMM, weight-load, and output-store activity.
7. No legacy compiler callback, GraphPack, AutoTVM, custom model editing, or
   non-LLVM host target is used.
8. Focused tests and repository checks pass while the pinned TVM checkout stays
   clean.

## Dependencies And Deferred Work

- Depends on the approved `vta-target-extension`, `vta-relay-to-tir`, and
  `vta-tir-to-runtime` contracts.
- Provides end-to-end evidence required before `vta-modern-cutover` retires the
  legacy repository-owned path.
- General CLI integration, TVM `c` target, AOT/CRT, dataset-calibrated
  quantization, model-accuracy evaluation, AutoTVM, performance targets,
  multi-convolution VTA regions, FVP, CMSIS-NN, and physical hardware are
  deferred or explicitly out of scope.

## Open Questions

None.

## Approval Gate

The user must approve this spec before planning begins. Approval does not
authorize implementation.
