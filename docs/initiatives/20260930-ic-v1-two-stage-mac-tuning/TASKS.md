# Tasks: 20260930-ic-v1-two-stage-mac-tuning

Branch: codex/20260930-ic-v1-two-stage-mac-tuning in ., tvm and vta.
Apply approved INTENT, capability map, module specs and PLAN in this directory.
Each task is a separate verified commit through git-workflow. Each Checkpoint is one fresh Default delegation, sequential, with no intermediate human approval gate. Owned paths below are repository-root-relative; tests/new helpers may be created at the stated paths. Do not edit approved lifecycle documents. Return exact commit maps and verification evidence, saved in CHECKPOINT-Cn.md under this initiative directory.

## Checkpoint C1: computation and measurement foundation

### T1 — Establish deployment-equivalent task computation (Medium)
- [ ] Acceptance: enumerate every real IC V1 VTA fusion and preserve occurrence identity; prove task computation/lowering matches real deployment including postprocessing and tensor argument order; logical MAC counts exclude padded lanes.
- [ ] Acceptance: reject unsupported/incomplete or semantically mismatched coverage with actionable evidence; verify outputs for representative fusions, including differing postprocessing.
- Verify: project Python pytest for tests/test_fused_tuning.py and tests/test_model_pipeline.py under the IC V1 app, with explicit FSIM environment and PYTHONPATH; real FSIM task-versus-deployment fusion execution where applicable.
- Owned paths (maximum 5): IC V1 fused_tasks.py; tests/test_fused_tuning.py; model_pipeline.py only if necessary; vta/python/vta/relay/transform.py only for a required equivalence fix; CHECKPOINT-C1.md.
- Dependencies: none. Preserve model semantics; architecture changes beyond equivalent lowering escalate.

### T2 — Reliable local RPC measurement and backend isolation (Medium)
- [ ] Acceptance: FSIM 60s and TSIM 120s are applied independently; TSIM measures a single counted invocation with warmup excluded; candidate abort/timeout does not poison subsequent trials.
- [ ] Acceptance: owned server/tracker/worker resources are cleaned on every path, infrastructure/permission errors are distinguished and encountered errors repaired or escalated with raw evidence.
- Verify: project Python pytest shared tests/test_autotvm_tuner.py plus new focused measurement tests; real local RPC smoke on both backends, including recovery after a failing candidate; inspect owned subprocess cleanup.
- Owned paths (maximum 5): shared autotvm_tuner.py; shared tests/test_autotvm_tuner.py; IC V1 tune/measurement.py; IC V1 tests/test_two_stage_measurement.py; CHECKPOINT-C1.md.
- Dependencies: T1. Shared defaults for unrelated commands remain compatible.

C1 exit: T1/T2 committed, focused tests and real RPC smoke pass, repository set clean. Return GREEN and commit map.

## Checkpoint C2: adaptive tuning and export

### T3 — All-workload adaptive FSIM search and TSIM candidate evaluation (Medium)
- [ ] Acceptance: default --all uses batches of 100 distinct trials until >=20 distinct successful schedules or space exhaustion; visited state survives batches/resume and last batch may be shorter.
- [ ] Acceptance: all distinct FSIM successes receive TSIM measurement; minimum valid TSIM cycles selects best; failures/progress/stop reasons are persisted in IC V1/build/ and mismatched resumes are rejected.
- Verify: project Python pytest IC V1 tests/test_two_stage_tuning.py covering success threshold, exhaustion, duplicates, resume, no-success and TSIM selection; bounded real multi-workload smoke with explicit incomplete labeling.
- Owned paths (maximum 5): IC V1 tune/tune.py; tune/search.py; tune/measurement.py; tests/test_two_stage_tuning.py; CHECKPOINT-C2.md.
- Dependencies: T2.

### T4 — Self-contained best artifacts and maintained interfaces (Medium)
- [ ] Acceptance: optimal native records and best manifest are in IC V1/tune/; replay validates model/geometry/configuration/protocol and does not require intermediate build/ artifacts.
- [ ] Acceptance: existing single-workload tune.py entry point remains usable via compatibility handling; usage documents paths, resume, timeouts and full versus bounded runs.
- Verify: focused artifact/replay and existing tests/test_tune.py; bounded export/replay with intermediate references unavailable; new and legacy --help with project Python; inspect generated placement and manifest hashes.
- Owned paths (maximum 5): IC V1 tune/artifacts.py; IC V1 tune.py; tests/test_tune.py; IC V1 README.md; scripts/README.md.
- Evidence: append to existing CHECKPOINT-C2.md as part of task commit (evidence file excluded from implementation file sizing).
- Dependencies: T3.

C2 exit: T3/T4 committed, bounded adaptive search/export/replay passes, clean repository set. Return GREEN with counts and commit map.

