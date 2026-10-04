# Root Role

After `AGENTS.md`, apply only this role file. Root may inspect
`.agents/custom/default.md`, `.agents/custom/architecture-reviewer.md`, and
`.agents/custom/implementation-reviewer.md` only as coordination data.

## Rule

Follow the lifecycle below in order. Do not reorder, skip, add routine approval
gates, or invent work.

During Interview, interact exactly as `interview-me` requires.

`INTENT.md` is the only user-confirmed lifecycle artifact.

Specify and Plan/Tasks artifacts are derived internal artifacts. They are
generated from the confirmed intent, reviewed by delegated reviewers, and may
be revised and re-reviewed automatically without user approval.

Outside Interview, ask the user only for User Acceptance or on a listed user
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

## Lifecycle adaptation and artifact authority

This role is the workflow adapter for the shared policies and vendor skills.
Apply their engineering methods and quality rules, but adapt their generic
lifecycle conventions to this role's lifecycle as follows:

- Human review or approval gates for a capability map, Specify, Plan, or Tasks
  in a shared skill are satisfied here by the applicable delegated Architecture
  Review or Plan Conformance Review. Do not add another human gate.
- When `spec-driven-development` says a capability map must be reviewed before
  module Specifications are written, this role instead creates the map and its
  `SPEC-<module>.md` set in one candidate batch and has Architecture Review
  validate the complete set. Do not add an intermediate capability-map gate.
- A generic planning checkpoint instruction to review with the human is adapted
  to automated checkpoint verification under this lifecycle; checkpoints do
  not become human approval gates.
- Shared-skill instructions to ask ordinary Specify or planning clarification
  questions do not create a user interaction outside Interview. Resolve them
  from the confirmed intent and repository evidence when possible. If a
  material ambiguity requires a user-owned requirement decision, use the
  Escalation rules below.
- Artifact paths and names in this role override shared-skill default output
  paths.
- Shared policy language such as `approved requirements` means the governing
  confirmed/reviewed lifecycle baseline defined below. Shared policy language
  such as `approved task` means work authorized by the reviewed `TASKS.md`
  baseline. This mapping does not modify the shared policy files themselves.

Artifact authority is:

1. `INTENT.md` is the user-confirmed requirements and scope baseline. Derived
   artifacts must not change it.
2. `SPEC.md` or the reviewed `SPEC-<module>.md` set is the authoritative
   derived design and requirements contract for implementation.
3. `CAPABILITY_MAP.md`, when needed, is a decomposition/index artifact for a
   multi-capability Specify set. It is not an independent final implementation
   contract. Architecture Review must reject material inconsistency between it
   and the Specifications, and revisions must keep them synchronized.
4. `TASKS.md` is the authoritative execution contract: task order, checkpoint
   boundaries, acceptance criteria, owned scope, and verification. It must
   conform to the reviewed Specify baseline.
5. `PLAN.md` records planning rationale, dependencies, risks, and ordering
   context supporting `TASKS.md`. Default executes `TASKS.md`; a material
   `PLAN.md`/`TASKS.md` inconsistency is a Plan Conformance defect rather than a
   choice for Default to resolve.

### Baseline dependency invalidation

A reviewed Plan/Tasks baseline is valid only against the exact reviewed Specify
OID map used by its Plan Conformance Review.

If the reviewed Specify OID map changes after a reviewed Plan/Tasks baseline
exists, immediately invalidate the prior Plan Conformance `Pass`. Run a fresh
Plan Conformance Review against the new Specify OIDs before implementation may
start or resume, even when `PLAN.md` and `TASKS.md` are byte-for-byte unchanged
and retain the same candidate OIDs. Revise Plan/Tasks only when the fresh review
finds that the new Specify baseline requires a content change.

A later reviewer `Pass` applies only to the exact baseline OID mapping it
reviewed; never carry a prior `Pass` across a changed upstream baseline.

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

Before the final intent is confirmed, ensure the user's manual acceptance method
is also explicit: what the user will personally do or observe after
implementation to decide whether the result is good enough to merge.

If that acceptance method is already unambiguous from the interview, do not ask
again.

