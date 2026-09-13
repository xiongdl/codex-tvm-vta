# Automation

This shared policy governs when to reuse, extend, or create automation. It is
project-agnostic: project commands, dependencies, and environments belong in
`scripts/README.md`.

## Decision Order

Keep a simple one-step system command inline. Prefer maintained automation
when an operation is repeated, multi-step, error-prone, project-specific, or
must produce consistent evidence.

Before creating or changing automation, search the repository's existing
scripts, task runners, CI workflows, and documentation. Read each relevant
candidate well enough to understand its responsibility, interface, side
effects, callers, and usage. Then decide in this order:

1. Reuse existing automation when it already satisfies the need.
2. Extend an existing entry point when its responsibility matches and its
   interface and compatibility can be preserved.
3. Create new focused automation only when the responsibility is distinct or
   extension would reduce clarity, compatibility, or testability.

Reusable project automation lives under `scripts/`. Keep one-off commands
inline unless a temporary helper is materially clearer or safer.

## Change Safety

Preserve existing interfaces and behavior unless approved work requires a
change. When compatibility cannot be preserved, minimize the impact and
update affected callers, tests, and documentation. Do not add unrelated
behavior to an existing automation entry point.

Read the project rules before editing automation. Keep generated artifacts,
credentials, and local environment files out of version control unless the
project explicitly requires them. Do not silently change a command's default
environment, dependency set, output location, or cleanup behavior.

## Temporary Work

Use a temporary script or data file only when it is clearer or safer than an
inline command. Give it the narrowest scope possible, keep it outside the
repository when practical, and remove it after use. If a temporary helper
proves generally useful, promote it to a focused maintained script under
`scripts/` with documented inputs, options, outputs, dependencies, and side
effects.

## Project Documentation

`scripts/README.md` is the project-specific source of truth for supported
commands, automation entry points, dependencies, environment setup, and
platform constraints. Read it before selecting a command or environment, and
update it when an automation interface or reproducible workflow changes.
