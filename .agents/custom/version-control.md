# Version Control

All Git mutations in the parent repository and managed submodules must run from
the parent repository root through:

```bash
./.agents/custom/scripts/git-workflow <subcommand> ...
```

Direct `git` commands are read-only only, such as `status`, `diff`, `log`,
`show`, `rev-parse`, `symbolic-ref`, `submodule status`, and `ls-files`.

## Do this

1. Before starting a task, Root may run `pull` only with explicit authorization.
   Never pull after the task branch is created.
2. Root runs `status`. Stop unless the parent repository and all managed
   submodules are clean and on the expected commits and branches.
3. After the user approves the branch and repository changes, Root runs:

   ```bash
   ./.agents/custom/scripts/git-workflow create <task>
   ```

4. Default implements the delegated checkpoint, runs Test and Verify, then
   makes no further content change and runs:

   ```bash
   ./.agents/custom/scripts/git-workflow commit -m "<message>"
   ```

   This commits all Git-visible task changes, including managed-submodule
   gitlinks, and returns the commit OIDs. Root uses the same command only for
   verified policy or lifecycle artifacts.
5. Hand off the exact commit OID. Reviewer reviews that commit read-only; never
   hand off working-tree, index, or patch state.
6. After required Review/Re-review passes, Root obtains explicit Ship
   authorization for each required command:
   - `push` publishes the managed repositories.
   - `merge <task>` fast-forwards into the recorded original branches.
   - `delete <task>` restores the original branches and force-deletes the task
     branches. It can abandon unmerged commits.

If `commit` fails, fix the reported cause and run it again. The workflow keeps
working-tree content, clears only the index entries it staged, and keeps any
child-submodule commit already created.

Do not use direct Git mutations, reset, stash, clean, or overwrite to bypass a
workflow check.

## Maintenance

`.codex/rules/default.rules` blocks direct Git mutations and prompts for remote,
integration, and deletion operations. Restart Codex after changing that file.

The workflow requires host Git, Bash, and standard-library-only `python3`.
Run its isolated regression suite with:

```bash
bash .agents/custom/scripts/test-git-workflow
```
