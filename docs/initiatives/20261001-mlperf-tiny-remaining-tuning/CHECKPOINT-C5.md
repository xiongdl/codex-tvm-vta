# Checkpoint C5: KWS full search and optimal deployment

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## T12: full two-stage search

The C4 seed deployment gate was bound into the KWS full-search identity by
SHA-256 `bf3836df4c2bf8b33c47ab05f919208fcc661d6a32ca224b8acb874ed696d91b`.
The completed, unbounded run is
`20261001T192416.141960Z`, using the absolute committed
`vta/config/vta_64mac.json`, 100-candidate FSIM batches, a 20-success target,
60-second FSIM timeout and 120-second TSIM timeout.

| Occurrence | Valid space | FSIM attempts | FSIM successes | FSIM candidate failures | TSIM attempts / successes | Selected AutoTVM TSIM cycles |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |
| 1 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |
| 2 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |
| 3 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |

Every workload reached at least 20 distinct successful schedules. The selected
configuration is the minimum positive TSIM-cycle candidate among all 21
successful TSIM measurements for that occurrence. Each selected entry retains
its occurrence, symbol, workload/fusion/config hashes and native record.

The 363 FSIM candidate failures per occurrence classify as 213 copy-pattern
lowering failures and 150 other schedule/build/execution failures. One local
RPC infrastructure event per occurrence is retained in the FSIM state
diagnostics and also appears with its candidate failure. All four states cover
384 distinct configuration indices and have 21 TSIM measurements. The initial
sandboxed launch's denied loopback startup remains in the run manifest's
`worker_failures`; resuming that same run after the authorized local-RPC access
completed all eight backend workers, with `status=complete` and
`completion_label=FULL_SEARCH`.

Standalone replay validated and replayed all **4 artifacts** from
`tune/optimal/20261001T192416.141960Z/best-manifest.json` without intermediate
build files. An audit matched every successful FSIM config exactly to one
positive TSIM record and confirmed the exported config and cycle count equal
the measured minimum for each occurrence. A foreign-model manifest was
rejected with `unsupported or mismatched best manifest`.

## T13: selected deployment and MAC utilization

The optimal manifest was applied to one committed sample,
`down-00176480_nohash_0.wav` (SHA-256
`68d8077e68d9c2c02a9eb744061e934f514fc523aa90ee63fd56bfec0227e65d`). The
deployment passed KWS HOST-reference correctness and covered all four routed
VTA occurrences. Every real deployment/AutoTVM cycle pair passed the inclusive
10% gate. Ordinary and debug full-model counters both measured 99,884 cycles.

| Occurrence | Symbol | Logical MACs | AutoTVM TSIM cycles | Deployment TSIM cycles | Difference | MAC utilization |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | `tvmgen_mlperf_kws_vta_main_0` | 512,000 | 24,970 | 24,971 | 0.0040% | 32.0372% |
| 1 | `tvmgen_mlperf_kws_vta_main_1` | 512,000 | 24,970 | 24,971 | 0.0040% | 32.0372% |
| 2 | `tvmgen_mlperf_kws_vta_main_2` | 512,000 | 24,970 | 24,971 | 0.0040% | 32.0372% |
| 3 | `tvmgen_mlperf_kws_vta_main_3` | 512,000 | 24,970 | 24,971 | 0.0040% | 32.0372% |

The 64-MAC/cycle geometry gives 2,048,000 useful logical MACs per invocation.
Measured untuned baseline and tuned complete-model TSIM cycles are 2,354,444
and 99,884 respectively, a 23.5718x cycle speedup. Whole-model utilization is
1.3591% for baseline and 32.0372% for tuned deployment. MAC counts derive from
the real Conv arithmetic; HOST work is excluded.

The versioned deployment evidence, MAC JSON/CSV and concise report are
`keyword_spotting_v1/tune/deployment-full.json`,
`keyword_spotting_v1/tune/mac-utilization-full.json`,
`keyword_spotting_v1/tune/mac-utilization-full.csv` and
`keyword_spotting_v1/tune/REPORT-FULL.md`.

## Verification

- Full search completed with the approved batch, quota, timeout and seed-gate
  identities; all four occurrence spaces were covered.
- Standalone optimal replay: **4 artifacts validated and replayed**; foreign
  model identity rejected.
- Selected deployment: `status=passed`, `sample_count=1`, 4/4 occurrence gates
  passed. HOST correctness and ordinary/debug full-model cycle agreement
  passed.
- `scripts/mac_utilization.py --deployment-report .../tune/deployment-full.json
  --output-json .../tune/mac-utilization-full.json` accepted the report; JSON,
  CSV and every occurrence row were cross-checked.
- Focused KWS and shared deployment/MAC regressions: **82 passed**.
- `git diff --check` and final managed-repository status passed.

## Commit maps

C5 began from root `6740415c8b24d2d3887b567f81383200f8abf655`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`1a84af5e74d01f4ad7d64aa92dc1b3153f58bd41`.

| Task | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| T12 | `dfeeb6bd39c283c5c7fae88b7887aad3d18a53d7` | unchanged | `a4c2db134d8b54d5b7bcfd31fd6eb488774c4447` | C5 search evidence, KWS optimal manifest and four result/native-record pairs |
| T13 | See final task commit map | unchanged | See final task commit map | KWS selected deployment, MAC JSON/CSV, report and final checkpoint |
