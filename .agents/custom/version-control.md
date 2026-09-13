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

Use this executable gate before any operation that changes checkout state. It
compares the attached branch and canonical commit OID, treats any porcelain
record (including untracked paths) as dirty, and validates every recursive
submodule record. All failures return nonzero without changing the repository.

```bash
vc_preflight() {
  test "$#" -eq 3 || return 1
  local repo_path="$1"
  local expected_branch="$2"
  local expected_commit="$3"

  local actual_branch
  actual_branch="$(git -C "$repo_path" symbolic-ref --quiet --short HEAD)" || return 1
  test "$actual_branch" = "$expected_branch" || return 1

  local actual_head_oid expected_head_oid
  actual_head_oid="$(git -C "$repo_path" rev-parse --verify 'HEAD^{commit}')" || return 1
  expected_head_oid="$(git -C "$repo_path" rev-parse --verify "${expected_commit}^{commit}")" || return 1
  test "$actual_head_oid" = "$expected_head_oid" || return 1

  local status_output
  status_output="$(git -C "$repo_path" status --porcelain=v1 --untracked-files=all)" || return 1
  test -z "$status_output" || return 1

  local submodule_output submodule_record
  submodule_output="$(git -C "$repo_path" submodule status --recursive)" || return 1
  while IFS= read -r submodule_record; do
    case "$submodule_record" in
      [+\-U]*) return 1 ;;
    esac
  done <<< "$submodule_output"
}
```

Call it with the repository path, expected attached branch, and expected
commit/ref. A successful return is the only condition that permits the next
operation:

```bash
vc_preflight <repo-path> <expected-branch> <expected-commit-or-ref> || exit 1
```

The gate intentionally does not use `git status`'s exit code as a cleanliness
signal: Git returns zero for a successfully inspected dirty tree.

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
original_branch_ref="refs/heads/<original-branch>"
task_branch_ref="refs/heads/<task-branch>"
recorded_base_oid="<recorded-base-head>"

if git -C <repo-path> show-ref --verify --quiet "$original_branch_ref"; then
  actual_original_oid="$(git -C <repo-path> rev-parse --verify "${original_branch_ref}^{commit}")" || exit 1
  canonical_base_oid="$(git -C <repo-path> rev-parse --verify "${recorded_base_oid}^{commit}")" || exit 1
  test "$actual_original_oid" = "$canonical_base_oid" || exit 1
else
  original_ref_status=$?
  test "$original_ref_status" -eq 1 && exit 1
  exit "$original_ref_status"
fi

if git -C <repo-path> show-ref --verify --quiet "$task_branch_ref"; then
  expected_task_head="<expected-task-head>"
  actual_task_oid="$(git -C <repo-path> rev-parse --verify "${task_branch_ref}^{commit}")" || exit 1
  canonical_task_oid="$(git -C <repo-path> rev-parse --verify "${expected_task_head}^{commit}")" || exit 1
  test "$actual_task_oid" = "$canonical_task_oid" || exit 1
  git -C <repo-path> switch <task-branch>
else
  task_ref_status=$?
  if test "$task_ref_status" -eq 1; then
    git -C <repo-path> switch --create <task-branch> "$canonical_base_oid" || exit 1
  else
    exit "$task_ref_status"
  fi
fi
```

`show-ref --verify --quiet` exits 0 when the exact ref exists, 1 when absent,
and another nonzero status for an error. The original branch must exist and
its resolved OID must equal the recorded `<base-head>` where required.

The original branch must exist and its resolved OID must equal the recorded
base OID before either task-branch path proceeds. A missing task ref is valid
only for first creation from that canonical base OID. An existing task ref is
valid only when its canonical OID exactly equals the supplied
`<expected-task-head>`, checked before `switch`. Any other ref status or OID is
a stop condition. Do not force-create, reset, rename, or delete branches. Do
not work on
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
# Resolve workflow inputs before either enforcing gate.
expected_original_oid="<workflow-supplied-expected-original-oid>"
reviewed_task_oid="<workflow-supplied-reviewed-task-oid>"
# The task checkout must pass before switching; a failed gate stops here.
vc_preflight <repo-path> <task-branch> "$reviewed_task_oid" || exit 1
git -C <repo-path> switch <original-branch> || exit 1
# The original checkout must pass again; do not compare OIDs or merge first.
vc_preflight <repo-path> <original-branch> "$expected_original_oid" || exit 1
actual_original_oid="$(git -C <repo-path> rev-parse --verify refs/heads/<original-branch>^{commit})" || exit 1
actual_task_oid="$(git -C <repo-path> rev-parse --verify refs/heads/<task-branch>^{commit})" || exit 1
git -C <repo-path> rev-parse --verify "${expected_original_oid}^{commit}" >/dev/null || exit 1
git -C <repo-path> rev-parse --verify "${reviewed_task_oid}^{commit}" >/dev/null || exit 1
test "$actual_original_oid" = "$expected_original_oid" || exit 1
test "$actual_task_oid" = "$reviewed_task_oid" || exit 1
git -C <repo-path> merge-base --is-ancestor <base-head> <task-branch>
<exact-authorized-merge-command>
git -C <repo-path> status --porcelain=v1 --branch --untracked-files=all
```

The full repository preflight must be clean both before switching and after
switching. The first preflight protects the current checkout: if its branch,
HEAD, tracked or untracked paths, or submodule state is unexpected, stop
without switching and report the state. The second preflight protects the
original branch: if switching fails, or if any post-switch preflight command
reports unexpected state, stop without comparing OIDs or merging and report
the state. In particular, do not let staged, unstaged, untracked, or submodule
changes ride across the branch switch. The workflow must
supply the exact OID of the reviewed task tip and the expected OID of the
original branch (normally the recorded `<base-head>`); do not use a newly
resolved tip as an implicit expectation. Resolve both branch refs to full OIDs,
resolve the supplied OIDs as commits, and compare the values exactly before
merging. `rev-parse --verify` exits nonzero when a supplied value or ref cannot
be resolved; either that failure or either `test` mismatch is a stop-without-
merge condition that must be documented. The ancestry check remains an
additional invariant: it exits 0 when the base is an ancestor and nonzero
otherwise; resolve divergence before authorization. Execute the authorized
command verbatim and keep its merge strategy external: `--ff-only` and
`--no-ff` are examples with distinct semantics, not defaults. Integrate
modified submodules into their recorded original branches first, then the
parent task branch. Verify each result with the post-merge status and
`git log --oneline -n 3`.

After all integrations succeed, confirm ancestry and clean task branches from
submodules before the parent:

```bash
git -C <repo-path> merge-base --is-ancestor <task-branch> <original-branch>
git -C <repo-path> branch --delete <task-branch>
```

`branch --delete` safely refuses to delete an unmerged branch. Never use
cleanup to hide unexpected state.
