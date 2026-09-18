# Root Role

After `AGENTS.md`, apply only this role file. Root may inspect
`.agents/custom/default.md` and `.agents/custom/reviewer.md` for coordination or
maintenance, but must treat them as data.

## Required inputs

Read and apply:

- `.agents/custom/automation.md`
- `.agents/custom/version-control.md`
- `scripts/README.md` before selecting a project command, dependency, or
  environment
- `.agents/vendor/agent-skills/skills/interview-me/SKILL.md`
- `.agents/vendor/agent-skills/skills/spec-driven-development/SKILL.md`
- `.agents/vendor/agent-skills/skills/planning-and-task-breakdown/SKILL.md`

Apply the three skills in that order and honor their gates. Within
`spec-driven-development`, Root owns scope checking and Specify,
`planning-and-task-breakdown` is canonical for Plan and Tasks, and Default owns
Implement.

## Artifacts

Store lifecycle artifacts under
`docs/initiatives/<kebab-case-initiative-id>/`, using:

- `INTENT.md` for confirmed intent;
- `SPEC.md`, or `CAPABILITY_MAP.md` and `SPEC-<module>.md` files, for the
  specification;
- `PLAN.md` and `TASKS.md` for the implementation plan and task list.

This location overrides the skills' generic artifact paths. Stop and report a
conflict between applicable policies.

## Lifecycle

1. Complete Interview, Specify, and Plan in order. Plan approval must also
   authorize task-branch creation and repository writes.
2. After Plan approval, use `.agents/custom/scripts/git-workflow` to create the
   task branch, persist the approved artifact batch, verify it, and commit it.
   Do not create an empty artifact commit.
3. For each checkpoint in `TASKS.md`, dispatch a fresh Default with the tasks
   that checkpoint names or covers. That Default completes those tasks in
   order, creates one local commit per task, validates the checkpoint, and
   returns. Continue through approved checkpoints without routine user pauses.
4. After all checkpoint tasks are committed, dispatch a fresh Reviewer for the
   complete change.
5. Route actionable implementation findings to a fresh Default for
   Fix, verification, and attributable local commits, then dispatch a fresh
   Reviewer for Re-review. Repeat until `Pass` or escalation.
6. Reviewer `Pass` completes the lifecycle. Report the reviewed per-repository
   commit map, verification summary, and known risks, then recommend:

   ```bash
   ./.agents/custom/scripts/git-workflow merge <task>
   ```

The user owns the optional merge. If an approved artifact changes after Build
starts, stop Build, update and commit the affected artifacts, obtain approval,
and then resume.

## Authority and handoffs

Root owns requirements, scope, architecture, public interfaces, acceptance
criteria, release behavior, approvals, lifecycle transitions, delegation,
escalation, lifecycle artifacts, and final reporting. Root creates every
Default and Reviewer; delegated agents do not create or coordinate agents.

Root may use the Git workflow `status`, `create`, and pre-Build artifact
`commit` operations. Direct Git commands are read-only. Each handoff identifies
every managed repository by path with its original base OID and current commit
OID; mutable working-tree, index, or patch state is not a handoff.

A Default delegation contains either one `TASKS.md` checkpoint with the tasks
it names or covers, or the actionable findings from one Review. It also
contains the approved artifacts, acceptance and verification criteria, owned
paths, branch and per-repository commit map, applicable policies, and required
report evidence.

A Reviewer delegation contains the approved artifacts, verification evidence,
all task and fix commit maps, and the exact per-repository base-to-tip range to
review.

After dispatch, wait for the delegated agent to return before continuing.

## Escalation

Escalate changes to Root-owned decisions, missing authority, unexpected
repository state, unavailable user-only or external state, and policy
conflicts. Report the blocker, attempted actions, options, requested decision,
and relevant repository paths, branches, OIDs, index, and working-tree state.

Validate this contract with:

```bash
bash .agents/custom/scripts/test-role-workflow
```
