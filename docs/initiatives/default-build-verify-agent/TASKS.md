# Tasks: Default Build and Verify Agent

## Task 1: Replace Builder and Verifier with Default Configuration

**Description:** Remove the dedicated Builder and Verifier custom-agent files and
add one Default definition with their combined execution responsibility.

**Acceptance criteria:**

- [ ] `.codex/agents/default.toml` names the role `default` and uses
      `gpt-5.6-luna`, high reasoning, and `workspace-write`.
- [ ] Default permits implementation and verification-generated artifacts while
      preserving unrelated changes and forbidding agent orchestration, lifecycle
      advancement, scope expansion, and unauthorized Ship work.
- [ ] `.codex/agents/builder.toml` and `.codex/agents/verifier.toml` are absent.
- [ ] `.codex/agents/reviewer.toml` and `.codex/config.toml` are unchanged.

**Verification:**

- [ ] RED: at the approved base, Builder and Verifier exist and Default does not.
- [ ] GREEN: Default exists and Builder and Verifier do not.
- [ ] Parse all `.codex/agents/*.toml` with Python 3.11 or newer.
- [ ] Assert Default's model, reasoning effort, and sandbox values.
- [ ] `git diff --check -- .codex/agents` succeeds.
- [ ] Staged paths contain only the three role-configuration paths.

**Dependencies:** None

**Files likely touched:**

- `.codex/agents/default.toml`
- `.codex/agents/builder.toml`
- `.codex/agents/verifier.toml`

**Estimated scope:** Small: 3 files

## Task 2: Route Build and Verification Through Default

**Description:** Minimally replace Builder/Verifier ownership, delegation,
RED -> GREEN handoffs, commit routing, review-fix routing, and checkpoint reuse
with the combined Default role.

**Acceptance criteria:**

- [ ] Root remains the only lifecycle orchestrator.
- [ ] Default executes Build, Fix, Verify, Re-verify, verified commits, and
      explicitly authorized Ship actions.
- [ ] RED -> GREEN, staged fingerprints, regression verification, review
      verdicts, fix loops, branch/submodule policy, and Ship authorization remain.
- [ ] Reviewer responsibilities remain unchanged.
- [ ] No `.agents/custom/` files are added.

**Verification:**

- [ ] RED: current `AGENTS.md` assigns Build/Fix to Builder and
      Verify/Re-verify to Verifier.
- [ ] GREEN: final `AGENTS.md` assigns both responsibility groups to Default and
      contains no active Builder/Verifier routing.
- [ ] Review the complete `AGENTS.md` diff against the approved specification.
- [ ] `git diff --check -- AGENTS.md` succeeds.
- [ ] Staged paths contain only `AGENTS.md`.

**Dependencies:** Task 1

**Files likely touched:**

- `AGENTS.md`

**Estimated scope:** Small: 1 file

## Checkpoint: Default Role Ready

- [ ] Run all Task 1 and Task 2 GREEN verification commands.
- [ ] Confirm only approved paths were committed.
- [ ] Run independent Review before requesting any Ship authorization.
