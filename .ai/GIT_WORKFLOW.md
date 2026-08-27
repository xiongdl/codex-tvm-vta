# Git Workflow

## Branch Model

Every repository defines one `Default Base Branch`. The template default is `main`; an instantiated project may configure another project-defined long-lived branch.

Each `CHANGE` Task resolves exactly one `Base Branch` for its complete lifecycle:

1. use the explicit Task Contract `Base Branch`, when provided;
2. otherwise use the repository `Default Base Branch`.

The Base Branch is the logical branch identity. The Base Commit is the exact commit of that branch used for a specific review or integration state. A Task's Base Branch is immutable: it is both the source from which the Task Branch is created and the final merge target.

Every `CHANGE` Task uses exactly one short-lived Task Branch:

The branch namespace is `task/*`.

```text
Base Branch
└── task/<task-id>-<short-name>
```

Do not branch from another Task Branch. Do not impose a framework-wide `main`, `dev`, `develop`, `feature/*`, `bugfix/*`, or `hotfix/*` taxonomy. `READ_ONLY` tasks need no branch.

```text
Task Branch creation source == final merge target == Base Branch
```

## Committed Review Target

Formal review requires a committed Review Target.

Multiple coherent task commits are allowed. Before Review Attempt 1, local history may be cleaned up. After it begins, reviewed history should not normally be rewritten and review fixes should be appended. Rebasing onto the updated Base Branch is allowed but invalidates prior approval.

Before Independent Review, Codex A must implement, verify, commit, and identify Base Commit and Review Commit. The Review Commit must be task branch `HEAD`. Review covers the complete `Base Commit..Review Commit` Task change set and repository at Review Commit, not only the final commit.

After `CHANGES_REQUESTED`, a new Review Commit is required only when Finding resolution changes tracked repository state. Repository changes must be verified and committed, and the new task-branch `HEAD` becomes the next Review Commit. If resolution is solely through Task Contract revision, Design Owner decision, required external input, or requirement clarification and tracked state is unchanged, do not create an artificial or empty commit; the next Review Attempt may use the same Review Commit.

## Integration Gate

Codex A integrates locally only when Independent Review is `APPROVED`, task `HEAD` equals Approved Commit, the tracked working tree is clean, the Task Branch is based on the current Base Branch, and required verification passes.

Integration must use:

```bash
git merge --ff-only
```

Do not squash reviewed commits by default. The target is:

```text
Reviewed Commit == Approved Commit == Integrated Commit
```

If the Base Branch advances, rebase the Task Branch onto the current Base Branch, re-verify, identify new Base and Review Commits, obtain a new Independent Review, and retry. Base Branch advancement alone is not `BLOCKED`.

## Permissions

A `CHANGE` Task Contract authorizes normal local task lifecycle operations: Git inspection, Task Branch creation from the resolved Base Branch, explicit-path staging, local commits, local rebase onto that Base Branch, ff-only integration back into that same Base Branch after the gate, and normal deletion of a merged local Task Branch. Codex A MUST NOT absorb unrelated pre-existing changes.

Remote push or branch writes, force push, release or Git tag publication, destructive cleanup, forced branch deletion, and shared-history rewriting require explicit authority or persistent project policy.
