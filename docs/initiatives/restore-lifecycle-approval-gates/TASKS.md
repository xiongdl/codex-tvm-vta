# Tasks: Restore Lifecycle Approval Gates

## Planning Artifact Checkpoint

After the user approves this PLAN and TASKS file, Root commits these exact
approved planning artifacts before dispatching Build:

- `docs/initiatives/restore-lifecycle-approval-gates/SPEC.md`
- `docs/initiatives/restore-lifecycle-approval-gates/PLAN.md`
- `docs/initiatives/restore-lifecycle-approval-gates/TASKS.md`

The planning-artifact commit must use the candidate-integrity procedure in
`.agents/custom/version-control.md` and leave a clean task branch.

## Task 1: Make Root Selection Deterministic

**Description:** Update the minimal role router so explicit runtime roles win,
the non-delegated primary user-facing agent reliably selects Root when no
literal `/root` label is available, and Default/Reviewer remain explicit
delegated roles.

**Acceptance criteria:**

- [ ] Explicit Root, Default, and Reviewer task context selects the matching
      role file.
- [ ] A non-delegated primary agent that owns the user conversation, lifecycle
      transitions, and Default/Reviewer dispatch selects Root.
- [ ] Default is not inferred from model or configuration text containing
      `default`.
- [ ] Contradictory or unknown role context fails closed to Root escalation.
- [ ] Reviewer retains the narrow inspection-only exception for role files
      explicitly delegated as review artifacts.
- [ ] Default may inspect a different role file only when Root explicitly lists
      that exact file in its implementation scope and staged-path allowlist;
      Default treats it only as task data and does not apply its instructions.

**Verification:**

- [ ] `rg` finds explicit runtime-context precedence, the primary-agent Root
      fallback, and explicit delegated Default/Reviewer selection.
- [ ] `rg` finds the prohibition on inferring Default from model/configuration.
- [ ] `rg` finds fail-closed handling and the inspection-only Reviewer clause.
- [ ] `rg` finds the exact-scope, exact-allowlist, task-data-only exception for
      Default and Reviewer.
- [ ] `git diff --cached --check -- AGENTS.md` succeeds.
- [ ] Staged paths equal only `AGENTS.md`; the frozen fingerprint is unchanged
      across verification; no unstaged tracked changes exist.

**Dependencies:** Approved planning-artifact checkpoint.

**Exact staged-path allowlist:**

- `AGENTS.md`

**Repositories:** Parent repository only; no submodules.

**Estimated scope:** XS (one file).

## Task 2: Restore Mandatory Define and Plan Gates

**Description:** Update Root instructions so every repository-mutating task
enters Define, confirms intent with `interview-me`, obtains explicit approval of
the displayed SPEC and PLAN/TASKS, and only then starts autonomous execution.

**Acceptance criteria:**

- [ ] Every repository-mutating task must enter Define and start with
      `interview-me` unless the user explicitly orders a bypass.
- [ ] Root must show and obtain explicit approval for the SPEC before writing
      PLAN/TASKS.
- [ ] Root must show and obtain explicit approval for PLAN/TASKS before
      dispatching Build.
- [ ] No implicit mechanical, documentation-only, local, small, or low-risk
      exception remains.
- [ ] `continue` or equivalent generic continuation does not approve an artifact
      that has not been shown.
- [ ] After both approvals, Root automatically coordinates
      Build -> Verify -> verified commit -> Review and any in-scope fix loop.
- [ ] Ship remains separately user-authorized and Root-executed.

**Verification:**

- [ ] `rg` finds `using-agent-skills`, `interview-me`, SPEC approval,
      PLAN/TASKS approval, and the post-approval automatic sequence.
- [ ] `rg` finds the explicit-user-only bypass and generic-continuation rule.
- [ ] `rg` confirms the listed implicit exception terms occur only in a
      prohibition, not as permission.
- [ ] `git diff --cached --check -- .agents/custom/root.md` succeeds.
- [ ] Staged paths equal only `.agents/custom/root.md`; the frozen fingerprint
      is unchanged across verification; no unstaged tracked changes exist.

**Dependencies:** Task 1.

**Exact staged-path allowlist:**

- `.agents/custom/root.md`

**Repositories:** Parent repository only; no submodules.

**Estimated scope:** XS (one file).

## Checkpoint: Lifecycle Gates Restored

- [ ] Tasks 1 and 2 are GREEN with separate verified atomic commits.
- [ ] Cumulative changed paths from the recorded base are exactly the three
      planning artifacts, `AGENTS.md`, and `.agents/custom/root.md`.
- [ ] `.agents/custom/default.md`, `.agents/custom/reviewer.md`, shared policy
      files, `.codex/**`, product code, and all submodule pointers are unchanged.
- [ ] Cumulative `git diff --check` succeeds.
- [ ] A fresh independent Reviewer checks the approved SPEC/PLAN/TASKS and task
      commits and returns Pass.
- [ ] The reviewed task branch remains unmerged pending explicit Ship
      authorization.
