# Checkpoint C2: anomaly detection v1 adapter and seed gate

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## Completed tasks

- **T4:** Added an AD-local adapter on the shared complete-fusion task and
  two-stage tuning infrastructure. Seed runs use a separate export location;
  full runs require a passing deployment alignment report. The actual prepared
  graph contains nine VTA Conv occurrences, and all nine are mapped to AD
  workloads with model and fusion identities.
- **T5:** Added one-sample AD deployment evidence. It lowers each selected
  occurrence with its exact manifest config, checks the existing HOST reference
  score, profiles graph-resident VTA nodes, and verifies ordinary/debug TSIM
  counter agreement. The representative window policy selects the first
  deterministic feature window.
- **T6:** Completed a real FSIM seed batch, AutoTVM TSIM measurements, one-sample
  real-model TSIM deployment, and standalone replay. Every occurrence passed
  the inclusive 10% gate; this run's measured differences are all 0%.

## Seed search and deployment evidence

Run: `20261001T162746.148776Z` (seed phase, VTA 64-MAC geometry).
The first 100-candidate batch ran for each occurrence. Occurrences 3 and 4
exhausted their 20-config spaces; the other seven each attempted 100 configs.
Invalid FSIM schedules were rejected by the simulator, while the following
successful FSIM schedules each received an AutoTVM TSIM measurement:

| Occurrence | Search space | FSIM attempts | FSIM successes / TSIM measurements | AutoTVM TSIM cycles | Deployment cycles | Difference | MACs | MAC utilization |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 100 | 100 | 32 / 32 | 2691 | 2691 | 0% | 16384 | 9.5132% |
| 1 | 100 | 100 | 32 / 32 | 2691 | 2691 | 0% | 16384 | 9.5132% |
| 2 | 100 | 100 | 32 / 32 | 2691 | 2691 | 0% | 16384 | 9.5132% |
| 3 | 20 | 20 (exhausted) | 5 / 5 | 437 | 437 | 0% | 1024 | 3.6613% |
| 4 | 20 | 20 (exhausted) | 6 / 6 | 516 | 516 | 0% | 1024 | 3.1008% |
| 5 | 100 | 100 | 32 / 32 | 2691 | 2691 | 0% | 16384 | 9.5132% |
| 6 | 100 | 100 | 32 / 32 | 2691 | 2691 | 0% | 16384 | 9.5132% |
| 7 | 100 | 100 | 32 / 32 | 2691 | 2691 | 0% | 16384 | 9.5132% |
| 8 | 200 | 100 | 31 / 31 | 12084 | 12084 | 0% | 81920 | 10.5925% |

Each seed manifest entry contains the selected config, native TSIM record,
cycle count and workload/fusion/config hashes. The seed manifest is
`vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/seed/20261001T162746.148776Z/best-manifest.json`;
the per-occurrence native logs and result JSON files are beside it.

The deployed sample was `normal_id_01_00000000.wav`
(SHA-256 `0385da04d6cf8c1f9d0df775f98fda55409a71890c02ed53bb5d2c66171f6828`).
One sample and one window were executed: deterministic window index 0 of 196.
HOST reference correctness passed. The baseline whole-model cycle count was
188773 and the tuned count was 29183. Ordinary and debug single-sample cycle
counts both measured 29183. No 10-sample deployment was run.

The passing deployment report is
`vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/deployment-seed.json`.
It records all 9 exact AutoTVM/deployment pairs and their hashes. The compatible
MAC utilization calculation reports 182272 total logical MACs, 1.5087%
baseline whole-model utilization, 9.7591% tuned whole-model utilization, and
6.4686x cycle speedup. Per-occurrence values are in the table above.

## Verification

The seed search was run with `VTA_BACKEND=fsim`; replay and deployment used
`VTA_BACKEND=tsim`, `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json"`, the
project Python at `.envs/tvm-vta-env/bin/python`, and repository TVM/VTA plus
AD benchmark directories on `PYTHONPATH`.

- Seed command: `python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/tune.py --seed --all`.
  The completed run reports `SEED_COMPLETE` and exports nine best manifests.
- Standalone replay of `.../tune/seed/20261001T162746.148776Z/best-manifest.json`
  validated and replayed **9 artifacts**.
- Deployment command:
  `python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/deployment.py --best-manifest .../tune/seed/20261001T162746.148776Z/best-manifest.json --output vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/deployment-seed.json`.
  It passed correctness, occurrence coverage, the 10% gate and counter
  agreement with `sample_count=1`.
- Final scoped regression command:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/tests/test_fused_tasks.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_two_stage_tuning.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_deployment_profile.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_tsim_deployment.py -q`
  — **25 passed, 1 skipped**.
- `scripts/mac_utilization.py --deployment-report .../tune/deployment-seed.json`
  accepted the report and reproduced all nine rows and whole-model metrics.
- `git diff --check` passed.

The initial seed export and deployment attempts exposed three integration bugs:
scalar bias task serialization in the shared task helper, missing real fusion
schedule lowering, then deployment config identity normalization and AD's
runtime status-callback API. These were repaired with focused regression tests;
the failed deployment diagnostics are retained as
`tune/deployment-seed-first-attempt-failure.json` and
`tune/deployment-seed-second-attempt-failure.json`. The durable seed search was
resumed without rerunning completed FSIM/TSIM measurements after the lowering
fix. These failures did not weaken the acceptance gate.

## Commit maps

C2 began from root `c1cf92f89e59937a467dd780a1b83db232dab794`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`02eecf8e693a1e02c8d4e01648485e94456e1770`.

| Task / change | Root commit | VTA commit | Committed paths |
| --- | --- | --- | --- |
| T4 adapter | `19d3bb1b512a2b09beb88ea561ad3a9e8b320017` | `94ea3ddbb5710831362ab453b6f8b7a5a1bba181` | AD tuning adapter, two-stage entry point, tests and README |
| T5 deployment adapter | `48ea04999e242126abb2d15c5dcde4abed03bf89` | `5fc0307864813ab99de54d156e3cf3202267f135` | AD deployment adapter, tests and README |
| T6 real lowering fix | `8edc3d6ad2cd51dca858e511f0efd8ffc4067d25` | `fd76793c0183aafe7baf5d3999b928f04fda1001` | Shared real fusion lowering seam and AD regression |
| T6 config identity and seed export | `4daa787255e143fc761f6dac1fd8857516fcf8d4` | `24d2a634467ee4c9481060f53282103cf3b5accb` | Config identity normalization, regression, initial seed artifacts |
| T6 profiler seam and generated seed artifacts | `a83c6f688ff24a4895a39110cb709f50ace5989c` | `57548798a28558eaebbab1a42ce069b1c547598b` | AD profiler adapter/regression, seed result/native records and retained failure diagnostics |
| T6 final passing deployment and checkpoint | pending | pending | Final seed deployment report and this checkpoint |

The T6 profiler fix commit also captured the then-current generated seed
artifacts because the AD report/native files had just been made trackable. The
final passing deployment report and checkpoint are committed separately below.
TVM has no C2 source changes and remains at
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`.

## Limits

This checkpoint is the seed alignment gate only. It does not claim the full
search quota of at least 20 successful schedules for each operator or the
optimal deployment; those are C3 tasks. Occurrences 3 and 4 have fewer than 20
valid schedules in their complete search spaces, so their later full-search
evidence must record exhaustion. Occurrence 8's first 100-trial seed batch
covered only half of its 200-config space.
