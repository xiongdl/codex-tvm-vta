# Tasks: Unify Lifecycle Approval Flow

## Task 1: Update Root lifecycle policy

**Description:** Update `.agents/custom/root.md` so Root states the
`using-agent-skills`-selected execution process, obtains initial authorization
before mutation, creates the task branch before lifecycle artifact writes,
commits all applicable Define/Plan artifacts as one batch, and obtains one
explicit batch approval before Build. Preserve role boundaries and all
post-approval automation.

**Acceptance criteria:**

- [ ] Intake states the proposed execution process and obtains explicit user
      authorization before task-branch creation or any repository mutation.
- [ ] When applicable, `interview-me` reaches confirmed intent before initial
      authorization and artifact generation.
- [ ] Root creates or safely reuses the task branch before writing any
      repository-resident lifecycle artifact.
- [ ] Root may modify only Define/Plan lifecycle artifacts; Default remains the
      sole modifier of implementation and verification files.
- [ ] All applicable lifecycle artifacts are generated or revised and committed
      as one candidate-checked batch before presentation to the user.
- [ ] One explicit approval of the exact committed batch replaces separate
      SPEC, PLAN, and TASKS approvals.
- [ ] A revised batch is committed again and presented through the same single
      approval gate before Build resumes.
- [ ] After batch approval, the existing Build -> Verify -> verified commit ->
      Review and Fix -> Re-verify -> verified commit -> Re-review loop remains
      automatic except for existing escalation conditions.
- [ ] Reviewer remains read-only and Ship requires separate explicit user
      authorization.
- [ ] `AGENTS.md`, `.codex`, `.agents/custom/default.md`, and
      `.agents/custom/reviewer.md` remain unchanged unless a concrete conflict
      with the approved specification is proven and escalated to Root.

**Verification:**

- [ ] `git diff --check` exits zero.
- [ ] `rg` finds `using-agent-skills`, explicit execution-process
      communication, initial authorization, task-branch-first lifecycle writes,
      Root lifecycle-only mutation, committed batch approval, automatic
      Build-through-Review, and separate Ship authorization.
- [ ] Focused diff review finds no sequential per-artifact approval requirement.
- [ ] Focused diff review confirms no unrelated role, runtime, or project code
      changes.
- [ ] The staged implementation candidate has the exact allowlist
      `.agents/custom/root.md`, unchanged fingerprints around verification, no
      unstaged tracked changes, and a verified local commit.

**Dependencies:** Explicit approval of the complete committed SPEC/PLAN/TASKS
batch.

**Files likely touched:**

- `.agents/custom/root.md`

**Estimated scope:** Small (one implementation file).

## Checkpoint: Root policy complete

- [ ] Task 1 acceptance criteria are met.
- [ ] Definition of Done is satisfied for this policy-only change.
- [ ] Default reports GREEN with commit OID, exact committed path, verification
      commands and outcomes, candidate fingerprints, clean staged/unstaged
      state, and risks.
- [ ] A fresh Reviewer returns Pass, or findings complete the required
      Fix/Re-verify/commit/Re-review loop.
- [ ] The reviewed task branch remains unmerged pending explicit Ship
      authorization.

## Root Artifact Commit Gate

Before presenting this batch for approval, Root stages exactly:

- `docs/initiatives/unify-lifecycle-approval-flow/SPEC.md`
- `docs/initiatives/unify-lifecycle-approval-flow/PLAN.md`
- `docs/initiatives/unify-lifecycle-approval-flow/TASKS.md`

Root applies the allowlist, staged diff, whitespace, candidate fingerprint,
and frozen verification checks from `.agents/custom/version-control.md`, then
commits the complete batch. Root presents the exact commit OID and all three
files for one explicit user approval. If the user requests revisions, Root
repeats this batch commit gate before presenting the revised batch again.
