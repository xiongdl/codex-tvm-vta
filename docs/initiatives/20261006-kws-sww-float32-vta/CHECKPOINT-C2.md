# Checkpoint 2: Float deployments and real VTA workload gate

Status: **GREEN**

Both apps now store only their verified float32 TFLite model. KWS uses
`keyword_spotting_v1/model/kws_ref_model_float32.tflite` (105,296 bytes,
SHA-256 `738a9f29d175aaa3928db9c8281265be5ec3406598fd3d30018b26084a3d5536`).
It imports as float32 `[1,49,10,1]` to `[1,12]`; preprocessing returns float32
MFCC features without the old int8 input scaling. SWW uses
`streaming_wakeword_v1/model/str_ww_ref_model_float32.tflite` (191,428 bytes,
SHA-256 `c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267`),
with float32 `[1,30,1,40]` input and `[1,3]` output. The old KWS int8 and SWW
int8 deployment assets were removed after their float replacements passed the
import and deployment gates. No H5 model or conversion intermediate is stored
in either app.

Both models use the reviewed Relay policy `global_scale=8.0,
skip_conv_layers=[0]`. Each app's CPU reference and mixed graph are built from
the same once-quantized Relay graph. CPU and FSIM mixed execution matched on
the committed WAV:

| App | Sample | CPU and mixed float32 scores | Prediction |
| --- | --- | --- | --- |
| KWS | `down-00176480_nohash_0.wav` | `[0.9999748468399048, 5.272670478007058e-06, 1.833493643368933e-12, 2.3079911315448953e-08, 2.833043521999201e-10, 4.320271727920044e-06, 2.3978605212526816e-10, 2.8744747737619036e-07, 3.892187407875808e-13, 3.036226825514632e-09, 1.7515120213570934e-12, 1.5419638657476753e-05]` | class 0, Down |
| SWW | `marvin-00176480_nohash_0.wav` | `[0.9999833106994629, 1.5706149714134199e-09, 1.6730595234548673e-05]` | class 0, Marvin |

Each mixed FSIM deploy compiled and executed four real VTA regions and
exported the actual workload Relay functions and captured activations. Each
snapshot contains four workload occurrences; activations at the quantized
VTA boundary are int8. Deployment reports show 20 VTA operation rows per
model and positive FSIM activity counters. FSIM does not report cycle counts.

| App | Model SHA-256 | WAV SHA-256 | Snapshot seal SHA-256 | Config SHA-256 |
| --- | --- | --- | --- | --- |
| KWS | `738a9f29d175aaa3928db9c8281265be5ec3406598fd3d30018b26084a3d5536` | `68d8077e68d9c2c02a9eb744061e934f514fc523aa90ee63fd56bfec0227e65d` | `87224ef87da4789fb4d31aad0095d12769889e7262d2c52af7a31020370b47fd` | `23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa` |
| SWW | `c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267` | `b95e103110b89a0d4dff88023edd537a92834f565cb8e3f38b16f725f3d58451` | `4aed1f204c755434eea23378c43f4ee1328ab3c27974fc519420e26d111841f7` | `23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa` |

Both `deploy.py` and `tune.py` require/accept `--model` as a float32 TFLite
input. Make passes `MODEL` to deployment and both tuning stages. Tuning imports
the selected model and rejects a workload snapshot with a different model
hash; model import also rejects non-float tensor contracts. The app suites
passed: KWS 69 tests and SWW 23 tests. No FSIM search or TSIM winner/replay was
run in C2.

Reproduce from the repository root:

```bash
KWS=vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1
SWW=vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/$KWS" \
  .envs/tvm-vta-env/bin/python -m pytest "$KWS/tests" -q
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/$SWW" \
  .envs/tvm-vta-env/bin/python -m pytest "$SWW/tests" -q
make -C "$KWS" deploy TARGET=llvm OUTPUT_DIR=/tmp/kws-cpu-build
make -C "$SWW" deploy TARGET=llvm OUTPUT_DIR=/tmp/sww-cpu-build
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/$KWS" \
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  .envs/tvm-vta-env/bin/python "$KWS/deploy.py" \
  --model "$KWS/model/kws_ref_model_float32.tflite" \
  --input "$KWS/samples/down-00176480_nohash_0.wav" --target vta,llvm \
  --simulator fsim --export-workloads /tmp/kws-workloads.json \
  --deployment-report /tmp/kws-fsim-report.md
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$SWW" \
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  .envs/tvm-vta-env/bin/python "$SWW/deploy.py" \
  --model "$SWW/model/str_ww_ref_model_float32.tflite" \
  --input "$SWW/samples/marvin-00176480_nohash_0.wav" --target vta,llvm \
  --simulator fsim --export-workloads /tmp/sww-workloads.json \
  --deployment-report /tmp/sww-fsim-report.md
```
