# Version Control

Apply the selected Addy Git workflow plus these project safeguards. The owning
workflow supplies scope and authorization; this file supplies Git mechanics.

## Required inputs

Before any repository mutation, record for the parent repository and every
repository in scope:

- repository path;
- task branch: `codex/<kebab-case-task>`;
- original branch and exact base commit;
- expected task-branch commit when reusing a branch;
- exact staged-path allowlist;
- required verification commands.

Before Ship, also record the exact authorized merge command. Missing input for
the current operation is a stop condition. Do not infer merge strategy or
permission.

## Preflight

Before changing checkout state, run for each repository:

```bash
git -C <repo> symbolic-ref --quiet --short HEAD
git -C <repo> rev-parse --verify 'HEAD^{commit}'
git -C <repo> status --porcelain=v1 --untracked-files=all
git -C <repo> submodule status --recursive
```

Continue only when all commands succeed, the attached branch and commit equal
the recorded values, status output is empty, and no submodule line starts with
`+`, `-`, or `U`. A zero exit from `git status` does not mean the tree is
clean; its output must be empty.

On failure, stop without changing state. Do not stash, reset, overwrite,
rename, delete, or commit unexpected work.

## Task branch

Before creating or reusing the task branch:

1. Resolve the original branch and recorded base to canonical commit IDs.
2. Require the IDs to match and rerun preflight on the original branch.
3. If the task branch is absent, create it from the recorded base.
4. If it exists, require its commit to equal the recorded expected task commit
   before switching to it.

Do not force-create, reset, rename, or delete a branch to pass these checks. Do
not work on the original branch. Use the same task-branch name in each modified
submodule after that repository passes its own preflight.

## Candidate commit

Stage only the allowlisted paths:

```bash
git -C <repo> add -- <allowlisted-path>...
git -C <repo> diff --cached --name-only
git -C <repo> diff --cached --check
git -C <repo> diff --quiet --
```

Require the sorted staged path list to equal the sorted allowlist exactly.
`git diff --quiet --` must return `0`; any unstaged tracked change stops the
candidate. Do not stage an untracked path unless it is allowlisted.

Freeze the staged candidate before verification:

```bash
candidate_before="$({
  set -o pipefail
  git -C <repo> diff --cached --binary --full-index |
    git hash-object --stdin
})" || exit 1
```

Run the required verification without editing tracked files or the index. Then
repeat all of the following:

- unstaged tracked change check;
- exact staged-path comparison;
- staged candidate fingerprint.

Store the second fingerprint as `candidate_after` with the same command and
require `test "$candidate_before" = "$candidate_after"`. Commit only when
verification succeeds and the fingerprints match. If any check fails, fix the
issue, restage the explicit allowlist, and repeat the full candidate procedure.
After committing, require empty porcelain status.

## Submodules

Commit verified submodule content before staging its parent gitlink. Before
staging the gitlink, require all of the following:

- the child checkout HEAD equals the verified child commit;
- recursive submodule status contains exactly one `+` record for that child
  path and commit;
- no other record starts with `+`, `-`, or `U`.

Then stage only the allowlisted gitlink and inspect its submodule diff. A parent
pointer without an authorized verified child commit is a stop condition.

## Integration and cleanup

Ship is Root-only and requires the workflow's exact authorized merge command.
For each repository:

1. Resolve the reviewed task commit and expected original-branch commit.
2. Preflight the task branch at the reviewed commit.
3. Switch to the original branch.
4. Preflight the original branch at the expected commit.
5. Require both branch refs to equal the supplied commits.
6. Require the original commit to be an ancestor of the task commit.
7. Run the authorized merge command verbatim.
8. Require clean status and inspect the latest commits.

Integrate modified submodules before the parent repository. Stop on any failed
command or mismatch.

Delete a task branch only after clean preflight and after confirming its tip is
an ancestor of the current original-branch tip. Use `git branch --delete`; do
not force-delete a branch.
