# Checkpoint C6: Streaming Wakeword adapter and seed gate

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## Completed tasks

- **T14:** Added a Streaming Wakeword V1 adapter for the actual prepared graph.
  The single routed VTA Conv occurrence becomes one complete fused AutoTVM
  workload; host-routed dense, softmax, and reshape operators remain in the
  existing model pipeline. The local CLI supports seed, alignment-gated full
  search, resume, and standalone replay.
- **T15:** Added exact-manifest deployment with selected-config lowering,
  existing HOST output comparison, graph-resident node profiling, ordinary and
  debug TSIM counters, and the shared versioned evidence format. The deployment
  records one committed WAV, one fixed 16,000-sample audio window, 30 log-mel
  feature frames, one model invocation, and stateless single-invocation policy.
- **T16:** Completed one FSIM seed success, one AutoTVM TSIM measurement,
  standalone replay, and real one-sample TSIM deployment. No full search ran.

## Seed and deployment evidence

The successful seed run is `20261001T204808.167658Z`. Its valid configuration
space contains 240 candidates. The seed batch size was one and stopped after
16 distinct attempts: 15 candidate failures followed by one successful FSIM
schedule at config index 4. Eight failures were VTA copy-pattern alignment
errors; seven were other schedule/build/runtime failures. The completed run
has no infrastructure errors. Every successful FSIM schedule received one
successful AutoTVM TSIM measurement: 19,054 cycles using the single-call TSIM
protocol.

The self-contained manifest replay validated and replayed **1 artifact**.
The real deployment passed HOST output correctness for sample
`marvin-00176480_nohash_0.wav` (SHA-256
`b95e103110b89a0d4dff88023edd537a92834f565cb8e3f38b16f725f3d58451`). The
selected node measured 19,055 TSIM cycles against 19,054 AutoTVM cycles, a
0.005248% relative difference. The inclusive 10% gate passed. Ordinary and
per-layer debug whole-model counters both measured 19,055 cycles; the untuned
baseline measured 174,633 cycles. The report records one sample and one model
invocation with the state and window policy above.

The durable seed manifest and its native/result record pair are under
`streaming_wakeword_v1/tune/seed/20261001T204808.167658Z/`; deployment evidence
is `streaming_wakeword_v1/tune/deployment-seed.json`.

An initial sandboxed FSIM process could not bind AutoTVM's localhost RPC tracker
and recorded an infrastructure failure before measuring candidates. The
approved localhost retry completed in a fresh run directory; the failed
startup remains in the ignored run diagnostics and is not part of seed
coverage.

## Verification

- Adapter and deployment CLI/model-specific contracts plus all existing
  Streaming Wakeword regressions:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests -q`
  — **56 passed**.
- Seed command with `VTA_BACKEND=fsim`:
  `.../streaming_wakeword_v1/tune/tune.py --seed --all --trial-batch 1`
  — `SEED_COMPLETE`, 16 FSIM attempts, 1 success, 1/1 TSIM measurement.
- Standalone replay command with `VTA_BACKEND=tsim`:
  `.../streaming_wakeword_v1/tune/tune.py --replay-manifest .../best-manifest.json`
  — **1 artifact replayed**.
- Real deployment command with `VTA_BACKEND=tsim`:
  `.../streaming_wakeword_v1/tune/deployment.py --best-manifest .../best-manifest.json --output .../deployment-seed.json`
  — `status=passed`, one sample, one occurrence gate, exact HOST output,
  ordinary/debug counter agreement.
- `git diff --check` and final managed-repository status passed.

## Commit maps

C6 began from root `2de6169998a30f23fb58bae170e4ad790e12f358`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`29c1f06b00565748cd804013c291e25139ef2813`.

| Task | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| T14 | `62bac514650ebdb3baec59f93cff2a31c29345d1` | unchanged | `700e42a04877ec26fcd34718a0c8059071b51698` | Streaming Wakeword tuning adapter, model-local two-stage CLI, adapter tests and README commands |
| T15 | `d4a581f4421c786b36bd23c0a5df40e3ef0f790d` | unchanged | `c15bd4cbf2edbb7a2433fd0d413f4bf43d2a44ac` | deployment adapter, one-window/state contract tests, README deployment command, runtime-asset test boundary |
| T16 | `db28f2809f09bf83f58d9d6f5b85b313240d0777` | unchanged | `f7c6b90e5431b1a508a93a803a0abe49d36c63ab` | seed native/result/manifest artifacts, passing deployment report, runtime window constant, artifact ignore exceptions |

The checkpoint evidence commit is recorded in the root repository after this
file is committed. TVM has no C6 source changes and remains at
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`.

## Limits

This checkpoint proves seed schedule/deployment alignment only. It does not
claim 20 successful schedules or search-space exhaustion; C7 owns the full
search and minimum-cycle deployment.
