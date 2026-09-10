# Implementation Plan: Agent Lifecycle Orchestration

## Overview

Introduce dedicated Builder and Verifier custom agents, then replace the
project's existing Addy delegation rules with the approved lifecycle,
verification-handoff, branch, submodule, and Ship policy. Work proceeds in two
small sequential tasks, each preserving RED → GREEN evidence and receiving its
own verified commit.

## Architecture Decisions

- Use project-scoped custom agents in `.codex/agents/`, matching the existing
  Reviewer convention. Keep role-specific model and reasoning settings out of
  `AGENTS.md` and do not duplicate them in `.codex/config.toml`.
- Keep root as the only lifecycle orchestrator. Builder, Verifier, and Reviewer
  do not trigger one another or advance phases.
- Use the Git index as the pre-commit candidate snapshot. Bind verification to
  `git diff --cached --binary --full-index | git hash-object --stdin` and commit
  only the unchanged GREEN candidate.
- Use Addy's existing task and checkpoint structures without adding a custom
  checkpoint schema.
- Reuse Builder and Verifier within a checkpoint; refresh both after a
  checkpoint. Use a fresh Reviewer for Review/Re-review and a fresh `default`
  subagent for Ship execution.

## Task List

### Phase 1: Custom Agent Roles

- [ ] Task 1: Add project-scoped Builder and Verifier definitions

### Phase 2: Lifecycle Policy

- [ ] Task 2: Rewrite Addy lifecycle orchestration in `AGENTS.md`

### Checkpoint: Agent Lifecycle Ready

- [ ] All custom-agent TOML parses successfully
- [ ] Builder and Verifier responsibilities are disjoint
- [ ] `AGENTS.md` contains the approved routing, TDD, fingerprint, checkpoint,
      Git/submodule, review, escalation, and Ship rules
- [ ] `git diff --check` passes
- [ ] Each implementation task has a verified atomic commit
- [ ] Final branch diff is ready for independent Review

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Builder and Verifier overlap | High | Put narrow stop rules in each custom-agent file and repeat only responsibility boundaries in `AGENTS.md` |
| Verifier cannot run build tools | High | Use `workspace-write` sandbox while explicitly forbidding tracked-file edits and staging |
| Verification applies to a changed candidate | High | Compare the staged fingerprint before and after every verification run and again before commit |
| Root/subagent communication becomes verbose | Medium | Pass PLAN task ids, repository paths, HEAD, candidate fingerprint, and concise verdicts rather than code or logs |
| Existing user files enter a commit | High | Stage exact task paths only and verify staged paths before commit |
| Lifecycle loops indefinitely | Medium | Return recurring findings to root for a changed strategy; ask the user only for root-owned decisions, new authority, or unavailable external state |

## Open Questions

None. The user approved the governing spec before this plan was written.
