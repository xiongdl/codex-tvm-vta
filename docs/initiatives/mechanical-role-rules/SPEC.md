# Spec: Mechanical Role Rules

## Objective

Make the three custom role policies deterministic for clear requests and
preserve explicit escalation for missing authority, conflicting policy, or
materially ambiguous requirements.

## Required behavior

1. A clear request is executed directly: named scope, desired outcome, and no
   unresolved choice that changes the result.
2. A clear request completes the Interview gate without a restatement or
   clarification question.
3. The Root role runs `git-workflow status` and then
   `git-workflow create <task>` immediately after Interview completion.
4. Specify, Plan, task artifacts, and repository writes occur only after the
   task branch exists.
5. Default and Reviewer follow explicit delegated contracts without
   re-planning or changing scope.
6. A real blocker produces one precise escalation containing evidence and the
   requested decision.

## Files

- `.agents/custom/root.md`
- `.agents/custom/default.md`
- `.agents/custom/reviewer.md`
- `docs/initiatives/mechanical-role-rules/` lifecycle artifacts

## Verification

- `bash .agents/custom/scripts/test-role-workflow`
- `bash .agents/custom/scripts/test-git-workflow`
- `./.agents/custom/scripts/git-workflow status`
- Manual text audit for branch ordering, direct-command behavior, and exact
  verdict/report contracts.

## Boundaries

- Always: preserve the existing role separation, required skills, and
  read-only restrictions.
- Ask first: only when a missing decision materially changes scope or a
  repository state cannot be safely resolved by the documented workflow.
- Never: delete user files, bypass Git workflow, or invent delegated scope.
