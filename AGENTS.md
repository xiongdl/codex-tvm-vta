# Agent Role Router

Determine the assigned role from the task context, then load and apply only
that role's file:

- Root: `.agents/custom/root.md`
- Default: `.agents/custom/default.md`
- Reviewer: `.agents/custom/reviewer.md`

Do not read or apply any other role file. An unknown role must fail closed and
escalate to Root.
