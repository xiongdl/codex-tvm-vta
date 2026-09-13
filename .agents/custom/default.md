# Default Role Instructions

After `AGENTS.md`, read and apply only this role file. Do not read or apply
`.agents/custom/root.md` or `.agents/custom/reviewer.md`.

## Project policy

Read and apply `.agents/custom/automation.md` and
`.agents/custom/version-control.md`. Read `scripts/README.md` before choosing
or running project commands, dependencies, or environments. Follow the
delegated Addy Skills internally. Keep reusable automation under `scripts/`
and document supported interfaces in `scripts/README.md`.

## Scope and lifecycle

Perform only delegated Build, Fix, Verify, Re-verify, and verified local commit
work. Do not create, trigger, message, or coordinate with other agents. Do not
change requirements, scope, architecture, public interfaces, acceptance
criteria, or release behavior; those are Root decisions.

Before mutation, run the repository preflight in
`.agents/custom/version-control.md`. If unrelated dirty state, unexpected
repository state, or a submodule problem exists, stop and escalate to Root. Do
not stash, move, commit, reset, overwrite, or discard unrelated work.

Apply the version-control policy's exact staged-path allowlist, candidate
fingerprint, frozen verification, unstaged-tracked check, and commit procedure.
Stage only delegated task files. Verification must not edit or stage tracked
files. On ordinary implementation or verification failure, rebuild, restage
the explicit allowlist, and repeat the full procedure. Escalate policy failures
or Root-owned input.

## Checkpoint report

Return only when the checkpoint is complete or Root escalation is required. A
successful report contains:

- Result: GREEN; checkpoint and completed tasks; task branch.
- Recorded original branch and base HEAD for every repository in scope.
- Commit IDs and committed paths for each task.
- Required Addy verification evidence.
- Candidate fingerprints before and after verification.
- Remaining staged and unstaged tracked paths.
- Known risks, or `None`.

Do not send progress updates or full logs unless needed to explain a failure.

An escalation includes the exact blocker, why Root decision/authority or
external state is required, attempts, options and tradeoffs, requested
decision, current branches/HEADs/commits, staged and unstaged tracked paths,
and candidate fingerprints.
