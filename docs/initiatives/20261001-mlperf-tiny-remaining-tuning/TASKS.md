# Tasks: remaining MLPerf Tiny tuning

Initiative: 20261001-mlperf-tiny-remaining-tuning
Branch: codex/20261001-mlperf-tiny-remaining-tuning
Approved contracts: INTENT.md, CAPABILITY_MAP.md, SPEC-operator-tuning.md and SPEC-deployment-evidence.md.
Every task includes implementation, verification and a separate git-workflow commit. Every checkpoint returns GREEN only with clean repositories, exact commit maps and evidence. Dependencies include all earlier checkpoints unless explicitly stated. Do not edit approved lifecycle documents. Evidence files are CHECKPOINT-C<N>.md in this directory.

## Checkpoint C1: shared infrastructure (T1–T3)
- [ ] T1: Implement remaining-model complete-fusion extraction contract.
  - Acceptance: faithful Conv/Dense arithmetic and occurrence identities from real prepared graphs; unsupported arithmetic rejected; IC compatibility preserved.
  - Verify: actual graph extraction tests for four models and affected IC tests; inspect shapes/dtypes/constants/layouts and host inventory.
  - Primary files: shared extraction helper, extraction tests, at most two existing helper files if necessary. Scope: medium. Dependencies: none.
- [ ] T2: Implement seed/full search controller contract.
  - Acceptance: separate seed exports; full-search report gate; unique 100-trial batching to quota/exhaustion; every FSIM success attempted on TSIM; minimum positive deployable selection; atomic resume and replay identity checks.
  - Verify: controller tests for quota/exhaustion, seed gate identity, duplicate rejection, TSIM failures, interruption/resume and foreign/tampered artifacts; bounded backend smoke when adapters are available.
  - Primary files: shared tuning controller, worker helper, tuning tests, scripts/README.md. Scope: medium. Dependencies: T1.
- [ ] T3: Implement shared real-deployment evidence contract.
  - Acceptance: exact symbol-config lowering, one-sample reference checks, ordinary/debug agreement, graph-resident node cycles, <=10% gate and compatible MAC report; failure diagnostics preserved.
  - Verify: boundary/identity/counter tests and calculator regressions; preserve IC V2 strict/default behavior; later model tasks provide real integration.
  - Primary files: shared deployment helper, deployment tests, scripts/mac_utilization.py, calculator tests, scripts/README.md. Scope: medium. Dependencies: T1–T2.
Checkpoint verification: focused shared tests and affected IC regressions pass; implementation contracts ready for model-specific real validation.

## Checkpoint C2: AD adapter and seed gate (T4–T6)
- [ ] T4: Add anomaly_detection_v1 complete-fusion tuning adapter.
  - Acceptance: all actual deployed VTA MAC occurrences mapped to faithful tasks; model identity and preserved routing/preprocessing; model-local seed/full/resume/replay CLI.
  - Verify: extraction and CLI tests using actual prepared graph; enumerate occurrence/host coverage; verify no foreign-model reuse.
  - Primary files: anomaly_detection_v1/tune.py or adapter helper, tune/tune.py, tests/test_two_stage_tuning.py, README.md. Scope: medium. Dependencies: C1 and prior checkpoints.
- [ ] T5: Add anomaly_detection_v1 one-sample deployment adapter.
  - Acceptance: exact configs consumed in real lowering; existing HOST reference/tolerances and state/window semantics preserved; compatible versioned report and failure output.
  - Verify: model-specific dispatch/reference/profile tests and existing deployment regressions; MAC report compatibility.
  - Primary files: anomaly_detection_v1/tune/deployment.py, runtime.py if necessary, tests/test_deployment_profile.py, tests/test_tsim_deployment.py, README.md. Scope: medium. Dependencies: T4.
- [ ] T6: Execute AD complete seed gate.
  - Acceptance: one successful FSIM config and successful AutoTVM TSIM measurement per occurrence; real deployment all pairs <=10%; one sample correct and ordinary/debug counters agree. No full search before pass.
  - Verify: actual seed/deployment commands in approved specs; inspect native records and complete coverage; standalone seed replay; evidence names sample/state/window and exact integer comparisons.
  - Files: anomaly_detection_v1/tune/seed/<run-id>/ generated artifacts, seed deployment JSON, CHECKPOINT-C2.md. Scope: small source / generated evidence batch. Dependencies: T5.
