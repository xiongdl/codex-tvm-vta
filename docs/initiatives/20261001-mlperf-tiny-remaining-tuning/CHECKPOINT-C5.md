# Checkpoint C5: KWS full search and optimal deployment

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **IN PROGRESS**

## T12: full two-stage search

The C4 seed deployment gate was bound into the KWS full-search identity by
SHA-256 `bf3836df4c2bf8b33c47ab05f919208fcc661d6a32ca224b8acb874ed696d91b`.
The completed, unbounded run is
`20261001T192416.141960Z`, using the absolute committed
`vta/config/vta_64mac.json`, 100-candidate FSIM batches, a 20-success target,
60-second FSIM timeout and 120-second TSIM timeout.

| Occurrence | Valid space | FSIM attempts | FSIM successes | Candidate failures | TSIM attempts / successes | Selected AutoTVM TSIM cycles |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |
| 1 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |
| 2 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |
| 3 | 384 | 384 | 21 | 363 | 21 / 21 | 24,970 |

Every workload reached at least 20 distinct successful schedules. The selected
configuration is the minimum positive TSIM-cycle candidate among all 21
successful TSIM measurements for that occurrence. Each selected entry retains
its occurrence, symbol, workload/fusion/config hashes and native record.

The 363 unsuccessful FSIM candidate records per occurrence classify as 213
copy-pattern lowering failures and 150 schedule/build/execution failures.
One local-RPC infrastructure event per occurrence is also retained in the
FSIM state diagnostics. These events did not prevent full coverage: each state
records all 384 distinct configuration indices, 21 FSIM successes, and 21
successful TSIM measurements. The initial sandboxed launch's denied loopback
startup is retained in the run manifest's `worker_failures`; resuming the same
run after the authorized local-RPC access completed all four FSIM and TSIM
workers (`status=complete`, `completion_label=FULL_SEARCH`).

Standalone replay validated and replayed all **4 artifacts** from
`tune/optimal/20261001T192416.141960Z/best-manifest.json` without intermediate
build files. An audit matched every successful FSIM config exactly to one
positive TSIM record and confirmed the exported config and cycle count equal
the measured minimum for each occurrence.

T12 commit map will be recorded after task commit.

## T13: selected deployment and MAC utilization

Pending.
