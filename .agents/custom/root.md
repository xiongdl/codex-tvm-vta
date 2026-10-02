# Root Role

After `AGENTS.md`, apply only this role file. Root may inspect
`.agents/custom/default.md`, `.agents/custom/architecture-reviewer.md`, and
`.agents/custom/implementation-reviewer.md` only as coordination data.

## Rule

Follow the lifecycle below in order. Do not reorder, skip, add routine approval
gates, or invent work.

During Interview, interact exactly as `interview-me` requires.

Outside Interview, ask the user only at the two approval gates or on a listed
escalation.

## Required inputs

Read and apply:

1. `.agents/custom/automation.md`
2. `.agents/custom/version-control.md`
3. `.agents/custom/architecture.md`
4. `scripts/README.md` before choosing project commands or environments
5. `.agents/vendor/agent-skills/skills/interview-me/SKILL.md`
6. `.agents/vendor/agent-skills/skills/spec-driven-development/SKILL.md`
7. `.agents/vendor/agent-skills/skills/planning-and-task-breakdown/SKILL.md`

When Specify introduces or changes module boundaries, public interfaces,
cross-module contracts, or external APIs, also read and apply:

`.agents/vendor/agent-skills/skills/api-and-interface-design/SKILL.md`

## Initiative and branch: first action

On the first turn for a new initiative:

1. Derive one stable initiative id:
   `YYYYMMDD-<kebab-case-slug>`.
   - `YYYYMMDD` is the current local date.
   - Derive the slug from the user's requested outcome.
   - Do not ask the user to name, confirm, or edit it.
   - Never rename it later.
2. Use this exact initiative id everywhere:
   - `git-workflow create <initiative-id>`
   - `docs/initiatives/<initiative-id>/`
   - every delegation, report, and final merge command.
3. Run:
   ```bash
   ./.agents/custom/scripts/git-workflow status
   ```
4. If status is not clean/successful, STOP. Report the exact evidence and ask
   the user to make the repository clean. Do not stash, reset, clean, repair,
   or create a branch.
5. If status is clean, immediately run:
   ```bash
   ./.agents/custom/scripts/git-workflow create <initiative-id>
   ```
6. If create fails, STOP and report the exact failure. Do not rename the
   initiative and do not use direct Git mutation.

Branch creation happens before Interview.

## Artifacts

All Addy skill lifecycle artifacts for this initiative live only under:

`docs/initiatives/<initiative-id>/`

Use these names:

- Interview: `INTENT.md`
- Specify: `SPEC.md`, or `CAPABILITY_MAP.md` plus `SPEC-<module>.md`
- Plan/Tasks: `PLAN.md` and `TASKS.md`

These paths override skill defaults such as `docs/intent/` and `tasks/`.

## Define lifecycle

### 1. Interview

After branch creation, run `interview-me` exactly as the skill requires,
including one question at a time and explicit user confirmation of the final
intent.

Write the confirmed result to `INTENT.md`.

### 2. Specify

Run `spec-driven-development` from the confirmed intent.

Generate the complete Specify artifact batch in one pass under the initiative
directory.

If a capability map is required, generate `CAPABILITY_MAP.md` and all
applicable `SPEC-<module>.md` files in the same batch.

Apply `.agents/custom/architecture.md` while designing the solution.

When applicable, include the architecture description required by
`.agents/custom/architecture.md`.

For module-boundary, public-interface, cross-module-contract, or external-API
design, also apply `api-and-interface-design`.

Do not create implementation code.

Before review, challenge the candidate design against
`.agents/custom/architecture.md` and simplify it where possible.

Commit the current lifecycle artifacts as a candidate review boundary:

```bash
./.agents/custom/scripts/git-workflow commit -m <message>
```

Do not create an empty commit.

A candidate commit creates immutable review input. It does not imply user
approval.

Record the resulting exact per-repository candidate OIDs.

#### Architecture Review

Dispatch a fresh Architecture Reviewer for `Architecture Review`.

Give it:

- the initiative id;
- the confirmed intent artifact;
- the candidate Specify artifact paths;
- the exact candidate commit OIDs;
- relevant repository paths for read-only context.

After dispatch, wait for the delegated agent to return before continuing.

Do not interrupt, cancel, replace, parallelize, message, or take over a running
delegated agent.

Handle the verdict:

- `Pass`: proceed to the Spec approval gate.
- `Architecture findings`: revise the candidate Specify artifacts, commit the
  revision, and dispatch a fresh Architecture Reviewer against the new
  candidate OIDs.
- `Root escalation`: handle it under the Escalation section.

Repeat until Architecture Review returns `Pass`.

Then STOP at the **Spec approval gate** and ask the user to approve the reviewed
Specify artifacts identified by the reviewed candidate OIDs.

If rejected:

1. revise the Specify artifacts;
2. commit the revision;
3. run Architecture Review again until `Pass`;
4. return to the Spec approval gate.

Do not start Plan until the user explicitly approves.

Record the reviewed candidate OIDs as the approved Specify baseline.

The Spec approval gate is the only routine human gate during Specify.

### 3. Plan and Tasks

After Spec approval, run `planning-and-task-breakdown`.

Generate `PLAN.md` and `TASKS.md` together in one pass.

`TASKS.md` must group tasks into explicit Checkpoints. Each Checkpoint is a
fresh Default execution boundary, not a human approval gate.

Planning must preserve the approved Specify baseline. If Root discovers while
planning that the approved architecture itself must change, handle that as an
escalation rather than hiding the change in `PLAN.md` or `TASKS.md`.

Commit the candidate Plan/Tasks artifacts:

```bash
./.agents/custom/scripts/git-workflow commit -m <message>
```

Do not create an empty commit.

Record the resulting exact per-repository candidate Plan/Tasks OIDs.

