# Spec: MLPerf Tiny VWW V1 deployment

## Objective

Add a fixed-purpose `visual_wake_words_v1` application under the VTA MLPerf
Tiny examples. The application deploys the official MLPerf Tiny v1.4 floating
Visual Wake Words model through the same HOST, FSIM, TSIM, LLVM-host, C-host,
artifact-export, reload, and execution-equivalence flow as
`image_classification_v1`.

The checked-in validation set contains exactly ten authenticated 96x96 RGB
JPEGs from the user-provided `vw_coco2014_96` directory: the lexicographically
first five files from `non_person` and the lexicographically first five files
from `person`. The manifest fixes `0=non_person` and `1=person`, the source
relative path, committed filename, and SHA-256 for every image.

This is an execution-equivalence example. It proves deterministic import,
quantization, partitioning, export/reload, correct top-1 labels for the ten
committed samples, and positive simulator activity. It does not train the
model or report full-dataset accuracy, performance, energy, or MLPerf
submission results.

## Confirmed assumptions

1. The application directory is
   `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/`.
2. The source model is copied byte-for-byte from
   `.envs/tiny-v1.4/benchmark/training/visual_wake_words/trained_models/vww_96_float.tflite`.
3. The committed source-model SHA-256 is
   `115bbc094d2119561320a21f01b6500a18bea8cc8589282ab007097bec8af38c`.
4. Input preprocessing is RGB `float32` NHWC divided by `255.0`, matching the
   MLPerf Tiny training and conversion code.
5. TVM quantization uses `calibrate_mode="global_scale"`,
   `global_scale=8.0`, and `skip_conv_layers=[0]`, once, before the reference
   and mixed graphs fork.
6. The fixed mixed graph contains 12 VTA regions. Depthwise and other
   unsupported operations remain on the host portion of the same graph. The
   VTA Relay strategy supplies an explicit host schedule for unpacked NHWC
   depthwise convolution so the mixed module can keep the standard single
   `Target("vta", host=...)` build contract.
7. The local `.envs` source trees and the complete dataset remain unmodified
   and uncommitted.
8. Exported graph JSON is compiler output and is never patched to alter device
   placement. Reference/mixed output comparisons require identical shape and
   dtype plus `numpy.testing.assert_allclose(rtol=1e-6, atol=1e-6)`; all ten
   top-1 labels must still exactly match the manifest.

## Source contracts

### Model

- TFLite FlatBuffer version: 3
- Subgraphs: 1
- Input: `input_1`, `(1, 96, 96, 3)`, `float32`
- Output: `Identity`, `(1, 2)`, `float32`
- Topology: the exact ordered operator list and convolution-channel sequence
  discovered from the authenticated model are asserted in tests.
- Class mapping: output index `0` is `non_person`; output index `1` is
  `person`.

### Samples

The committed manifest and extractor use this fixed ordered selection:

| Order | Class | Source filename | SHA-256 |
|---:|---|---|---|
| 0 | non_person | `COCO_train2014_000000000009.jpg` | `d8f0e1e6e7635f189ab52e3e98aef1f7d734814a1fbe41fdb2c5ff8cbfc6dcfc` |
| 1 | non_person | `COCO_train2014_000000000025.jpg` | `d635da6fef7b8968653bdfc1289d8cfa88b551010e8d85ed1f384f7a6e60a2b2` |
| 2 | non_person | `COCO_train2014_000000000030.jpg` | `c69bcd53f365ec472243f32a4ef9e0a00f389c1c10b3f892ece2392223f92fd6` |
| 3 | non_person | `COCO_train2014_000000000034.jpg` | `fb4b1a2d533b1935103e5083a7d17b22a7dabfdffb2ddf09f75a98f19337c27d` |
| 4 | non_person | `COCO_train2014_000000000064.jpg` | `21eab2520d5dd01d3a10ce6b322a882bc7c6856ac50b3fbf1317362dcf7f53a0` |
| 5 | person | `COCO_train2014_000000000036.jpg` | `068b7ad53d46c9c075b47df4505bd6369a14cd4bcbad06c1e679dc7dfc51156f` |
| 6 | person | `COCO_train2014_000000000049.jpg` | `23959ed66eb87f75c51895b174024ea8af0da9fc2e301c52045a8a01332a8bc2` |
| 7 | person | `COCO_train2014_000000000077.jpg` | `18f612634fd4d1636181b96bc7fed3eaf61b0e38d4bf19c26f4011db75130868` |
| 8 | person | `COCO_train2014_000000000086.jpg` | `c4cb9d7b9f7a6e8b2ffc17acbbdcd74d062b43849ef16bd124eca572df316254` |
| 9 | person | `COCO_train2014_000000000110.jpg` | `577704fec55b656ca27e4ce444b9767b9bd20e196b16952e400d52747363abda` |

All ten decode as 96x96 RGB JPEGs. The manifest records that the samples were
provided locally from a COCO-derived VWW dataset and does not misrepresent the
MLPerf Tiny Apache license as an image-data license.

