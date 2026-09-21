# MLPerf Tiny Verification

Date: 2026-09-21

Initiative: `20260921-add-vta-config-and-verify-mlperf-tiny`

Branch: `codex/20260921-add-vta-config-and-verify-mlperf-tiny`

Task: 5 (backend and MLPerf Tiny verification)

## Contract and environment

Every build and runtime command used the same geometry file:

```text
VTA_CONFIG_FILE=/Users/xdl/Projects/codex-tvm-vta/vta/config/vta_64mac.json
```

The canonical geometry values remained `LOG_BLOCK=3`, `LOG_UOP_BUFF_SIZE=12`,
`LOG_INP_BUFF_SIZE=13`, `LOG_WGT_BUFF_SIZE=14`, and `LOG_ACC_BUFF_SIZE=15`.
The project environment was used for every Python command:
`/Users/xdl/Projects/codex-tvm-vta/.envs/tvm-vta-env/bin/python`.
No environment was created, no dependency was installed, and no dataset was
downloaded.

Build commands and results:

```bash
bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend fsim --jobs 4
# exit 0; libtvm-vta-ext.dylib and libvta_fsim.dylib built

bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend tsim --jobs 4 --skip-deps --skip-tests
# exit 0; libtvm-vta-ext.dylib and libvta_tsim.dylib built;
# existing libvta_hw.dylib was available
```

The TSIM prerequisites were present at verification time: Verilator was
available, Java was at
`.envs/tvm-vta-env/lib/jvm/bin/java`, and `vta/build/libvta_hw.dylib` existed.
The TSIM build cache recorded the same config path and `VTA_BACKEND=tsim`.

The backend/config/ABI focused tests passed:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/tests/python/unittest/test_backend_contract.py \
  vta/tests/python/unittest/test_runtime_backend.py \
  vta/tests/python/unittest/test_abi_fingerprint.py
# 41 passed in 3.38s; exit 0
```

The ABI fingerprint command returned `09d98811c06abcab` for both
`VTA_BACKEND=fsim` and `VTA_BACKEND=tsim`; backend selection is therefore not
part of the geometry ABI fingerprint.

## Focused suite results

The following common prefix was used for each suite, with
`<suite>/tests` substituted for the suite path:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/<suite>/tests
```

| Suite | Result | Exit | Evidence |
| --- | --- | ---: | --- |
| `anomaly_detection_v1` | FAIL | 1 | 59 passed, 3 failed, 1 skipped. The model tests observed 0 dense nodes instead of 2 and a quantized reference that did not contain exactly 8 convolutions. The remaining failure was the TSIM fixture rejecting `VTA_BACKEND=fsim` versus explicit `tsim`. |
| `image_classification_v1` | FAIL | 1 | 67 passed, 3 failed. All failures were TSIM fixtures rejecting `VTA_BACKEND=fsim` versus explicit `tsim`. |
| `image_classification_v2` | FAIL | 1 | 65 passed, 7 failed. The model/partition path observed 8 VTA regions instead of the required 4; four TSIM fixture failures also reported the explicit backend mismatch. |
| `keyword_spotting_v1` | FAIL | 1 | 38 passed, 1 failed. The failure was the TSIM fixture rejecting `VTA_BACKEND=fsim` versus explicit `tsim`. |
| `streaming_wakeword_v1` | FAIL | 1 | Isolated rerun with generated `build/`, `__pycache__/`, and `.pytest_cache/` displaced and restored: 48 passed, 1 failed. The only failure was the TSIM fixture rejecting `VTA_BACKEND=fsim` versus explicit `tsim`. |
| `visual_wake_words_v1` | FAIL | 1 | 65 passed, 7 failed. The model/partition path observed 13 VTA regions instead of the required 12; three TSIM fixture failures also reported the explicit backend mismatch. |

The focused suite failures retain the existing model and topology assertions;
no assertion, model, partition, or topology expectation was changed.

