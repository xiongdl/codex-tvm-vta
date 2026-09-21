# MLPerf Tiny Verification

Date: 2026-09-21

Initiative: `20260921-add-vta-config-and-verify-mlperf-tiny`

Branch: `codex/20260921-add-vta-config-and-verify-mlperf-tiny`

Configuration used for every test and deployment command:

```text
VTA_CONFIG_FILE=/Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json
```

The configuration loader check through the approved SPEC command was attempted
and exited 1 with `ModuleNotFoundError: No module named 'vta.config'` because
this checkout provides `vta/config/vta_config.py` as a top-level config module
and does not provide `load_vta_config`. The supported runtime loader was then
checked with `vta.get_env()` and passed, reporting `TARGET=sim` and
`LOG_BLOCK=3`, `LOG_UOP_BUFF_SIZE=12`, `LOG_INP_BUFF_SIZE=13`,
`LOG_WGT_BUFF_SIZE=14`, `LOG_ACC_BUFF_SIZE=15`.

## Environment

The existing `.envs/tvm-vta-env` was used; no environment was created and no
data was downloaded. Present prerequisites were:

- Python 3.11.16, pytest 9.1.1, TVM 0.17.0, and VTA Python packages.
- `tvm/build/libtvm.dylib` and `libtvm_runtime.dylib`.
- `vta/build/libtvm-vta-ext.dylib`, `libvta_fsim.dylib`, `libvta_tsim.dylib`,
  and `libvta_hw.dylib`.
- Environment `verilator`, `sbt`, and `clang++`.

Environment blocker: `.envs/tvm-vta-env/bin/java` was absent. Existing
`libvta_hw.dylib` allowed the TSIM commands to reach runtime validation, but a
hardware-library rebuild would require Java. TSIM was blocked earlier by the
active configuration target (`sim`) before Java was needed.

## Focused test suites

All commands used the project Python environment and the configuration above.

| Benchmark | Command | Result | Exit | Evidence / root cause |
| --- | --- | --- | ---: | --- |
| anomaly_detection_v1 | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests` | FAIL | 1 | `60 passed, 1 skipped, 2 failed`; dense rewrite expected 2 `nn.dense` nodes but found 0, then quantized reference expected 8 convolutions but found a different topology. |
| image_classification_v1 | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests` | FAIL | 134 | Process aborted in `test_end_to_end_host_fsim_deployment` at `graph_executor.run`; no pytest summary. |
| image_classification_v2 | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests` | FAIL | 1 | `68 passed, 4 failed`; expected four VTA regions but observed eight; TSIM test also reported active target `sim` instead of required `tsim`. |
| keyword_spotting_v1 | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests` | PASS | 0 | `39 passed`. |
| streaming_wakeword_v1 | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests` | PASS | 0 | `49 passed`. |
| visual_wake_words_v1 | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests` | FAIL | 1 | `67 passed, 5 failed`; expected twelve VTA regions but observed thirteen; TSIM test also reported active target `sim` instead of required `tsim`. |

## Documented deployment commands

The following commands were run from the repository root. Commands that use
`--host-codegen all` execute the documented LLVM/C matrix.

| Benchmark / mode | Command | Result | Exit | Evidence / root cause |
| --- | --- | --- | ---: | --- |
| anomaly_detection_v1 HOST | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --mode host --build-dir vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/build --output-json /tmp/anomaly-host-64mac.json` | FAIL | 1 | `quantized reference must contain exactly eight convolutions`. |
| anomaly_detection_v1 FSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --mode fsim --host-codegen llvm --build-dir vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/build --output-json /tmp/anomaly-fsim-64mac.json` | FAIL | 1 | Same quantized-reference topology error before FSIM execution. |
| anomaly_detection_v1 TSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --simulator tsim --host-codegen all` | BLOCKED | 1 | TSIM requires VTA target `tsim`; active target from the required new config is `sim`. |
| image_classification_v1 HOST (README command; CLI default is FSIM) | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py` | FAIL | 134 | FSIM virtual-memory abort: `vta/src/vmem/virtual_memory.cc:52`, `loc < ptable_.size()`, `phy_addr=67408384`. |
| image_classification_v1 FSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py --simulator fsim --host-codegen all` | FAIL | 134 | Same FSIM virtual-memory abort (`phy_addr=67408384`). |
| image_classification_v1 TSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py --simulator tsim --host-codegen all` | BLOCKED | 1 | Active target is `sim`; TSIM requires `tsim`. |
| image_classification_v2 HOST (README command; CLI default is FSIM) | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py` | FAIL | 1 | Expected four VTA symbols (`_0` through `_3`), observed eight (`_0` through `_7`). |
| image_classification_v2 FSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator fsim --host-codegen all` | FAIL | 1 | Same unexpected eight-region routing. |
| image_classification_v2 TSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all` | BLOCKED | 1 | Active target is `sim`; TSIM requires `tsim`. |
| keyword_spotting_v1 HOST | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator host --host-codegen llvm` | PASS | 0 | 12 samples compared; mixed execution intentionally not run in HOST mode. |
| keyword_spotting_v1 FSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator fsim --host-codegen all` | FAIL | 134 | FSIM virtual-memory abort: `vta/src/vmem/virtual_memory.cc:52`, `loc < ptable_.size()`, `phy_addr=67167920`. |
| keyword_spotting_v1 TSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator tsim --host-codegen all` | BLOCKED | 1 | Active target is `sim`; TSIM requires `tsim`. |
| streaming_wakeword_v1 HOST | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator host --host-codegen llvm` | PASS | 0 | 3 samples compared; mixed execution intentionally not run in HOST mode. |
| streaming_wakeword_v1 FSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator fsim --host-codegen all` | FAIL | 134 | FSIM virtual-memory abort: `vta/src/vmem/virtual_memory.cc:52`, `loc < ptable_.size()`, `phy_addr=67158016`. |
| streaming_wakeword_v1 TSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator tsim --host-codegen all` | BLOCKED | 1 | Active target is `sim`; TSIM requires `tsim`. |
| visual_wake_words_v1 HOST (README command; CLI default is FSIM) | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py` | FAIL | 1 | Expected twelve VTA symbols (`_0` through `_11`), observed thirteen (`_0` through `_12`). |
| visual_wake_words_v1 FSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator fsim --host-codegen all` | FAIL | 1 | Same unexpected thirteen-region routing. |
| visual_wake_words_v1 TSIM | `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator tsim --host-codegen all` | BLOCKED | 1 | Active target is `sim`; TSIM requires `tsim`. |

## Working-tree verification

The six benchmark suites and all documented deployment commands were run
without changing benchmark source, shared scripts, configuration values, or
downloading data. Generated files remained under ignored benchmark `build/`
directories; no generated files are included in this change. Final tracked
scope is this report only.
