# Implementation Plan: Unify Lifecycle Approval Flow

## Overview

Replace Root's sequential SPEC/PLAN/TASKS approval cadence with two distinct
gates: initial authorization of the stated execution process before repository
mutation, and one approval of the complete committed lifecycle-artifact batch
before Build. Keep role ownership narrow: Root creates the task branch and may
write only Define/Plan lifecycle artifacts; Default owns implementation and
verification files; Reviewer owns read-only review.

## Approved Source

This plan implements
`docs/initiatives/unify-lifecycle-approval-flow/SPEC.md` as part of the same
batch presented for one approval.

## Architecture Decisions

- Change `.agents/custom/root.md` only. The behavior belongs to Root lifecycle
  policy, while `AGENTS.md` already routes the primary conversation owner to
  Root and `.codex` already permits normal task-level branch and commit work.
- Keep initial execution authorization, lifecycle-artifact batch approval, and
  Ship authorization as three separate authorities; none implies another.
- Put `interview-me` confirmation before repository mutation whenever that
  skill applies. Read-only discovery and clarification may occur before initial
  authorization.
- Require Root to create or safely reuse the task branch before writing any
  lifecycle artifact.
- Replace per-artifact approval with one committed-batch gate. Root writes all
  applicable artifacts, commits the candidate-checked batch, displays it, and
  obtains one explicit approval before Build dispatch.
- Preserve the post-approval Build/Fix/Verify/Review automation and the existing
  separate Ship gate.

## Dependency Flow

```text
using-agent-skills + stated execution process
    -> confirmed interview-me intent when applicable
        -> explicit initial execution authorization
            -> Root task-branch creation/reuse
                -> Root generates/revises all applicable lifecycle artifacts
                    -> Root candidate-checks and commits the complete batch
                        -> one explicit batch approval
                            -> Build Default
                                -> Verify + implementation commit
                                    -> Reviewer
                                        -> Fix/Re-review loop when needed
                                            -> separate Ship authorization
```

## Task List

### Phase 1: Root lifecycle policy

- [ ] Task 1: Implement the intake, branch, ownership, and batch-approval rules
  in `.agents/custom/root.md`.

### Checkpoint: Policy verification

- [ ] Required lifecycle and ownership language is present.
- [ ] Sequential per-artifact approval language is absent.
- [ ] Post-approval Build-through-Review and separate Ship behavior is intact.
- [ ] Focused diff contains no unrelated role or runtime configuration changes.
- [ ] Candidate-integrity verification passes and Default creates a verified
  local implementation commit.

### Phase 2: Independent review

- [ ] A fresh Reviewer reviews the approved artifact batch, base HEAD, exact
  changed paths, verification evidence, and implementation commit.
- [ ] Any implementation findings are fixed by a fresh Default, re-verified,
  committed, and sent to a fresh Reviewer.
- [ ] A Pass leaves the reviewed task branch unmerged pending separate Ship
  authorization.

## Verification Commands

```bash
git status --short --branch --untracked-files=all
git diff --check
rg -n 'using-agent-skills|execution process|explicit user authorization|task branch|lifecycle artifact|single.*approval|Build|Ship' \
  .agents/custom/root.md
git diff -- AGENTS.md .codex .agents/custom
```

Before committing, Default must additionally apply the staged-path allowlist,
candidate fingerprint, frozen verification, and unstaged-tracked checks from
`.agents/custom/version-control.md`.

## Delegation Contract

After this artifact batch is explicitly approved, Root dispatches one fresh
Default with:

- Approved artifacts: this SPEC, PLAN, and TASKS.
- Artifact commit OID and exact artifact-path allowlist.
- Repository: `/Users/xdl/Projects/codex-tvm-vta` only; submodules are out of
  scope.
- Original branch: `new`.
- Base HEAD: `4ef6fc596f2894c25e830e78bd5d313f0af7b50f`.
- Task branch: `codex/unify-lifecycle-approval-flow`.
- Exact implementation staged-path allowlist:
  `.agents/custom/root.md`.
- Required verification: the commands above plus a focused comparison against
  the approved success criteria and protected behavior.
- Required result: verified local implementation commit and the complete
  checkpoint evidence required by `.agents/custom/default.md`.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Initial authorization is confused with batch approval | High | Name both gates and state that neither implies the other |
| Root modifies implementation files | High | Limit Root mutation to repository-resident Define/Plan lifecycle artifacts |
| Per-artifact approvals survive in another clause | High | Search for all approval-cadence language and review the complete Root policy |
| Unapproved artifact drafts reach Build | High | Require approval of the exact committed batch OID before Default dispatch |
| User revisions invalidate the artifact commit | Medium | Commit the complete revised batch and repeat its single approval gate |
| Unnecessary router or `.codex` edits broaden scope | Medium | Keep them unchanged unless a concrete compatibility conflict is demonstrated |
| New gates accidentally add pauses after Build starts | Medium | Preserve the automatic Build/Fix/Verify/Review loop verbatim in substance |

## Open Questions

None.
