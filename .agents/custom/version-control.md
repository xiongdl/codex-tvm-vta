# Version Control

This policy defines safe Git and submodule mechanics. The owning workflow
supplies the repositories in scope, task name, recorded base state, allowed
paths, verification commands, merge authorization, and merge strategy.

## Required context

Before changing a repository, record for the parent and every repository in
scope: `<repo-path>`, `<task-branch>` (`codex/<kebab-case-work-name>`),
`<original-branch>`, `<base-head>`, and (when reusing a branch)
`<expected-task-head>`. Also record an explicit staged-path allowlist,
required verification commands, and the owning workflow's authorized merge
command/strategy.

Do not infer merge strategy or authorization here. For example,
`git merge --ff-only <task-branch>` permits only a fast-forward, while
`git merge --no-ff <task-branch>` creates a merge commit; either is valid only
when authorized by the owning workflow.

## Repository preflight

```bash
git -C <repo-path> symbolic-ref --quiet --short HEAD
git -C <repo-path> rev-parse HEAD
git -C <repo-path> status --short --branch
git -C <repo-path> submodule status --recursive
```

The first command prints the attached branch and exits nonzero for detached
HEAD. Record the second command's exact value. Inspect status for staged
(`A/M/D` in the index column), unstaged (`A/M/D` in the worktree column), and
untracked (`??`) paths. Submodule status must show expected commits; leading
`+`, `-`, or `U` is unexpected. If branch, HEAD, working tree, or submodule
state is unexpected, stop without changing state and report it. Do not stash,
reset, overwrite, rename, or delete anything to conceal the condition.

## Task branch creation and reuse

```bash
git -C <repo-path> show-ref --verify --quiet refs/heads/<original-branch>
git -C <repo-path> rev-parse <original-branch>
git -C <repo-path> show-ref --verify --quiet refs/heads/<task-branch>
git -C <repo-path> rev-parse <task-branch>
```

An absent task branch is created from the recorded base without altering the
original branch:

```bash
git -C <repo-path> switch --create <task-branch> <base-head>
```

For reuse, require the task branch HEAD to equal `<expected-task-head>` before:

```bash
git -C <repo-path> switch <task-branch>
```

An unexpected existing HEAD or detached original branch is a failure. Do not
force-create, reset, rename, or delete branches. Do not work on
`<original-branch>`. Every modified submodule uses the same task-branch name,
after its own preflight and base recording.

## Candidate staging and integrity

```bash
git -C <repo-path> add -- <path> [<path> ...]
git -C <repo-path> diff --cached --name-only
git -C <repo-path> diff --cached --
git -C <repo-path> diff --cached --check
git -C <repo-path> diff --name-only --
```

The staged names must exactly equal the allowlist. Review the staged diff;
`diff --cached --check` exits nonzero for whitespace errors. The final command
must print no tracked paths. Untracked paths remain visible in status and must
not be added unless allowed.

Compute the candidate fingerprint, freeze it, and run required verification
without editing tracked files:

```bash
git -C <repo-path> diff --cached --binary --full-index \
  | git hash-object --stdin
<required-verification-command>
git -C <repo-path> diff --cached --binary --full-index \
  | git hash-object --stdin
```

Verification must exit zero and fingerprints must match. Otherwise fix,
restage the explicit allowlist, and repeat. Then commit:

```bash
git -C <repo-path> commit -m "<type>: <description>"
git -C <repo-path> status --short
```

## Submodule commits and parent pointers

Commit verified submodule content before its parent pointer:

```bash
git -C <submodule-path> add -- <path> [<path> ...]
git -C <submodule-path> diff --cached --check
git -C <submodule-path> commit -m "<type>: <description>"
git -C <repo-path> submodule status --recursive
git -C <repo-path> add -- <submodule-path>
git -C <repo-path> diff --cached --submodule=diff -- <submodule-path>
```

A pointer without an authorized, verified submodule commit is a failure.

## Integration and cleanup

```bash
git -C <repo-path> switch <original-branch>
git -C <repo-path> status --short --branch
git -C <repo-path> rev-parse <original-branch>
git -C <repo-path> rev-parse <task-branch>
git -C <repo-path> merge-base --is-ancestor <base-head> <task-branch>
```

The ancestry check exits zero when the base is an ancestor. Resolve
unexpected divergence before the owning workflow authorizes a merge. Integrate
modified submodules into their recorded original branches first, then the
parent task branch. Verify each result with `git status --short --branch` and
`git log --oneline -n 3`.

After all integrations succeed, confirm ancestry and clean task branches from
submodules before the parent:

```bash
git -C <repo-path> merge-base --is-ancestor <task-branch> <original-branch>
git -C <repo-path> branch --delete <task-branch>
```

`branch --delete` safely refuses to delete an unmerged branch. Never use
cleanup to hide unexpected state.
