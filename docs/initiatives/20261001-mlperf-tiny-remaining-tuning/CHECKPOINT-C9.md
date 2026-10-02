# Checkpoint C9: VWW full search and optimal deployment

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## T22: full two-stage search

The full-search run `20261001T220401.514781Z` bound its identity to the passing
C8 seed deployment report
`visual_wake_words_v1/tune/deployment-seed.json` (SHA-256
`b6f4f1f5f1f5de118a1a959d8b1cda21ad157cca4fcb7e2d127f9de1222ed44a`). It used
the approved 100-trial batches, 20-success quota, 60-second FSIM timeout,
120-second TSIM timeout, and `vta/config/vta_64mac.json`. The manifest is
labeled `FULL_SEARCH`; all 13 prepared VTA fusion occurrences completed.

| Occurrence | Valid space | FSIM attempts | FSIM successes | Candidate failures | TSIM attempts / successes | Selected config | Minimum TSIM cycles |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 800 | 200 | 36 | 164 | 36 / 36 | 195 | 36,524 |
| 1 | 1,536 | 200 | 29 | 171 | 29 / 29 | 953 | 18,149 |
| 2 | 2,304 | 200 | 32 | 168 | 32 / 32 | 569 | 28,713 |
| 3 | 1,728 | 100 | 22 | 78 | 22 / 22 | 609 | 11,827 |
| 4 | 2,304 | 200 | 43 | 157 | 43 / 43 | 947 | 17,386 |
| 5 | 1,280 | 100 | 29 | 71 | 29 / 29 | 494 | 8,976 |
| 6 | 1,600 | 100 | 30 | 70 | 30 / 30 | 615 | 15,462 |
| 7 | 1,600 | 100 | 30 | 70 | 30 / 30 | 669 | 13,408 |
| 8 | 1,600 | 100 | 23 | 77 | 23 / 23 | 1,022 | 14,389 |
| 9 | 1,600 | 100 | 40 | 60 | 40 / 40 | 974 | 15,737 |
| 10 | 1,600 | 100 | 29 | 71 | 29 / 29 | 653 | 15,214 |
| 11 | 480 | 100 | 30 | 70 | 30 / 30 | 191 | 7,829 |
| 12 | 576 | 100 | 28 | 72 | 28 / 28 | 111 | 20,498 |

The search attempted 1,700 unique configurations and found 401 successful
FSIM schedules. Every success has one positive TSIM measurement, and each
exported config is the minimum-cycle result for its occurrence. There were
1,299 candidate failures: 492 copy-pattern/alignment failures and 807 other
schedule, build, or runtime failures. The completed FSIM and TSIM worker states
record no infrastructure errors. The initial sandboxed launch could not bind
the local RPC tracker; that failed startup remains outside the completed run's
coverage and is preserved in its run diagnostics.

The self-contained optimal artifact manifest and native/result pairs are under
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/optimal/20261001T220401.514781Z/`.
Standalone replay validated all **13 artifacts** without using the intermediate
run directory. A manifest with a foreign model identity was rejected with
`unsupported or mismatched best manifest`.

## T22 verification

- Full search:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/tune.py --all --alignment-report vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/deployment-seed.json`
  — `complete (FULL_SEARCH)`, 13/13 occurrences.
- Audit checked unique FSIM indices, quota-or-exhaustion stop reasons, exact
  success-to-TSIM config coverage, zero TSIM failures, positive cycles, and each
  exported minimum against all TSIM results.
- Standalone replay: **13 artifacts replayed**. Foreign-model replay was
  rejected. Replay used a fresh empty build directory.
- Focused VWW regressions:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_two_stage_tuning.py vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_deployment_profile.py vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py -q`
  — **15 passed**.
- `git diff --check` and final managed-repository status are checked after the
  T22 commit.

## T23: selected deployment and MAC utilization

The selected manifest was applied to one committed image,
`00-non-person-000000000009.jpg` (SHA-256
`d8f0e1e6e7635f189ab52e3e98aef1f7d734814a1fbe41fdb2c5ff8cbfc6dcfc`). VWW's
existing preprocessing and HOST output check passed. The deployment made one
stateless model invocation. Ordinary and debug full-model TSIM counters both
measured **224,115 cycles**; the untuned baseline measured **6,862,109 cycles**.

| Occurrence | AutoTVM TSIM cycles | Deployment TSIM cycles | Difference | MAC utilization |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 36,524 | 36,525 | 0.002738% | 12.6160% |
| 1 | 18,149 | 18,149 | 0.000000% | 25.3898% |
| 2 | 28,713 | 28,714 | 0.003483% | 32.0958% |
| 3 | 11,827 | 11,827 | 0.000000% | 38.9617% |
| 4 | 17,386 | 17,386 | 0.000000% | 53.0082% |
| 5 | 8,976 | 8,976 | 0.000000% | 51.3369% |
| 6 | 15,462 | 15,462 | 0.000000% | 59.6042% |
| 7 | 13,408 | 13,408 | 0.000000% | 68.7351% |
| 8 | 14,389 | 14,389 | 0.000000% | 64.0489% |
| 9 | 15,737 | 15,737 | 0.000000% | 58.5626% |
| 10 | 15,214 | 15,214 | 0.000000% | 60.5758% |
| 11 | 7,829 | 7,829 | 0.000000% | 58.8581% |
| 12 | 20,498 | 20,499 | 0.004879% | 44.9583% |

All 13 selected config identities match the C9 manifest and pass the inclusive
10% cycle gate. Useful-MAC utilization uses logical Conv MACs divided by real
deployment cycles and the 64-MAC/cycle geometry. The tuned whole-model
utilization is **43.1778%**, baseline utilization is **1.4102%**, and cycle
speedup is **30.6187x**. HOST-only work is excluded from VTA MAC totals.

Published evidence is
`visual_wake_words_v1/tune/deployment-full.json`,
`mac-utilization-full.json`, `mac-utilization-full.csv`, and `REPORT-FULL.md`.

## T23 verification

- One-sample selected deployment command from the approved specification:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/deployment.py --best-manifest vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/optimal/20261001T220401.514781Z/best-manifest.json --output vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/deployment-full.json`
  — passed, one image, 13/13 occurrence gates.
- MAC calculator accepted the deployment report. A separate audit matched all
  13 sample/config/workload identities, integer cycles, MAC counts and
  invocations to the selected manifest and both JSON reports; CSV rows match
  the calculator output.
- Focused VWW tuning/deployment and shared deployment/MAC regressions:
  **53 passed**.
- `git diff --check` and final managed-repository status passed after the T23
  commit.
