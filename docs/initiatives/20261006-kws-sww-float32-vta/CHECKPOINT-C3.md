# Checkpoint 3: Deployment and bounded tuning

Status: **GREEN**

C2 passed for both float32 TFLite models, with four real VTA occurrences per
model. C3 completed the two independent application workflows without changes
to `image_classification_v1`, TVM, or the VTA compiler. Both applications
provide the `deploy`, `tune-fsim`, `tune-tsim`, `tune`, and `clean` Make targets;
all deployment and tuning commands take the float32 TFLite model through
`MODEL`/`--model`. Workload snapshots, FSIM candidate logs, and selected TSIM
schedule logs are bound to the model and current VTA geometry.

## Inputs and sealed evidence

| App | Float32 model SHA-256 | WAV SHA-256 | Workload snapshot seal | VTA config SHA-256 |
| --- | --- | --- | --- | --- |
| KWS | `738a9f29d175aaa3928db9c8281265be5ec3406598fd3d30018b26084a3d5536` | `68d8077e68d9c2c02a9eb744061e934f514fc523aa90ee63fd56bfec0227e65d` | `87224ef87da4789fb4d31aad0095d12769889e7262d2c52af7a31020370b47fd` | `23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa` |
| SWW | `c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267` | `b95e103110b89a0d4dff88023edd537a92834f565cb8e3f38b16f725f3d58451` | `4aed1f204c755434eea23378c43f4ee1328ab3c27974fc519420e26d111841f7` | `23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa` |

Every FSIM VTA-target deployment exported four real workload functions and
their captured activations; each app report lists 20 VTA operation rows. The
CPU `c` and `llvm` runs and both FSIM mixed runs returned identical float32
scores for each app:

| App | Target result | Output scores |
| --- | --- | --- |
| KWS | class 0, Down | `[0.9999748468399048, 5.272670478007058e-06, 1.8334936433689334e-12, 2.3079911315448953e-08, 2.833043521999201e-10, 4.320271727920044e-06, 2.3978605212526816e-10, 2.8744747737619036e-07, 3.892187407875808e-13, 3.036226825514632e-09, 1.7515120213570934e-12, 1.5419638657476753e-05]` |
| SWW | class 0, Marvin | `[0.9999833106994629, 1.5706149714134199e-09, 1.6730595234548673e-05]` |

These are outputs of the once-quantized Relay graph used by both CPU and mixed
execution. They are not a bitwise comparison against the float TFLite source.

## Bounded FSIM and measured TSIM results

The `make tune` flow exported workloads, tested exactly one candidate per
occurrence (`TRIAL_BATCH=1`, `MIN_SUCCESSFUL=1`, `FSIM_TIMEOUT=60`), and stopped
each FSIM occurrence after one correctness-verified candidate. TSIM measured
one candidate per occurrence (`TSIM_TIMEOUT=120`) and selected the measured
minimum. The per-occurrence selected cycle counts were:

| App | Occurrence 0 | Occurrence 1 | Occurrence 2 | Occurrence 3 | TSIM replay whole-model cycles |
| --- | ---: | ---: | ---: | ---: | ---: |
| KWS | 565,916 | 565,916 | 565,916 | 565,916 | 2,263,664 |
| SWW | 166,099 | 407,683 | 254,683 | 4,357 | 832,822 |

Both `vta,c` and `vta,llvm` TSIM replays selected all four occurrences and
returned the same scores and predictions as the corresponding CPU and FSIM
runs. Reports show 2,263,664 whole-model cycles for KWS and 832,822 for SWW;
each total equals the sum of the measured VTA-layer cycles in its report.
FSIM does not provide cycle counts. These are one-candidate smoke results, not
exhaustive autotuning or a comparative performance claim.

The persistent schedule evidence is model-bound and checksummed:

| App | File | SHA-256 |
| --- | --- | --- |
| KWS | `tune/vta_64mac/fsim.tmp` | `b123004f4ce0ffa31097677f1dfe3bb7aefcc769f2df31762961ac2c2652533e` |
| KWS | `tune/vta_64mac/fsim.json` | `2083ff821ba0e95ca2ee06a8ed7ecaf4de949e4aada035172512a4f3c5c51fdc` |
| KWS | `tune/vta_64mac/best.log` | `6f0adcd65bdd3fe11fc96cf08f9004dfd53328e4b9dc4edfaf022bcde3e1ee18` |
| KWS | `tune/vta_64mac/best.json` | `09594f941ab942b006c7b29831148582454e8cbd68a0fa3d22898cfd25725145` |
| SWW | `tune/vta_64mac/fsim.tmp` | `72bf3432b88618c118e7e4a8b38dcd7d492522b18617f8ddfc5beb590cb2d488` |
| SWW | `tune/vta_64mac/fsim.json` | `e091e8cf01f529b1276603f7914299a817bd4455f502cf3ddaa223deec1570c4` |
| SWW | `tune/vta_64mac/best.log` | `86ba0f080af0187a4c9bff3f018c01f782256bf81d1087e17e7bd6ce77618fc0` |
| SWW | `tune/vta_64mac/best.json` | `6176e777ceeada0d09e29e21617eb77d3b1ee37d7ef93ec3eb4afba2779969e0` |

