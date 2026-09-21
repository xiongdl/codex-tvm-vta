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

## Checkpoint 2 rerun: config-compatible VTA library rebuild

The preceding results are retained above. This section records the rerun after
rebuilding the VTA native libraries directly with CMake, using the absolute
new configuration path. No build script or version-controlled source was
changed.

### Native rebuild evidence

The project environment and checked-out library revisions were unchanged:

```text
Python: .envs/tvm-vta-env/bin/python (Python 3.11.16)
TVM:   9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca
VTA:   94629e144fb8cd3d2d5ce4d0570da2d790896a5c
Config: /Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json
```

The following commands were run successfully from the repository root:

```bash
PATH="/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin:$PATH" \
  /Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/cmake \
  -S /Users/xdl/Projects/codex-tvm-vta/vta \
  -B /Users/xdl/Projects/codex-tvm-vta/vta/build \
  -DTVM_PATH=/Users/xdl/Projects/codex-tvm-vta/tvm \
  -DVTA_PATH=/Users/xdl/Projects/codex-tvm-vta/vta \
  -DVTA_CONFIG_FILE=/Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json \
  -DVERILATOR_ROOT=/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/share/verilator \
  -DPython3_EXECUTABLE=/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/python \
  -DCMAKE_BUILD_TYPE=Release

/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/cmake \
  --build /Users/xdl/Projects/codex-tvm-vta/vta/build \
  --target tvm_vta_ext --parallel 4

/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/cmake \
  --build /Users/xdl/Projects/codex-tvm-vta/vta/build \
  --target vta_fsim --parallel 4
```

Results: CMake configure succeeded; `tvm_vta_ext` built successfully; and
`vta_fsim` built successfully. `vta/build/CMakeCache.txt` records the absolute
`vta_64mac.json` path. The rebuilt `libtvm-vta-ext.dylib` and
`libvta_fsim.dylib` were produced at 2026-09-21 10:31:54 and 10:32:06,
respectively. The loader check after the rebuild reported:

```text
TARGET=sim
LOG_BLOCK=3
LOG_UOP_BUFF_SIZE=12
LOG_INP_BUFF_SIZE=13
LOG_WGT_BUFF_SIZE=14
LOG_ACC_BUFF_SIZE=15
```

### Focused suite rerun

All six suites used the absolute configuration through
`VTA_CONFIG_FILE=/Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json`
and the project Python environment. The streaming suite was rerun with its
old ignored application `build/` directory temporarily moved aside because
its asset test scans every non-test file and otherwise attempts to decode
binary generated `params.bin` as UTF-8. No source or test file was changed.

| Benchmark | Result after rebuild | Evidence |
| --- | --- | --- |
| anomaly_detection_v1 | **FAIL** | `60 passed, 1 skipped, 2 failed`; dense rewrite expected 2 `nn.dense` nodes but found 0, and quantized reference expected 8 convolutions. |
| image_classification_v1 | **FAIL** | `69 passed, 1 failed`; the only failure was TSIM validation because active target was `sim`, not `tsim`. FSIM-focused execution no longer aborted in `virtual_memory.cc`. |
| image_classification_v2 | **FAIL** | `68 passed, 4 failed`; exact routing expected 4 VTA regions but observed 8, plus the TSIM target validation failure. |
| keyword_spotting_v1 | **PASS** | `39 passed`. |
| streaming_wakeword_v1 | **PASS** | `49 passed` after generated-build isolation. |
| visual_wake_words_v1 | **FAIL** | `67 passed, 5 failed`; exact routing expected 12 VTA regions but observed 13, plus the TSIM target validation failure. |

The focused commands were the six approved suite paths:

```bash
VTA_CONFIG_FILE=/Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json \
PYTHONPATH=/Users/xdl/Projects/codex-tvm-vta/tvm/python:/Users/xdl/Projects/codex-tvm-vta/vta/python \
  /Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/python -m pytest \
  vta/apps/mlperf_tiny_benchmark/{anomaly_detection_v1,image_classification_v1,image_classification_v2,keyword_spotting_v1,streaming_wakeword_v1,visual_wake_words_v1}/tests
```

