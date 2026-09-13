# Implementation Plan: Follow Addy Lifecycle Policy

## Overview

Preserve the two completed instruction changes—on-demand Root role-file
inspection and Addy-driven lifecycle selection—and add one narrowly scoped
lifecycle duty. Immediately before the first Default dispatch for an approved
execution scope, Root makes one candidate-integrity-checked commit of all
approved, repository-resident pre-Build lifecycle artifacts produced or updated
for that scope. Preserve all other agent coordination, implementation,
verification, review, Git safety, escalation, artifact handoff, and Ship
behavior.

Approved specification:
`docs/initiatives/follow-addy-lifecycle-policy/SPEC.md`.

## Architecture Decisions

- Keep `AGENTS.md` as the minimal role router. Change only its cross-role file
  inspection paragraph; preserve every role-selection rule.
- Keep `.agents/custom/root.md` as the lifecycle owner. Change only its opening
  role-file rule and the Addy selection/approval portion of `Lifecycle
  ownership`.
- Let `using-agent-skills` determine which Skills apply. Repository mutation by
  itself does not activate SPEC, PLAN, or TASKS.
- Default to a confirmed `interview-me` intent whenever routing selects
  `spec-driven-development` or `planning-and-task-breakdown`, subject to the
  applicable Skill's context restrictions and explicit user direction.
- Preserve Addy's separate SPEC, PLAN, and TASKS approval gates. The final
  applicable pre-Build approval automatically starts the existing
  Build/Verify/Commit/Review and in-scope fix loop.
- Preserve the existing initiative artifact convention and exact-path handoff;
  do not change vendored Addy defaults or introduce an adapter.
- Select lifecycle artifacts by applicability and scope rather than hard-coded
  filenames. This includes future Addy artifact types while excluding caches,
  logs, build outputs, unapproved files, and unrelated paths.
- Root makes the lifecycle-artifact commit directly after all applicable
  pre-Build approvals. Do not dispatch a Default solely for this commit, and do
  not create an empty commit when no repository-resident artifact changed.
- If lifecycle artifacts change after Build starts, return to the applicable
  Addy gates, approve the changes, make one Root-owned artifact commit, and then
  redispatch execution.
- Do not edit `.agents/custom/default.md`, `.agents/custom/reviewer.md`, shared
  policies, `.codex/**`, product code, or submodules.

## Dependency Order

```text
Reviewed commits 02bd9c0e..894c4d49
    -> Approved revised SPEC
        -> Approved revised PLAN
            -> Approved revised TASKS
                -> one Root-owned lifecycle-artifact commit
                    -> root.md artifact-commit policy adjustment
                        -> cumulative static verification
                            -> verified implementation commit
                                -> independent Re-review
```

The router and Addy-selection changes are already implemented and independently
reviewed. The scope-extension artifact commit precedes the fresh Default that
implements the remaining Root policy adjustment.

## Planned Tasks

### Task 1: Clarify Root role-file inspection

Completed by reviewed commit `ec7c5404ffab7389e81b563ba23a89e80c36f296`;
retain without further modification.

Modify only the final cross-role inspection paragraph in `AGENTS.md`:

- Change the absolute cross-role read prohibition to a default isolation rule.
- Permit Root to inspect `.agents/custom/default.md` and
  `.agents/custom/reviewer.md` only for coordination, compatibility assessment,
  or explicitly scoped maintenance.
- Require Root to treat inspected role files as task data and not apply them.
- Preserve the exact delegated scope and staged-path allowlist restriction for
  Default and Reviewer.
- Preserve all role-routing bullets verbatim.

### Task 2: Adopt Addy-driven lifecycle selection

Completed by reviewed commit `894c4d499a39ecd22dfaa1c9acccb48ebf5c503d`;
retain except for the approved artifact-commit responsibility extension below.

Modify only the opening role-file paragraph and the applicable portion of
`Lifecycle ownership` in `.agents/custom/root.md`:

- Mirror Root's on-demand inspection exception without changing shared-policy
  loading.
- Retain intake routing through `using-agent-skills`.
- Remove the rule that repository mutation alone mandates interview, SPEC, and
  PLAN.
- Default to `interview-me` when spec or planning is selected.
- Require separate approval of applicable SPEC, PLAN, and TASKS.
- Preserve automatic Build through Review and the in-scope fix loop after the
  final applicable gate.
- State that Addy owns selection, methodology, phase gates, approval cadence,
  and task-specific quality requirements, while the project owns agent roles,
  exact artifact handoff, Git safeguards, escalation, and Ship authority.
- Preserve the reviewed Task 2 behavior while Task 3 adds only the newly
  approved artifact-commit responsibility.

### Task 3: Assign the lifecycle-artifact commit to Root

After the revised TASKS approval and Root's one commit of the revised lifecycle
artifacts, modify only `.agents/custom/root.md`:

