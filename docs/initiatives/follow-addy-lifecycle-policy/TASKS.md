# Tasks: Follow Addy Lifecycle Policy

## Recorded Repository State

- Repository: `/Users/xdl/Projects/codex-tvm-vta`
- Current branch: `skill_dev`
- Recorded base HEAD: `d32ebdb05be5696b71c5cb95d361a8075b679a80`
- Planned task branch: `codex/follow-addy-lifecycle-policy`
- Submodules: inspection only; no submodule content or pointer changes allowed
- Current non-clean paths: only the Root-created planning artifacts for this
  initiative

After TASKS approval, Root must preserve the approved artifacts, obtain a clean
preflight of the recorded `skill_dev` base, create the planned task branch from
the exact recorded base, restore the artifacts on that branch, and recheck the
repository state before staging. Stop on any unexpected branch, HEAD, tracked
change, untracked path, or submodule condition.

## Planning-Artifact Checkpoint

Commit the three separately approved lifecycle artifacts before Build:

- `docs/initiatives/follow-addy-lifecycle-policy/SPEC.md`
- `docs/initiatives/follow-addy-lifecycle-policy/PLAN.md`
- `docs/initiatives/follow-addy-lifecycle-policy/TASKS.md`

**Acceptance criteria:**

- [ ] The task branch starts at the exact recorded base HEAD.
- [ ] The staged paths equal only the three paths above.
- [ ] `git diff --cached --check` succeeds.
- [ ] The staged candidate fingerprint is unchanged across verification.
- [ ] No unstaged tracked changes or unrelated untracked paths exist.
- [ ] The verified planning-artifact commit leaves a clean task branch.

**Exact staged-path allowlist:** the three lifecycle artifact paths listed
above.

## Task 1: Clarify Root Role-File Inspection

**Description:** Modify only the final cross-role inspection paragraph in
`AGENTS.md`. Make cross-role isolation the default while allowing Root to
inspect Default/Reviewer role files on demand for coordination, compatibility
assessment, or explicitly scoped maintenance. Inspection is task-data-only and
does not apply another role's instructions.

**Acceptance criteria:**

- [ ] The four existing role-routing bullets are byte-for-byte unchanged.
- [ ] Roles still load and apply only their matching role file by default.
- [ ] Root may inspect only `.agents/custom/default.md` and
      `.agents/custom/reviewer.md` for the approved on-demand purposes.
- [ ] Root must treat inspected files as task data and not apply their
      instructions.
- [ ] Default/Reviewer may inspect another role file only when Root names the
      exact file in delegated scope and the staged-path allowlist.
- [ ] Default/Reviewer must continue to treat inspected role files solely as
      task data.
- [ ] No other `AGENTS.md` text changes.

**Verification:**

- [ ] `rg` finds the default isolation rule, the Root-only on-demand exception,
      its three approved purposes, and the task-data-only restriction.
- [ ] `rg` finds explicit runtime-role precedence, the primary-agent Root
      fallback, the prohibition on model-name inference, and fail-closed
      handling.
- [ ] Diff review confirms only the final paragraph changed.
- [ ] `git diff --cached --check -- AGENTS.md` succeeds.
- [ ] The staged allowlist and frozen candidate fingerprint pass with no
      unstaged tracked changes.

**Dependencies:** Planning-artifact checkpoint.

**Exact staged-path allowlist:**

- `AGENTS.md`

**Estimated scope:** XS, one paragraph in one file.

## Task 2: Follow Addy Skill Selection and Gates

**Description:** Modify only the opening role-file paragraph and the Addy
selection/approval portion of `Lifecycle ownership` in
`.agents/custom/root.md`. Make Addy Skills authoritative for applicable Skill
selection and gates while preserving all project-owned coordination and
post-approval automation.

**Acceptance criteria:**

- [ ] The opening paragraph defaults to role-file isolation and gives Root the
      same on-demand, task-data-only inspection exception as `AGENTS.md`.
- [ ] Shared policy loading and the initiative artifact path are byte-for-byte
      unchanged.
- [ ] Root still invokes `using-agent-skills` at task intake.
- [ ] Addy Skills, rather than repository mutation, determine which Skills and
      phases apply.