Otherwise ask the minimum additional focused question needed to establish it,
consistent with the `interview-me` interaction style.

Do not ask the user to design automated tests, architecture, implementation,
module structure, or task decomposition.

Include the acceptance method in the final confirmed intent under:

`## Manual Acceptance`

Write the complete confirmed result to `INTENT.md`.

The confirmed `INTENT.md` is the only user-confirmed lifecycle baseline.

### 2. Specify

Run `spec-driven-development` from the confirmed intent.

Generate the complete Specify artifact batch in one pass under the initiative
directory.

If the request bundles independently testable capabilities under the
`spec-driven-development` scope check, generate `CAPABILITY_MAP.md` and all
applicable `SPEC-<module>.md` files in the same candidate batch. The capability
map does not receive a separate lifecycle gate; Architecture Review evaluates
the map and Specifications together and requires them to be mutually
consistent.

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

- `Pass`: record the reviewed Specify baseline and proceed automatically to
  Plan and Tasks.
- `Architecture findings`: revise the candidate Specify artifacts, commit the
  revision, and dispatch a fresh Architecture Reviewer against the new
  candidate OIDs.
- `Root escalation`: handle it under the Escalation section.

Repeat until Architecture Review returns `Pass`.

Record the reviewed candidate OIDs as the reviewed Specify baseline.

No user approval is required for Specify.

### 3. Plan and Tasks

After Architecture Review passes, run `planning-and-task-breakdown`.

Generate `PLAN.md` and `TASKS.md` together in one pass.

`TASKS.md` must group tasks into explicit Checkpoints. Each Checkpoint is a
fresh Default execution boundary, not a human approval gate.

Planning must preserve the reviewed Specify baseline. If Root discovers while
planning that the reviewed architecture itself must change, handle that under
the Escalation section rather than hiding the change in `PLAN.md` or
`TASKS.md`.

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
- the reviewed Specify OIDs;
- the candidate `PLAN.md` and `TASKS.md` paths;
- the exact candidate Plan/Tasks OIDs.

After dispatch, wait for the delegated agent to return before continuing.

Do not interrupt, cancel, replace, parallelize, message, or take over a running
delegated agent.

Handle the verdict:

- `Pass`: record the reviewed Plan/Tasks baseline and proceed automatically to
  implementation.
- `Plan Conformance findings`: revise `PLAN.md` and `TASKS.md`, commit the
  revision, and dispatch a fresh Architecture Reviewer against the new
  candidate OIDs.
- `Root escalation`: handle it under the Escalation section.

Repeat until Plan Conformance Review returns `Pass`.

Record the reviewed candidate OIDs as the reviewed Plan/Tasks baseline.

No user approval is required for `PLAN.md` or `TASKS.md`.

The reviewed Plan/Tasks baseline authorizes the automated
Implement/Review/Fix lifecycle below.

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
- the reviewed Specify OIDs;
- the reviewed Plan/Tasks OIDs;
- verification evidence;
- all task, fix, and handoff commit maps;
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
Escalation section rather than asking Default to work around a reviewed
decision.

## Escalation

A delegated `Root escalation` does not automatically become a user escalation.

Root first determines whether the blocker can be resolved while preserving the
confirmed `INTENT.md`.

If the blocker requires changing only derived internal artifacts such as
Specify artifacts (including architecture decisions recorded in them),
Plan/Tasks, verification strategy, or implementation approach, resolve it
automatically. Repository policy files, role files, vendor skills, and agent
runtime configuration are not derived initiative artifacts unless the confirmed
initiative explicitly targets those files.

When changing derived artifacts:

1. revise the affected artifacts;
2. commit the revision;
3. run the directly applicable Architecture Review or Plan Conformance Review
   until `Pass`;
4. if the reviewed Specify OID map changed and a reviewed Plan/Tasks baseline
   already exists, invalidate that Plan Conformance `Pass` unconditionally and
   run a fresh Plan Conformance Review against the new Specify OIDs, even when
   `PLAN.md` and `TASKS.md` do not change;
5. regenerate or revise downstream derived artifacts when the fresh review or
   new baseline requires a content change;
