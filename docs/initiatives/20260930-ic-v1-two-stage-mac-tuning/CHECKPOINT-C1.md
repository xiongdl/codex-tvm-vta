# Checkpoint C1 evidence

Initiative: `20260930-ic-v1-two-stage-mac-tuning`
Branch: `codex/20260930-ic-v1-two-stage-mac-tuning` in `.`, `tvm`, and `vta`
Delegation: Default, C1 (T1 then T2)
Approved inputs: this initiative's `INTENT.md`, `CAPABILITY_MAP.md`, three `SPEC-*.md` files, `PLAN.md`, and `TASKS.md`.

## Starting and task commit maps

Starting OIDs:

| Repository | Starting OID |
|---|---|
| `.` | `13502688f80d639e0c7e0ecb0841d8af6446d5ac` |
| `tvm` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| `vta` | `d91fdae82c2cc98f1b090791dc1efaf0937da112` |

T1 commit: `Validate IC V1 fusion task coverage and semantics`

| Repository | Commit OID | Committed paths |
|---|---|---|
| `vta` | `0399a31281c311c163e4c41579a614c55389f60e` | `apps/mlperf_tiny_benchmark/image_classification_v1/fused_tasks.py`; `apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py` |
| `.` | `3682718a6dd91a6357b716e08d3e7fbe809eca16` | `vta` gitlink |
| `tvm` | unchanged | — |

T2 commit: `Isolate IC V1 simulator RPC measurements`

| Repository | Commit OID | Committed paths |
|---|---|---|
| `vta` | `1a573c08a255f57557f010346acebc22a5af37e7` | `apps/mlperf_tiny_benchmark/autotvm_tuner.py`; `apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py`; `apps/mlperf_tiny_benchmark/image_classification_v1/tune/measurement.py`; `apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_two_stage_measurement.py` |
| `.` | `62cb781e3fc6dbeaeb3474d3898dbaa989994c89` | `vta` gitlink |
| `tvm` | unchanged | — |

Implementation OIDs at checkpoint completion, before this evidence-only root commit: `.` `62cb781e3fc6dbeaeb3474d3898dbaa989994c89`; `tvm` `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`; `vta` `1a573c08a255f57557f010346acebc22a5af37e7`. The resulting root OID after committing this evidence file is reported separately in the C1 handoff.

## T1 — Deployment-equivalent computation

`extract_fused_identities` now matches every VTA fusion symbol against the prepared deployment routing report, rejects missing, extra, duplicate, or unnamed coverage, and orders identities by deployment occurrence. The task retains the real Conv schedule key and now uses a shared bias → arithmetic right shift → clip → cast helper for its postprocessing.

Verification confirms all eight deployed fusion symbols and occurrence indices; rejects incomplete coverage; checks AutoTVM argument order, packed tensor shapes and dtypes; and compares task FLOPs against logical output dimensions and unpadded input/output channels. The extracted task preserves distinct occurrence identity for repeated workloads. CPU TE checks cover distinct bias/shift/clip/dtype variants, and the real Relay fusion test compares its output to the Conv accumulator plus deployment postprocessing, including negative and saturated values.

## T2 — Local RPC reliability and timeout isolation

IC V1 measurement defaults are independent: FSIM 60 seconds and TSIM 120 seconds. Each `measure_candidate` call owns a fresh runner and builder, preserves AutoTVM's candidate result, and closes runner RPC processes, executor workers, builder workers, and temporary build output even when setup or measurement fails. Runner startup and cleanup failures are surfaced as `SimulatorInfrastructureError` with the original failure detail. A failed configuration therefore cannot reuse or poison the next candidate's runner.

The shared tuner defaults for unrelated model commands are unchanged. The TSIM smoke returned one positive native cycle count after warmup exclusion and profiler reset.

## Verification evidence

Project Python was `.envs/tvm-vta-env/bin/python`. Focused command (explicit FSIM backend, geometry and Python paths):

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_two_stage_measurement.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_model_pipeline.py
```

Result: **53 passed**. Seven existing warnings came from asynchronous unsupported depthwise lowering in other model tests and the deprecated `target_host` argument; there were no test failures.

Real deployment smoke:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py::test_end_to_end_host_fsim_deployment
```

Result: **1 passed**; actual FSIM mixed deployment matched the HOST output contract on committed samples.

Real local RPC recovery smoke ran the same first IC V1 workload independently with `VTA_BACKEND=fsim` and `VTA_BACKEND=tsim`. Each backend measured an intentionally invalid configuration, then a fresh valid configuration. Both returned candidate error code `1` for the invalid configuration and success code `0` for the next. FSIM used the 60-second default and returned a wall-time measurement; TSIM used the 120-second default and returned **376,959 cycles**. After both candidates, each captured runner had `server`, `tracker`, and `executor` cleared. FSIM/TSIM libraries and the TSIM hardware library loaded from the existing `vta/build/` outputs.

The first unprivileged RPC attempt returned `PermissionError: [Errno 1] Operation not permitted` while binding the loopback tracker socket. The same approved smoke succeeded with the supported sandbox permission escalation, without changing the RPC path or bypassing socket checks. No permission blocker remains for this environment.

## C1 exit

T1 and T2 have separate verified commits. Focused tests, actual FSIM deployment, and real RPC failure/recovery smoke passed on both backends. Repository status was clean after the task commits and before adding this evidence file. No TVM or VTA runtime transformation source change was needed. Full search, deployment profiling, and MAC reporting remain for later checkpoints.
