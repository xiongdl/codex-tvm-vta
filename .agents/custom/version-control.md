# Version Control

This policy defines safe Git and submodule mechanics. The owning workflow
supplies the repositories in scope, task name, recorded base state, allowed
paths, verification commands, merge authorization, and merge strategy.

## Required context

Before changing a repository, record for the parent and every repository in
scope: `<repo-path>`, `<task-branch>` (`codex/<kebab-case-work-name>`),
`<original-branch>`, `<base-head>`, and (when reusing a branch)
`<expected-task-head>`. Also record an explicit staged-path allowlist,
required verification commands, and the exact authorized merge command supplied
by the owning workflow.

Do not infer merge strategy or authorization here. For example,
`git merge --ff-only <task-branch>` permits only a fast-forward, while
`git merge --no-ff <task-branch>` creates a merge commit; either is valid only
when authorized by the owning workflow.

## Repository preflight

```bash
git -C <repo-path> symbolic-ref --quiet --short HEAD
git -C <repo-path> rev-parse HEAD
git -C <repo-path> status --porcelain=v1 --branch --untracked-files=all
git -C <repo-path> submodule status --recursive
```

The first command prints the attached branch and exits nonzero for detached
HEAD. Record the second command's exact value. Status exits 0 when Git runs it
successfully, not only when the tree is clean. With `--branch`, a clean
attached repository has a branch header followed by no path records; any
additional record is a change. `--untracked-files=all` makes all untracked
files visible even when `status.showUntrackedFiles=no` is configured. A
nonzero status exit is a command failure, not evidence of cleanliness. Inspect
the index and worktree columns for staged/unstaged changes and `??` for
untracked paths. During this initial preflight, submodule output must show
expected commits with no leading `+`, `-`, or `U`: `+` means the checked-out
submodule differs, `-` means it is not initialized, and `U` means a conflict.
If any branch, HEAD, working tree, or submodule state is unexpected, stop
without changing state and report it. Do not stash, reset, overwrite, rename,
or delete anything to conceal the condition.

## Task branch creation and reuse

```bash
git -C <repo-path> show-ref --verify --quiet refs/heads/<original-branch>
git -C <repo-path> rev-parse --verify refs/heads/<original-branch>^{commit}
git -C <repo-path> show-ref --verify --quiet refs/heads/<task-branch>
```

`show-ref --verify --quiet` exits 0 when the exact ref exists, 1 when absent,
and another nonzero status for an error. The original branch must exist and
its resolved OID must equal the recorded `<base-head>` where required.

If the task-ref command exits 1, create it from the recorded base without
altering the original branch:

```bash
git -C <repo-path> switch --create <task-branch> <base-head>
```

If it exits 0, resolve and compare its existing OID before switching:

```bash
git -C <repo-path> rev-parse --verify refs/heads/<task-branch>^{commit}
git -C <repo-path> switch <task-branch>
```

The resolved OID must equal `<expected-task-head>`; only then may `switch` run.
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
git -C <repo-path> diff --quiet --
```

The staged names must exactly equal the allowlist. Produce and compare the
newline-delimited lists deterministically:

```bash
git -C <repo-path> diff --cached --name-only | LC_ALL=C sort > <actual-allowlist>
cmp --silent <actual-allowlist> <recorded-allowlist>
```

Both files must contain one path per line in bytewise sorted order. `cmp`
exit 0 means byte-for-byte equality, 1 means mismatch (stop), and another
nonzero status means comparison failure (stop). No path may be added outside
the allowlist.
Review the staged diff. `diff --cached --check` exits 0 when no whitespace
errors are found and nonzero when errors are found. `git diff --quiet --`
checks unstaged tracked changes: 0 means none, 1 means changes exist (stop),
and another nonzero status means the check failed (stop). Untracked paths
remain visible in status and must not be added unless allowed.

Compute the candidate fingerprint, freeze it, and run required verification
without editing tracked files:

```bash
git -C <repo-path> diff --cached --binary --full-index \
  | git hash-object --stdin
<required-verification-command>
git -C <repo-path> diff --quiet --
git -C <repo-path> diff --cached --binary --full-index \
  | git hash-object --stdin
```

Verification must exit 0. After it completes, the repeated unstaged-tracked
check must also exit 0, and the two fingerprint values must match exactly.
Otherwise fix, restage the explicit allowlist, and repeat the entire procedure.
Do not commit a candidate whose allowlist, unstaged check, verification, or
fingerprints fail. Then commit:

```bash
git -C <repo-path> commit -m "<type>: <description>"
git -C <repo-path> status --porcelain=v1 --untracked-files=all
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

A leading `+` is allowed only as the deliberate intermediate state for the
exact verified child commit (confirm the checked-out child OID with
`git -C <submodule-path> rev-parse HEAD`) while its parent pointer awaits
staging. Any other `+`, or any `-` or `U`, is a failure. A pointer without an
authorized, verified submodule commit is also a failure.

## Integration and cleanup

```bash
git -C <repo-path> switch <original-branch>
git -C <repo-path> status --porcelain=v1 --branch --untracked-files=all
git -C <repo-path> rev-parse --verify refs/heads/<original-branch>^{commit}
git -C <repo-path> rev-parse --verify refs/heads/<task-branch>^{commit}
git -C <repo-path> merge-base --is-ancestor <base-head> <task-branch>
<exact-authorized-merge-command>
git -C <repo-path> status --porcelain=v1 --branch --untracked-files=all
```

The full repository preflight above must be clean before the exact
workflow-supplied authorized merge command is executed. The ancestry check
exits 0 when the base is an ancestor and nonzero otherwise; resolve divergence
before authorization. Execute the authorized command verbatim and keep its
merge strategy external: `--ff-only` and `--no-ff` are examples with distinct
semantics, not defaults. Integrate modified submodules into their recorded
original branches first, then the parent task branch. Verify each result with
the post-merge status and `git log --oneline -n 3`.

After all integrations succeed, confirm ancestry and clean task branches from
submodules before the parent:

```bash
git -C <repo-path> merge-base --is-ancestor <task-branch> <original-branch>
git -C <repo-path> branch --delete <task-branch>
```

`branch --delete` safely refuses to delete an unmerged branch. Never use
cleanup to hide unexpected state.