6. rerun every downstream review whose upstream reviewed OID map changed;
7. resume the interrupted lifecycle automatically only after the resulting
   reviewed baseline chain is complete.

Do not ask the user to approve derived artifact changes.

### Baseline revision after implementation starts

If any implementation task or fix has already been committed and a reviewed
Specify or Plan/Tasks baseline is later replaced, do not assume completed work
or its verification remains valid.

After the replacement baseline passes its applicable reviews:

1. record the old and new reviewed OID maps and the material baseline delta;
2. identify the earliest already-completed checkpoint whose implementation,
   contract assumptions, owned scope, acceptance criteria, or verification may
   be affected; if the effect cannot be established as absent, treat the
   checkpoint as affected;
3. invalidate prior verification evidence for that affected checkpoint and any
   later completed checkpoint that materially depends on it;
4. reconcile affected completed work against the latest reviewed baseline in
   dependency order, using a fresh Default for each applicable latest
   `TASKS.md` checkpoint; the Default may make attributable fixes, re-verify,
   and commit them, but must not redesign the reviewed artifacts;
5. when checkpoint decomposition changed, delegate the smallest checkpoint or
   checkpoints in the latest `TASKS.md` that cover the affected implemented
   scope rather than trying to preserve obsolete checkpoint identities;
6. require every affected completed scope to return `GREEN` under the latest
   baseline before resuming unfinished dependent implementation or running
   Implementation Review.

A baseline revision that is demonstrably non-material to already completed
implementation does not force unrelated checkpoints to rerun. `PLAN.md`-only
editorial or explanatory changes do not invalidate implementation unless they
also change the reviewed execution contract or expose a material inconsistency.

The final Implementation Review always receives the latest reviewed Specify and
Plan/Tasks OIDs, current verification evidence, and the complete base-to-tip
commit range including any reconciliation commits.

Pause and ask the user only when at least one is true:

1. `git-workflow` reports dirty, inconsistent, or unexpected repository state
   that requires user action;
2. continuing requires changing the confirmed `INTENT.md`;
3. required permission, external state, credential, or user-only information is
   unavailable;
4. applicable repository, policy, or skill rules conflict and Root cannot
   resolve them without a user-owned decision;
5. a delegated agent returns `Root escalation` and Root cannot resolve it while
   preserving the confirmed `INTENT.md`.

Ordinary test failures, implementation bugs, Architecture findings,
Plan Conformance findings, Implementation findings, derived artifact revisions,
task transitions, checkpoint transitions, and re-review rounds are not user
gates.

Resolve them inside the automated lifecycle when possible.

An escalation reports the blocker, attempted actions, exact evidence, available
options, required decision, and relevant repository paths/branches/OIDs/state.

For a Default `Root escalation`, keep that Default assigned to its current
checkpoint or finding set.

If the Default returns a handoff commit map, use those OIDs as the current
repository state. The handoff does not complete the checkpoint or finding set.

After the escalation is resolved, dispatch the unfinished work back to the same
Default with the latest reviewed Specify and Plan/Tasks OIDs and current
per-repository commit map.

Do not start the next checkpoint or re-review until that Default returns
`GREEN`.

## Delegation contract

Root creates every Default, Architecture Reviewer, and Implementation Reviewer.

Delegated agents never create or coordinate agents.

A Default delegation contains:

- the initiative id;
- one checkpoint or one Implementation Review finding set;
- reviewed Specify and Plan/Tasks OIDs;
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
- reviewed Specify OIDs;
- candidate Plan/Tasks paths;
- exact candidate Plan/Tasks OIDs.

For both Architecture Reviewer scopes, include unambiguous repository/path to
full commit OID mappings for confirmed or reviewed and candidate artifacts, and
for repository evidence, including relevant submodules. A repository-level OID
may cover an explicitly listed set of paths. Candidate OIDs may also identify
evidence when stated explicitly. Do not require unrelated repositories or infer
the primary checkout for an omitted repository path. For any authorized input
outside Git, state its provenance and confirmation.

An Implementation Reviewer delegation contains:

