# Checkpoint C10: final delivery

Initiative: `20261001-mlperf-tiny-remaining-tuning`
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`
Status: **GREEN**

## T24: four-model results and commands

Published [`RESULTS.md`](RESULTS.md) with one summary row per model and all 27
deployed VTA occurrence rows. The occurrence table records logical MACs,
AutoTVM-to-deployment TSIM cycle pairs, deviation, per-occurrence MAC
utilization, workload SHA-256, and selected config SHA-256. The summary records
full-search FSIM attempts/successes, TSIM success coverage, exhausted spaces,
maximum deviation, committed sample identity and hash, measured baseline and
tuned whole-model cycles, and whole-model MAC utilization. It distinguishes
measured full-model cycles from isolated operator measurements and links the
committed optimal manifests, deployment JSON, and MAC CSV/JSON artifacts.

Added the four-model seed/full/deploy/resume/replay/calculator command template
to `scripts/README.md` and `vta/apps/mlperf_tiny_benchmark/README.md`. Commands
select one model at a time, keep FSIM and TSIM in separate processes, and use
the one-sample deployment entry point. `git diff --check` passed. The results
summary audit checked each table cycle pair, occurrence count, utilization,
and identity against the committed model reports and optimal manifest.

## T25: final verification

- `bash .agents/custom/scripts/test-role-workflow` — passed.
- FSIM-focused shared, four-model, and IC V1/V2 regressions — **144 passed,
  1 skipped**. The skip is the explicitly gated IC V2 real-candidate smoke
  (`IC_V2_SIMULATOR_SMOKE=1`); no source change required it.
- TSIM-focused deployment test files were run separately to keep each
  model-local top-level `runtime` import isolated. Results: AD **9 passed, 1
  integration deselected**; KWS **9 passed**; Streaming Wakeword **7 passed**;
  VWW **7 passed**; IC V1 **8 passed, 1 integration deselected**; IC V2 **10
  passed, 1 integration deselected**. Ten-sample full deployment matrix tests
  were excluded; the approved selected-deployment evidence uses one sample.
- Running all model-local TSIM files in one pytest process first exposed the
  test fixtures' shared top-level import names (`runtime` and
  `graph_artifacts`), causing cross-model import collisions. No source change
  was made; each affected file passed in its own process with the intended
  TSIM environment.
- Standalone optimal-manifest replay passed without using any intermediate
  search result to identify selected records: AD **9 artifacts**, KWS **4**,
  Streaming Wakeword **1**, and VWW **13**. All report `FULL_SEARCH`.
- The independent identity/candidate audit checked actual model and geometry
  hashes, full-search options and labels, distinct FSIM visited indices,
  successes within visited indices, every-success-to-TSIM coverage, positive
  TSIM cycles, minimum-cycle selection, report/manifest identities, the
  inclusive 10% deployment gate, one-sample protocol, and ordinary/debug
  whole-model counter agreement for all four models. Audit passed: 27/27
  occurrence identities and cycle reports matched.
- `git diff --check` and managed-repository status passed before the evidence
  commit. No test repairs or source changes were needed.

## Commit maps

C10 began from root `79d6c7086802a72688cad274869f9cb1bff8a19d`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`9b2e84b3c0e93dc19be24e4680fce220aef36d3c`.

| Task | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| T24 | `dc9c32a6d1647c1ab1e3be4af911d5abc9802741` | unchanged | `9e4935eda0ef229792218a7d02f60fda00531114` | `docs/initiatives/20261001-mlperf-tiny-remaining-tuning/RESULTS.md`; root and benchmark `README.md` command documentation |
| T25 evidence | recorded after this file is committed | unchanged | unchanged | `docs/initiatives/20261001-mlperf-tiny-remaining-tuning/CHECKPOINT-C10.md` |

The clean source map before the T25 evidence commit is root
`dc9c32a6d1647c1ab1e3be4af911d5abc9802741`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`9e4935eda0ef229792218a7d02f60fda00531114`. TVM had no C10 changes.

## Limits

The final verification did not rerun any full FSIM search or selected
deployment simulation. It used the committed completed-run evidence, replayed
all optimal artifacts, and ran the scoped regression suites above. The
ten-sample IC V2 integration contract remains unchanged and was not run as part
of this one-sample final delivery.
