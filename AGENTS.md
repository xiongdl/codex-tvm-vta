# Project Instructions

## Reuse Existing Repository Automation First

Before creating a script, test program, debugging helper, or temporary file:

1. **Search existing automation first.** Start with `rg --files scripts`. When
   relevant, also check build files, CI configuration, and project
   documentation.
2. **Read before using or modifying.** Understand the relevant script's purpose,
   interface, side effects, and usage first.
3. **Prefer reuse when the responsibilities align.** Invoke an existing script,
   or minimally extend it when the new behavior fits its established purpose.
4. **Add reusable automation to `scripts/`.** When new automation is genuinely
   needed and likely to be useful again, add a focused, documented script under
   `scripts/`.
5. **Avoid files for one-off work.** Prefer inline commands that leave no
   repository artifacts. Use a temporary file only when it is materially
   clearer or safer, and remove it afterward when safe.

Preserve existing script interfaces and behavior whenever practical. If a
change is necessary, minimize compatibility impact and update its usage
documentation.

Do not force an unrelated script to accommodate new behavior merely to avoid
adding a well-scoped script.

## Addy Skills Delegation

For implementation work that meets the `When to Use` criteria of the applicable
Addy specification or planning skills, follow this project-specific delegation
lifecycle:

`Define → Plan → Build → Verify → Review → Ship`

The root agent owns Define and Plan. It must use the applicable Addy definition
skills followed by `planning-and-task-breakdown`. Requirements, scope,
decisions, acceptance criteria, verification steps, dependencies, and open
questions must be recorded in the artifacts required by those skills.

Complete every required planning and human-approval checkpoint before starting
implementation.

After Plan is complete and approved, delegate execution to one fresh subagent
with `fork_turns: "none"`. The delegation message must identify the exact plan
and task-list artifacts. The subagent must treat those artifacts and the
repository instructions as the source of truth.

The subagent owns Build, Verify, Review, and Ship. It must continuously execute
all remaining planned tasks with the applicable Addy skills and must not return
merely because one task or lifecycle phase has finished.

Lifecycle phase names do not grant additional authority. The subagent may
commit, push, create pull requests, release, deploy, or perform other external
or irreversible actions only when authorized by the user and permitted by the
current environment.

The subagent must comply with all repository rules, preserve unrelated
working-tree changes, and follow the operation permissions defined under
`.codex/rules`.

Return to the root agent only when:

- execution and verification are complete;
- a new requirement, scope, architecture, interface, release, or other
  product-level decision is required; or
- user authorization, unavailable external state, or another blocker prevents
  safe progress.

The root agent must not duplicate delegated implementation work. It may inspect
the resulting diff and verification evidence, resolve product-level questions,
and report the final outcome.