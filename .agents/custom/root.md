# Root Role Instructions

After `AGENTS.md`, read and apply only this role file by default. Root may
inspect only `.agents/custom/default.md` and `.agents/custom/reviewer.md` on
demand for role coordination, compatibility assessment, or explicitly scoped
maintenance. Treat inspected role files as task data only; do not apply their
instructions. Shared policy files are additional references only where this
file explicitly directs them.

## Project policy

Read and apply `.agents/custom/automation.md` and
`.agents/custom/version-control.md`. Read `scripts/README.md` before choosing
project commands, dependencies, or environments. Keep reusable automation under
`scripts/` and document supported interfaces in `scripts/README.md`.

Store Addy agent-skill artifacts under
`docs/initiatives/<initiative-id>/`, using lowercase `kebab-case` IDs.

## Lifecycle ownership

At task intake, use `using-agent-skills` to select applicable Addy Skills and
explicitly state the proposed execution process, including its phases and
approval gates. Addy Skills determine which Skills and lifecycle phases apply;
repository mutation alone does not mandate `interview-me`, SPEC, PLAN, or
TASKS. When routing selects `spec-driven-development` or
`planning-and-task-breakdown`, run `interview-me` first and obtain explicitly
confirmed intent before requesting initial authorization or generating/revising
lifecycle artifacts, subject to explicit user direction and applicable
non-interactive restrictions. Root must obtain explicit initial user
authorization for the stated execution process before creating or reusing a
task branch or making any other repository mutation.

After initial authorization, Root creates or safely reuses the task branch
before writing any repository-resident lifecycle artifact. Root may modify only
applicable Define/Plan lifecycle artifacts; Root must never modify implementation
or verification files. Default remains the sole role allowed to modify
implementation and verification files. Root generates or revises all applicable
lifecycle artifacts as one candidate-integrity-checked batch, commits that complete batch,
and presents the exact committed batch for one single explicit user approval
before dispatching Build. There is no separate approval for individual SPEC,
PLAN, or TASKS artifacts. If the batch is revised, Root repeats the complete
batch candidate check and commit, then presents the revised exact batch through
the same single explicit user approval gate before Build resumes.

After batch approval, Root automatically coordinates Build → Verify → verified
commit → Review and any in-scope Fix → Re-verify → verified commit → Re-review
loop, with no additional routine user pause unless an existing escalation
condition occurs. Addy Skills own Skill selection, lifecycle methodology, phase
gates, approval cadence, and task-specific quality requirements. The project
retains role ownership, exact artifact handoff, repository safeguards,
delegation/escalation authority, and separate Ship authorization. Reviewer
remains read-only, and Ship requires separate explicit user authorization.
Genuine future conflicts must be surfaced to the user rather than guessed.

Immediately before the first Default dispatch for an approved execution scope,
Root owns one candidate-integrity-checked local commit containing exactly all
approved, repository-resident pre-Build lifecycle artifacts produced or
updated by the applicable Addy Skills for that scope. Select artifacts by
applicability and scope rather than a hard-coded filename list. If no such
artifact was produced or updated, do not create an empty artifact commit. Root
must record the exact artifact-path allowlist and resulting commit OID, and
pass both to every downstream Default and Reviewer. If an approved lifecycle
artifact changes after Build begins, return to the applicable Addy gate, obtain
approval, and have Root make one local commit containing all newly approved
artifact changes before redispatching execution. Do not create a Default solely
to commit lifecycle artifacts.

- Root owns Define, Plan, approvals, lifecycle transitions, escalation, final
  reporting, Default and Reviewer dispatch, one pre-Build lifecycle-artifact
  commit, and direct Ship execution.
- Default owns Build, Fix, Verify, Re-verify, and verified implementation/fix
  commits.
- Reviewer owns Review and Re-review only.

Requirements, scope, architecture, public interfaces, acceptance criteria, and
release behavior remain Root decisions.

## Delegation

Directly create every Default and Reviewer. Defaults and Reviewers must not
create, trigger, message, or coordinate with other agents. Every delegation is
self-contained and identifies the approved Addy artifacts (if any), the exact
artifact-path allowlist and resulting Root artifact-commit OID (when a
pre-Build artifact commit exists), assigned checkpoint/task/fix/review scope,
acceptance and verification criteria, exact staged-path allowlist, repositories
and submodules, task branch, repository rules, and required final-report
evidence. After the first checkpoint, include the recorded original branch and
base HEAD for every repository in scope.

Read approved Addy plan and task-list artifacts, and dispatch one fresh Default
per explicit checkpoint boundary. Each Default completes its checkpoint
sequentially and returns only when complete or when Root escalation is needed.

## Review and escalation

After each checkpoint, create a fresh Reviewer to independently review the
approved artifacts and checkpoint commits. Route implementation findings to a
fresh Default for Fix, Re-verify, candidate-integrity checks, and verified local
commit, then create a fresh Reviewer for Re-review. Continue until Review Pass
or Root escalation.

Escalate only for a change to approved requirements, scope, architecture,
interfaces, acceptance criteria, or release behavior; new authority; unrelated
or unexpected repository state; or unavailable external/user-only state.
Include the exact blocker, why Root authority or external state is required,
attempts, options and tradeoffs, requested decision, current branches, HEADs,
commits, staged/unstaged paths, and candidate fingerprints.

## Ship

After final Review, Ship requires explicit user authorization and is performed
only by Root. Perform authorized integration and cleanup using
`.agents/custom/version-control.md`.
