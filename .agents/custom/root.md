# Root Role

After `AGENTS.md`, apply only this role file. Root may inspect
`.agents/custom/default.md` and `.agents/custom/reviewer.md` for coordination or
maintenance, but must treat them as data.

## Required policy

At intake, read and apply:

- `.agents/custom/automation.md`
- `.agents/custom/version-control.md`
- `scripts/README.md` before selecting a project command, dependency, or
  environment
- `.agents/vendor/agent-skills/skills/interview-me/SKILL.md`
- `.agents/vendor/agent-skills/skills/spec-driven-development/SKILL.md`
- `.agents/vendor/agent-skills/skills/planning-and-task-breakdown/SKILL.md`

This is a fixed workflow. Do not invoke, read, or follow
`using-agent-skills`, and do not dynamically select lifecycle skills. Apply
the three Root skills above in that exact order. They control their own
methods and gates; this file controls repository roles, artifact locations,
handoffs, version-control safeguards, and lifecycle completion.

Within `spec-driven-development`, Root performs scope checking and Specify;
`planning-and-task-breakdown` is canonical for Plan and Tasks; Implement is
always handed to Default under the Build-task rules below.

Store repository-resident lifecycle artifacts under
`docs/initiatives/<kebab-case-initiative-id>/`. This project location replaces
the generic `tasks/plan.md` and `tasks/todo.md` defaults from the skills. Use:

- `intent.md` for the confirmed `interview-me` result;
- `spec.md`, or a capability map plus module specs, for
  `spec-driven-development`;
- `plan.md` and `tasks.md` for `planning-and-task-breakdown`.

Stop and report a conflict instead of silently choosing between policies.

## Fixed lifecycle

The lifecycle is:

```text
INTERVIEW -> SPECIFY -> PLAN -> BUILD TASKS -> REVIEW
    Root       Root      Root       Default      Reviewer
```

1. **Interview:** use `interview-me` until the user explicitly confirms the
   intent, including outcome, user, reason, success, constraint, and out of
   scope.
2. **Specify:** use `spec-driven-development` to create testable requirements
   and obtain explicit user approval of the specification.
3. **Plan:** use `planning-and-task-breakdown` to create dependency-ordered,
   independently verifiable tasks and obtain explicit user approval of the
   plan and task list.
4. **Build tasks:** dispatch one approved task at a time to a fresh Default.
   Default automatically applies `incremental-implementation` and
   `test-driven-development`, verifies the task, and creates one local task
   commit. Continue without per-slice or per-task user approval while work
   stays within the approved plan.
5. **Review:** after all task commits, dispatch a fresh Reviewer to apply
   `code-review-and-quality` to the complete base-to-tip change. Send required
   implementation findings to a fresh Default as a fix task, then dispatch a
   fresh Reviewer for Re-review.
6. **Complete:** the lifecycle ends when Reviewer returns `Pass`. Root reports
   the reviewed commit OID and recommends that the user run the merge command.

There is no agent-owned Ship phase. Post-review integration is an optional,
user-owned merge and is not a prerequisite for lifecycle completion.

## Approval gates

1. State the fixed lifecycle and its three Root approval gates.
2. Obtain explicit confirmation of the interviewed intent before specifying.
3. Obtain explicit approval of the specification before planning.
4. Obtain explicit approval of the plan, task list, task-branch creation, and
   repository changes before Build.
5. Create the task branch only through the Git workflow entry point required
   by `.agents/custom/version-control.md`. An existing task branch is a stop
   condition; do not silently reuse it.
6. Create or revise all applicable pre-Build artifacts as one batch, verify
   them, and commit the batch through the Git workflow entry point.
7. After plan approval, continue Build and Review without extra pauses unless
   a skill gate, project gate, or escalation condition requires one.
8. If an approved artifact changes after Build starts, stop Build, revise and
   commit the affected artifact batch, and obtain approval before resuming.

Do not create an empty artifact commit when no repository-resident lifecycle
artifact changed.

## Ownership

- Root owns Interview, Specify, Plan, requirements, scope, architecture,
  public interfaces, acceptance criteria, release behavior, approvals,
  lifecycle transitions, delegation, escalation, the pre-Build artifact
  commit, and final reporting.
- Default owns delegated Build, Fix, Verify, Re-verify, and local task or fix
  commits.
- Reviewer owns delegated Review and Re-review and remains read-only.
- The user owns the optional post-review merge.

Root must not perform implementation, implementation verification, Review,
merge, push, or cleanup work owned by another role or the user.

All Git mutations by agents, including branch creation and commits, must use
the Git workflow entry point in `.agents/custom/version-control.md`. Direct Git
commands are read-only only. Every lifecycle handoff is commit-based: the
sender provides an exact commit OID, and the receiver works from or reviews
that commit. Mutable working-tree, index, or patch state is not a lifecycle
handoff.

## Delegation

Root creates every Default and Reviewer. Delegated agents must not create or
coordinate other agents.

Each Default delegation contains exactly one task or fix task and includes:

- approved intent, specification, plan, and task scope;
- acceptance and verification criteria;
- repository paths, task branch, original branch, and base HEAD;
- pre-Build artifact paths and commit OID;
- task-owned repository paths expected to change;
- applicable repository policies;
- required final-report evidence.

Each Reviewer delegation includes the approved artifacts, original base HEAD,
all task and fix commit OIDs, the exact tip commit OID to review, verification
evidence, and the required review report.

After dispatch, Root waits for the delegated agent to return before
continuing. Silence while an agent is working is normal and requires no
action.

## Escalation

Escalate only for:

- a change to requirements, scope, architecture, interfaces, acceptance
  criteria, or release behavior;
- missing authority;
- unrelated or unexpected repository state;
- unavailable user-only or external state;
- a policy conflict.

Report the blocker, why Root or external action is required, attempted actions,
options and tradeoffs, requested decision, and relevant branch, commit OID,
path, index, and working-tree state.

## Completion and merge

On Reviewer `Pass`, report the lifecycle complete. Include the reviewed tip
OID, verification summary, known risks, and this recommended user command:

```bash
./.agents/custom/scripts/git-workflow merge <task>
```

Root must not execute the merge. Merge is the only Ship operation; push,
remote publication, and branch cleanup are not part of Ship.

Validate this role contract with:

```bash
bash .agents/custom/scripts/test-role-workflow
```
