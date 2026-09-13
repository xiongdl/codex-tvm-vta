# Implementation Plan: Default Build and Verify Agent

## Overview

Consolidate Builder and Verifier into one Default custom agent, then minimally
rewrite the existing lifecycle policy to route both responsibilities to Default.
The change keeps every other policy and role behavior intact.

## Architecture Decisions

- Default owns execution of Build, Fix, Verify, and Re-verify, but Root remains
  the only lifecycle orchestrator.
- Default also retains the existing responsibility for explicitly authorized
  Ship execution.
- The same Default is reused within an existing Addy checkpoint and replaced
  after the checkpoint, matching the current agent-refresh policy.
- Existing staged-candidate fingerprints remain the verification identity; the
  proposed tree/helper protocol is out of scope.
- Reviewer remains independent and unchanged.

## Task List

### Phase 1: Consolidate Custom-Agent Configuration

- [ ] Task 1: Replace Builder and Verifier TOML with Default TOML

### Phase 2: Update Lifecycle Routing

- [ ] Task 2: Route combined execution through Default in `AGENTS.md`

### Checkpoint: Default Role Ready

- [ ] All remaining custom-agent TOML parses successfully
- [ ] Default model, reasoning, sandbox, responsibilities, and stop rules match
      the approved specification
- [ ] Builder and Verifier definitions are absent
- [ ] Reviewer and project-wide Codex configuration are unchanged
- [ ] Existing lifecycle gates remain intact
- [ ] `git diff --check` passes
- [ ] Each task has a verified atomic commit
- [ ] Final branch diff passes independent Review

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Default verifies its own implementation | High | Preserve exact candidate fingerprints, RED -> GREEN evidence, regression checks, and independent final Review |
| Role consolidation accidentally changes lifecycle behavior | High | Make minimal substitutions and assert unchanged Root, Reviewer, Ship, Git, and automation behavior |
| Deleted roles remain referenced | High | Search all in-scope policy/configuration files for Builder and Verifier references |
| Default broadens scope during verification | Medium | Require pre/post candidate checks and forbid lifecycle advancement or agent orchestration |

## Open Questions

None.
