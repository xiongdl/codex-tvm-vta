# Tasks: Follow Addy Lifecycle Policy

## Recorded Repository State

- Repository: `/Users/xdl/Projects/codex-tvm-vta`
- Current branch: `skill_dev`
- Recorded base HEAD: `d32ebdb05be5696b71c5cb95d361a8075b679a80`
- Planned task branch: `codex/follow-addy-lifecycle-policy`
- Current reviewed HEAD before the scope extension:
  `894c4d499a39ecd22dfaa1c9acccb48ebf5c503d`
- Submodules: inspection only; no submodule content or pointer changes allowed
- Current non-clean paths: only the Root-created planning artifacts for this
  initiative

For the initial approved scope, Root preserved the approved artifacts, obtained
a clean preflight of the recorded `skill_dev` base, created the planned task
branch from that exact base, restored the artifacts, and rechecked repository
state before staging. Those completed branch-setup steps must not be repeated
for this scope extension.

## Initial Planning-Artifact Checkpoint — Complete

Completed by commit `02bd9c0ead9366d40d5b2dd3f1812122bfc46a22`.

Commit the three separately approved lifecycle artifacts before Build:

- `docs/initiatives/follow-addy-lifecycle-policy/SPEC.md`
- `docs/initiatives/follow-addy-lifecycle-policy/PLAN.md`
- `docs/initiatives/follow-addy-lifecycle-policy/TASKS.md`

**Historical acceptance criteria, satisfied by the recorded commit:**

- [ ] The task branch starts at the exact recorded base HEAD.
- [ ] The staged paths equal only the three paths above.
- [ ] `git diff --cached --check` succeeds.
- [ ] The staged candidate fingerprint is unchanged across verification.
- [ ] No unstaged tracked changes or unrelated untracked paths exist.
- [ ] The verified planning-artifact commit leaves a clean task branch.

**Exact staged-path allowlist:** the three lifecycle artifact paths listed
above.

## Task 1: Clarify Root Role-File Inspection

**Status:** Complete and independently reviewed at
`ec7c5404ffab7389e81b563ba23a89e80c36f296`. Retain without modification.

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

**Status:** Complete and independently reviewed at
`894c4d499a39ecd22dfaa1c9acccb48ebf5c503d`. Retain the reviewed behavior while
Task 3 adds only the approved artifact-commit responsibility.

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

## Scope-Extension Lifecycle-Artifact Commit Gate

After this revised TASKS file is explicitly approved, Root—not a Default—must
create one local commit containing exactly the newly approved or updated
repository-resident lifecycle artifacts for the current execution scope:

- `docs/initiatives/follow-addy-lifecycle-policy/SPEC.md`
- `docs/initiatives/follow-addy-lifecycle-policy/PLAN.md`
- `docs/initiatives/follow-addy-lifecycle-policy/TASKS.md`

**Acceptance criteria:**

- [ ] The task branch is attached at
      `894c4d499a39ecd22dfaa1c9acccb48ebf5c503d` before staging.
- [ ] Root confirms that the three files above are the only changed paths.
- [ ] Root stages exactly the three-path allowlist and reviews the staged diff.
- [ ] `git diff --cached --check` succeeds.
- [ ] No unstaged tracked changes or unrelated untracked paths exist.
- [ ] The staged candidate fingerprint is unchanged across static verification.
- [ ] Root commits once with subject
      `docs: expand lifecycle artifact commit policy`.
- [ ] Root records the artifact commit OID and exact paths for the downstream
      Default and Reviewer.
- [ ] The commit leaves a clean task branch and no Default was created solely
      for the artifact commit.

**Exact staged-path allowlist:** the three revised lifecycle artifact paths
listed above.

## Task 3: Assign Lifecycle-Artifact Commits to Root

**Description:** Modify only `.agents/custom/root.md` to assign Root the generic,
single pre-Build commit of all approved, repository-resident lifecycle artifacts
produced or updated for an execution scope. Preserve the already reviewed Addy
routing, approval, automatic execution, agent coordination, escalation, and Ship
behavior.

**Acceptance criteria:**

- [ ] Root owns one candidate-integrity-checked lifecycle-artifact commit before
      the first Default dispatch for an approved execution scope.