Checkpoint verification: real complete seed gate passes, artifacts replay and repository clean.

## Checkpoint C3: AD full search and optimal deployment (T7–T8)
- [ ] T7: Complete AD full two-stage search.
  - Acceptance: bound seed gate; default 100 distinct FSIM trials per batch until >=20 successes or exhaustion for every occurrence; every success measured/attempted on TSIM; minimum-cycle deployable schedule exported per occurrence.
  - Verify: actual full command/resume as needed; audit counts, failure classifications and selected minima; replay all exported records without build intermediates; reject foreign identity.
  - Files: anomaly_detection_v1/tune/optimal/<run-id>/ generated artifacts, CHECKPOINT-C3.md. Scope: generated evidence batch. Dependencies: T6.
- [ ] T8: Deploy AD optimal schedules and calculate MAC utilization.
  - Acceptance: selected config attribution; real per-occurrence <=10% gate, one-sample correctness, ordinary/debug agreement; baseline/tuned whole-model cycles and deployment-cycle MAC rows published.
  - Verify: actual selected deployment and calculator commands; audit logical MAC derivations, invocation counts, report identities and all rows; model-focused and affected shared regression tests.
  - Files: anomaly_detection_v1/tune/deployment-full.json, MAC JSON/CSV, REPORT-FULL.md, CHECKPOINT-C3.md. Scope: generated evidence batch. Dependencies: T7.
Checkpoint verification: full search quota/exhaustion evidence, optimal deployment, MAC reports and self-contained replay pass; clean committed state.

## Checkpoint C4: KWS adapter and seed gate (T9–T11)
- [ ] T9: Add keyword_spotting_v1 complete-fusion tuning adapter.
  - Acceptance: all actual deployed VTA MAC occurrences mapped to faithful tasks; model identity and preserved routing/preprocessing; model-local seed/full/resume/replay CLI.
  - Verify: extraction and CLI tests using actual prepared graph; enumerate occurrence/host coverage; verify no foreign-model reuse.
  - Primary files: keyword_spotting_v1/tune.py or adapter helper, tune/tune.py, tests/test_two_stage_tuning.py, README.md. Scope: medium. Dependencies: C1 and prior checkpoints.
- [ ] T10: Add keyword_spotting_v1 one-sample deployment adapter.
  - Acceptance: exact configs consumed in real lowering; existing HOST reference/tolerances and state/window semantics preserved; compatible versioned report and failure output.
  - Verify: model-specific dispatch/reference/profile tests and existing deployment regressions; MAC report compatibility.
  - Primary files: keyword_spotting_v1/tune/deployment.py, runtime.py if necessary, tests/test_deployment_profile.py, tests/test_tsim_deployment.py, README.md. Scope: medium. Dependencies: T9.
- [ ] T11: Execute KWS complete seed gate.
  - Acceptance: one successful FSIM config and successful AutoTVM TSIM measurement per occurrence; real deployment all pairs <=10%; one sample correct and ordinary/debug counters agree. No full search before pass.
  - Verify: actual seed/deployment commands in approved specs; inspect native records and complete coverage; standalone seed replay; evidence names sample/state/window and exact integer comparisons.
  - Files: keyword_spotting_v1/tune/seed/<run-id>/ generated artifacts, seed deployment JSON, CHECKPOINT-C4.md. Scope: small source / generated evidence batch. Dependencies: T10.
Checkpoint verification: real complete seed gate passes, artifacts replay and repository clean.

## Checkpoint C5: KWS full search and optimal deployment (T12–T13)
- [ ] T12: Complete KWS full two-stage search.
  - Acceptance: bound seed gate; default 100 distinct FSIM trials per batch until >=20 successes or exhaustion for every occurrence; every success measured/attempted on TSIM; minimum-cycle deployable schedule exported per occurrence.
  - Verify: actual full command/resume as needed; audit counts, failure classifications and selected minima; replay all exported records without build intermediates; reject foreign identity.
  - Files: keyword_spotting_v1/tune/optimal/<run-id>/ generated artifacts, CHECKPOINT-C5.md. Scope: generated evidence batch. Dependencies: T11.
