# Tasks: IC V2 operator tuning

Initiative: 20261001-ic-v2-operator-tuning
Execute in order; one verified commit per task. Approved specifications are mandatory. No task may weaken the strict <10% criterion.

## Verification command contracts
Run from repository root. In the commands below, set backend explicitly to fsim for extraction/search unit tests and tsim for deployment integration. Never load both simulator backends into one process.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests -q
```

Use focused test-file selection for each task, documenting exact filenames and results. For V1 regressions, run a separate process with V1's app path in PYTHONPATH and the same environment/geometry. For TSIM tests replace VTA_BACKEND=fsim with VTA_BACKEND=tsim. Respect integration marker/environment requirements in the actual tests; list any deselection and provide actual simulator execution evidence separately.

## Checkpoint C1: tuning implementation
Owned paths: V2/fused_tasks.py, V2/tune.py if needed for V1-equivalent candidate worker integration, V2/tune/, V2/tests/test_fused_tuning.py, V2/tests/test_two_stage_*.py; model-independent helpers under mlperf_tiny_benchmark only when necessary; affected V1 helper/tests when sharing requires compatibility verification; V2/README.md, scripts/README.md, this initiative's CHECKPOINT-C1.md. Do not change model bytes, quantization or routing.

### T1: complete V2 fusion tasks and isolated measurement
- [ ] Implement model-specific extraction/task registration and one-candidate FSIM/TSIM measurement using the proven single-call protocol.
- Acceptance: all eight actual prepared V2 occurrences have complete arithmetic/shape identities; no V1 model imports or cross-model registration collision; one successful bounded candidate can be measured with each backend or infrastructure errors are distinguished from candidate failures.
- Verify: focused real-graph extraction and identity tests; separate-process FSIM and TSIM measurement smoke and cleanup/protocol tests.
- Likely files: V2/fused_tasks.py, V2/tune.py, V2/tune/measurement.py, V2/tests/test_fused_tuning.py, V2/tests/test_two_stage_measurement.py (up to five primary files).
- Dependencies: none.

### T2: durable full search and standalone artifacts
- [ ] Add V2 CLI orchestration, durable search/resume, minimum-cycle selection and standalone best export/replay.
- Acceptance: defaults use 100-trial batches and >=20 distinct successes or exhaustion; all successes receive TSIM measurement; artifact identity/coverage/integrity and resume mismatches are rejected; bounded runs are labeled incomplete and V1 compatibility is retained.
- Verify: focused search/selection/resume/export/replay negative tests, CLI help and changed V1 regression tests. Replay exported bounded records without requiring their intermediate build directory.
- Likely files: V2/tune/tune.py, V2/tune/search.py, V2/tune/artifacts.py, V2/tests/test_two_stage_tuning.py, README updates. Reuse existing independent helpers where possible; avoid a broad refactor.
- Dependencies: T1.
- Before final verification, document tuning command, prerequisites, outputs and side effects in V2/README.md and scripts/README.md; record C1 evidence.

C1 gate: task tests pass, backend measurement smoke is attributable, artifacts replay and managed repositories are clean after commits. Return GREEN with task commit maps.

## Checkpoint C2: selected deployment and bounded integration
Owned paths: V2/tune/deployment.py, V2/tests/test_deployment_profile.py, V2 runtime/graph helpers only as needed for selected deployment; model-independent deployment/report helpers and their focused tests when necessary; affected V1 compatibility tests; V2/README.md, scripts/README.md, this initiative's CHECKPOINT-C2.md. Tuning helper corrections are allowed only to satisfy already approved contracts. No change to approved artifacts or model/quantization/routing.

### T3: actual deployment profiling and strict cycle gate
- [ ] Consume complete selected artifacts, apply configurations per V2 symbol, reload deployed bundles, verify outputs, profile real VTA graph nodes and enforce strict integer threshold.
- Acceptance: selected configuration attribution and complete occurrence coverage are validated; debug and ordinary complete-run counters agree; every positive cycle pair is checked strictly below 10%, equality fails, and invalid report publication is blocked.
- Verify: focused dispatch/identity/instrumentation/report tests; below/equal/above threshold in both directions, invalid counts and large integers; affected V1 regressions.
- Likely files: V2/tune/deployment.py, V2/tests/test_deployment_profile.py and up to three required helper/test files.
- Dependencies: T2.

### T4: bounded end-to-end simulator verification
- [ ] Run a bounded search covering all eight occurrences with explicit incomplete status, replay selected artifacts and first execute selected-config real TSIM performance validation on one sample across all eight occurrences, then run the same selected configuration on ten samples for correctness only.
- Acceptance: both simulator stages, replay and actual deployment operate end to end; real per-occurrence measurements and output checks are available; any discrepancy is fixed inside approved scope without threshold relaxation or a slower substitute. Bounded evidence is never presented as completed full tuning.
- Verify: actual commands from specifications using --all --trial-batch 1 --min-successful 1 for smoke, with unchanged candidate timeouts; resume further valid candidates if required. Run deployment against that complete-coverage bounded manifest; run focused regressions for fixes.
- Likely files: necessary localized implementation fixes, command documentation and CHECKPOINT-C2.md (target <=5 edited source/test files per fix slice). Generated bounded build artifacts remain ignored.
- Dependencies: T3.
- Document deployment entry-point prerequisites, outputs and side effects in both READMEs before final verification.

C2 gate: attributable eight-occurrence bounded replay/deployment works, all ten outputs pass and strict comparison/protocol tests pass; clean committed state. A candidate-only failed trial is not an escalation; repair or continue the permitted search. Return GREEN with commands and maps.

## Checkpoint C3: full search and final deployment evidence
Owned paths: V2/tune/optimal/<full-run-id>/ exported best artifacts, V2/tune/deployment-full.json, V2/tune/REPORT-FULL.md, compatible MAC report if generated; localized V2/shared implementation and regression fixes required by full verification; this initiative's CHECKPOINT-C3.md. Keep intermediate graphs/logs/resume files under ignored V2/build/. Do not alter approved defaults or success conditions.

### T5: complete the default eight-occurrence search
- [ ] Run --all with default 100-trial batches, >=20 successes or exhaustion and 60/120-second timeouts. Resume interrupted valid state until all occurrences complete.
- Acceptance: all eight occurrences complete; every distinct FSIM success is measured on TSIM; minimum positive valid-cycle records and full model-specific manifest are exported and independently replayable.
- Verify: full-run counts/status/selection audit, exported native log hashes and standalone replay. Verify artifacts reject foreign identities; run focused affected tests if fixes occur.
- Likely files: complete best-manifest.json and per-occurrence exported result/native log pairs (generated artifact batch), plus checkpoint evidence. The multi-file artifact batch is one inseparable output, not independent implementation changes.
- Dependencies: T4.
- Commit selected artifacts only after completion and integrity/replay verification. Preserve ignored full search evidence for final report.

### T6: full selected deployment and publish evidence
- [ ] Execute deployment using T5's committed complete manifest; measure baseline/tuned ordinary full-model cycles and all eight real VTA node cycle pairs on exactly one sample; after this strict gate passes, verify all ten outputs using the same optimal configuration without repeating performance alignment; publish final evidence.
- Acceptance: eight of eight satisfy 10 * abs(deployed - best) < best; chosen configs and record hashes are attributable; all ten reference output checks pass; full-model figures are actual measurements and separately labeled; no final unresolved regression remains.
- Verify: actual full deployment command in SPEC-deployment-validation.md, validate deployment JSON and optional MAC report, run focused V2 tests and affected V1/shared regressions. Confirm debug/ordinary agreement. Record exact commands, counts, config indices, cycle pairs, differences, outputs, full-model cycles, failure/root-cause evidence and known limitations in REPORT-FULL.md and CHECKPOINT-C3.md before final verification.
- Likely files: deployment-full.json, REPORT-FULL.md, CHECKPOINT-C3.md, optional MAC JSON; localized contract-preserving fixes and meaningful regression tests if required. Reverify affected final artifacts after any fixes.
- Dependencies: T5.

C3 gate: complete default search, all-eight strict agreement and all-ten correct outputs with committed self-contained evidence; clean state. Return GREEN with full base-to-tip maps and known risks for Root's independent Reviewer.

## Final review
Root dispatches fresh Reviewer on complete committed ranges against approved artifacts. Required findings receive fresh Default Fix/Verify and fresh Reviewer; continue until Pass. No additional checkpoint approval is required after Plan/Tasks approval. Optional final merge remains user-owned.

## Approved clarification (2026-10-01)

The user explicitly clarified and authorized: one sample suffices for AutoTVM-to-deployment performance alignment for all eight VTA occurrences; after that passes, run the optimal configuration on ten samples solely to verify correctness. This supersedes any earlier requirement to profile ten samples or to execute them before the one-sample performance gate. Strict <10% and single counted invocation with warmup excluded remain unchanged.
