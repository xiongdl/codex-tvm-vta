# Spec: Agent Lifecycle Orchestration

## Objective

Define a project-level Codex workflow that keeps user intent, lifecycle routing,
agent responsibilities, verification evidence, Git state, and Ship authority
aligned. The workflow must reduce strong-model usage without weakening Addy
Skills gates: root controls the lifecycle, a strong Builder writes production
and verification code, a low-cost Verifier executes verification independently,
and a fresh Reviewer evaluates completed implementation changes.

## Tech Stack

- `AGENTS.md` for project-wide orchestration and Git policy.
- Project-scoped Codex custom agents under `.codex/agents/`.
- TOML for custom-agent configuration.
- Addy agent-skills vendored under `.agents/vendor/agent-skills/`.
- Git branches, the index, staged-diff fingerprints, and commits for state
  isolation and verified handoff.

## Commands

- Validate Markdown whitespace: `git diff --check`
- Parse custom-agent TOML:
  `python3 -c 'import pathlib, tomllib; [tomllib.loads(p.read_text()) for p in pathlib.Path(".codex/agents").glob("*.toml")]'`
- Inspect scoped changes: `git status --short`
- Inspect staged paths: `git diff --cached --name-only`
- Fingerprint a staged candidate:
  `git diff --cached --binary --full-index | git hash-object --stdin`

## Project Structure

- `AGENTS.md` — lifecycle routing, ownership, delegation, escalation, Git, and
  Ship rules.
- `.codex/config.toml` — project-wide Codex defaults; it does not duplicate
  role-specific model configuration.
- `.codex/agents/builder.toml` — Builder model, reasoning, permissions, and
  role-specific behavior.
- `.codex/agents/verifier.toml` — Verifier model, reasoning, permissions, and
  role-specific behavior.
- `.codex/agents/reviewer.toml` — existing independent Reviewer definition.
- `docs/initiatives/agents-lifecycle-orchestration/` — Addy lifecycle artifacts
  for this change.

## Code Style

- Keep `AGENTS.md` prescriptive and role-oriented; do not repeat model IDs or
  reasoning settings stored in custom-agent TOML.
- Give each custom agent a narrow responsibility and an explicit stop rule.
- Use concise TOML consistent with the existing Reviewer definition:

```toml
name = "builder"
description = "Implementation agent for Build, Fix, and Ship execution."
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

## Testing Strategy

- Parse all project custom-agent TOML with Python `tomllib`.
- Review the final diff for lifecycle completeness and contradictions.
- Confirm Builder and Verifier responsibilities are disjoint.
- Confirm the Verifier can execute repository automation while being forbidden
  from editing or staging tracked files.
- Confirm staged fingerprints bind RED/GREEN evidence to the exact candidate.
- Confirm ignored pre-existing untracked paths are absent from the staged diff.
- Run `git diff --check` before every documentation/configuration commit.

## Boundaries

### Always

- Apply `using-agent-skills` at task intake.
- Run `interview-me` to explicit user confirmation whenever routing enters
  Define.
- Require the applicable SPEC and PLAN approvals before autonomous Build.
- Have root directly trigger Builder, Verifier, and Reviewer.
- Preserve Addy's RED → GREEN discipline and per-task verified commits.
- Use ordinary task branches for every repository-mutating task.
- Use matching task branches in every modified submodule.
- Delete task branches after successful merge.

### Ask First

- Any merge, push, pull-request mutation, tag, release, deployment, production
  migration, rollout, or rollback.
- Any change to approved requirements, architecture, interfaces, acceptance
  criteria, or task scope.
- Proceeding when unrelated dirty worktree or submodule state is present.

### Never

- Let a subagent trigger another agent or advance the lifecycle.
- Let Verifier edit or stage tracked files, implement fixes, or commit.
- Let Reviewer implement fixes, commit, merge, or trigger another agent.
- Create unverified commits or commit a staged candidate whose fingerprint has
  changed since verification.
- Automatically merge, push, tag, release, or deploy.
- Use independent worktrees as the normal isolation mechanism.
- Stash, move, commit, or discard unrelated user changes.
- Modify the vendored Addy Skills or introduce a custom PLAN/checkpoint schema.

## Success Criteria

1. `AGENTS.md` assigns Define/Plan and lifecycle control to root; Build/Fix and
   Ship execution to Builder; Verify/Re-verify to Verifier; and
   Review/Re-review to Reviewer.
2. Define always begins with a confirmed `interview-me` intent; subsequent
   skills decide their own applicability and completion.
3. After required SPEC/PLAN approval, root automatically coordinates
   Build → Verify → Commit → Review → Fix/Re-verify → Re-review.
4. Only requirement/scope changes, new authority, or unavailable external state
   cause a user-facing pause; repeated findings return to root for a changed
   strategy rather than an identical loop.
5. Builder and Verifier preserve RED → GREEN using the Git index as the
   uncommitted candidate snapshot and a staged-diff fingerprint as the evidence
   identity.
6. Every task is independently verified and committed; agents are reused within
   an existing Addy checkpoint and refreshed after the checkpoint.
7. Repository-mutating tasks use ordinary branches; unrelated dirty state
   pauses work; modified submodules use the same branch name and are committed
   before the parent pointer.
8. Review completion leaves an approved, locally committed task branch awaiting
   explicit Ship authorization.
9. Authorized Ship is delegated by root to a fresh Builder, including merge;
   successfully merged task branches are deleted.
10. Builder and Verifier model/reasoning settings live only in their custom-agent
    TOML files, not in `AGENTS.md`.

## Open Questions

None. The user confirmed the intent and all material policy choices before this
spec was written.
