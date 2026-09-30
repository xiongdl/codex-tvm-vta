# Checkpoint C2 evidence

Initiative: `20260930-ic-v1-two-stage-mac-tuning`
Delegation: Default, C2 (T3 then T4)
Branch: `codex/20260930-ic-v1-two-stage-mac-tuning` in `.`, `tvm`, and `vta`
Approved inputs: initiative `INTENT.md`, `CAPABILITY_MAP.md`, the three
`SPEC-*.md` files, `PLAN.md`, and `TASKS.md`.

## Commit maps

C2 starting commits after C1:

| Repository | Starting OID |
|---|---|
| `.` | `aac8f13af4a455622d8f54fded716541b1cea099` |
| `tvm` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| `vta` | `1a573c08a255f57557f010346acebc22a5af37e7` |

T3 — `Add adaptive IC V1 FSIM to TSIM search`:

| Repository | Commit OID | Committed paths |
|---|---|---|
| `vta` | `e2bdaf976441f5f4983eed3aa13d5e0df39fc63e` | `apps/mlperf_tiny_benchmark/image_classification_v1/tune/search.py`; `tune/tune.py`; `tests/test_two_stage_tuning.py` |
| `.` | `42b00a0e596a9a6b9e415bbb15aa2ceefd8f2ab5` | `vta` gitlink |
| `tvm` | unchanged | — |

T4 — `Export self-contained IC V1 best schedules`:

| Repository | Commit OID | Committed paths |
|---|---|---|
| `vta` | `59d6b2abf12d368d5b4d33c2ea615412f27d7aa4` | `apps/mlperf_tiny_benchmark/image_classification_v1/tune/artifacts.py`; `tune.py`; `tune/tune.py`; `tests/test_tune.py`; `tests/test_two_stage_tuning.py`; `README.md` |
| `.` | `b961183b3b94a3d7968c4eec568c7b4a03ff25ae` | `scripts/README.md`; `vta` gitlink |
| `tvm` | unchanged | — |

Checkpoint implementation tip: root `b961183b3b94a3d7968c4eec568c7b4a03ff25ae`,
TVM `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, VTA
`59d6b2abf12d368d5b4d33c2ea615412f27d7aa4`. The root tip after committing
this evidence file is reported in the C2 handoff.

## T3 — Adaptive FSIM and TSIM evaluation

The new controller creates one task per prepared fusion occurrence, runs each
backend in a separate worker process, and persists native records plus search
state below IC V1 `build/two_stage_tuning/`. Random search continues in
100-distinct-configuration batches until the distinct successful schedule
quota is reached or the valid space is exhausted. Resume validates model,
geometry, occurrence, workload, options, native FSIM records, and TSIM state;
already visited configurations and already measured TSIM candidates are
skipped. Infrastructure errors are saved separately from candidate failures.
Every successful distinct FSIM record is measured once on TSIM. The best
candidate is the one with the minimum positive single-call TSIM cycles.

Focused tests cover success quota, exhaustion, short final batches, resume,
identity mismatch, duplicate trial rejection, schedule deduplication, no
successful candidate, minimum-cycle selection, and occurrence-index handling.

## T4 — Self-contained artifacts and maintained interfaces

Selected TSIM native records and per-workload JSON metadata are written below
`tune/optimal/<run-id>/`; `best-manifest.json` lists the entries, model and
geometry hashes, occurrence identities, record hashes, cycles, and bounded
completion label. Replay verifies the standalone native record and real model
lowering without opening FSIM/TSIM files from `build/`. The prior
`image_classification_v1/tune.py` single-workload options remain available.
The IC V1 and project script READMEs describe paths, backend timeouts, bounded
runs, resume, and replay.

## Verification

Project Python: `.envs/tvm-vta-env/bin/python`.

Focused suite, run with explicit FSIM geometry and Python paths:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v1" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_two_stage_tuning.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py
```

Result: **29 passed**. Python compilation passed for the legacy entry point and
all modules under `tune/`. New and legacy `--help` commands passed. `git diff
--check` passed in root and VTA.

Bounded real multi-workload smoke used `--all --max-workloads 2 --trial-batch
1 --min-successful 1`, with FSIM 60s and TSIM 120s. The prepared model has eight
fusion occurrences; this run selected occurrences 0 and 1, so it is explicitly
incomplete. FSIM attempted 10 configurations for occurrence 0 and 9 for
occurrence 1; each found one distinct successful schedule out of 576 valid
configurations. TSIM measured each successful record once and returned **108,099**
and **65,289** cycles. Invalid schedules, including simulator child-process
crashes, were recorded as candidate failures and later candidates succeeded.

Resuming the same build manifest preserved counts at 10/9 FSIM attempts and
1/1 TSIM measurements, proving it did not repeat completed trials. A bounded
export then wrote two standalone native records to `/private/tmp/c2-artifact-run/`;
`--replay-manifest` validated and replayed both after the result JSONs were
separated from the intermediate build paths. The manifest says
`BOUNDED_SMOKE_INCOMPLETE`; these results are not full-search results.

## Remaining boundary

Full eight-workload search is intentionally deferred to C4. The local RPC
tracker requires sandbox permission for loopback binding: the unprivileged
smoke returned `PermissionError: [Errno 1] Operation not permitted`; the
bounded smoke succeeded after the supported permission escalation. No approved
scope changes or remaining C2 blockers.