## Checkpoint C3: deployment evidence and generic calculator

### T5 — Apply selected schedules and profile real deployment (Medium)
- [ ] Acceptance: apply intended configuration to every deployed occurrence with validated identity and cache handling; actual baseline/tuned outputs match host reference on committed samples.
- [ ] Acceptance: collect real per-occurrence cycles and uninstrumented full-model cycles with aligned invocation counts, validate profiling equivalence, export versioned deployment JSON; per-operator absolute relative error uses selected AutoTVM cycles and fails above 10%.
- Verify: project Python pytest IC V1 tests/test_tsim_deployment.py and new tests/test_deployment_profile.py; real TSIM bounded selected-schedule deployment with actual per-occurrence cycle comparisons; preserve existing host/FSIM behavior.
- Owned paths (maximum 5): IC V1 runtime.py; tune/deployment.py; tune/artifacts.py; tests/test_deployment_profile.py; tests/test_tsim_deployment.py.
- Evidence: CHECKPOINT-C3.md.
- Dependencies: T4. Additional runtime instrumentation in TVM/VTA requires a focused fix within delegated behavior and must be reported to Root if it exceeds these owned paths.

### T6 — Generic deployment-based MAC utilization CLI (Medium)
- [ ] Acceptance: extend existing scripts/mac_utilization.py with --deployment-report and --output-json; model identity remains metadata, repeated occurrences remain counted; preserve scalar --macs/--cycles/--config interface.
- [ ] Acceptance: validate deployment contract and cycles, report operator and whole-model ratios using actual full-model cycles, baseline/tuned comparison and scope; reject incomplete/mismatched data and >10% comparisons with nonzero status.
- Verify: project Python pytest scripts/tests/test_mac_utilization.py using unrelated synthetic model IDs, repeated workloads, invocation normalization and 10% boundary tests; consume T5 real deployment report and reconcile output with counters; scalar/new --help.
- Owned paths (maximum 5): scripts/mac_utilization.py; scripts/tests/test_mac_utilization.py; scripts/README.md; IC V1 README.md; CHECKPOINT-C3.md.
- Dependencies: T5.

C3 exit: T5/T6 committed, real deployment/export/calculator path passes bounded verification, repository set clean. Return GREEN with actual cycle evidence and commit map.

## Checkpoint C4: full real tuning and final acceptance

### T7 — Complete full FSIM→TSIM tuning (Small maintained-code scope, long runtime)
- [ ] Acceptance: run every IC V1 workload using approved 100-trial increments, >=20 FSIM distinct-success quota or documented exhausted space, 60s/120s timeouts; measure every FSIM success on TSIM and export minimum-cycle best configurations.
- [ ] Acceptance: all required workloads have successful TSIM choices and full identity/coverage evidence; raw intermediates remain in IC V1/build/, final selected records and manifest in tune/; resolve encountered RPC failures without skipping coverage.
- Verify: execute documented full tuning command and validate counts/config uniqueness/native record hashes and stop reasons for every workload; resume/recovery as needed. Exhausted space with fewer than 20 successes is allowed and explicitly reported. No successful TSIM candidate is a failure.
- Owned paths: generated optimal files under IC V1/tune/; intermediate files under IC V1/build/; CHECKPOINT-C4.md. If implementation defects appear, repair within prior implementation modules and run their affected tests before committing; approved decisions remain fixed.
- Dependencies: T6. Commit real best artifacts and evidence, excluding bulk intermediates.

### T8 — Full-model validation, regression checks and final report (Small)
- [ ] Acceptance: execute real baseline/tuned deployment on committed samples, validate correctness and <=10% error for every operator; calculate baseline/tuned whole-model utilization from actual deployment cycles.
- [ ] Acceptance: produce readable and JSON final reports including per-occurrence MACs/cycles/utilization, all errors, search counts, coverage, full-model cycles, operator sum/residual and gains/limitations. Do not claim completion from bounded output.
- Verify: deployment validation command with final best manifest; scripts/mac_utilization.py consumes final deployment report; run focused tests for all changed modules plus affected IC V1 HOST/FSIM/TSIM deployment tests and bash scripts/test_vta_byoc.sh with documented environment. Required failures are fixed and rerun; unavailable infrastructure escalates.
- Owned paths: final validated deployment/utilization reports under IC V1/tune/; IC V1 README.md; scripts/README.md if runtime instructions need correction; CHECKPOINT-C4.md. Implementation fixes follow T7 scope rule.
- Dependencies: T7. Commit final reports and verification evidence separately from T7.

C4 exit: all workload searches complete, real deployment correctness and every <=10% comparison pass, reports verified, required regressions pass and repository set clean. Return GREEN, exact commit maps, commands/results, final artifact paths and known risks. Root then dispatches a fresh read-only Reviewer over the complete base-to-tip committed range.
