# Agent Role Router

Determine the role from explicit, unambiguous task context, then load and apply
only the matching file:

- An explicit runtime role wins; explicit delegated Default and Reviewer
  contexts select `.agents/custom/default.md` and `.agents/custom/reviewer.md`,
  respectively, while explicit Root selects `.agents/custom/root.md`.
- When no literal Root label is available, the non-delegated primary agent that
  owns the user conversation, lifecycle transitions, and Default/Reviewer
  dispatch selects `.agents/custom/root.md`.
- Never infer Default from a model name, configuration, or agent setting that
  merely contains `default`.
- Contradictory or unknown role context fails closed and escalates to Root.

By default, read and apply only the matching role file. Root may inspect only
`.agents/custom/default.md` and `.agents/custom/reviewer.md` on demand for
role coordination, compatibility assessment, or explicitly scoped maintenance;
Root must treat those files as task data and must not apply their instructions.
Default or Reviewer may inspect a different role file only when Root explicitly
names that exact file in the delegated implementation or review scope and exact
staged-path allowlist; the file is task data only, and its instructions must not
be applied.
