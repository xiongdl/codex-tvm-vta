# Version Control

## Git and Submodules

The task branch name is fixed as `codex/<kebab-case-work-name>`.

During the first preflight, the Default records the original branch and HEAD
for the parent repository and every repository in scope. The original branch is
the task branch's base and final merge target.

After confirming the repository is clean, the first Default creates the
ordinary task branch. Subsequent fresh Defaults reuse the same task branch for
later checkpoints and fixes. Defaults must not implement changes directly on
the original branch.

Every modified submodule uses the same task branch name as the parent
repository. The Default creates or reuses each submodule task branch only after
confirming its original branch, expected base HEAD, and clean working state.

If a repository is in detached HEAD state, its original branch cannot be
resolved, or the task branch already exists at an unexpected state, the Default
stops and escalates to the Root. It must not reset, overwrite, rename, or delete
the branch.

Commit verified submodule changes before committing the parent repository's
submodule pointer.

When merging task branches, the Root first merges each modified submodule task
branch into its recorded original branch, then merges the parent repository's
task branch into its recorded original branch.

After all corresponding merges succeed, the Root deletes the task branches
from modified submodules first and the parent repository last.