- [ ] Repository mutation alone no longer mandates interview, SPEC, PLAN, or
      TASKS.
- [ ] Selection of `spec-driven-development` or
      `planning-and-task-breakdown` defaults to `interview-me` and an explicitly
      confirmed intent first.
- [ ] Explicit user direction and non-interactive restrictions remain governed
      by the applicable Addy Skills.
- [ ] Applicable SPEC, PLAN, and TASKS are displayed and explicitly approved
      separately in that order.
- [ ] The final applicable pre-Build approval automatically starts
      `Build -> Verify -> verified commit -> Review` and the existing in-scope
      `Fix -> Re-verify -> verified commit -> Re-review` loop.
- [ ] No new routine user pause is introduced within the automatic execution
      loop.
- [ ] Addy owns Skill selection, lifecycle methodology, phase gates, approval
      cadence, and task-specific quality requirements.
- [ ] The project retains role ownership, exact artifact handoff, repository
      safeguards, escalation, delegation authority, and Ship authorization.
- [ ] The Root/Default/Reviewer responsibility list is byte-for-byte unchanged.
- [ ] The complete Delegation, Review and escalation, and Ship sections are
      byte-for-byte unchanged.

**Verification:**

- [ ] `rg` finds the required Addy routing, interview trigger, separate approval
      gates, automatic post-gate sequence, and policy boundary language.
- [ ] `rg` no longer finds a rule making repository mutation alone sufficient
      to activate Define/SPEC/PLAN.
- [ ] Focused diff review confirms changes are limited to the approved opening
      paragraph and lifecycle selection/approval text.
- [ ] Protected-section comparison confirms the artifact/shared-policy text,
      responsibility list, Delegation, Review and escalation, and Ship text are
      unchanged.
- [ ] `git diff --cached --check -- .agents/custom/root.md` succeeds.
- [ ] The staged allowlist and frozen candidate fingerprint pass with no
      unstaged tracked changes.

**Dependencies:** Task 1.

**Exact staged-path allowlist:**

- `.agents/custom/root.md`

**Estimated scope:** S, two localized sections in one file.

## Checkpoint: Addy Policy Alignment

**Cumulative acceptance criteria:**

- [ ] Tasks 1 and 2 are GREEN and locally committed.
- [ ] The cumulative implementation diff changes only `AGENTS.md` and
      `.agents/custom/root.md`.
- [ ] The cumulative branch diff additionally contains only the three approved
      initiative artifacts.
- [ ] `.agents/custom/default.md`, `.agents/custom/reviewer.md`, shared policy
      files, `.codex/**`, vendored Addy Skills, product files, and all submodule
      pointers are unchanged.
- [ ] Existing fresh-agent boundaries, self-contained delegation requirements,
      Build/Verify/Commit/Review automation, escalation criteria, and Ship
      authorization are preserved.
- [ ] Cumulative `git diff --check` and static assertions succeed.
- [ ] A fresh independent Reviewer checks the approved SPEC, PLAN, TASKS, base
      HEAD, commits, exact changed paths, and protected-section evidence and
      returns Pass.
- [ ] Any actionable finding is routed to a fresh Default for
      Fix/Re-verify/commit and then a fresh Reviewer for Re-review.
- [ ] The reviewed task branch remains unmerged pending explicit user Ship
      authorization.

## Agent Delegation Requirements

Root dispatches one fresh Default for the approved checkpoint. The delegation
must include:

- Approved SPEC, PLAN, and TASKS paths.
- Recorded original branch, base HEAD, planned task branch, and parent repository
  scope.
- Tasks 1 and 2 in dependency order.
- Exact per-task staged-path allowlists.
- Protected sections and paths that must remain unchanged.
- Focused and cumulative verification commands.
- Candidate-integrity procedure and required final-report evidence.
- A prohibition on subagents, scope expansion, unrelated edits, submodule
  changes, and Ship actions.

After the Default returns verified commits, Root dispatches a fresh Reviewer
with the same approved artifacts, recorded base, commit range, exact changed
paths, preservation requirements, and review evidence expectations.
