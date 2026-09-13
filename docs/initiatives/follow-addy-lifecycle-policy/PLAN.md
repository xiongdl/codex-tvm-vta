# Implementation Plan: Follow Addy Lifecycle Policy

## Overview

Make two surgical instruction changes: permit Root to inspect Default/Reviewer
role files on demand without applying them, and replace the project's
repository-mutation-based SPEC/PLAN mandate with Addy-driven skill selection.
Preserve all existing agent coordination, implementation, verification, review,
Git safety, escalation, artifact handoff, and Ship behavior.

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
- Do not edit `.agents/custom/default.md`, `.agents/custom/reviewer.md`, shared
  policies, `.codex/**`, product code, or submodules.

## Dependency Order

```text
Approved SPEC
    -> Approved PLAN
        -> Approved TASKS
            -> AGENTS.md inspection boundary
                -> root.md Addy lifecycle policy
                    -> cumulative static verification
                        -> verified commits
                            -> independent Review
```

The router boundary is updated first so the resulting Root policy can describe
on-demand inspection without contradicting the always-loaded `AGENTS.md`.

## Planned Tasks

### Task 1: Clarify Root role-file inspection

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
- Preserve the role responsibility list and the complete Delegation, Review and
  escalation, and Ship sections verbatim.

### Checkpoint: Policy aligned without coordination drift

- Both tasks satisfy their focused static assertions.
- The cumulative diff changes only the approved paragraphs in `AGENTS.md` and
  `.agents/custom/root.md` plus approved initiative artifacts.
- Default/Reviewer responsibilities, fresh-agent boundaries, delegation data,
  automated Build-through-Review behavior, escalation, and Ship remain intact.
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
- The Root/Default/Reviewer responsibility list is unchanged.
- The complete Delegation, Review and escalation, and Ship sections are
  unchanged.
- `.agents/custom/default.md`, `.agents/custom/reviewer.md`,
  `.agents/custom/automation.md`, `.agents/custom/version-control.md`,
  `.codex/**`, vendored Skills, product paths, and submodule pointers are
  unchanged.

Before every commit, use `.agents/custom/version-control.md` to compare the
exact staged-path allowlist, freeze and recheck the staged candidate
fingerprint, reject unstaged tracked changes, and record the verification
evidence. No TVM/VTA build is required because no runtime code changes.

## Commit and Review Strategy

- Commit the approved planning artifacts before Build so the implementation
  agent starts from a clean recorded base.
- Implement Task 1 and Task 2 as separate focused verified commits if the
  candidate-integrity procedure can keep each state internally consistent;
  otherwise use one atomic implementation commit covering both mutually
  dependent instruction updates.
- Dispatch Build/Verify to a fresh Default with exact file and staged-path
  allowlists.
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
| Cross-role reading causes instruction leakage | High | Require task-data-only inspection and retain role-specific application rules |
| Unrelated coordination policy drifts | High | Restrict edits by paragraph and compare protected sections verbatim |

## Open Questions

None. The approved specification and confirmed modification boundaries determine
the implementation approach.
