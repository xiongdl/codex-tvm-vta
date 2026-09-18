# Version Control

Apply the selected Addy Git workflow plus these project safeguards. The owning
workflow supplies scope and authorization; this file supplies the single Git
mutation entry point and its required inputs.

## Entry point

Run from the parent repository root:

```bash
./.agents/custom/scripts/git-workflow <subcommand> ...
```

The entry point requires host Git, Bash, and standard-library-only `python3`.
This bootstrap dependency is intentionally available before the project Conda
environment and does not run project Python code.

Run its isolated regression suite with:

```bash
bash .agents/custom/scripts/test-git-workflow
```

The suite mutates only temporary fixture repositories and removes them on exit.

All Git mutations in the parent repository and initialized submodules must go
through this entry point. Direct Git commands are limited to read-only
inspection such as `status`, `diff`, `log`, `show`, `rev-parse`,
`symbolic-ref`, `submodule status`, and `ls-files`.

`.codex/rules/default.rules` is a required defense-in-depth boundary. It must
keep direct Git mutations gated and must separately gate workflow commands
that integrate, publish, update from remotes, or delete branches. Do not remove
it merely because this script validates workflow state.

Project-local rules apply only when the project `.codex/` layer is trusted.
Restart Codex after changing a rules file so the active session reloads it.

## Required inputs

Before mutation, record for the parent repository and every managed repository
in scope:

- repository path;
- task name and derived branch `codex/<kebab-case-task>`;
- original branch and exact base commit;
- delegated task scope and expected affected paths;
- every required verification command.

Missing input for the current operation is a stop condition. Do not infer
permission, merge strategy, scope, or verification commands.

## Commands and ownership

- `status` is read-only and verifies clean parent, managed submodule, gitlink,
  branch, and HEAD state.
- `create <task>` is Root-only after the explicit task-branch/change approval.
  It requires a clean project, snapshots every managed repository, rejects an
  existing task branch, and creates the same task branch in each managed
  repository.
- `commit -m <message>` is Default-owned after delegated Test and Verify
  complete, and Root-owned only for verified policy or lifecycle artifacts. It
  commits all Git-visible changes made on the clean task branch.
- `pull` changes local refs and worktrees from remotes and therefore requires
  explicit Root authorization. Do not pull after a task snapshot is created.
- `push` publishes every managed repository and is Root-only with separate
  explicit authorization.
- `merge <task>` is Root-only after Review/Re-review passes and explicit Ship
  authorization. Its only strategy is fast-forward-only, deepest repository
  first.
- `delete <task>` is Root-only with explicit authorization. It restores the
  original branches and force-deletes the task branches, so it can clean up an
  integrated task or explicitly abandon an unmerged task.

## Commit contract

The `commit` command must:

1. require every managed repository to use the same `codex/<task>` branch and
   require every index to be initially empty;
2. reject changes in detached dependency-only submodules;
3. stage all Git-visible changes in each managed repository with
   `git add -A -- .`, plus direct managed-child gitlinks produced by the same
   or an interrupted transaction;
4. run `git diff --cached --check` before each repository commit;
5. commit deepest managed repositories first and propagate their gitlinks to
   their parents;
6. finish with an entirely clean project and print every created commit OID for
   the delegated report.

The owning role runs required Test and Verify commands before invoking
`commit`, records their commands and results, and makes no content change
between successful verification and the commit invocation. The entry point
does not run verification; it turns the already verified clean content into
the exact commit used for handoff.

On a staging or commit failure, stop without destructive recovery. The entry
point restores only the index entries it staged and preserves working-tree
content. A retry detects and propagates any managed child commit already
created by the interrupted transaction.

## Handoff contract

Every Root, Default, and Reviewer lifecycle handoff names an exact commit OID.
The receiver works from or reviews that commit. Working trees, indexes, and
patches are never lifecycle handoff state.

## Integration and cleanup

The task begin snapshot freezes the original branch and base commit in each
managed repository. `merge` freezes the task tip, rejects moved refs or a
non-fast-forward plan before mutation, integrates deepest repositories first,
then restores dependency-only submodules from the integrated parent gitlinks.

`delete` restores the recorded original branches, then force-deletes the task
branches. Because this may abandon unmerged commits, the exact delete command
requires explicit Root authorization. Never reset, stash, clean, or overwrite
to pass a workflow check.