For the recorded per-suite results, the brace-expanded command was run once
for each benchmark directory. The streaming rerun additionally set
`PYTHONDONTWRITEBYTECODE=1`.

### Documented HOST/FSIM rerun

The following common environment was used for every deployment command:

```text
VTA_CONFIG_FILE=/Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json
PYTHONPATH=/Users/xdl/Projects/codex-tvm-vta/tvm/python:/Users/xdl/Projects/codex-tvm-vta/vta/python
PYTHON=/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/python
```

| Benchmark | HOST / README command | FSIM README command | Final evidence |
| --- | --- | --- | --- |
| anomaly_detection_v1 | `run.py --mode host --build-dir .../anomaly_detection_v1/build --output-json /tmp/anomaly-host-64mac-rerun.json` — **FAIL**, exact eight-convolution reference assertion | `run.py --mode fsim --host-codegen llvm --build-dir .../anomaly_detection_v1/build --output-json /tmp/anomaly-fsim-64mac-rerun.json` — **FAIL**, same assertion | Rebuild did not change the model topology assertion. |
| image_classification_v1 | README default command `run.py` — **PASS**, 10 comparisons and 8 partitions; CLI default is FSIM despite the README HOST heading | `run.py --simulator fsim --host-codegen all` — **PASS**, LLVM/C each compared 10 samples with 8 partitions and positive profiler counters | The prior FSIM virtual-memory abort is resolved by the rebuilt libraries. |
| image_classification_v2 | README default command `run.py` — **FAIL**, observed 8 VTA symbols instead of 4 | `run.py --simulator fsim --host-codegen all` — **FAIL**, same 8-versus-4 routing assertion | Exact partition-count expectation remains incompatible. |
| keyword_spotting_v1 | `run.py --simulator host --host-codegen llvm` — **PASS**, 12 comparisons | `run.py --simulator fsim --host-codegen all` — **PASS**, LLVM/C each compared 12 samples with positive FSIM counters | Both modes pass with rebuilt `vta_fsim`. |
| streaming_wakeword_v1 | `run.py --simulator host --host-codegen llvm` — **PASS**, 3 comparisons | `run.py --simulator fsim --host-codegen all` — **PASS**, LLVM/C each compared 3 samples with positive FSIM counters | Both modes pass with rebuilt `vta_fsim`. |
| visual_wake_words_v1 | README default command `run.py` — **FAIL**, observed 13 VTA symbols instead of 12; CLI default is FSIM | `run.py --simulator fsim --host-codegen all` — **FAIL**, same 13-versus-12 routing assertion | Exact partition-count expectation remains incompatible. |

The deployment commands above were executed with the full paths shown in the
common environment and the benchmark paths from each README. Generated
artifacts remain ignored under benchmark `build/` directories.

### TSIM status and root-cause conclusion

TSIM is **BLOCKED** for all six benchmarks, not passed or silently skipped.
The new configuration loads with `TARGET=sim`, while every TSIM runner requires
`TARGET=tsim`; the focused TSIM failures report `active target is 'sim'`.
The environment also lacks
`/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/java`, so rebuilding
`libvta_hw`/`libvta_tsim` for a TSIM-compatible configuration was not possible.
The existing hardware library was not treated as a valid replacement for a
new-config rebuild.

The rebuild separates the old-library compatibility issue from the remaining
failures: image classification v1 FSIM and both keyword/streaming FSIM paths
now pass, and the previous `virtual_memory.cc` abort is gone. The remaining
anomaly, image classification v2, and visual wake words failures are exact
model/partition topology assertions (0 dense nodes, or 8/13 VTA regions where
the tests require 2/4/12), not native-library load failures. Because rebuilding
alone does not make those exact test expectations true, the checkpoint remains
**FAIL**. Tests, benchmark/runtime sources, configs, scripts, and dependencies
were not changed.
