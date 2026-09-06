# Project Instructions

## Reuse Repository Scripts First

Before creating a script, test program, debugging helper, or temporary file for one-off commands:

1. **Search `scripts/` first.** Start with `rg --files scripts`, and search script contents when useful.
2. **Read before using or modifying.** Understand the relevant script and its usage first.
3. **Prefer reuse over duplication.** Invoke or minimally extend an existing script instead of duplicating its behavior.
4. **Add reusable automation to `scripts/`.** When new automation is genuinely needed and likely to be useful again, add a focused, documented script under `scripts/`.
5. **Avoid temporary scripts for one-off work.** Prefer inline shell commands that leave no files behind. Use a temporary script only when it is materially clearer or safer, and remove it afterward when safe.

Preserve existing script interfaces and behavior unless the task explicitly requires changing them.

Do not force an unrelated script to fit merely to avoid adding a well-scoped new one.
