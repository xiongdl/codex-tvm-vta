# Spec: Follow Addy Lifecycle Policy

## Objective

Align the project's Root-controlled workflow with the applicable Addy Skills
instead of imposing SPEC and PLAN on every repository-mutating task. Addy skill
routing determines which lifecycle phases apply. Whenever routing selects
`spec-driven-development` or `planning-and-task-breakdown`, Root invokes
`interview-me` first by default and obtains a confirmed intent before entering
those phases.

Follow Addy's gated `SPEC -> PLAN -> TASKS -> IMPLEMENT` workflow, including a
separate user review and explicit approval after SPEC, PLAN, and TASKS. Preserve
the project's existing automatic Build, Verify, verified commit, Review, and
in-scope fix loop after those gates. Preserve the current agent coordination,
role ownership, exact artifact handoff, repository safety rules, and separate
user authorization for Ship, except that Root—not a dedicated Default—owns the
single pre-Build commit of approved lifecycle artifacts.

## Instruction Context

- `AGENTS.md` remains the minimal role router loaded for every role.
- `.agents/custom/root.md` owns skill routing, lifecycle transitions, user
  approvals, delegation, escalation, and Ship authorization.
- `.agents/custom/default.md` and `.agents/custom/reviewer.md` remain unchanged.
  Default retains Build, Fix, Verify, Re-verify, and verified
  implementation/fix commits; Reviewer retains Review and Re-review.
- `.agents/custom/automation.md` and
  `.agents/custom/version-control.md` remain unchanged shared policies.
- Initiative-scoped lifecycle artifacts remain under
  `docs/initiatives/<initiative-id>/` and are passed to downstream roles by
  exact path.
- The vendored Addy Skills remain unchanged and are the source of truth for
  skill applicability, methodology, phase gates, and quality requirements.

No product runtime, external API, dependency, TVM/VTA source, or submodule
change is involved.

## Required Workflow

At task intake, Root applies `using-agent-skills` and follows the Skills it
selects:

1. Addy Skills determine whether Define, Plan, Build, Verify, Review, or Ship
   methodology applies to the task.
2. Do not require SPEC, PLAN, or TASKS merely because a task modifies repository
   state.
3. If routing selects `spec-driven-development` or
   `planning-and-task-breakdown`, invoke `interview-me` first by default and
   obtain an explicitly confirmed intent before creating downstream artifacts.
4. If `spec-driven-development` applies, follow its gated sequence and obtain
   separate explicit user approval for the displayed SPEC, PLAN, and TASKS.
5. Do not write a downstream artifact before the preceding applicable artifact
   has been approved.
6. Before the first Default dispatch for an approved execution scope, Root
   creates one candidate-integrity-checked local commit containing exactly all
   approved, repository-resident pre-Build lifecycle artifacts produced or
   updated by the applicable Addy Skills for that scope. The artifact set is
   capability-based rather than a hard-coded filename list and may include, for
   example, a persisted intent, capability map, module specifications, plans,
   task lists, constraints, ADRs, or future Addy artifact types when applicable.
7. Root records and verifies the exact artifact-path allowlist and passes those
   paths and the resulting commit OID to every downstream Default and Reviewer.
   Do not create a separate Default solely to commit lifecycle artifacts. If no
   repository-resident lifecycle artifact was produced or updated, do not
   create an empty artifact commit.
8. After the artifact commit gate, Root automatically coordinates
   `Build -> Verify -> verified commit -> Review` and any in-scope
   `Fix -> Re-verify -> verified commit -> Re-review` loop. Do not introduce an
   additional user pause between these stages unless an existing escalation
   condition occurs.
9. Preserve the existing Root, Default, and Reviewer coordination model,
   including fresh-agent boundaries, self-contained delegation, exact artifact
   paths, task scope, acceptance and verification criteria, branches, commits,
   staged-path allowlists, and required final-report evidence.