- [ ] T13: Deploy KWS optimal schedules and calculate MAC utilization.
  - Acceptance: selected config attribution; real per-occurrence <=10% gate, one-sample correctness, ordinary/debug agreement; baseline/tuned whole-model cycles and deployment-cycle MAC rows published.
  - Verify: actual selected deployment and calculator commands; audit logical MAC derivations, invocation counts, report identities and all rows; model-focused and affected shared regression tests.
  - Files: keyword_spotting_v1/tune/deployment-full.json, MAC JSON/CSV, REPORT-FULL.md, CHECKPOINT-C5.md. Scope: generated evidence batch. Dependencies: T12.
Checkpoint verification: full search quota/exhaustion evidence, optimal deployment, MAC reports and self-contained replay pass; clean committed state.

## Checkpoint C6: Streaming Wakeword adapter and seed gate (T14–T16)
- [ ] T14: Add streaming_wakeword_v1 complete-fusion tuning adapter.
  - Acceptance: all actual deployed VTA MAC occurrences mapped to faithful tasks; model identity and preserved routing/preprocessing; model-local seed/full/resume/replay CLI.
  - Verify: extraction and CLI tests using actual prepared graph; enumerate occurrence/host coverage; verify no foreign-model reuse.
  - Primary files: streaming_wakeword_v1/tune.py or adapter helper, tune/tune.py, tests/test_two_stage_tuning.py, README.md. Scope: medium. Dependencies: C1 and prior checkpoints.
- [ ] T15: Add streaming_wakeword_v1 one-sample deployment adapter.
  - Acceptance: exact configs consumed in real lowering; existing HOST reference/tolerances and state/window semantics preserved; compatible versioned report and failure output.
  - Verify: model-specific dispatch/reference/profile tests and existing deployment regressions; MAC report compatibility.
  - Primary files: streaming_wakeword_v1/tune/deployment.py, runtime.py if necessary, tests/test_deployment_profile.py, tests/test_tsim_deployment.py, README.md. Scope: medium. Dependencies: T14.
- [ ] T16: Execute Streaming Wakeword complete seed gate.
  - Acceptance: one successful FSIM config and successful AutoTVM TSIM measurement per occurrence; real deployment all pairs <=10%; one sample correct and ordinary/debug counters agree. No full search before pass.
  - Verify: actual seed/deployment commands in approved specs; inspect native records and complete coverage; standalone seed replay; evidence names sample/state/window and exact integer comparisons.
  - Files: streaming_wakeword_v1/tune/seed/<run-id>/ generated artifacts, seed deployment JSON, CHECKPOINT-C6.md. Scope: small source / generated evidence batch. Dependencies: T15.
Checkpoint verification: real complete seed gate passes, artifacts replay and repository clean.

## Checkpoint C7: Streaming Wakeword full search and optimal deployment (T17–T18)
- [ ] T17: Complete Streaming Wakeword full two-stage search.
  - Acceptance: bound seed gate; default 100 distinct FSIM trials per batch until >=20 successes or exhaustion for every occurrence; every success measured/attempted on TSIM; minimum-cycle deployable schedule exported per occurrence.
  - Verify: actual full command/resume as needed; audit counts, failure classifications and selected minima; replay all exported records without build intermediates; reject foreign identity.
  - Files: streaming_wakeword_v1/tune/optimal/<run-id>/ generated artifacts, CHECKPOINT-C7.md. Scope: generated evidence batch. Dependencies: T16.
- [ ] T18: Deploy Streaming Wakeword optimal schedules and calculate MAC utilization.
  - Acceptance: selected config attribution; real per-occurrence <=10% gate, one-sample correctness, ordinary/debug agreement; baseline/tuned whole-model cycles and deployment-cycle MAC rows published.
  - Verify: actual selected deployment and calculator commands; audit logical MAC derivations, invocation counts, report identities and all rows; model-focused and affected shared regression tests.
  - Files: streaming_wakeword_v1/tune/deployment-full.json, MAC JSON/CSV, REPORT-FULL.md, CHECKPOINT-C7.md. Scope: generated evidence batch. Dependencies: T17.
Checkpoint verification: full search quota/exhaustion evidence, optimal deployment, MAC reports and self-contained replay pass; clean committed state.

## Checkpoint C8: VWW adapter and seed gate (T19–T21)
- [ ] T19: Add visual_wake_words_v1 complete-fusion tuning adapter.
  - Acceptance: all actual deployed VTA MAC occurrences mapped to faithful tasks; model identity and preserved routing/preprocessing; model-local seed/full/resume/replay CLI.
  - Verify: extraction and CLI tests using actual prepared graph; enumerate occurrence/host coverage; verify no foreign-model reuse.
  - Primary files: visual_wake_words_v1/tune.py or adapter helper, tune/tune.py, tests/test_two_stage_tuning.py, README.md. Scope: medium. Dependencies: C1 and prior checkpoints.
