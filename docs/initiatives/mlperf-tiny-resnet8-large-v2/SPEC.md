# Spec: MLPerf Tiny ResNet8 Large V2 Deployment

Status: Proposed

## Objective

Add a self-contained deployment at
`vta/apps/mlperf_tiny_benchmark/image_classification_v2/` for the MLPerf Tiny
v1.4 floating ResNet8 Large model. The application must provide the same user
capabilities as `image_classification_v1`: authenticated source assets,
deterministic TFLite import and TVM quantization, explicit HOST/VTA routing,
reloadable LLVM/C Graph Executor bundles, exact ten-sample execution on FSIM
and TSIM, and documented commands.

The new deployment is an execution-equivalence example. It does not report
accuracy, latency, energy, or an official MLPerf result.

## Authoritative Inputs

- Behavioral template: VTA commit
  `7add5bf069cde2172e0b70592a549e854c293f66`, directory
  `apps/mlperf_tiny_benchmark/image_classification_v1/`.
- Local MLCommons source artifact:
  `.envs/tiny-v1.4/benchmark/training/image_classification/trained_models/pretrainedResnet_large_float.tflite`.
- Official project: <https://github.com/mlcommons/tiny>.
- Official image-classification reference implementation:
  <https://github.com/mlcommons/tiny/tree/master/benchmark/training/image_classification>.
- MLPerf Tiny benchmark rules identify CIFAR-10/ResNet as the image
  classification workload:
  <https://github.com/mlcommons/tiny/blob/master/benchmark/MLPerfTiny_Rules.adoc>.

The local source model is copied byte-for-byte into the V2 application. Its
approved contract is:

| Property | Required value |
| --- | --- |
| Filename | `pretrainedResnet_large_float.tflite` |
| Size | `1,929,208` bytes |
| SHA-256 | `fb17ae9c1b6d0e5bd97f0f35024f207556261d7310b249716c87cc0628214b0e` |
| FlatBuffer | TFLite v3, one subgraph |
| Input | `serving_default_input_5:0`, float32 NHWC `[1, 32, 32, 3]` |
| Output | `StatefulPartitionedCall:0`, float32 `[1, 10]` |
| Operators | Same ordered 16-operator ResNet8 topology as V1 |
| Convolution outputs | `40/40/40/80/80/80/160/160/160` |

The source bytes remain floating point. Deployment-time quantization retains
the V1 policy exactly: `global_scale`, scale `8.0`, and
`skip_conv_layers=[0]`, with no calibration dataset.

## Functional Contract

### Application layout

V2 contains the same tracked content categories as V1, with model-specific
names and contracts adapted for Large:

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v2/
  LICENSE.mlperf-tiny
  README.md
  graph_artifacts.py
  model_pipeline.py
  run.py
  runtime.py
  model/
    README.md
    pretrainedResnet_large_float.tflite
  samples/
    manifest.json
    00-airplane.png ... 09-truck.png
  tests/
    test_assets.py
    test_graph_artifacts.py
    test_host_deployment.py
    test_model_pipeline.py
    test_tsim_deployment.py
```

Generated `build/`, bytecode, pytest caches, simulator traces, and `.envs/`
content remain ignored and untracked.

### Asset provenance

- The committed Large model must match the approved size and SHA-256.
- `model/README.md` must record the MLPerf Tiny v1.4 source-relative path,
  exact hash, tensor/operator/channel contract, Apache-2.0 notice, and
  deployment-time quantization policy.
- The MLPerf Tiny license and ten CIFAR-10 sample PNGs/manifest are identical
  to V1 byte-for-byte. V2 asset tests independently authenticate them.
- No network access or `.envs/` lookup is required after the source model has
  been committed.

### Import, quantization, and routing

- Import rejects any model whose hash, tensor names, shapes, dtypes, operator
  order, or convolution channels differ from the approved contract.
- The Relay input/output shapes and dtypes remain `[1,32,32,3]` float32 and
  `[1,10]` float32.
- The model is quantized once, then forked into reference and mixed graphs.
- The mixed graph uses module name `mlperf_resnet_large`.
- Under `vta/config/vta_config.json`, deterministic partitioning must produce
  exactly these four symbols:
  `tvmgen_mlperf_resnet_large_vta_main_0` through
  `tvmgen_mlperf_resnet_large_vta_main_3`.
- Each VTA region contains one convolution. Five convolutions remain on HOST.
  Four `vta.*` composites are required.
- This 4-VTA/5-HOST contract is an intentional model-specific difference from
  V1's 8-VTA/1-HOST contract. A read-only probe against the pinned stack
  established it before specification.

### Deployment and CLI

- Preserve the V1 command interface: optional `--output-dir`,
  `--host-codegen {llvm,c,all}`, and `--simulator {fsim,tsim}`; defaults remain
  LLVM and FSIM.
- Use artifact identity `resnet8_large` and V2-local output roots so V1 and V2
  runs cannot overwrite one another.
- For each selected host, build, export, reload from disk, and execute a HOST
  reference and a mixed VTA Graph Executor artifact.
- The same ten committed samples must produce exact reference/mixed tensor
  equality. LLVM and C references must also agree exactly in matrix mode.
- FSIM requires independently positive GEMM, weight-load, and output-store
  evidence for each mixed run. TSIM requires independently positive
  `cycle_count` evidence.
- TSIM loading and initialization remain lazy until all bundles have been
  exported and reloaded.
- Errors in assets, routing, target/config selection, symbols, output equality,
  artifact integrity, or simulator activity must return a nonzero exit.

### Aggregate gate

`scripts/test_vta_byoc.sh` must retain the complete V1 gate and add V2 asset,
model-pipeline, HOST/FSIM, and real TSIM matrix coverage. V1 runs first, then
V2, with each TSIM matrix in its own configured Python process. The documented
script contract in `scripts/README.md` must describe both deployments.

## Tech Stack

- Python 3.11 from `.envs/tvm-vta-env/bin/python`.
- Pinned TVM and VTA submodules from the recorded task baselines.
- `pytest`, NumPy, Pillow 11.3.0, and `tflite` 2.10.0 already provided by the
  repository environment.
- Existing Graph Executor, LLVM/C host codegen, FSIM, TSIM, and hardware
  libraries. No new dependency is permitted.

## Commands

Run commands from the repository root.

Focused asset and model tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_assets.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py
```

