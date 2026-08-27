# AI Engineering Workflow

## Ownership

- ChatGPT = Design Owner
- Codex A = Implementation Owner
- Codex B = Review Owner
- Repository = durable engineering memory
- CI / Automation = repeatable verification

ChatGPT owns requirements, architecture, material decisions, Task Contracts, and Engineering Task decomposition. Codex A owns implementation, verification, local Git lifecycle, Engineering Task status, and preparation of the Independent Review handoff. The human user owns creation of the new Codex B session and manual transfer of the formal review artifacts. Codex B performs read-only Independent Review and owns Findings and the review conclusion.

Detailed contracts are in `.ai/AI_HANDOFF_PROTOCOL.md`; Git and integration rules are in `.ai/GIT_WORKFLOW.md`.

## Standard Flow

```text
Human Goal
    ↓
ChatGPT / Design Owner
    ↓ Codex Task Prompt
Codex A / Implementation Owner
    ↓ readiness, implementation, verification, committed Review Target, Review Prompt
HARD STOP → Human creates new Codex B session and transfers Review Prompt
    ↓
Codex B / Review Owner in the human-created session
    ↓ Codex Review Report
Human returns Review Report to Codex A
    ↓
APPROVED ──────────────── CHANGES_REQUESTED
    ↓                         ↓ resolve, commit if tracked state changed, mandatory re-review
ff-only local integration ←───┘
    ↓
Engineering Result Report to ChatGPT
```

Task Type is immutable and limited to `READ_ONLY` and `CHANGE`. `READ_ONLY` authorizes no repository modification. Every `CHANGE` uses one `task/*` branch and mandatory committed-state Independent Review by Codex B in a new Codex session explicitly created by the human user. Internal, delegated, sub-agent, hidden, automatically spawned, same-session, and self-review mechanisms are informational only and do not consume Review Attempt count. Every `CHANGES_REQUESTED` requires re-review; a new Review Commit is required only when Finding resolution changes tracked repository state.

Engineering terminal status is limited to `COMPLETED` and `BLOCKED`. Task completion is not release authorization.

## Verification Hierarchy

```text
Component-local
      ↓
Cross-component Integration
      ↓
Project-level / End-to-End
```

Use shared repository-defined commands where practical. Codex A reports verification actually performed and Final Version Impact.
