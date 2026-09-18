# Version Control

Run every Git mutation from the repository root through:

```bash
./.agents/custom/scripts/git-workflow <subcommand> ...
```

The applicable policy defines who may run each command and what approval is
required. Direct `git` commands are read-only only, such as `status`, `diff`,
`log`, `show`, `rev-parse`, `symbolic-ref`, `submodule status`, and `ls-files`.

## Workflow

1. Run `status`. Stop unless every managed repository is clean and on the
   expected branch and commit.
2. Run `pull` only with explicit authorization and only before creating the task
   branch.
3. After task-branch and change approval, run:

   ```bash
   ./.agents/custom/scripts/git-workflow create <task>
   ```

4. Make the scoped changes, complete the required Test and Verify work, then
   make no further content change and run:

   ```bash
   ./.agents/custom/scripts/git-workflow commit -m "<message>"
   ```

   This commits all Git-visible task changes and returns the commit OIDs.
5. Use an exact commit OID for every handoff. Never hand off working-tree,
   index, or patch state.
6. Run `push`, `merge <task>`, or `delete <task>` only with their required
   explicit authorization. `merge` is fast-forward-only. `delete` restores the
   recorded branches and force-deletes the task branches, so it may abandon
   unmerged commits.

If `commit` fails, fix the reported cause and retry. The workflow preserves
working-tree content, clears only the index entries it staged, and keeps any
managed child commit already created.

Do not use direct Git mutations, reset, stash, clean, or overwrite to bypass a
workflow check.

Run the isolated regression suite with:

```bash
bash .agents/custom/scripts/test-git-workflow
```
