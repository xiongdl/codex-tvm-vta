# Version Control

Run every Git mutation from the repository root through:

```bash
./.agents/custom/scripts/git-workflow <command> ...
```

Direct `git` commands are read-only only.

Do not use direct Git mutations, reset, stash, clean, overwrite, or any other
bypass to make a workflow check pass.

Every handoff uses exact commit OIDs, never working-tree, index, patch, or
copied snapshot state.

## Authorization

A command marked `Requires explicit authorization` may run only when that
command has been explicitly authorized.

Authorization for one command does not authorize another. Permission to inspect,
edit, test, or commit does not authorize `pull`, `push`, `merge`, or `delete`.

## Git-visible ownership

Before `commit`, every Git-visible change in every managed repository must be
attributable to the work being committed.

If a Git-visible change is unrelated or its ownership is uncertain, do not
modify it, remove it, add an ignore rule for it, or include it in the commit.

Do not commit until every Git-visible change is attributable to the work being
committed.

`git-workflow commit` stages the complete Git-visible state. It does not infer
ownership. Establish ownership before invoking it.

## Commands

- `status`
  - Use before starting work, before a command that requires a clean repository,
    or whenever repository state is uncertain.
  - Read-only.
  - Succeeds only when all discovered repositories and gitlinks are clean and
    consistent, then prints their paths, branches, and commit OIDs.

- `pull`
  - Requires explicit authorization.
  - Use only on clean managed repositories with configured upstreams and before
    creating a task branch.
  - Pulls each managed repository with `--ff-only --prune`.

- `create <task>`
  - Use only from clean managed repositories.
  - The derived `codex/<task>` branch and task-begin snapshot must not exist.
  - Records each current branch and commit, then creates the same task branch in
    every managed repository.

- `commit -m <message>`
  - Use only on the common `codex/<task>` branch with initially empty indexes.
  - Before invocation, every Git-visible change must satisfy the Git-visible
    ownership rules above.
  - Stages all Git-visible changes, checks the staged diff, commits managed
    repositories deepest first, requires a clean result, and prints commit OIDs.
  - If it fails, fix the reported cause and retry. Working-tree content and any
    child commit already created are preserved.

- `push`
  - Requires explicit authorization.
  - Use only with clean managed repositories.
  - Pushes each managed branch to its upstream, or sets `origin/<branch>` as the
    upstream when none exists.

- `merge <task>`
  - Requires explicit authorization.
  - Use only when all managed repositories are clean and on the task branch,
    the original branches have not moved, and every update is fast-forwardable.
  - Fast-forwards the recorded original branches to the task commits, deepest
    repository first, then leaves the repository set clean on the original
    branches.

- `delete <task>`
  - Requires explicit authorization.
  - Use only with a task-begin snapshot, existing original branches, and clean
    managed repositories.
  - Restores the original branches and force-deletes the task branches.
  - It can delete an unmerged task and abandon its commits.

## Verification

Run the isolated regression suite with:

```bash
bash .agents/custom/scripts/test-git-workflow
```