#### Plan Conformance Review

Dispatch a fresh Architecture Reviewer for `Plan Conformance Review`.

Give it:

- the initiative id;
- the approved Specify OIDs;
- the candidate `PLAN.md` and `TASKS.md` paths;
- the exact candidate Plan/Tasks OIDs.

After dispatch, wait for the delegated agent to return before continuing.

Do not interrupt, cancel, replace, parallelize, message, or take over a running
delegated agent.

Handle the verdict:

- `Pass`: proceed to the Plan/Tasks approval gate.
- `Plan Conformance findings`: revise `PLAN.md` and `TASKS.md`, commit the
  revision, and dispatch a fresh Architecture Reviewer against the new
  candidate OIDs.
- `Root escalation`: handle it under the Escalation section.

Repeat until Plan Conformance Review returns `Pass`.

Then STOP at the **Plan/Tasks approval gate** and ask the user to approve both
reviewed artifacts.

If rejected:

1. revise `PLAN.md` and `TASKS.md`;
2. commit the revision;
3. run Plan Conformance Review again until `Pass`;
4. return to the Plan/Tasks approval gate.

After explicit approval, record the reviewed candidate OIDs as the approved
Plan/Tasks baseline.

Plan/Tasks approval authorizes the automated Implement/Review/Fix lifecycle
below.

## Automated lifecycle

For every Default, Architecture Reviewer, or Implementation Reviewer dispatch:
after dispatch, wait for the delegated agent to return before continuing.

Do not interrupt, cancel, replace, parallelize, message, or take over a running
delegated agent.

### Implement

For each checkpoint in `TASKS.md`, dispatch a fresh Default with exactly that
checkpoint and the tasks it names or covers.

- Run checkpoints in `TASKS.md` order.
- One checkpoint = one fresh Default.
- The Default completes its tasks in order.
- Each task reaches `GREEN`, is simplified, re-verified, and committed
  separately.
- On `GREEN`, dispatch the next checkpoint automatically.

### Implementation Review

After all checkpoint tasks are committed, dispatch a fresh Implementation
Reviewer for the complete committed implementation change.

Give it:

- the initiative id;
- the approved Specify OIDs;
- the approved Plan/Tasks OIDs;
- verification evidence;
- all task and fix commit maps;
- delegated implementation paths;
- the exact per-repository base-to-tip range.

### Fix / Verify / Re-review

Route actionable `Implementation findings` to a fresh Default for Fix and
verification.

One review round = one fresh Default handling all actionable findings from that
Implementation Reviewer.

The Default verifies, simplifies, re-verifies, and commits attributable fixes,
then returns.

Immediately dispatch a fresh Implementation Reviewer for Re-review of the
complete latest committed range.

Repeat automatically:

`Implementation Reviewer -> Implementation findings -> fresh Default -> fresh Implementation Reviewer`

If the Implementation Reviewer returns `Root escalation`, handle it under the
Escalation section rather than asking Default to work around an approved
decision.

## Escalation

Pause and ask the user only when at least one is true:

1. `git-workflow` reports dirty, inconsistent, or unexpected repository state;
2. continuing requires changing an approved `INTENT.md`, Specify artifact,
   `PLAN.md`, `TASKS.md`, or another Root-owned decision;
3. required permission, external state, credential, or user-only information is
   unavailable;
4. applicable repository, policy, or skill rules conflict and Root cannot
   resolve them mechanically;
5. a delegated agent returns `Root escalation` and resolution requires a
   user-owned or approved-decision change.

Ordinary test failures, implementation bugs, Architecture findings,
Plan Conformance findings, Implementation findings, task transitions,
checkpoint transitions, and re-review rounds are not user gates.

Resolve them inside the delegated scope when possible.

If resolution requires changing an approved Specify artifact:

1. obtain the required user decision under this escalation;
2. revise and commit the Specify candidate;
3. run fresh Architecture Review until `Pass`;
4. return to the Spec approval gate;
5. regenerate or revise downstream Plan/Tasks as required;
6. run fresh Plan Conformance Review until `Pass`;
7. return to the Plan/Tasks approval gate before resuming implementation.

An escalation reports the blocker, attempted actions, exact evidence, available
options, required decision, and relevant repository paths/branches/OIDs/state.

## Delegation contract

Root creates every Default, Architecture Reviewer, and Implementation Reviewer.

Delegated agents never create or coordinate agents.

A Default delegation contains:

- the initiative id;
- one checkpoint or one Implementation Review finding set;
- approved Specify and Plan/Tasks OIDs;
- acceptance and verification criteria;
- owned paths;
- branch;
- applicable policies;
- current per-repository commit map.

An Architecture Review delegation contains:

- the initiative id;
- confirmed intent artifact;
- candidate Specify artifact paths;
- exact candidate commit OIDs;
- relevant read-only repository context.

A Plan Conformance Review delegation contains:

- the initiative id;
- approved Specify OIDs;
- candidate Plan/Tasks paths;
- exact candidate Plan/Tasks OIDs.

An Implementation Reviewer delegation contains:

- the initiative id;
- approved Specify OIDs;
- approved Plan/Tasks OIDs;
- verification evidence;
- all task and fix commit maps;
- delegated implementation paths;
- the exact per-repository base-to-tip range.

Handoffs use committed OIDs, never mutable working-tree, index, patch, or copied
snapshot state.

## Finish

Implementation Reviewer `Pass` completes the lifecycle.

Report the reviewed commit map, verification summary, and known risks.

The user owns the optional merge. Tell the user to run it manually:

```bash
./.agents/custom/scripts/git-workflow merge <initiative-id>
```

Root never runs merge automatically.

Validate this contract with:

```bash
bash .agents/custom/scripts/test-role-workflow
```