## Reproduction

Run from the repository root with the built project environment and simulator
libraries. The sample/model paths below are the committed app assets.

```bash
KWS="$PWD/vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1"
SWW="$PWD/vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1"
CONFIG="$PWD/vta/config/vta_64mac.json"
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python"
```

Run the target matrix on FSIM. CPU targets need no VTA backend; the VTA targets
export the genuine workloads.

```bash
for APP in "$KWS" "$SWW"; do
  if [[ "$APP" == "$KWS" ]]; then
    MODEL="$APP/model/kws_ref_model_float32.tflite"
    INPUT="$APP/samples/down-00176480_nohash_0.wav"
  else
    MODEL="$APP/model/str_ww_ref_model_float32.tflite"
    INPUT="$APP/samples/marvin-00176480_nohash_0.wav"
  fi
  env -u VTA_BACKEND -u VTA_CONFIG_FILE make -C "$APP" deploy \
    MODEL="$MODEL" INPUT="$INPUT" TARGET=c SIMULATOR=fsim
  env -u VTA_BACKEND -u VTA_CONFIG_FILE make -C "$APP" deploy \
    MODEL="$MODEL" INPUT="$INPUT" TARGET=llvm SIMULATOR=fsim
  VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=fsim make -C "$APP" deploy \
    MODEL="$MODEL" INPUT="$INPUT" TARGET=vta,c SIMULATOR=fsim \
    EXPORT_WORKLOADS="/tmp/$(basename "$APP")-workloads.json"
  VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=fsim make -C "$APP" deploy \
    MODEL="$MODEL" INPUT="$INPUT" TARGET=vta,llvm SIMULATOR=fsim \
    EXPORT_WORKLOADS="/tmp/$(basename "$APP")-workloads.json"
done
```

The actual bounded end-to-end Make command was:

```bash
VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=fsim make -C "$APP" tune \
  MODEL="$MODEL" WORKLOAD=-1 TRIAL_BATCH=1 MIN_SUCCESSFUL=1 \
  FSIM_TIMEOUT=60 TSIM_TIMEOUT=120 OUTPUT_DIR="/tmp/c3-full-tune"
```

It was run for each app with that app's float model. Replay both host codegens
on TSIM:

```bash
for TARGET in vta,c vta,llvm; do
  VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=tsim make -C "$APP" deploy \
    MODEL="$MODEL" INPUT="$INPUT" TARGET="$TARGET" SIMULATOR=tsim \
    SCHEDULE="$APP/tune/vta_64mac/best.log" \
    REPORT="/tmp/$(basename "$APP")-${TARGET//,/-}-tsim.md"
done
```

The focused suites passed (KWS 70, SWW 23), including Make workflow and clean
preservation, snapshot integrity/model mismatch, and artifact validation:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$KWS" \
  .envs/tvm-vta-env/bin/python -m pytest "$KWS/tests" -q
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$SWW" \
  .envs/tvm-vta-env/bin/python -m pytest "$SWW/tests" -q
```

Actual CLI rejection probes were also run for each app. With the app's
`MODEL`, exported `WORKLOADS`, and `tune/vta_64mac/best.log` paths, these
commands produce the expected rejection messages before searching or replay:

```bash
# A changed snapshot seal is rejected by tune.py.
jq '.snapshot_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"' \
  "$WORKLOADS" > /tmp/corrupt-workloads.json
VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=fsim \
  PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$APP" \
  .envs/tvm-vta-env/bin/python "$APP/tune.py" --model "$MODEL" \
  --workloads /tmp/corrupt-workloads.json --simulator fsim \
  --trial-batch 1 --min-successful 1 --timeout 60 \
  --output-logs /tmp/unused-candidates.tmp
# Expected: workloads snapshot integrity hash mismatch

# Appending one byte changes the model SHA while retaining a valid FlatBuffer.
cp "$MODEL" /tmp/changed-model.tflite
printf '\0' >> /tmp/changed-model.tflite
VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=fsim \
  PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$APP" \
  .envs/tvm-vta-env/bin/python "$APP/tune.py" \
  --model /tmp/changed-model.tflite --workloads "$WORKLOADS" \
  --simulator fsim --trial-batch 1 --min-successful 1 --timeout 60 \
  --output-logs /tmp/unused-candidates.tmp
# Expected: workloads model hash does not match --model

# Changing the native log without changing its metadata is rejected by deploy.py.
cp "$APP/tune/vta_64mac/best.log" /tmp/corrupt-best.log
cp "$APP/tune/vta_64mac/best.json" /tmp/corrupt-best.json
printf '\n' >> /tmp/corrupt-best.log
VTA_CONFIG_FILE="$CONFIG" VTA_BACKEND=tsim \
  PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$APP" \
  .envs/tvm-vta-env/bin/python "$APP/deploy.py" --model "$MODEL" \
  --input "$INPUT" --target vta,llvm --simulator tsim \
  --schedule /tmp/corrupt-best.log --output-dir /tmp/corrupt-schedule-build
# Expected: schedule log hash does not match its metadata
```

`make clean` removes the app's generated `build/` and Python caches while
preserving its float32 TFLite model, samples, license, and valid tuning logs
and metadata. The clean preservation checks passed in both app suites.
