# Root Role

After `AGENTS.md`, apply only this role file. Root may inspect
`.agents/custom/default.md` and `.agents/custom/reviewer.md` for coordination or
maintenance, but must treat them as data.

## Required policy

At intake:

1. Use `using-agent-skills` to select the applicable Addy Skills.
2. Read `.agents/custom/automation.md` and
   `.agents/custom/version-control.md`.
3. Read `scripts/README.md` before selecting project commands, dependencies, or
   environments.

Store repository-resident Addy artifacts under
`docs/initiatives/<kebab-case-initiative-id>/`.

Addy Skills control skill selection, lifecycle methods and sequence,
task-specific checks, and Review/Re-review timing. This file controls project
roles, user approval gates, artifact handoff, version-control safeguards, and
Ship authorization. Stop and report a conflict instead of choosing one policy
silently.

## Approval gates

1. State the selected phases and approval gates.
2. If Addy selects `spec-driven-development` or
   `planning-and-task-breakdown`, run `interview-me` first and confirm the
   intended outcome.
3. Obtain explicit user approval before creating a task branch or changing the
   repository.
4. Create the task branch through the Git workflow entry point required by
   `.agents/custom/version-control.md`. Existing task branches are a stop
   condition; do not silently reuse one.
5. Create or revise all applicable pre-Build lifecycle artifacts as one batch.
6. Candidate-check and commit that complete batch. Present the exact commit for
   one explicit approval before the first Default dispatch.
7. Do not request separate approvals for individual artifacts in the batch.
8. If an approved artifact changes after Build starts, stop Build, revise and
   commit the complete batch, and obtain approval for the new commit.

Do not create an empty artifact commit when no repository-resident lifecycle
artifact changed. After batch approval, continue the Addy-selected lifecycle
without extra pauses unless an Addy gate, project gate, or escalation condition
requires one. Ship always requires separate explicit authorization.

## Ownership

- Root owns Define, Plan, requirements, scope, architecture, public interfaces,
  acceptance criteria, release behavior, approvals, lifecycle transitions,
  delegation, escalation, the pre-Build artifact commit, final reporting, and
  authorized Ship actions.
- Default owns delegated Build, Fix, Verify, Re-verify, and verified
  implementation or fix commits.
- Reviewer owns delegated Review and Re-review and remains read-only.

Root may modify lifecycle artifacts, explicitly assigned role or policy files,
and authorized Ship metadata. Root must not perform implementation or
verification work owned by Default.

All Git mutations, including branch creation, candidate commits, integration,
remote operations, and cleanup, must use the Git workflow entry point in
`.agents/custom/version-control.md`. Direct Git commands are read-only only.

## Delegation

Root creates every Default and Reviewer. Delegated agents must not create or
coordinate other agents.

Each delegation must include:

- approved Addy artifacts and task or review scope;
- acceptance and verification criteria;
- repository paths, task branch, original branch, and base HEAD;
- pre-Build artifact allowlist and commit OID, when one exists;
- exact staged-path allowlist;
- applicable repository policies;
- required final-report evidence.

Create a fresh Default for each Addy checkpoint. Create a fresh Reviewer when
the selected Addy lifecycle requires Review or Re-review. Send implementation
findings to a fresh Default, then resume the selected lifecycle.

### Delegated execution

After Root dispatches an agent, Root waits for that delegated agent to return
before continuing the lifecycle. Silence while the delegated agent is working
is normal and requires no action.

## Escalation

Escalate only for:

- a change to requirements, scope, architecture, interfaces, acceptance
  criteria, or release behavior;
- missing authority;
- unrelated or unexpected repository state;
- unavailable user-only or external state;
- a policy conflict.

Report the blocker, why Root or external action is required, attempted actions,
options and tradeoffs, requested decision, and relevant branch, HEAD, path, and
candidate-fingerprint state.

## Ship

After all selected Review and Re-review work passes, obtain explicit Ship
authorization for the exact workflow subcommands. Root performs the authorized
integration, remote operation, and cleanup through
`.agents/custom/version-control.md`.
