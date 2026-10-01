# Checkpoint C8: Visual Wake Words V1 adapter and seed gate

Initiative: `20261001-mlperf-tiny-remaining-tuning`
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`
Status: **GREEN**

## T19: faithful tuning adapter

The adapter prepares the actual Visual Wake Words V1 graph and extracts all 13
VTA Conv fusion occurrences as distinct complete AutoTVM workloads. It retains
the existing HOST routing, quantization, preprocessing, and reference checks.
The model-local CLI supports seed, full search, resume, and standalone replay;
foreign manifest/model identity is rejected. The tests verify occurrence and
HOST coverage against the prepared graph and the exact fusion lowering.

## T20: one-sample deployment adapter

Deployment consumes the exact manifest configs in selected-config lowering,
then runs the existing VWW image preparation and HOST reference check. The
profile records graph-resident VTA nodes and ordinary/debug full-model TSIM
counters using the shared deployment evidence format. The run below used one
committed image, one model invocation, and `stateless_single_image` state
policy.

## T21: seed and alignment gate

The seed run is `20261001T213545.307779Z`, labeled `SEED_COMPLETE`. With
`--seed --all --trial-batch 1`, all 13 occurrences obtained one successful
FSIM schedule and one successful AutoTVM TSIM single-call measurement. Across
the 13 workload spaces, 52 candidates were attempted: 13 FSIM successes and
39 candidate failures (18 VTA copy-pattern alignment/build failures and 21
other candidate build/runtime failures). These candidate failures are
separate from infrastructure failures; the completed run has zero recorded
infrastructure errors. Each occurrence stopped at the one-success seed quota.

Standalone replay validated and replayed **13 artifacts**. The real deployment
passed the existing HOST output correctness check on
`00-non-person-000000000009.jpg` (SHA-256
`d8f0e1e6e7635f189ab52e3e98aef1f7d734814a1fbe41fdb2c5ff8cbfc6dcfc`). The
preprocessing contract is the existing RGB conversion, 96x96 validation, and
float32 normalization by 255. Ordinary and debug full-model counters agree at
1,162,741 cycles; the untuned baseline is 6,862,109 cycles.

| Occurrence | Logical MACs | AutoTVM TSIM cycles | Deployment TSIM cycles | Difference | MAC utilization |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 294,912 | 94,065 | 94,082 | 0.018073% | 4.8979% |
| 1 | 294,912 | 22,054 | 22,055 | 0.004534% | 20.8932% |
| 2 | 589,824 | 91,109 | 91,078 | 0.034025% | 10.1188% |
| 3 | 294,912 | 14,989 | 14,990 | 0.006672% | 30.7405% |
| 4 | 589,824 | 70,851 | 70,852 | 0.001411% | 13.0074% |
| 5 | 294,912 | 85,494 | 85,487 | 0.008188% | 5.3903% |
| 6 | 589,824 | 93,544 | 93,529 | 0.016035% | 9.8536% |
| 7 | 589,824 | 75,347 | 75,354 | 0.009290% | 12.2303% |
| 8 | 589,824 | 26,984 | 26,984 | 0.000000% | 34.1536% |
| 9 | 589,824 | 15,991 | 15,991 | 0.000000% | 57.6324% |
| 10 | 589,824 | 16,399 | 16,400 | 0.006098% | 56.1951% |
| 11 | 294,912 | 43,689 | 43,702 | 0.029756% | 10.5441% |
| 12 | 589,824 | 512,237 | 512,237 | 0.000000% | 1.7992% |

All 13 comparisons pass the inclusive 10% gate. The largest difference is
0.034025% (occurrence 2). With VTA geometry of 64 MAC/cycle, occurrence
utilization is derived from logical MACs divided by deployment cycles and
peak MACs/cycle. Whole-model tuned utilization is 8.3224%; baseline utilization
is 1.4102% (HOST operations excluded from VTA MAC totals).

The seed artifacts are under
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/seed/20261001T213545.307779Z/`;
the passing deployment report is
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/deployment-seed.json`.
This checkpoint proves the seed and deployment alignment gate only. It does
not claim 20 successful schedules, full search, or space exhaustion; C9 owns
the full search.

## Verification

- Focused adapter, deployment profile, and shared deployment-evidence tests:
  **24 passed**.
- FSIM seed command with one-candidate batches: 13/13 occurrences have one
  successful FSIM schedule and one successful AutoTVM TSIM result.
- Standalone seed replay: **13 artifacts validated and replayed**.
- One-image TSIM deployment: `status=passed`, one image and invocation,
  successful HOST correctness, and ordinary/debug full-model cycle agreement.
- Native records and deployment JSON agree on all 13 occurrence identities,
  selected configs, and cycle pairs; all deployment rows pass at <=10%.
- `git diff --check` and final managed-repository status are checked after the
  evidence commit.

## Commit maps

C8 began from root `d509aab2d0dcacd688ad58738203b631ad15212f`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`b1caa9b71c872b21af616fad068d47a3fcc1cf1e`.

| Task | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| T19 adapter | `d86eb73bfa291352e12d9de956dde9992342cae1` | unchanged | `af5b56c2ad73671fbb2d7455d59b29fe05285aa9` | VWW tuning adapter, model-local CLI, adapter tests and README; scripts README |
| T20 deployment adapter | `c54e3e85570f012da421f3c6c050b053137d09ae` | unchanged | `4f034d1ce6a53e5b63751cb8fe7be0ed78d8c9d2` | VWW deployment adapter, profile tests and deployment README; scripts README |
| Integration correctness fixes | `29730e9456101b3b8eeac4c4eb63727cf1d4a6bb` | unchanged | `a76f7a8d3218984580e4a0d22d37bb59f96e2dfb` | Read runtime input shape/dtype through model pipeline; exact symbol matching for overlapping occurrence suffixes; regression tests |
| T21 seed and checkpoint evidence | recorded after commit | unchanged | recorded after commit | Seed native/result/manifest artifacts, deployment report, VTA `.gitignore` exceptions, this checkpoint |