## Tech stack

- Python from `.envs/tvm-vta-env`
- TVM Relay and Graph Executor from the checked-out `tvm` submodule
- VTA BYOC and FSIM/TSIM from the checked-out `vta` submodule
- `tflite==2.10.0`, NumPy, Pillow, and pytest from the pinned environment
- Shell automation under the parent repository `scripts/` directory

No TensorFlow, `tflite-runtime`, AutoTVM, legacy graph packing, or network
download is introduced.

## Commands

Focused asset/model verification:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_assets.py \
  vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py
```

FSIM deployment matrix:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py \
  --simulator fsim --host-codegen all
```

TSIM deployment matrix:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py \
  --simulator tsim --host-codegen all
```

Complete repository gate:

```bash
bash scripts/test_vta_byoc.sh
```

## Project structure

```text
scripts/
  extract_mlperf_vww_samples.py       deterministic local sample extractor
  test_vta_byoc.sh                    aggregate HOST/FSIM/TSIM gate
vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/
  README.md                           usage and behavior
  LICENSE.mlperf-tiny                 source-model license text
  graph_artifacts.py                  authenticated graph bundle export/reload
  model_pipeline.py                   import, quantize, partition, preprocess
  runtime.py                          HOST/FSIM/TSIM build and execution
  run.py                              CLI entry point
  model/                              authenticated floating source model
  samples/                            ten JPEGs and provenance manifest
  tests/                              assets, model, artifacts, HOST/FSIM, TSIM
```

## Code style

Follow the neighboring application: immutable dataclasses for observable
results, `pathlib.Path` for paths, explicit fixed constants for authenticated
contracts, and narrow functions with validation at every boundary.

```python
def load_sample(sample_path):
    with Image.open(sample_path) as image:
        rgb = np.asarray(image.convert("RGB"), dtype="float32")
    if rgb.shape != (96, 96, 3):
        raise ValueError(f"unexpected sample shape: {rgb.shape}")
    return rgb[None, ...] / np.float32(255.0)
```

## Testing strategy

- Asset tests authenticate the model, license, manifest, and every JPEG byte;
  validate dimensions and class balance; and optionally reproduce the samples
  from the local source directory.
- Model tests start RED, then prove the exact TFLite/Relay contract,
  preprocessing, one-time quantization, and deterministic 12-region routing.
- A focused VTA runtime regression test proves that a mixed graph containing
  an unpacked NHWC depthwise convolution builds with the single VTA target,
  leaves that operation on the host, executes without graph mutation, and
  preserves positive accelerator activity for its VTA region.
- Artifact tests prove atomic authenticated export/reload for LLVM and C host
  code generators.
- HOST/FSIM tests prove reference/mixed output agreement within the fixed
  `rtol=1e-6, atol=1e-6` bound, identical output shapes and dtypes, correct
  manifest top-1 labels for all ten samples, expected VTA symbols, and
  positive FSIM counters.
- TSIM tests and the CLI prove the corresponding matrix with positive TSIM
  cycle activity in a fresh process.
- The parent aggregate gate includes the VWW focused tests and both simulator
  runs without weakening existing ResNet gates.

## Boundaries

- Always: authenticate source bytes; use the repository Python environment;
  keep host and mixed graphs derived from one quantized module; preserve
  existing public CLI defaults; use the standard compiler-produced graph JSON;
  test before each implementation commit.
- Ask first: change the selected samples, class mapping, quantization policy,
  expected partition count, application name, dependencies, or aggregate-gate
  scope.
- Never: modify or commit `.envs`; download data; train the model; import
  TensorFlow at runtime; use legacy graph packing; weaken or skip tests; claim
  an image-data license not established by the source.

## Success criteria

1. The committed model, license, ten samples, and manifest pass byte-level and
   structural provenance tests.
2. The model imports as the fixed float32 `96x96x3 -> 2` graph, preprocesses
   inputs to `[0,1]`, quantizes once with the approved policy, and partitions
   deterministically into 12 VTA regions.
3. The VTA single-target build supports unpacked NHWC depthwise host fallback
   without graph JSON mutation; a focused regression test proves host fallback
   and positive VTA-region simulator activity in the same graph.
4. LLVM and C HOST/FSIM matrices build, export, reload, and execute; reference
   and mixed outputs have identical shape/dtype and match within
   `rtol=1e-6, atol=1e-6` for all ten samples; top-1 labels match the manifest;
   required FSIM counters are positive.
5. LLVM and C HOST/TSIM matrices satisfy the same output and label checks and
   report positive TSIM cycle activity.
6. Generated bundles include authenticated graph, params, library, manifest,
   and inspectable host source, and partial exports are cleaned on failure.
7. `bash scripts/test_vta_byoc.sh` passes with all existing gates retained.
8. The source directories under `.envs` are unchanged and absent from Git.

## Open questions

None.
