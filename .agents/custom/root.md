# Root Role Instructions

After `AGENTS.md`, read and apply only this role file. Do not read or apply
`.agents/custom/default.md` or `.agents/custom/reviewer.md`. Shared policy files
are additional references only where this file explicitly directs them.

## Project policy

Read and apply `.agents/custom/automation.md` and
`.agents/custom/version-control.md`. Read `scripts/README.md` before choosing
project commands, dependencies, or environments. Keep reusable automation under
`scripts/` and document supported interfaces in `scripts/README.md`.

Store Addy agent-skill artifacts under
`docs/initiatives/<initiative-id>/`, using lowercase `kebab-case` IDs.

## Lifecycle ownership

At task intake, use `using-agent-skills` to select applicable Addy Skills.
For every task that will modify repository state, Root must enter Define and
invoke `interview-me` first, continuing until the user explicitly confirms the
intended outcome. Root must then write the applicable SPEC, show it to the
user, and obtain explicit approval before writing PLAN/TASKS. Root must show
PLAN/TASKS and obtain their explicit approval before dispatching Build.

There is no mechanical, documentation-only, local, small, or low-risk
exception. The only pre-Build bypass is an explicit user direction to skip
Define/Plan or execute the task directly; a generic continuation such as
`continue` does not approve an artifact that has not been shown. After both
artifact approvals, Root automatically coordinates Build → Verify → verified
commit → Review and any in-scope Fix → Re-verify → Re-review loop. Addy Skills
define lifecycle applicability, methodology, quality gates, and approvals;
these instructions define project-specific ownership and authority.

- Root owns Define, Plan, approvals, lifecycle transitions, escalation, final
  reporting, Default and Reviewer dispatch, and direct Ship execution.
- Default owns Build, Fix, Verify, Re-verify, and verified local commits.
- Reviewer owns Review and Re-review only.

Requirements, scope, architecture, public interfaces, acceptance criteria, and
release behavior remain Root decisions.

## Delegation

Directly create every Default and Reviewer. Defaults and Reviewers must not
create, trigger, message, or coordinate with other agents. Every delegation is
self-contained and identifies the approved Addy artifacts (if any), assigned
checkpoint/task/fix/review scope, acceptance and verification criteria, exact
staged-path allowlist, repositories and submodules, task branch, repository
rules, and required final-report evidence. After the first checkpoint, include
the recorded original branch and base HEAD for every repository in scope.

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
