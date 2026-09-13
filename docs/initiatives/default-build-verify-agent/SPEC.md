# Spec: Default Build and Verify Agent

## Objective

Replace the dedicated Builder and Verifier custom agents with one project-scoped
Default agent. Default performs Build, Fix, Verify, and Re-verify while preserving
the existing lifecycle, RED -> GREEN evidence, review loop, Git safeguards, and
explicitly authorized Ship execution.

Success means the role consolidation is complete without adopting the proposed
`.agents/custom/` policy split or changing any unrelated policy.

## Tech Stack

- `AGENTS.md` for project-wide lifecycle orchestration.
- Project-scoped Codex custom agents under `.codex/agents/`.
- TOML custom-agent configuration.
- Addy agent-skills vendored under `.agents/vendor/agent-skills/`.

## Commands

- Parse custom-agent TOML with Python 3.11 or newer:
  `python3 -c 'import pathlib, tomllib; [tomllib.loads(p.read_text()) for p in pathlib.Path(".codex/agents").glob("*.toml")]'`
- Validate Markdown and TOML whitespace: `git diff --check`
- Inspect scoped changes: `git status --short`
- Inspect staged paths: `git diff --cached --name-only`
- Fingerprint a staged candidate:
  `git diff --cached --binary --full-index | git hash-object --stdin`

## Project Structure

- `AGENTS.md` — replace Builder/Verifier routing with Default routing while
  leaving Root, Reviewer, Ship, Git, and automation behavior unchanged.
- `.codex/agents/default.toml` — Default model, reasoning, sandbox, combined
  execution responsibility, and stop rules.
- `.codex/agents/reviewer.toml` — unchanged.
- `.codex/agents/builder.toml` — removed.
- `.codex/agents/verifier.toml` — removed.
- `.codex/config.toml` and `.codex/rules/` — unchanged.

## Code Style

- Keep role-specific model settings in TOML, not `AGENTS.md`.
- Keep the Default instructions concise, imperative, and explicit about tracked
  file mutation during verification.
- Preserve unrelated wording in `AGENTS.md` whenever practical.

## Testing Strategy

- Prove the pre-change state has Builder and Verifier definitions and no Default
  definition.
- Parse every remaining `.codex/agents/*.toml` file.
- Confirm Default uses `gpt-5.6-luna`, `high`, and `workspace-write`.
- Confirm Builder and Verifier definitions are absent and Reviewer is unchanged.
- Review the final diff for lifecycle equivalence outside role consolidation.
- Run `git diff --check` before commit.

## Boundaries

### Always

- Use one Default agent for Build/Fix and Verify/Re-verify work delegated by Root.
- Preserve RED -> GREEN, candidate fingerprinting, regression verification,
  verified commits, fresh Reviewer routing, and the review/fix loop.
- Keep Default as the executor of explicitly authorized Ship actions.
- Use `gpt-5.6-luna` with high reasoning and `workspace-write`.

### Ask First

- Any change to Root, Reviewer, Ship authorization, Git/submodule policy,
  automation policy, lifecycle gates, or approved scope.
- Any Ship action.

### Never

- Introduce `.agents/custom/` files in this task.
- Modify `.codex/config.toml`, `.codex/rules/`, submodules, or unrelated files.
- Stage the user-approved untracked exceptions.
- Let Default trigger agents, advance the lifecycle, or broaden its delegation.

## Success Criteria

1. `.codex/agents/default.toml` defines the combined Default role using
   `gpt-5.6-luna` with high reasoning and `workspace-write`.
2. `.codex/agents/builder.toml` and `.codex/agents/verifier.toml` are removed.
3. `AGENTS.md` routes Build, Fix, Verify, Re-verify, verified commit, and
   authorized Ship execution through Default while Root remains orchestrator.
4. All non-role lifecycle behavior remains unchanged.
5. Reviewer configuration and project-wide Codex configuration remain unchanged.
6. The exact candidate passes TOML parsing, policy assertions, whitespace checks,
   and independent Review.

## Open Questions

None. The user confirmed the intent and excluded `.agents/custom/` from scope.
