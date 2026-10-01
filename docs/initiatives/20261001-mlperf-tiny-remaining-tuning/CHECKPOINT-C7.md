# Checkpoint C7: Streaming Wakeword full search and optimal deployment

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## T17: full two-stage search

The full-search identity binds the passing C6 seed deployment report
`deployment-seed.json` (SHA-256
`5aed8a57ac81b3de2ba0f1621dce3d41274e8d8ef86d8858aef6f370de23740b`). The
unbounded run is `20261001T205934.834798Z`, with 100-trial batches, a
20-success target, 60-second FSIM timeout, and 120-second TSIM timeout. Its
valid space contains 240 candidates.

| Occurrence | Space | FSIM attempts | FSIM successes | Candidate failures | TSIM successes | Selected cycles |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 240 | 240 | 12 | 228 | 12 / 12 | 9,871 |

Search exhausted the space below the 20-success target. The 228 candidate
failures include 8 fold/build assertions and 220 other schedule/build/runtime
errors. One sandbox-denied localhost RPC tracker startup event is preserved
separately in FSIM infrastructure errors and the controller's failed first
launch entry. The run resumed under the already-used local RPC permission and
completed all 240 distinct indices; the completed candidate record set has no
missing success-to-TSIM pair.

The exported best schedule is config index 11, the minimum positive cycle
result among all 12 successful TSIM measurements. Standalone replay validated
and replayed **1 artifact**. A copied manifest with a foreign model identity
was rejected with `unsupported or mismatched best manifest`. Search artifacts
are under
`streaming_wakeword_v1/tune/optimal/20261001T205934.834798Z/`.

## T18: selected deployment and MAC utilization

The selected manifest was applied to one committed sample,
`marvin-00176480_nohash_0.wav` (SHA-256
`b95e103110b89a0d4dff88023edd537a92834f565cb8e3f38b16f725f3d58451`). HOST
output correctness passed with one 16,000-sample audio window, 30 feature
frames, one model invocation, and stateless single-invocation policy.

| Occurrence | Logical MACs | AutoTVM TSIM cycles | Deployment TSIM cycles | Difference | MAC utilization |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 143,360 | 9,871 | 9,872 | 0.010131% | 22.6904% |

The inclusive 10% comparison passed. Ordinary and debug full-model counters
both measured 9,872 cycles. The untuned baseline measured 174,633 cycles;
tuned whole-model utilization is 22.6904%, baseline utilization is 1.2827%,
and cycle speedup is 17.6897x. Per-occurrence and whole-model MAC values are
derived from the deployment cycle count and the 64 MAC/cycle geometry.

Published evidence is `streaming_wakeword_v1/tune/deployment-full.json`,
`mac-utilization-full.json`, `mac-utilization-full.csv`, and `REPORT-FULL.md`.

## Verification

- Full search used the C6 alignment report hash, default batch/quota/timeouts,
  and completed with `FULL_SEARCH`; the 240-index space was exhausted.
- Native audit: 240 FSIM records, 12 successful FSIM configs, and 12 successful
  TSIM records. The successful config identities match exactly and selected
  cycles equal the minimum measured value.
- Standalone replay: **1 artifact validated and replayed**; foreign model
  identity rejected.
- Selected deployment: `status=passed`, `sample_count=1`, one VTA occurrence,
  passing HOST correctness and ordinary/debug cycle agreement.
- MAC calculator accepted the deployment report. CSV and JSON values were
  cross-checked against the occurrence and whole-model report.
- Focused regression:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests vta/apps/mlperf_tiny_benchmark/tests/test_deployment_evidence.py vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py --import-mode=importlib -q`
  — **93 passed**.
- `git diff --check` passed before both task commits; final managed repository
  status is checked after the T18 commit.

## Commit maps

C7 began from root `a5ed36b0578f3ea85e657c8252c297c6904067c5`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`f7c6b90e5431b1a508a93a803a0abe49d36c63ab`.

| Task | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| T17 | `912065c968e7d622ef95efdfa970d3e6e73491ec` | unchanged | `7ad544e0354fbc2d4aca506ddb65e139df40cce8` | VTA optimal manifest and native/result pair; VTA `.gitignore` exception |
| T18 | This checkpoint commit | unchanged | This checkpoint commit | Deployment and MAC JSON/CSV, full report, this checkpoint |
