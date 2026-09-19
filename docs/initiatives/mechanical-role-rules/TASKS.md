# Tasks: Mechanical Role Rules

## Checkpoint: Role policy update

- [x] Update Root with the Interview gate, immediate branch creation, and
  deterministic escalation rules.
- [x] Update Default with direct delegated execution and commit commands.
- [x] Update Reviewer with read-only review commands and an exact verdict
  contract.
- [ ] Run contract and workflow verification, commit, and report evidence.

### Acceptance criteria

- Clear requests do not trigger redundant interpretation or confirmation.
- `codex/<task>` is created immediately after Interview completion.
- Delegated roles do not broaden scope or mutate outside their authority.
- Existing role contract checks remain green.
