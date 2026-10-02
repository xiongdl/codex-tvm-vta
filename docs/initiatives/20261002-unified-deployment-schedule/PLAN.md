# Implementation plan
Initiative: 20261002-unified-deployment-schedule
Branch: codex/20261002-unified-deployment-schedule
Specify batch approved by human: 2026-10-02 “确认”.
This plan requires explicit approval before any implementation.
Approved source: INTENT.md, CAPABILITY_MAP.md, and all four SPEC-*.md.

## Architecture and dependency order
Start with an end-to-end IC V2 slice to resolve the high-risk actual-computation capture seam. Capture the outlined deployment Relay function and schedule context, before schedule decisions become fixed. Candidates re-enter the same VTA legalization/packing/lowering code as ordinary deployment. Never clone already-scheduled TIR or hand-reconstruct fusion arithmetic.
Place reusable facilities in vta/apps/common as an importable package; retain benchmark model registration in mlperf_tiny_benchmark. Avoid broad TVM changes; VTA lowering changes are allowed only where needed to expose shared compute/configuration-space capture.

Checkpoints C1–C3 deliver IC V2 default/candidate/best operation and actual-compute tuning. C4–C8 migrate the other models sequentially. C9 retires obsolete shared infrastructure after dependency replacement. C10 adds scoped cleanup. C11 completes documentation, integration evidence and independent review.

## Concrete interfaces
- run.py --schedule PATH|none; omitted means none. PATH is one exported native AutoTVM log plus automatically discovered same-stem JSON metadata.
- run.py --deployment-report PATH emits shared provenance/coverage evidence using the same execution path.
- run.py --validate-schedule-evidence additionally performs the model's existing seed/selected cycle-alignment and sample gates. It requires suitable TSIM measurement provenance; arbitrary candidates do not need these gates merely to run.
- tune.py --seed --all exports a deployable seed snapshot through actual-compute lowering.
- tune.py --all --alignment-report PATH runs full search, preserving existing search/quota/timeouts.
- tune.py --workload-index N limits search to one actual occurrence; export remains a valid partial schedule.
- tune.py --resume-manifest PATH resumes a matching internal search state.
- tune.py --export-candidate N --resume-manifest PATH --output-log PATH exports the Nth ledger candidate (zero-based ledger position for each selected workload; choose one workload with --workload-index). A syntactically valid unmeasured candidate may be exported, with validation status explicit.
- tune.py --export-best --resume-manifest PATH --output-log PATH exports the best successful measured config for each selected occurrence. Search completion automatically exports the same best-snapshot format.
- Preserve the existing bounded controls: --trial-batch, --min-successful, --max-workloads, --fsim-timeout, --tsim-timeout. Print exact native-log, metadata and resume paths.
- Optional apps/common migration wrapper converts a validated historical full-fusion manifest to the new pair; never treats old evidence as proof of new measurement correctness.
- scripts/clean_mlperf_tiny.py --model ID|all --cache|--tuning-runs [--dry-run]; category required. Run cleanup against fixtures during implementation, not the user's existing results.

Snapshots contain one configuration per represented occurrence, bound to real compute/model/geometry identities. Partial coverage uses defaults with explicit per-layer reporting. Duplicate, unknown, mismatched or corrupt entries fail. Candidate costs are optional; backend/cycle protocol only describe measurements that actually exist. No timing unit conversion invents TSIM cycles.

## Source organization
common/deployment_compute.py: layer descriptions and actual lowering/config-space capture.
common/schedule.py: artifact schema, atomic export/load, selection, coverage.
common/measurement.py: simulator workers, provenance, actual-task execution.
common/tuning.py: search/controller/resume/candidate ledger.
common/deployment.py: shared schedule application and evidence helpers.
common/artifacts.py: generated-output categories/cleanup inventory.
common/tests/: focused provider-contract tests.
Each model retains its preprocessing, asset handling, sample policy and HOST checks. Its run.py calls runtime.py; its tune.py uses common tuning with a model adapter. tune/ becomes saved artifacts only.
Existing common helper files can transition temporarily as internal forwarding modules until C9; old public CLI support is removed for each model as it migrates.
Preserve historical committed evidence at existing paths; consolidate ignore rules without deleting evidence or broadening generated-file tracking.

## Verification
Every task is independently verified and committed. TASKS.md is the sole executable task list; no task-status edits by Default are needed. Delegated GREEN reports and commit maps track progress.
Commands run from root, using ./.envs/tvm-vta-env/bin/python, explicit VTA_CONFIG_FILE, backend and appropriate PYTHONPATH. Shared tests need vta/apps; model tests additionally need the chosen model directory when old imports require it.
C1 proves real arithmetic/output and config changes. C2 proves the artifact/error contract. C3 proves default, partial and complete IC V2 deployment plus bounded seed/search/resume/export.
Other models repeat these contracts using representative inputs and HOST reference comparisons.
Preserve existing strict IC V2 evidence checks, other model sample policies, and tsim_single_call v1. Separate isolated task cycles, graph-resident layer cycles and whole-model cycles.
Run focused tests per task, meaningful model integration at checkpoints, and the full maintained BYOC gate once all callers are migrated. Do not launch six exhaustive searches to prove a structural refactor.

## Risks and mitigations
| Risk | Mitigation |
|---|---|
| TECompiler capture loses bound constants, ABI or packing | Early IC V2 real-layer input/output comparison and configuration-sensitive lowered output checks |
| Captured default configuration space differs from candidate path | Validate template/config-space identity at capture, export and application |
| Cached lowering ignores changed config | Clear compiler cache in owned scope, test two configs and exception restoration |
| Standalone and resident timings differ | Preserve separate units/scopes; run existing strict evidence gates |
| Legacy helpers remain runtime dependencies | Read-only reference audit before removal; move used helpers before deleting public CLI |
| Historical records encode handcrafted task identities | Explicit validated migration or actionable rejection, retain historical files |
| Search state is mistaken for cache | Categorized inventory; cleanup defaults do not erase resume state |
| Task grows beyond five files | Split implementation within approved acceptance contract into another attributable local commit; report exact scope. Do not change approved Root artifacts |

## Execution and review
Run checkpoints in order, each with a fresh Default, waiting for completion before continuing. Each named task is a separate verified commit. No parallel execution.
After C11, dispatch a fresh Reviewer over the complete per-repository base-to-tip range. Route all actionable findings to a fresh Default, then re-review. Human owns optional final merge.

## Base commit map
- root: 7416243c22d59300c22e6c222c364d155a7fb7e8
- tvm: 9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca
- vta: a24152a6875b4fe09d3d43a150bac3727b435688

No unresolved user-owned design choices. Implementation that cannot satisfy actual-compute equivalence escalates rather than substituting handwritten fused tasks.
