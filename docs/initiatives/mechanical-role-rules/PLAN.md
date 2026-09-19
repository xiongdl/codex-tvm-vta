# Plan: Mechanical Role Rules

## Ordered implementation

1. Replace Root's implicit interpretation points with an explicit clear-vs-
   blocked decision table and move task-branch creation to immediately after
   Interview completion.
2. Add direct command sequences and no-replanning rules to Default.
3. Add read-only command and verdict rules to Reviewer.
4. Run the role contract test, Git workflow regression test, final status, and
   a text audit.

## Risk controls

- Preserve all existing required skill references and lifecycle handoffs so the
  contract test continues to protect the workflow.
- Keep Git mutations behind `.agents/custom/scripts/git-workflow`.
- Do not touch TVM or VTA content.

## Checkpoint

The change is complete only when all verification commands pass and the
working tree is clean after the commit.