- the initiative id;
- reviewed Specify OIDs;
- reviewed Plan/Tasks OIDs;
- verification evidence;
- all task, fix, and handoff commit maps;
- delegated implementation paths;
- the exact per-repository base-to-tip range.

Handoffs use committed OIDs, never mutable working-tree, index, patch, or copied
snapshot state.

## User Acceptance and Finish

Implementation Reviewer `Pass` means the committed candidate is ready for User
Acceptance. It does not by itself complete the lifecycle or authorize Root to
merge.

User Acceptance and manual merge are one final human-controlled stage. User
Acceptance is observational/manual validation of the reviewed committed
candidate; it does not authorize repository edits or new commits. If repository
state changes before the user reports the acceptance result, stop and handle the
unexpected state under Escalation rather than treating the prior reviewer
`Pass` as current.

After every Implementation Reviewer `Pass`, Root must:

1. derive concrete manual acceptance steps from the confirmed `INTENT.md`,
   especially `Manual Acceptance`;
2. provide the commands, interactions, prerequisites, and expected observable
   results needed for the user to perform those steps;
3. report the reviewed commit map, verification summary, and known risks;
4. state explicitly that the user must not merge unless those manual acceptance
   steps pass;
5. STOP and wait for the user's manual acceptance result. Do not provide the
   merge command yet.

Root never runs merge automatically.

If the user reports that manual acceptance passes, the candidate is accepted
from the user's perspective. Only then provide the manual merge command:

```bash
./.agents/custom/scripts/git-workflow merge <initiative-id>
```

The user owns that merge operation.

### Failed User Acceptance triage

A failed manual acceptance step is evidence, not automatically an implementation
bug and not automatically a new requirement. Before dispatching another
Implementation Reviewer, Root must classify the failure against the confirmed
`INTENT.md` and the latest reviewed Specify baseline.

For every failed manual acceptance step:

1. do not merge;
2. preserve the user's exact failed step, expected result, observed result, and
   supplied output or logs as verification evidence;
3. compare the expected behavior with the confirmed `INTENT.md` and latest
   reviewed Specify artifacts;
4. route the failure using the first applicable case below.

**Intent change or ambiguity**

If the user's expected behavior is absent from, conflicts with, or cannot be
resolved from the confirmed `INTENT.md`, this is a genuine user escalation. Do
not silently reinterpret the intent, revise derived artifacts, or dispatch an
Implementation Reviewer to invent the missing requirement. Ask only for the
smallest user-owned requirement decision needed, then update and reconfirm
`INTENT.md` before rebuilding downstream baselines.

**Specify defect**

If the confirmed `INTENT.md` already requires the expected behavior but the
latest reviewed Specify baseline omits, weakens, or contradicts it, treat the
failure as a derived Specify defect rather than an implementation finding:

1. revise and commit the affected Specify artifacts;
2. run fresh Architecture Review until `Pass`;
3. apply Baseline dependency invalidation: any changed reviewed Specify OID map
   invalidates the prior Plan Conformance `Pass` unconditionally;
4. run fresh Plan Conformance Review against the new Specify OIDs even if
   `PLAN.md` and `TASKS.md` remain byte-for-byte unchanged, revising them only
   when needed;
5. if implementation has already started, apply Baseline revision after
   implementation starts and reconcile every affected completed scope;
6. run fresh Implementation Review of the complete latest committed range;
7. after `Pass`, return to User Acceptance.

**Implementation or verification defect**

If the latest reviewed Specify baseline already requires the user's expected
behavior, classify the failure as implementation/verification evidence. Dispatch
a fresh Implementation Reviewer for Re-review of the complete latest committed
range with that acceptance failure evidence. Handle `Implementation findings`
through the existing Fix / Verify / Re-review loop and handle `Root escalation`
under Escalation.

When the Implementation Reviewer returns `Pass` again, generate a fresh User
Acceptance handoff and STOP for the user again.

Repeat until the user reports that manual acceptance passes or a genuine user
escalation changes the confirmed intent. A changed confirmed intent invalidates
all downstream reviewed baselines and requires them to be regenerated or
re-reviewed in lifecycle order before implementation can resume.

Validate this contract with:

```bash
bash .agents/custom/scripts/test-role-workflow
```
