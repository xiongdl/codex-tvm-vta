# Plan: Workflow consistency validation

Initiative: `20261003-workflow-consistency-validation`.

## Approved baseline

User approved SPEC.md on 2026-10-03 (Asia/Shanghai).
Approved Specify commit map:

| Repository | OID |
| --- | --- |
| root | `ed4cc7ad785632cceb08732085ad3c3a1f08f1c6` |
| tvm | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| vta | `2708a80c19246ec99efe359125f02ae9b121e164` |

Independent Architecture Review returned Pass for this map.
Audit input is the root range `470b501dcc7e2b1a51baad5968f75e68efeb6848`
to `e1d9589cd4b5a9b3bac58d50c04823e640c98aac`.

## Execution and ownership

One fresh Default executes checkpoint C1 sequentially, writing only evidence
under this initiative directory. It runs maintained verification, records
results, and maps concrete policy/configuration/script statements to scenarios.
It does not perform formal Review or edit workflow files.

After C1 commits, Root dispatches a fresh Implementation Reviewer against the
complete original-base-to-current-tip root range, unchanged child OIDs, approved
Specify/Plan maps, and C1 evidence. The reviewer performs independent semantic
review and returns all blocking findings. Documentation added during the audit
must not obscure the original workflow changes under review.

Root presents each actionable problem with location, evidence, impact, smallest
solution, affected paths, and verification to the user. No fix agent is
dispatched until the user explicitly approves that repair. If concrete repairs
require changing the approved design/plan, Root revises candidate artifacts,
obtains independent review, and returns to the applicable approval gates.

Approved repairs use scoped tasks/checkpoints, focused verification, attributable
commits, and independent re-review. This plan deliberately authorizes no
workflow repair before findings and user decisions exist.

## Ordered tasks

1. C1/T1: run existing relevant verification and commit VERIFICATION.md.
2. C1/T2: trace contracts and scenarios and commit CONTRACT-MATRIX.md.
3. Independent Implementation Review, then user decisions on concrete findings.
4. Plan explicitly approved repairs when needed; verify and independently review.

No parallel execution: every delegated agent returns before the next starts.

## Verification strategy

Reuse the SPEC commands and project environment. Inspect the full regression
suite before running it; temporary fixture Git operations are isolated. Record
exit status, concise output, input OIDs, and limitations. Shell parsing and text
assertions are structural evidence; agent runtime behavior requires separate
evidence. Check all 13 changed files, their references, and relevant consumers.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Text tests pass despite contradictory policy | Explicit scenario matrix and independent semantic review |
| Unintended workflow change during diagnosis | C1 writes only reports; user must approve each repair |
| Tests generate unrelated repository state | Inspect first; isolate fixtures; report uncertainty without hiding files |
| Configuration semantics cannot be exercised | Parse locally and use primary sources if necessary; record unverified runtime limits |
| Existing baseline lacks tests for new rules | Report exact coverage gap; add tests only after user approval |

## Completion

Report tested evidence, approved fixes, reviewed commit map, and residual risks.
User owns optional manual merge; do not push or merge.
