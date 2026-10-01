# Checkpoint C3: AD full search and selected deployment

Initiative: `20261001-mlperf-tiny-remaining-tuning`
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`
Status: **GREEN**

## T7: full two-stage search

The passing C2 seed deployment report was bound into the run identity. Full
search used the approved defaults: 100 distinct FSIM candidates per batch,
20 successful schedules per occurrence unless its valid configuration space
was exhausted, and 60/120-second FSIM/TSIM candidate timeouts. The run
completed with 740 distinct FSIM attempts, 240 successful schedules and 240
successful single-call TSIM measurements. Every exported selected config is
the minimum positive TSIM-cycle schedule among that occurrence's successful,
deployment-lowerable configs.

| Occurrence | FSIM attempts / space | Successes | TSIM measurements | Stop reason | Selected cycles |
| ---: | ---: | ---: | ---: | --- | ---: |
| 0 | 100 / 100 | 32 | 32 | quota | 2,691 |
| 1 | 100 / 100 | 32 | 32 | quota | 2,691 |
| 2 | 100 / 100 | 32 | 32 | quota | 2,691 |
| 3 | 20 / 20 | 5 | 5 | exhausted | 437 |
| 4 | 20 / 20 | 6 | 6 | exhausted | 516 |
| 5 | 100 / 100 | 32 | 32 | quota | 2,691 |
| 6 | 100 / 100 | 32 | 32 | quota | 2,691 |
| 7 | 100 / 100 | 32 | 32 | quota | 2,691 |
| 8 | 100 / 200 | 37 | 37 | quota | 11,889 |

The 500 candidate failures are preserved separately: 397 schedule copy-pattern
lowering failures and 103 other TVM build/measurement failures. Each occurrence
also retains one local RPC tracker permission failure from the initial
sandboxed attempt; the durable full run resumed after the approved local-RPC
permission escalation and completed all searches. Those infrastructure
failures are outside the distinct candidate counts. The durable run manifest
and intermediate search state remain under the ignored AD V1
`build/two_stage_tuning/20261001T174411.872234Z/` directory. All nine exported
records replayed successfully from the self-contained manifest without using
that build directory.

## T8: selected deployment and MAC utilization

The selected manifest was deployed with the existing AD V1 HOST reference
check using one committed sample and one deterministic feature window:
`normal_id_01_00000000.wav` (SHA-256
`0385da04d6cf8c1f9d0df775f98fda55409a71890c02ed53bb5d2c66171f6828`), window
0 of 196. Correctness passed. All nine deployment/AutoTVM TSIM cycle pairs
matched exactly, so the maximum difference was 0% and every occurrence passed
the inclusive 10% gate. Ordinary and debug full-model runs both measured
28,988 cycles.

The deployed occurrence MAC counts are 16,384 for occurrences 0–2 and 5–7,
1,024 for occurrences 3–4, and 81,920 for occurrence 8. At 64 peak MAC/cycle,
their deployment-based utilizations are 9.5132%, 3.6613%, 3.1008% and 10.7663%
respectively. Total useful MACs are 182,272 per invocation. Measured full-model
baseline and tuned cycles are 188,773 and 28,988, yielding 1.5087% baseline
utilization, 9.8248% tuned utilization and 6.5121x cycle speedup. The calculator
validates that the separate per-occurrence costs are consistent with the
measured complete-model count; host work is excluded from VTA MAC totals.

The full report, versioned deployment evidence and MAC JSON/CSV are committed
in the AD V1 application at `tune/REPORT-FULL.md`, `tune/deployment-full.json`,
`tune/mac-utilization-full.json` and `tune/mac-utilization-full.csv`.

## Verification

- Full search command completed `FULL_SEARCH` with `status=complete`, default
  batch/quota/timeout identity and the passing seed-report hash.
- Standalone replay of `tune/optimal/20261001T174411.872234Z/best-manifest.json`
  validated and replayed **9 artifacts**.
- The audit matched all 240 successful FSIM configs to TSIM records, verified
  every successful config received TSIM, checked the minimum positive cycle
  selection, and confirmed quota or proven exhaustion for all nine occurrences.
- Final selected deployment command used `VTA_BACKEND=tsim`, the absolute
  shared geometry path and the project environment; result:
  `status=passed`, `sample_count=1`, 9/9 occurrences.
- `scripts/mac_utilization.py --deployment-report .../tune/deployment-full.json
  --output-json .../tune/mac-utilization-full.json` passed. A CSV/JSON audit
  confirmed all nine rows and whole-model metrics agree.
- Focused regression command:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/tests/test_deployment_evidence.py vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_deployment_profile.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_tsim_deployment.py -q`
  — **52 passed, 1 skipped**.
- `git diff --check` and final `git-workflow status` passed.

The selected deployment report initially inherited the seed label despite
`phase=selected`. A focused regression reproduced this metadata bug. The
shared report helper now emits `OPTIMAL_DEPLOYMENT` for selected runs and
continues to emit `SEED_ALIGNMENT` for seed runs; the final deployment report
and MAC result were regenerated and validated.

## Commit maps

C3 original map: root `10578919bd7e1afaf05210e2539dc9e610d2a0cc`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, VTA
`c9f643d4e9847b6af15f65242ceca3645ae21554`.

| Task | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| T7 | `a8d1f17d79a5373ad81f29cda24f9e4f3d1807c5` | unchanged | `484ca0d798e4e309b422be699261df350a7bdd76` | AD optimal manifest and nine selected result/native-record pairs; scoped `.gitignore` exceptions |
| T8 | `4cb0e1684d1906099c6a6781e24d723d4a33f15f` | unchanged | `65d4f358edbc9a992098a5f828d37a7f6d68bc4d` | Selected deployment/MAC JSON and CSV, full report, selected-label regression and shared report helper |

Before this checkpoint document was added, the clean source/evidence map was
root `4cb0e1684d1906099c6a6781e24d723d4a33f15f`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`65d4f358edbc9a992098a5f828d37a7f6d68bc4d`.
