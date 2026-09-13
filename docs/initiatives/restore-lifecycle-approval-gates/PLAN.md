# Implementation Plan: Restore Lifecycle Approval Gates

## Overview

Restore deterministic Root selection in the role router, then restore the
mandatory Define and Plan approval gates in the Root instructions. Keep the
implementation narrowly scoped to the two owning instruction files and verify
the resulting policy with static assertions and independent Review.

Approved specification:
`docs/initiatives/restore-lifecycle-approval-gates/SPEC.md`.

## Architecture Decisions

- Keep `AGENTS.md` as the sole role router. It identifies Root from explicit
  runtime context or from the non-delegated primary user-facing agent fallback;
  Default and Reviewer still require explicit delegated roles.
- Keep lifecycle gates only in `.agents/custom/root.md`. Default and Reviewer
  must not decide whether Define or Plan can be skipped.
- Use mandatory language and enumerate the only bypass: an explicit user
  instruction to skip Define/Plan or execute directly.
- Preserve the existing automatic Build-through-Review loop after both artifact
  approvals and the separate user authorization for Ship.
- Use focused inline static assertions rather than adding a repository script
  for this two-file instruction change.
- Commit the approved SPEC/PLAN/TASKS as a Root-owned planning artifact before
  Build so the fresh Default begins from the clean preflight required by
  `.agents/custom/version-control.md`.

## Dependency Order

```text
Approved SPEC
    -> Approved PLAN/TASKS
        -> Root role selection
            -> Root lifecycle gates
                -> Cumulative static verification
                    -> Independent Review
```

The tasks are sequential because the lifecycle assertions depend on the router
selecting Root reliably.

## Task List

### Phase 1: Role routing

- [ ] Task 1: Make Root selection deterministic in `AGENTS.md`.

### Phase 2: Lifecycle gates

- [ ] Task 2: Restore mandatory Define/Plan approvals in
      `.agents/custom/root.md`.

### Checkpoint: Lifecycle gates restored

- [ ] Router and Root lifecycle static assertions pass.
- [ ] Default, Reviewer, shared policy, custom-agent configuration, product
      code, and submodule pointers are unchanged.
- [ ] Exact staged-path allowlists and candidate fingerprints are verified for
      each implementation commit.
- [ ] Independent Reviewer returns Pass.
- [ ] The reviewed task branch awaits explicit user Ship authorization.

## Verification Strategy

- Use `rg` assertions for required and forbidden routing/lifecycle clauses.
- Use `git diff --check` for each staged candidate and the cumulative diff.
- Compare staged-path allowlists exactly before each commit.
- Freeze and compare the staged candidate fingerprint around verification.
- Compare the cumulative diff against the approved base to confirm only the
  planning artifacts, `AGENTS.md`, and `.agents/custom/root.md` changed.
- Do not run TVM/VTA builds or tests; no product or submodule behavior changes.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Root is misclassified as Default when no literal `/root` is exposed | High | Define the non-delegated primary user-facing agent fallback and forbid inference from the word `default` |
| Root still invents a low-risk bypass | High | Enumerate prohibited implicit exceptions and make explicit user direction the only bypass |
| Generic continuation is mistaken for artifact approval | High | State that each displayed SPEC and PLAN/TASKS needs explicit approval |
| Restored gates accidentally stop post-approval automation | Medium | Assert the automatic Build/Fix/Verify/Review loop remains explicit |
| Role split regresses while lifecycle text changes | Medium | Keep Default/Reviewer files out of the allowlist and review the cumulative diff |

## Open Questions

None. The user approved the specification and rejected all implicit low-risk
exceptions.
