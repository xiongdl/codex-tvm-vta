# Tasks: Agent Lifecycle Orchestration

## Task 1: Add Project-Scoped Builder and Verifier Definitions

**Description:** Add narrow custom-agent definitions that bind implementation
work to a strong Builder and deterministic verification execution to a
low-cost Verifier. Follow the existing `.codex/agents/reviewer.toml` convention.

**Acceptance criteria:**

- [ ] `.codex/agents/builder.toml` defines Builder for Build and Fix execution,
      with implementation-focused instructions and explicit stop rules.
- [ ] `.codex/agents/verifier.toml` defines Verifier for Verify and Re-verify,
      permits build/test artifacts, and forbids tracked-file edits, staging,
      commits, fixes, and agent orchestration.
- [ ] Builder uses `gpt-5.6-sol` with high reasoning; Verifier uses
      `gpt-5.6-luna` with low reasoning.
- [ ] `.codex/config.toml` remains unchanged.

**Verification:**

- [ ] RED: `test -f .codex/agents/builder.toml && test -f .codex/agents/verifier.toml`
      fails before implementation because both definitions are absent.
- [ ] GREEN: the same file-existence command succeeds.
- [ ] Codex `load_workspace_dependencies` resolves a project-available bundled
      Python interpreter at version 3.11 or newer, and all
      `.codex/agents/*.toml` files parse with that interpreter and the command
      documented in the approved SPEC.
- [ ] `git diff --check -- .codex/agents/builder.toml .codex/agents/verifier.toml`
      succeeds.
- [ ] Staged paths contain only the two new custom-agent files.

**Dependencies:** None

**Files likely touched:**

- `.codex/agents/builder.toml`
- `.codex/agents/verifier.toml`

**Estimated scope:** Small: 2 files

## Task 2: Rewrite Addy Lifecycle Orchestration in AGENTS.md

**Description:** Replace the current broad delegation section with the approved
skill routing, root-owned lifecycle control, separated Builder/Verifier roles,
RED/GREEN staged-candidate handoff, checkpoint refresh, review routing, Git branch
and submodule rules, pause conditions, and Ship authorization/execution policy.

**Acceptance criteria:**

- [ ] Task intake delegates phase selection to `using-agent-skills`; every
      entered Define phase starts with confirmed `interview-me` intent.
- [ ] Ownership assigns Define/Plan/control to root, Build/Fix to Builder,
      Verify/Re-verify to Verifier, Review/Re-review to Reviewer, and authorized
      Ship execution to a `default` subagent.
- [ ] Root directly triggers all agents; subagents return concise evidence and
      do not trigger one another or advance the lifecycle.
- [ ] SPEC/PLAN approval starts automatic Build through final Review, with only
      the approved user-facing pause conditions.
- [ ] RED/GREEN candidates use exact staging and a stable staged-diff
      fingerprint; the verified unchanged GREEN candidate is committed per
      task.
- [ ] Existing Addy checkpoints control agent reuse/refresh without a new PLAN
      schema.
- [ ] Every repository mutation uses an ordinary task branch; unrelated dirty
      state pauses; modified submodules use the same branch name and commit
      before the parent pointer.
- [ ] All Ship operations require explicit user authorization, are delegated to
      a fresh `default` subagent, and successfully merged task branches are
      deleted.
- [ ] Builder/Verifier model IDs and reasoning settings do not appear in
      `AGENTS.md`.

**Verification:**

- [ ] RED: `rg -q '^### Builder$' AGENTS.md && rg -q '^### Verifier$' AGENTS.md`
      fails before implementation.
- [ ] GREEN: the same role-heading command succeeds.
- [ ] `rg -n 'using-agent-skills|interview-me|staged.*fingerprint|submodule|Ship|delete.*branch' AGENTS.md`
      finds every required policy area.
- [ ] `rg -n 'gpt-5\.6|reasoning_effort' AGENTS.md` returns no matches.
- [ ] `git diff --check -- AGENTS.md` succeeds.
- [ ] Staged paths contain only `AGENTS.md`.

**Dependencies:** Task 1

**Files likely touched:**

- `AGENTS.md`

**Estimated scope:** Small: 1 file

## Checkpoint: Agent Lifecycle Ready

- [ ] Run all Task 1 and Task 2 GREEN verification commands.
- [ ] Confirm the approved SPEC success criteria against the final branch diff.
- [ ] Confirm only approved lifecycle/configuration artifacts are committed.
- [ ] Run independent Review before requesting any Ship authorization.
