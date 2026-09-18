# Version Control

Run every Git mutation from the repository root through:

```bash
./.agents/custom/scripts/git-workflow <command> ...
```

The applicable role policy defines authorization and ownership. Direct `git`
commands are read-only only. Every handoff uses an exact commit OID, never
working-tree, index, or patch state.

The fixed lifecycle uses `status`, `create`, and `commit`. It completes when
Reviewer returns `Pass`. Ship is an optional, user-owned post-review step that
contains exactly `merge <task>`; Root, Default, and Reviewer must not execute
it. `pull`, `push`, and `delete` remain administrative script capabilities,
not lifecycle or Ship operations, and require a separate explicit user
request.

## Commands

- `status`
  - Use before a mutating command or whenever repository state is uncertain.
  - Read-only. Succeeds only when all discovered repositories and gitlinks are
    clean and consistent, then prints their paths, branches, and commit OIDs.

- `pull`
  - Use only with explicit authorization, on clean managed repositories with
    configured upstreams, and before creating a task branch.
  - Pulls each managed repository with `--ff-only --prune`.

- `create <task>`
  - Use after task-branch and change approval, from clean managed repositories.
    The derived `codex/<task>` branch and task-begin snapshot must not exist.
  - Records each current branch and commit, then creates the same task branch in
    every managed repository.

- `commit -m <message>`
  - Use on the common task branch after required Test and Verify work succeeds,
    with empty indexes and no later content changes.
  - Stages all Git-visible task changes, checks the staged diff, commits managed
    repositories deepest first, requires a clean result, and prints commit OIDs.
    If it fails, fix the reported cause and retry; working-tree content and any
    child commit already created are preserved.

- `push`
  - Use only with explicit authorization and clean managed repositories.
  - Pushes each managed branch to its upstream, or sets `origin/<branch>` as the
    upstream when none exists.

- `merge <task>`
  - Recommended for the user after Reviewer `Pass`. Agents do not run it.
    Requires all managed repositories to be clean and on the task branch, the
    original branches not to have moved, and every update to be
    fast-forwardable.
  - Fast-forwards the recorded original branches to the task commits, deepest
    repository first, then leaves the repository set clean on the original
    branches.

- `delete <task>`
  - Use only with explicit authorization, a task-begin snapshot, existing
    original branches, and clean managed repositories.
  - Restores the original branches and force-deletes the task branches. It can
    delete an unmerged task and abandon its commits.

Do not use direct Git mutations, reset, stash, clean, or overwrite to bypass a
workflow check.

Run the isolated regression suite with:

```bash
bash .agents/custom/scripts/test-git-workflow
```

Validate the fixed role workflow contract with:

```bash
bash .agents/custom/scripts/test-role-workflow
```