## Deployment matrix

All commands below used the project Python environment, the shared config path,
and an explicit `VTA_BACKEND`. HOST is a CPU-reference execution mode, not a
VTA backend; where a runner exposes HOST, `VTA_BACKEND=fsim` was retained as the
explicit process backend while HOST did not load the simulator.

| Benchmark | HOST | FSIM | TSIM |
| --- | --- | --- | --- |
| `anomaly_detection_v1` | `--mode host --host-codegen llvm`: FAIL, exit 1, `quantized reference must contain exactly eight convolutions` | `--mode fsim --host-codegen llvm`: FAIL, exit 1, same topology assertion | `--mode tsim --host-codegen llvm`: FAIL, exit 1, same topology assertion before TSIM initialization |
| `image_classification_v1` | Not exposed by the current runner; its README's default path is FSIM | `--simulator fsim --host-codegen all`: PASS, exit 0; LLVM/C each compared 10 samples with 8 partitions and positive FSIM counters | `--simulator tsim --host-codegen all`: blocked after the hardware model emitted repeated `FetchVME64.scala:161 Unknown instruction type`; the runaway process was manually interrupted, so no natural application exit code was observed |
| `image_classification_v2` | Not exposed by the current runner | `--simulator fsim --host-codegen all`: FAIL, exit 1, observed 8 VTA symbols instead of 4 | `--simulator tsim --host-codegen all`: FAIL, exit 1, same 8-versus-4 topology assertion before TSIM initialization |
| `keyword_spotting_v1` | `--simulator host --host-codegen llvm`: PASS, exit 0; 12 samples | `--simulator fsim --host-codegen all`: PASS, exit 0; LLVM/C each compared 12 samples with positive FSIM counters | `--simulator tsim --host-codegen llvm`: blocked by repeated `FetchVME64.scala:161 Unknown instruction type`; the process was manually interrupted after assertion flooding, with no natural application exit code |
| `streaming_wakeword_v1` | `--simulator host --host-codegen llvm`: PASS, exit 0; 3 samples | `--simulator fsim --host-codegen all`: PASS, exit 0; LLVM/C each compared 3 samples with positive FSIM counters | Controlled probe with `--simulator tsim --host-codegen llvm` timed out after 20 seconds while the log contained repeated `FetchVME64.scala:161 Unknown instruction type`; process-group termination returned `-15` (controlled stop, not a benchmark pass) |
| `visual_wake_words_v1` | Not exposed by the current runner | `--simulator fsim --host-codegen all`: FAIL, exit 1, observed 13 VTA symbols instead of the required 12 | `--simulator tsim --host-codegen all`: FAIL, exit 1, same 13-versus-12 topology assertion before TSIM initialization |

Representative successful commands were run as follows:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py \
  --simulator fsim --host-codegen all --output-dir /tmp/vta-checkpoint3/image-v1-fsim
# exit 0

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py \
  --simulator fsim --host-codegen all --output-dir /tmp/vta-checkpoint3/kws-fsim
# exit 0
```

TSIM is not reported as passed. Its libraries and prerequisites were found,
but actual mixed execution is blocked by the hardware-model
`FetchVME64.scala:161 Unknown instruction type` assertion. Runs that fail in
model preparation retain their own exact topology failure evidence. FPGA
backends such as `pynq` and `zcu104` were not exercised and remain deferred.

## Source-diff guard

The following checks were empty:

```bash
git diff --name-only c944927fb5d1a5c905e93704898e8326821fb1b9 \
  -- vta/apps/mlperf_tiny_benchmark
git -C vta diff --name-only 1c7d8f5de3096f70b6d6b787bda20c03033bbe5b \
  -- apps/mlperf_tiny_benchmark
```

No benchmark model, partition implementation, model asset, or topology
expectation changed. The only tracked file changed by Task 5 is this report;
all generated deployment output remained outside the repository or ignored.
