# Implementation plan: stable Architecture Reviewer

## Approved baseline

Initiative: `20261003-mature-architecture-reviewer`.
User approved SPEC on 2026-10-04. Primary repository Specify baseline:
`21ab5171bf43fd46dafd62a6a229c38f695bcd62`, paths
`docs/initiatives/20261003-mature-architecture-reviewer/INTENT.md` and `SPEC.md`.
Unchanged managed repositories: `tvm` at
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`; `vta` at
`2708a80c19246ec99efe359125f02ae9b121e164`.

## One complete contract update

One checkpoint and one cohesive task deliver the role, its producer-side mapping
agreement, stable contract checks and verification record together. Splitting
these edits into independent commits could leave producer and reviewer inputs
inconsistent. No concurrent work or new architecture is required.

Task 1 work maps directly to SPEC:

| Specify obligation | Implementation work | Acceptance and verification |
| --- | --- | --- |
| Reviewer workflow, common standard, both six-axis scopes, evidence and output | Rewrite architecture-reviewer.md in direct English, using short steps and one verdict table/schema | Trace all approved checks to final sections; manual scenario review |
| Committed input contract and role ownership | Add shared mapping paragraph to Root's Delegation contract, preserve its lifecycle | Compare producer/consumer inputs; primary/submodule mapping scenarios |
| Stable critical invariants | Extend existing test-role-workflow with a small number of assertions for mapping, read-only scope and verdict priority | Existing suite, shell syntax, isolated removal of each new guarded invariant must fail |
| Honest verification and reliability limits | Record commands, results, spec coverage and expected/observed routing in REVIEW_EVIDENCE.md | All listed scenarios assessed; distinguish static interpretation from actual model execution |

## Execution order and risks

Default first reviews the approved SPEC and current consumers, then drafts the
shared input paragraph and critical checker assertions before rewriting the
role. This exposes producer/consumer mismatches early. Complete the coupled
contract before verifying and committing; intermediate edits are not handoffs.

Review evidence must cover all SPEC scenarios, including cases where evidence
is unavailable. Tests using copies must reside in a temporary directory outside
the repository, keep relative layout intact and be removed afterward. Do not
mutate active instructions merely to test rejection.

No TVM/VTA runtime behavior changes; runtime builds/tests provide no relevant
proof. No dependency installation, external execution, migration or operational
rollout is required. Existing roles and exact verdict names remain compatible.

Main risks are omitted substantive checks, ambiguity hidden by compression,
mapping requirements Root cannot supply, over-escalation, false Pass and overstated
Luna-low validation. Mitigate with explicit SPEC traceability, both directions
of routing scenarios and independent Implementation Review of the committed range.

## Verification and end state

Required commands from repository root:

```bash
bash -n .agents/custom/scripts/test-role-workflow
bash .agents/custom/scripts/test-role-workflow
git diff --check
```

Also run isolated negative checks on each newly added critical text invariant.
Record exact reproducible commands and observed exits in REVIEW_EVIDENCE.md.
The checker guards text contracts only. Manual scenarios assess rule meaning;
independent review challenges that assessment. Neither proves Luna-low runtime
reliability, and neither should be presented as such.

Task and checkpoint GREEN require the above checks, full SPEC coverage, complete
scenario record, scoped attributable edits, one verified task commit and clean
managed repositories. After checkpoint completion Root dispatches independent
Implementation Review and follows the existing automated fix/re-review loop.
Merge remains user-owned. No edits to approved INTENT/SPEC/PLAN/TASKS are needed.