- [ ] T20: Add visual_wake_words_v1 one-sample deployment adapter.
  - Acceptance: exact configs consumed in real lowering; existing HOST reference/tolerances and state/window semantics preserved; compatible versioned report and failure output.
  - Verify: model-specific dispatch/reference/profile tests and existing deployment regressions; MAC report compatibility.
  - Primary files: visual_wake_words_v1/tune/deployment.py, runtime.py if necessary, tests/test_deployment_profile.py, tests/test_tsim_deployment.py, README.md. Scope: medium. Dependencies: T19.
- [ ] T21: Execute VWW complete seed gate.
  - Acceptance: one successful FSIM config and successful AutoTVM TSIM measurement per occurrence; real deployment all pairs <=10%; one sample correct and ordinary/debug counters agree. No full search before pass.
  - Verify: actual seed/deployment commands in approved specs; inspect native records and complete coverage; standalone seed replay; evidence names sample/state/window and exact integer comparisons.
  - Files: visual_wake_words_v1/tune/seed/<run-id>/ generated artifacts, seed deployment JSON, CHECKPOINT-C8.md. Scope: small source / generated evidence batch. Dependencies: T20.
Checkpoint verification: real complete seed gate passes, artifacts replay and repository clean.

## Checkpoint C9: VWW full search and optimal deployment (T22–T23)
- [ ] T22: Complete VWW full two-stage search.
  - Acceptance: bound seed gate; default 100 distinct FSIM trials per batch until >=20 successes or exhaustion for every occurrence; every success measured/attempted on TSIM; minimum-cycle deployable schedule exported per occurrence.
  - Verify: actual full command/resume as needed; audit counts, failure classifications and selected minima; replay all exported records without build intermediates; reject foreign identity.
  - Files: visual_wake_words_v1/tune/optimal/<run-id>/ generated artifacts, CHECKPOINT-C9.md. Scope: generated evidence batch. Dependencies: T21.
- [ ] T23: Deploy VWW optimal schedules and calculate MAC utilization.
  - Acceptance: selected config attribution; real per-occurrence <=10% gate, one-sample correctness, ordinary/debug agreement; baseline/tuned whole-model cycles and deployment-cycle MAC rows published.
  - Verify: actual selected deployment and calculator commands; audit logical MAC derivations, invocation counts, report identities and all rows; model-focused and affected shared regression tests.
  - Files: visual_wake_words_v1/tune/deployment-full.json, MAC JSON/CSV, REPORT-FULL.md, CHECKPOINT-C9.md. Scope: generated evidence batch. Dependencies: T22.
Checkpoint verification: full search quota/exhaustion evidence, optimal deployment, MAC reports and self-contained replay pass; clean committed state.

## Checkpoint C10: final delivery (T24–T25)
- [ ] T24: Publish four-model result summary and maintained commands.
  - Acceptance: complete occurrence counts, success/exhaustion/TSIM counts, selected cycles, maximum deviations, sample identities, model cycles and operator MAC report links; reproducible seed/full/deploy/resume/replay commands documented.
  - Verify: cross-check summary against committed native/JSON evidence; no isolated cost labeled measured whole-model; all four models present.
  - Primary files: initiative RESULTS.md, scripts/README.md, benchmark README.md. Scope: medium. Dependencies: C9.
- [ ] T25: Complete scoped final regression and evidence audit.
  - Acceptance: affected model/shared/IC/calculator regressions and role-workflow validation pass; all artifacts replay; source and generated evidence identities consistent; no incomplete smoke labeled full.
  - Verify: scoped pytest commands from specs/README, bash .agents/custom/scripts/test-role-workflow, final git-workflow status; use narrow existing checks and rebuild only for necessary source changes.
  - Files: CHECKPOINT-C10.md; attributable test repairs within delegated implementation scope, at most four additional files. Scope: medium. Dependencies: T24.
Checkpoint verification: final evidence and task commit maps ready for fresh Reviewer on complete base-to-tip ranges.

## Review handoff
Root dispatches read-only Reviewer after C10. Required findings are fixed by a fresh Default and re-reviewed automatically. Reviewer Pass completes delivery; user owns optional merge.