- [ ] Artifact selection is applicability- and scope-based, not limited to a
      hard-coded SPEC/PLAN/TASKS list.
- [ ] Only approved, repository-resident pre-Build lifecycle artifacts produced
      or updated for the scope may enter the exact artifact-path allowlist.
- [ ] Root records the artifact paths and commit OID in every downstream Default
      and Reviewer delegation.
- [ ] No Default may be created solely to commit lifecycle artifacts.
- [ ] No empty artifact commit is created when no repository-resident lifecycle
      artifact was produced or updated.
- [ ] If an approved lifecycle artifact changes after Build begins, Root returns
      to the applicable Addy gate, obtains approval, commits all newly approved
      artifact changes once, and only then redispatches execution.
- [ ] Default remains responsible for Build, Fix, Verify, Re-verify, and verified
      implementation/fix commits; `.agents/custom/default.md` remains unchanged.
- [ ] The previously reviewed role-file inspection, Addy skill selection,
      interview trigger, separate SPEC/PLAN/TASKS approvals, and automatic
      Build-through-Review loop remain unchanged.
- [ ] Shared policy loading, artifact storage convention, Review and escalation,
      and Ship remain unchanged.

**Verification:**

- [ ] `rg` finds Root artifact-commit ownership, applicability-based artifact
      selection, exact paths and commit OID handoff, no dedicated
      artifact-commit Default, no empty commit, and the post-Build artifact
      change loop.
- [ ] Focused diff review confirms only the minimum approved responsibility,
      lifecycle, and delegation clauses changed since `894c4d49`.
- [ ] Comparison against `894c4d49` confirms all protected previously reviewed
      behavior is unchanged.
- [ ] `git diff --cached --check -- .agents/custom/root.md` succeeds.
- [ ] The exact one-path staged allowlist, no-unstaged-change check, and frozen
      candidate fingerprint pass.

**Dependencies:** Scope-extension lifecycle-artifact commit gate.

**Exact staged-path allowlist:**

- `.agents/custom/root.md`

**Estimated scope:** S, localized policy additions in one file.

## Checkpoint: Addy Policy Alignment

**Cumulative acceptance criteria:**

- [ ] Tasks 1 and 2 remain at their reviewed commits; Task 3 is GREEN and
      locally committed.
- [ ] The cumulative implementation diff changes only `AGENTS.md` and
      `.agents/custom/root.md`.
- [ ] The cumulative branch diff additionally contains only the three approved
      initiative artifacts.
- [ ] `.agents/custom/default.md`, `.agents/custom/reviewer.md`, shared policy
      files, `.codex/**`, vendored Addy Skills, product files, and all submodule
      pointers are unchanged.
- [ ] Existing fresh-agent boundaries, self-contained delegation requirements,
      Build/Verify/implementation-commit/Review automation, escalation criteria,
      and Ship authorization are preserved; only Root's artifact-commit duty is
      added.
- [ ] Cumulative `git diff --check` and static assertions succeed.
- [ ] A fresh independent Reviewer checks the approved SPEC, PLAN, TASKS, base
      HEAD, commits, exact changed paths, and protected-section evidence and
      returns Pass.
- [ ] Any actionable finding is routed to a fresh Default for
      Fix/Re-verify/commit and then a fresh Reviewer for Re-review.
- [ ] The reviewed task branch remains unmerged pending explicit user Ship
      authorization.

## Agent Delegation Requirements

After Root completes the approved scope-extension lifecycle-artifact commit,
Root dispatches one fresh Default for Task 3. The delegation
must include:

- Approved SPEC, PLAN, and TASKS paths.
- Recorded original branch, base HEAD, task branch, reviewed pre-extension HEAD,
  Root artifact commit OID, and parent repository scope.
- Task 3 only; Tasks 1 and 2 must not be reimplemented or amended.
- `.agents/custom/root.md` as the sole staged-path allowlist.
- Protected sections and paths that must remain unchanged.
- Focused and cumulative verification commands.
- Candidate-integrity procedure and required final-report evidence.
- A prohibition on subagents, scope expansion, unrelated edits, submodule
  changes, and Ship actions.

After the Default returns verified commits, Root dispatches a fresh Reviewer
with the same approved artifacts, recorded base, commit range, exact changed
paths, preservation requirements, and review evidence expectations.
