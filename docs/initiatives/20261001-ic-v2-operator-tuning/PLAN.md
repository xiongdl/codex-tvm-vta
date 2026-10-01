# Implementation plan: IC V2 operator tuning

Initiative: 20261001-ic-v2-operator-tuning
Branch in root, tvm and vta: codex/20261001-ic-v2-operator-tuning
Approved input: INTENT.md, CAPABILITY_MAP.md, SPEC-two-stage-tuning.md and SPEC-deployment-validation.md in this directory. User approved specifications on 2026-10-01.

## Approach
Extend the proven IC V1 complete-fusion tuning and deployment approach to IC V2 with explicit model-specific identities. First establish real V2 fusion extraction and single-candidate measurement; next implement durable full search, export and replay; then implement selected-config deployment and strict comparison. A bounded end-to-end run first verifies all eight performance comparisons on one sample; only after that passes, it verifies correctness on ten samples. This identifies integration failures before the expensive full search. Finally complete all eight occurrences, execute all ten samples, and commit verifiable best artifacts and the real deployment report.

Retain V1 interfaces and measurement semantics. Prefer reuse of model-independent helpers; any sharing must have explicit model/task/runtime dependencies and import isolation. Avoid blindly importing V1's model pipeline or registering V2 tasks under the V1 task name. Concrete helper placement is an implementation choice within the delegated paths, subject to the approved contracts. No new dependencies, quantization changes or routing changes are planned.

The selected schedule is the minimum positive TSIM-cycle candidate that lowers for the real fusion, with rejected candidates attributable. Comparison failures must be investigated in fusion scope, counting, dispatch or lowering; selecting a slower candidate solely to meet agreement is prohibited. V2's strict threshold uses integer arithmetic and has explicit equality tests. Existing V1 <=10% compatibility remains intact unless a shared implementation can preserve it explicitly.

## Ordered checkpoints
1. C1, tasks T1–T2: real fusion tasks and durable two-stage tuning, including standalone export/replay and tuning command documentation.
2. C2, tasks T3–T4: real deployment profiling with strict validation, followed by bounded end-to-end simulator verification.
3. C3, tasks T5–T6: complete default search with committed selected artifacts; full real deployment and final performance evidence.

Each checkpoint is executed by one fresh Default, sequentially. Each task is verified and committed separately through git-workflow. A checkpoint is an execution boundary, not a user gate. Root dispatches an independent fresh Reviewer after C3. Implementation findings route through fresh Default Fix/Verify and fresh Reviewer until Pass. Root never takes over a running delegated agent.

## Verification
Use project Python and explicit absolute geometry with matching backend in separate FSIM/TSIM processes. Focused tests cover real extraction, search bookkeeping, selection, artifact identity, resume and replay; deployment tests cover strict boundaries, occurrence mapping, selected dispatch and instrumentation. Run affected V1 regressions for shared helper changes. Bounded real runs prove both simulators and selected deployment. Performance alignment and full-model baseline/tuned counters use one sample only, before ten-sample correctness execution. Only full default search plus all-eight strict comparisons on that one sample and all-ten output checks satisfy completion.

TASKS.md defines exact commands, task ownership and evidence. At each task's final verification, write evidence before verification and make no content changes between successful final verification and commit. Record task commits and per-repository OIDs in the agent's return; checkpoint evidence is written within delegated checkpoint files before the final task's verification and commit.

## Risks and response
| Risk | Response |
| --- | --- |
| Larger V2 channels make searches expensive | Durable state, progress evidence, resume with unchanged defaults; bounded run first. No smaller success target for final acceptance. |
| V1/V2 import or task-registration collisions | Explicit model-qualified task/module identity and cross-model rejection tests. |
| Isolated and deployed fusion lowering differ | Compare complete arithmetic, selected config dispatch and real graph-resident node counters; fix within approved scope and remeasure. |
| Debug instrumentation changes counts | Require agreement with ordinary full-model invocation before using per-node counters. |
| Exactly 10% accidentally passes | Exact integer strict checks and both-direction boundary tests. |
| External permissions or environment unavailable | Return Root escalation with exact command/evidence; preserve completed artifacts and resume state. |

## Ownership and handoff
Defaults own only paths listed for their checkpoint, with approved artifacts read-only. All operate on the common task branch and committed OIDs. They are not alone in the codebase and must preserve others' changes. Root supplies current committed maps; any unexpected dirty state is an escalation. Original bases: root 7a151b064fe552cdec39c44dd9d16a362ab96847; tvm 9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca; vta 5b4cca7da0e50d1ac2d6f99ec89e4320acdc7b24.

## Open questions
None. No remote push or merge is requested. User owns optional final merge.

## Approved clarification (2026-10-01)

The user explicitly clarified and authorized: one sample suffices for AutoTVM-to-deployment performance alignment for all eight VTA occurrences; after that passes, run the optimal configuration on ten samples solely to verify correctness. This supersedes any earlier requirement to profile ten samples or to execute them before the one-sample performance gate. Strict <10% and single counted invocation with warmup excluded remain unchanged.