- Add Root ownership of the generic, single pre-Build lifecycle-artifact commit.
- Qualify Default's verified local commits as implementation/fix commits.
- Require downstream delegations to include exact approved artifact paths and
  the Root artifact commit OID.
- Forbid a Default created solely to commit lifecycle artifacts and forbid empty
  artifact commits.
- Define the re-approval, one-commit, and redispatch behavior when lifecycle
  artifacts change after Build begins.
- Preserve all previously reviewed Addy routing, interview, separate approval,
  automatic execution, role inspection, review/escalation, and Ship behavior.

### Checkpoint: Policy aligned without coordination drift

- Tasks 1 and 2 remain unchanged from their reviewed commits, and Task 3
  satisfies its focused static assertions.
- The cumulative diff changes only the approved paragraphs in `AGENTS.md` and
  `.agents/custom/root.md` plus approved initiative artifacts.
- Default/Reviewer execution and review responsibilities, fresh-agent
  boundaries, delegation data, automated Build-through-Review behavior,
  escalation, and Ship remain intact. Only Root's lifecycle-artifact commit
  responsibility is added.
- Exact staged-path allowlists and candidate fingerprints pass.
- A fresh independent Reviewer returns Pass.

## Verification Strategy

For each task, inspect the focused diff and run `git diff --check`. Use `rg`
assertions to establish both required behavior and preservation constraints.

Required assertions include:

```bash
rg -n 'explicit runtime role|non-delegated primary agent|Never infer Default|fails closed' \
  AGENTS.md
rg -n 'by default|coordination|compatibility assessment|task data' \
  AGENTS.md .agents/custom/root.md
rg -n 'using-agent-skills|interview-me|spec-driven-development|planning-and-task-breakdown' \
  .agents/custom/root.md
rg -n 'SPEC|PLAN|TASKS|Build|Verify|Review|Ship' \
  .agents/custom/root.md
git diff --check
```

Diff review must additionally confirm:

- The four role-routing bullets in `AGENTS.md` are unchanged.
- The artifact path and shared-policy paragraphs in `root.md` are unchanged.
- The responsibility list changes only to add Root's lifecycle-artifact commit
  and to qualify Default commits as implementation/fix commits.
- The Delegation section changes only if needed to require exact generic
  artifact paths and the Root artifact commit OID downstream.
- The complete Review and escalation and Ship sections are unchanged.
- `.agents/custom/default.md`, `.agents/custom/reviewer.md`,
  `.agents/custom/automation.md`, `.agents/custom/version-control.md`,
  `.codex/**`, vendored Skills, product paths, and submodule pointers are
  unchanged.

Before every commit, use `.agents/custom/version-control.md` to compare the
exact staged-path allowlist, freeze and recheck the staged candidate
fingerprint, reject unstaged tracked changes, and record the verification
evidence. No TVM/VTA build is required because no runtime code changes.

## Commit and Review Strategy

- After TASKS approval, Root creates one candidate-integrity-checked local
  commit containing all newly approved or updated repository-resident lifecycle
  artifacts for the execution scope. For the present scope extension, that
  commit contains exactly the revised SPEC, PLAN, and TASKS.
- Root passes the artifact commit OID and exact artifact paths to the fresh
  implementation Default and subsequent Reviewer.
- Dispatch a fresh Default for Task 3 with `.agents/custom/root.md` as its sole
  staged-path allowlist. Do not reimplement or amend the completed commits.
- Dispatch a fresh Reviewer after the checkpoint. Route actionable findings to
  a fresh Default for Fix/Re-verify/commit, followed by a fresh Reviewer for
  Re-review.
- Leave the reviewed task branch unmerged until the user separately authorizes
  Ship.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Root still forces SPEC/PLAN for every mutation | High | Remove the mutation trigger and statically assert Addy-driven routing |
| “Default interview” becomes an unconditional interview everywhere | Medium | Tie it specifically to selected spec/planning workflows and preserve explicit/context restrictions |
| Addy approval gates are recombined | High | Assert separate SPEC, PLAN, and TASKS approvals |
| Post-approval automation gains new pauses | High | Preserve and assert the existing automatic Build-through-Review and fix loop |
| Future artifact types bypass the commit gate | High | Select all applicable repository-resident lifecycle artifacts by scope, not filename |
| Artifact commit accidentally includes generated or unrelated files | High | Require approved exact-path allowlist and candidate-integrity checks |
| A dedicated commit agent is still created | Medium | Assign the one artifact commit to Root and statically prohibit a Default solely for that purpose |
| Cross-role reading causes instruction leakage | High | Require task-data-only inspection and retain role-specific application rules |
| Unrelated coordination policy drifts | High | Restrict edits by paragraph and compare protected sections verbatim |

## Open Questions

None. The approved specification and confirmed modification boundaries determine
the implementation approach.