10. If an approved lifecycle artifact changes after Build begins, return to the
    applicable Addy gate, obtain approval, commit all newly approved artifact
    changes once, and only then redispatch execution.
11. Ship remains a separate, explicit user-authorized Root action.

An explicit user instruction may skip an otherwise applicable interview or
pre-Build phase. Non-interactive contexts must follow the applicable Addy Skill
restrictions rather than attempting an interactive interview.

## Role-File Inspection

Roles load and apply only their matching role instructions by default. Root may
inspect `.agents/custom/default.md` and `.agents/custom/reviewer.md` when needed
for role coordination, compatibility assessment, or explicitly scoped
maintenance. Root treats those files as task data and does not apply their
instructions as Root policy.

Default and Reviewer retain the existing narrow rule: they may inspect another
role file only when Root names the exact file in the delegated scope and staged
path allowlist, and they must treat it solely as task data.

## Policy Precedence

- Applicable Addy Skills define skill selection, lifecycle methodology, phase
  gates, approval cadence, and task-specific quality requirements.
- Project instructions define Root/Default/Reviewer ownership, artifact storage
  and exact-path handoff, repository and candidate-integrity safeguards,
  delegation authority, escalation ownership, and separate Ship authorization.
- Root owns the single candidate-integrity-checked commit of approved pre-Build
  lifecycle artifacts for an execution scope. Default owns verified
  implementation and fix commits.
- Project instructions must not silently weaken or replace an applicable Addy
  Skill's workflow. A deliberate exception requires an explicit user direction.
- If a future Addy upgrade creates a genuine conflict with project-owned role,
  repository-safety, or Ship authority rules, Root must surface the conflict and
  request a decision rather than guessing.

## Project Structure

```text
AGENTS.md
    Minimal role routing and the Root inspection exception
.agents/custom/root.md
    Addy-driven lifecycle selection, approvals, lifecycle-artifact commit,
    delegation, and Ship policy
docs/initiatives/follow-addy-lifecycle-policy/
    SPEC.md, followed by separately approved PLAN.md and TASKS.md
```

## Commands

This is instruction-only work. Verification uses static repository checks:

```bash
rg -n 'using-agent-skills|interview-me|spec-driven-development|planning-and-task-breakdown' \
  .agents/custom/root.md
rg -n 'SPEC|PLAN|TASKS|Ship' .agents/custom/root.md
rg -n 'by default|task data|compatibility assessment' \
  AGENTS.md .agents/custom/root.md
git diff --check
git diff -- AGENTS.md .agents/custom/root.md
```

Before a verified commit, apply the candidate-integrity and exact staged-path
procedures in `.agents/custom/version-control.md`. Product builds and TVM/VTA
tests are not required because product and submodule code are out of scope.

## Documentation Style

- Keep `AGENTS.md` concise and limited to role routing and cross-role inspection
  boundaries.
- Keep lifecycle selection and approval rules in `.agents/custom/root.md`.
- Use imperative, testable language and distinguish Addy-owned methodology from
  project-owned execution authority.
- Refer to Skills by their canonical kebab-case names.
- Do not duplicate the contents of vendored Skills in project instructions.

## Testing Strategy

Use static assertions and independent review:

- Confirm Root always performs `using-agent-skills` routing at intake.
- Confirm repository mutation alone no longer forces SPEC/PLAN/TASKS.
- Confirm selection of spec or planning defaults to a confirmed
  `interview-me` intent first.
- Confirm SPEC, PLAN, and TASKS each require a separate user approval when the
  Addy gated workflow applies.
- Confirm Root creates at most one pre-Build commit per approved execution scope
  containing exactly all approved, repository-resident lifecycle artifacts
  produced or updated for that scope.
- Confirm artifact selection is not limited to SPEC/PLAN/TASKS, an empty commit
  is forbidden, and no Default is created solely for the artifact commit.
