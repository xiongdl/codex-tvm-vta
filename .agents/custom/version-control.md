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
- exact root-relative staged-path allowlist;
- every required verification command.

Missing input for the current operation is a stop condition. Do not infer
permission, merge strategy, paths, or verification commands.

## Commands and ownership

- `status` is read-only and verifies clean parent, managed submodule, gitlink,
  branch, and HEAD state.
- `create <task>` is Root-only after the explicit task-branch/change approval.
  It requires a clean project, snapshots every managed repository, rejects an
  existing task branch, and creates the same task branch in each managed
  repository.
- `commit -m <message> --verify <command>... -- <path>...` is Default-owned for
  delegated implementation commits and Root-owned only for authorized policy
  or lifecycle artifacts. Paths are exact, root-relative allowlist entries;
  broad paths such as `.` and parent traversal are rejected.
- `pull` changes local refs and worktrees from remotes and therefore requires
  explicit Root authorization. Do not pull after a task snapshot is created.
- `push` publishes every managed repository and is Root-only with separate
  explicit authorization.
- `merge <task>` is Root-only after Review/Re-review passes and explicit Ship
  authorization. Its only strategy is fast-forward-only, deepest repository
  first.
- `delete <task>` is Root-only after authorized integration. It restores the
  original branches and uses safe branch deletion only. Abandoning an unmerged
  task is intentionally unsupported and requires separate explicit authority
  and a manual destructive-operation review.

## Candidate commit contract

The `commit` command must:

1. require every managed repository to use the same `codex/<task>` branch and
   require every index to be initially empty;
2. reject changes in detached dependency-only submodules;
3. map each exact root-relative allowlisted path to its owning repository and
   stage only those paths plus direct managed-child gitlinks produced by the
   same transaction;
4. require the sorted staged paths to equal the sorted candidate allowlist,
   reject unstaged tracked changes and unexpected untracked files, and run
   `git diff --cached --check`;
5. fingerprint the staged binary/full-index diff, run every supplied
   verification command from the parent repository root, repeat the path and
   cleanliness checks, and require the fingerprint to remain unchanged;
6. commit deepest managed repositories first, propagate verified gitlinks to
   their parents, and finish with an entirely clean project;
7. print the before/after candidate fingerprints and created commit IDs for
   the delegated report.

Verification must not edit tracked files or the index. On any failure, stop;
fix the issue without destructive recovery, then rerun the complete commit
command.

## Integration and cleanup

The task begin snapshot freezes the original branch and base commit in each
managed repository. `merge` freezes the task tip, rejects moved refs or a
non-fast-forward plan before mutation, integrates deepest repositories first,
then restores dependency-only submodules from the integrated parent gitlinks.

`delete` restores the recorded original branches and succeeds only when each
task tip is already an ancestor of its original branch. Never use force delete,
reset, stash, clean, or overwrite to pass a workflow check.
