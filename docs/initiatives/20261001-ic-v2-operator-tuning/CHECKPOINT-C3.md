# Checkpoint C3 evidence

Initiative: `20261001-ic-v2-operator-tuning`
Branch: `codex/20261001-ic-v2-operator-tuning`

## T5: full search and exported records

- Run ID: `20261001T035246.904010Z`; final manifest status `complete`, label
  `FULL_SEARCH`, unbounded, all eight workloads.
- FSIM successes and TSIM measurements by occurrence: `23/23, 28/28, 32/32,
  25/25, 23/23, 35/35, 23/23, 20/20`. All reached the default success quota;
  no configuration space was exhausted.
- Selected config indices: `314, 309, 171, 471, 418, 270, 589, 591`.
- Best TSIM cycles: `267819, 267565, 38273, 136801, 250389, 30634, 126893,
  241969`.
- The durable state retains initial local RPC tracker bind failures from the
  first restricted attempt as infrastructure errors. The authorized resume
  completed all eight workloads. Candidate errors remain classified separately
  and are not included in successful configuration counts.
- Standalone replay of the exported best manifest validated all eight entries
  and lowered them without intermediate build files. A copied manifest with
  `model=image_classification_v1` was rejected.

## T6: selected deployment

- Performance alignment used exactly one sample, `00-airplane.png`; full-model
  baseline was `21,226,413` cycles and tuned/debug/ordinary were each
  `1,360,351` cycles. Debug and ordinary counters agree.
- All eight occurrences passed the strict integer `<10%` gate. Deployed cycles
  were `267819, 267565, 38274, 136801, 250389, 30641, 126893, 241969`; the
  maximum difference was `0.022850%`.
- After the gate passed, ten selected-config outputs passed correctness checks.
  No ten-sample performance profiling was performed.
- The model-independent MAC calculator rejected the deployment JSON as an
  unsupported artifact kind, so no MAC utilization report was published.

## Verification commands and results

- Full resume: `tune/tune.py --all --resume-manifest
  build/two_stage_tuning/20261001T035246.904010Z/manifest.json` with the
  specified project environment, FSIM backend and unchanged default limits;
  `FULL_SEARCH` complete.
- Standalone replay: `tune/tune.py --replay-manifest
  tune/optimal/20261001T035246.904010Z/best-manifest.json`; 8 artifacts replayed.
- Foreign-model replay rejection: passed.
- `test_host_deployment.py`: 21 passed.
- `test_two_stage_tuning.py`: 10 passed.
- V2 FSIM tests excluding the separate TSIM test file: 97 passed, 1 skipped.
- V2 TSIM deployment suite: 11 passed in 175.80s. The first run exposed a test
  that accessed the removed eager `runtime.autotvm` attribute; the test now
  stubs the `_autotvm_api()` lazy import seam, and the complete rerun passed.
- V1 tuning and deployment-profile regressions: 26 passed.
- Full deployment command from `SPEC-deployment-validation.md`: passed with
  8/8 occurrence checks on one sample and 10/10 correctness outputs.

## Commits

- T5 AutoTVM lazy-import regression: VTA
  `c970bfaa465a1667fce1c366a4e9a11dbeec194b`; root
  `9f0dd1b5ea65ed0da40f54eea3ee497a4828cb13`; TVM unchanged at
  `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`.
- T5 selected artifact batch: VTA
  `3b30a8fbda60186f9e8109df32bca34856515fdd`; root
  `74b898c908b7a9de3dc5e4c692bf5a420e2f2be0`; TVM unchanged.
Full per-occurrence hashes and measurements are in
`vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/deployment-full.json`;
the reviewer-facing summary is in
`vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/REPORT-FULL.md`.
