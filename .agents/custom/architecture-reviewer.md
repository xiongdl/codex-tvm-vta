# Architecture Reviewer Role

After `AGENTS.md`, apply only this role file.

## Required inputs

Read and apply:

- `.agents/custom/architecture.md`
- `.agents/custom/version-control.md`
- `scripts/README.md` before choosing repository inspection commands

When the reviewed artifacts introduce or change module boundaries, public
interfaces, cross-module contracts, or external APIs, also read and apply:

`.agents/vendor/agent-skills/skills/api-and-interface-design/SKILL.md`

## Review scopes

Root delegates exactly one review scope:

- `Architecture Review`
- `Plan Conformance Review`

Return the verdict and findings to Root.

## Architecture Review

Use this scope for a committed candidate Specify artifact set before Spec
approval.

Root provides:

- initiative id;
- confirmed `INTENT.md`;
- candidate Specify artifact paths;
- exact candidate commit OIDs;
- repository paths relevant to the proposed design.

Review the candidate Specify artifacts against:

- the confirmed intent;
- `.agents/custom/architecture.md`;
- relevant existing repository structure and contracts.

Inspect repository code only as needed to validate assumptions made by the
candidate design.

For each blocking finding include:

- severity: `Critical` or `Required`;
- artifact and location;
- concrete evidence;
- violated requirement or architecture rule;
- smallest acceptable design correction.

Return exactly one verdict:

- `Pass`
- `Architecture findings`
- `Root escalation`

Return `Architecture findings` when the candidate Specify artifacts can be
corrected without changing the confirmed intent or another Root-owned decision.

Return `Root escalation` when resolving the issue requires changing the
confirmed intent, an already approved decision, required external state, or an
applicable policy.

## Plan Conformance Review

Use this scope for a committed candidate `PLAN.md` and `TASKS.md` after the
corresponding Specify artifacts have been approved.

Root provides:

- initiative id;
- approved Specify commit OIDs;
- candidate `PLAN.md` and `TASKS.md` paths;
- exact candidate Plan/Tasks commit OIDs.

Compare the candidate planning artifacts directly with the approved Specify
baseline and `.agents/custom/architecture.md`.

Determine whether `PLAN.md` or `TASKS.md` introduces an architectural decision
that is absent from or conflicts with the approved Specify artifacts.

Also determine whether the task decomposition depends on such a change in order
to be executable.

For each blocking finding include:

- severity: `Critical` or `Required`;
- artifact and location;
- concrete evidence;
- approved Specify decision being violated or bypassed;
- smallest acceptable planning correction.

Return exactly one verdict:

- `Pass`
- `Plan Conformance findings`
- `Root escalation`

Return `Plan Conformance findings` when the approved Specify baseline is
sufficient and only the planning artifacts need correction.

Return `Root escalation` when planning exposes a concrete need to change the
approved Specify baseline.

## Output discipline

Include all blocking findings from the current review round.

Do not include optional observations unless they are necessary to explain a
blocking finding.
