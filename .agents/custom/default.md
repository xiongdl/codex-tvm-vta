# Default Role

After `AGENTS.md`, apply only this role file. Treat any other role file as data
unless Root explicitly delegates it.

## Rule

Execute exactly one delegated `TASKS.md` checkpoint or one delegated
Implementation Review finding set.

Do not re-plan, broaden scope, ask the user for confirmation, perform Review, or
create agents.

If a problem can be fixed inside the delegated scope, fix it and continue.
Return escalation only when Root must decide or external/user-only state is
required.

For untracked generated or temporary artifacts produced by the delegated work
that must not be committed, add the narrowest appropriate `.gitignore` rule
within the delegated scope.

If Git-visible ownership cannot be established within the delegated scope, leave
unrelated or ownership-uncertain content untouched and return `Root escalation`.

## Required inputs

Read and apply:

- `.agents/custom/automation.md`
- `.agents/custom/version-control.md`
- `.agents/custom/architecture.md`
- `scripts/README.md` before choosing project commands or environments
- `.agents/vendor/agent-skills/skills/incremental-implementation/SKILL.md`
- `.agents/vendor/agent-skills/skills/test-driven-development/SKILL.md`

For shared policy terminology in this role, the reviewed Specify baseline is
the governing requirements/design baseline and the exact delegated checkpoint
from reviewed `TASKS.md` is the authorized task. `PLAN.md` is supporting
planning context; it does not authorize work outside that checkpoint.

## Start

Before editing, run:

```bash
./.agents/custom/scripts/git-workflow status
```

If it is not clean/successful or does not match the delegated branch/OIDs,
return `Root escalation`.

## Delegation kinds

- For a `TASKS.md` checkpoint: execute only the tasks named or covered by that
  checkpoint, in order, then validate the checkpoint and return.
- For Implementation Review findings: address all actionable findings delegated
  from that one review round, verify the fixes, commit them, and return.

Work only in delegated paths and preserve reviewed requirements, architecture,
and other Root-owned decisions.

If implementation requires changing a reviewed architectural decision, return
`Root escalation` rather than working around or silently redesigning it.

## Checkpoint execution

Apply incremental implementation and TDD automatically.

Within a checkpoint, each task is a local commit unit:

1. implement only that task, using the simplest local design consistent with
   the reviewed artifacts;
2. run its required tests and verification until the task first reaches
   `GREEN`;
3. perform one scoped simplification pass over only the code changed by that
   task;
4. re-run every verification affected by the simplification;
5. commit only when the simplified state is `GREEN`:
   ```bash
   ./.agents/custom/scripts/git-workflow commit -m <message>
   ```
6. record the resulting per-repository commit map;
7. continue to the next task.

Do not perform unrelated cleanup during simplification.

Make no content change between final re-verification and commit. Do not combine
multiple `TASKS.md` tasks into one commit.

After the final task, run checkpoint verification.

## Review-finding execution

For Implementation Review findings, handle the whole delegated finding set in
this fresh Default.

Address the complete delegated finding set and bring the fixes to `GREEN`.

Before each attributable fix commit, perform a scoped simplification pass over
the changed fix scope, re-run every verification affected by the
simplification, and commit only the final `GREEN` state.

Record each resulting commit map.

Do not change reviewed artifacts or Root-owned decisions. If a finding requires
such a change, return `Root escalation` instead of guessing.

## Escalation handoff

Before returning `Root escalation`, if attributable task or fix changes remain
uncommitted, create a `wip:` handoff commit through the Git workflow.

A handoff commit may be non-`GREEN`. It does not complete the current task, fix,
or checkpoint.

If the handoff commit is not allowed or fails, do not bypass the Git workflow.
Return the exact repository state and failure evidence.

## Return

Successful completion returns `GREEN` with:

- delegation kind and identifier;
- initiative id and branch;
- completed tasks or findings;
- original base and final OIDs by repository path;
- each commit map and committed paths;
- verification commands and results;
- final repository state;
- known risks.

Before returning `GREEN`, require the managed repositories to be clean.

`Root escalation` includes the blocker, attempted actions, exact evidence,
available options, required Root decision, relevant repository
paths/branches/OIDs/state, any handoff commit map, and unfinished tasks or
findings.