Focused artifact and HOST/FSIM tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_graph_artifacts.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_host_deployment.py
```

Real FSIM and TSIM matrices:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py \
  --simulator fsim --host-codegen all

VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py \
  --simulator tsim --host-codegen all
```

Complete gate:

```bash
bash scripts/test_vta_byoc.sh
```

## Code Style

Match V1's application-local modules, immutable dataclasses, explicit tuple
contracts, `pathlib.Path`, actionable validation errors, deterministic ordering,
and Apache license headers. Prefer the smallest model-specific substitutions;
do not refactor V1 or create a speculative generic framework.

## Testing Strategy

- Follow RED -> GREEN -> REFACTOR for each behavioral slice. A copied/adapted
  V2 test must fail because its V2 implementation or contract is absent before
  the implementation is added.
- Asset tests authenticate exact model/license/sample bytes and inspect the
  TFLite topology.
- Model-pipeline tests cover rejection paths, one-time quantization, exact
  4-VTA/5-HOST routing, and sample loading.
- Graph tests preserve schema, atomic publication, symbol, hash, source, and
  reload contracts under V2 artifact identity.
- HOST/FSIM tests cover LLVM/C builds, disk reload, exact outputs, symbols, and
  independent profiler windows.
- TSIM tests cover lazy initialization, matrix ordering, cycle evidence, and
  exact outputs; the aggregate gate runs the real TSIM matrix.
- Run V1 and V2 together at the final gate to prove no regression.

## Boundaries

### Always

- Preserve exact upstream model bytes and record their provenance.
- Use the repository Python environment and maintained build/test scripts.
- Keep V1 behavior and files unchanged.
- Commit verified VTA content before the parent VTA gitlink.
- Review every checkpoint across correctness, simplicity, architecture,
  security, and performance.

### Ask first

- Changing the approved model, quantization policy, 4-VTA/5-HOST contract,
  CLI, executor, simulator evidence, or aggregate-gate scope.
- Adding dependencies or modifying TVM/VTA compiler/runtime behavior outside
  the new application.
- Sharing/refactoring implementation with V1 instead of keeping V2 isolated.

### Never

- Modify or regenerate the source model.
- Commit `.envs/`, build products, caches, CIFAR-10 archives, or traces.
- Weaken, skip, or delete V1 tests to make V2 pass.
- Claim accuracy, performance, energy, or official submission validity.

## Success Criteria

- [ ] V2 contains every tracked content category listed above and uses the
  exact approved Large model.
- [ ] Asset and pipeline tests prove the model/tensor/topology contracts and
  deterministic 4-VTA/5-HOST routing.
- [ ] LLVM/C HOST/FSIM and TSIM matrices export, reload, and execute all ten
  samples with exact output equality and positive simulator evidence.
- [ ] `scripts/test_vta_byoc.sh` covers V1 and V2 and exits zero.
- [ ] V1 remains unchanged and all existing checks pass.
- [ ] Generated output is untracked; scoped repositories are clean after
  verified commits.
- [ ] Independent checkpoint reviews report no unresolved required findings.

## Out Of Scope

- The Large INT8 model, retraining, calibration datasets, or accuracy scoring.
- Changes to `image_classification_v1`.
- TVM or VTA compiler/runtime feature work.
- Alternative executors, new host code generators, hardware synthesis, or
  MLPerf submission packaging.

## Open Questions

None.