- Confirm exact artifact paths and the commit OID are passed downstream.
- Confirm the final applicable pre-Build approval automatically starts Build,
  after Root's artifact commit gate, followed by Verify, verified implementation
  commit, Review, and the in-scope fix/re-review loop without another routine
  user approval.
- Confirm Root can inspect Default/Reviewer role files only on demand and never
  applies their instructions.
- Confirm Default/Reviewer inspection restrictions remain intact.
- Confirm existing agent coordination, project role ownership, exact artifact
  handoff, Git safety, escalation conditions, and Ship authorization remain
  explicit.
- Confirm only approved instruction and initiative artifact paths change.

## Boundaries

### Always

- Use Addy routing to select applicable Skills.
- Preserve Addy's applicable workflow and approval cadence.
- Commit approved, repository-resident pre-Build lifecycle artifacts exactly
  once per execution scope before the first Default dispatch.
- Preserve the automatic Build-through-Review lifecycle and project-owned agent
  coordination, role isolation, repository safety, exact artifact handoff,
  escalation, and Ship authorization.
- Surface conflicts introduced by future Addy upgrades.

### Ask First

- Any change to this confirmed intent or approved specification.
- Any deliberate exception from an applicable Addy Skill.
- Any change to Default/Reviewer responsibilities, shared policies, model
  configuration, or artifact storage conventions beyond the Root artifact
  commit ownership approved here.
- Ship, merge, push, release, deployment, or external publication.

### Never

- Force SPEC or PLAN solely because repository state will change.
- Skip an applicable Addy phase or combine its approval gates without explicit
  user direction.
- Apply another role file's instructions to the active role.
- Create a dedicated Default solely to commit lifecycle artifacts.
- Create an empty artifact commit or include an unapproved/unrelated path in the
  artifact commit.
- Modify vendored Addy Skills as part of this initiative.
- Modify product code, submodule content, or submodule pointers.

## Success Criteria

1. `using-agent-skills` determines the applicable workflow for every task.
2. Repository mutation alone does not activate SPEC, PLAN, or TASKS.
3. Selecting `spec-driven-development` or `planning-and-task-breakdown`
   defaults to `interview-me` and an explicitly confirmed intent first.
4. Applicable SPEC, PLAN, and TASKS are displayed and approved separately in
   that order before implementation.
5. Before the first Default dispatch for an approved execution scope, Root
   creates one candidate-integrity-checked commit containing exactly all
   approved, repository-resident pre-Build lifecycle artifacts produced or
   updated for that scope; no hard-coded filename list or dedicated
   artifact-commit Default is used.
6. Root passes the exact artifact paths and commit OID downstream, creates no
   empty commit, and repeats the applicable approval-and-single-commit gate if
   lifecycle artifacts change after Build starts.
7. Root then automatically coordinates Build, Verify, verified implementation
   commits, Review, and all in-scope
   Fix/Re-verify/Re-review work without another routine user pause.
8. Existing Root/Default/Reviewer delegation, fresh-agent boundaries,
   escalation conditions, and evidence requirements remain unchanged.
9. Root may inspect Default/Reviewer role files on demand for coordination,
   compatibility assessment, or scoped maintenance without applying them.
10. Default and Reviewer continue to load only their own role policy and retain
   their exact delegated inspection exception.
11. Addy owns lifecycle methodology and gates; the project retains role
   ownership, exact artifact handoff, Git safeguards, escalation, and Ship
   authority.
12. Static verification and independent Review pass without actionable findings.
13. No vendored Skill, product code, submodule, shared policy, or model
   configuration changes.

## Open Questions

None. The user explicitly confirmed Addy-driven applicability, a default
`interview-me` step before spec/planning, separate SPEC/PLAN/TASKS approvals,
on-demand Root role-file inspection, automatic Build-through-Review execution,
Root ownership of one generic pre-Build lifecycle-artifact commit per execution
scope, no dedicated artifact-commit Default, otherwise unchanged agent
coordination, and preservation of Ship safeguards.
