# Checkpoint C1 evidence

Initiative: `20261001-ic-v2-operator-tuning`
Branch: `codex/20261001-ic-v2-operator-tuning`

## Implemented

- T1 adds an IC V2-qualified AutoTVM fusion task and extracts all eight
  prepared VTA fusion occurrences with distinct symbol/occurrence identities
  and complete Conv/postprocessing values. FSIM and TSIM candidates use fresh
  measurement resources and the existing one-formal-call protocol.
- T2 adds model-local search, durable per-occurrence progress, resume identity
  checks, minimum-positive-cycle selection, validated standalone native record
  export/replay, CLI help/options, and the V2 tuning documentation.
- Bounded runs retain the `BOUNDED_SMOKE_INCOMPLETE` label. V1 keeps its own
  task name and unchanged interfaces.

## Verification evidence

- `test_fused_tuning.py`: 10 passed.
- `test_two_stage_measurement.py`: 2 passed, 1 real-backend test skipped by
  default; separate FSIM and TSIM invocations of the smoke passed, one candidate
  each.
- `test_two_stage_tuning.py`: 10 passed.
- V2 FSIM suite excluding the TSIM-specific test file: 84 passed, 1 skipped.
- V2 `test_tsim_deployment.py` in a separate `VTA_BACKEND=tsim` process:
  10 passed, including the real reloaded-bundle ten-sample TSIM matrix.
- V1 two-stage tuning and measurement regression tests: 10 passed.
- V2 CLI `--help` lists the approved search, resume, artifact and replay
  options.
- Bounded real V2 run for occurrence 0 used
  `--trial-batch 1 --min-successful 1`: FSIM reached 1 success after 18
  attempts; TSIM measured that success at 316257 cycles. It exported a
  `BOUNDED_SMOKE_INCOMPLETE` manifest. After removing the intermediate build
  directory, replay validated and lowered the exported record successfully.
  The temporary output was `/tmp/ic-v2-c1-artifacts/best-manifest.json`.

## Commits

- T1: root `7a151b064fe552cdec39c44dd9d16a362ab96847` →
  `d871ce7bbd562307614ba484a0da7672a0d5550a`; VTA
  `5b4cca7da0e50d1ac2d6f99ec89e4320acdc7b24` →
  `2a11dd66d537d90c59fcd8b35cf8b16ce3072a07`. TVM remained
  `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`.
- T2 implementation and evidence are included in the current checkpoint
  commit; its resulting repository commit map is reported at handoff.

## Scope and status

No model bytes, quantization policy, or VTA routing were changed. The bounded
run validates execution and artifact flow only; it is not full tuning evidence.
