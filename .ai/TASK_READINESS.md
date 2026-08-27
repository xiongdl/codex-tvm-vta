# AI Task Readiness Protocol

## Purpose

Before substantive work, determine whether the task can be executed reliably without material unauthorized assumptions.

This protocol is shared by ChatGPT and Codex.

## States

### PASS

Sufficient information, evidence, decisions, and capabilities exist to proceed without material unauthorized assumptions.

Behavior:

- continue,
- normally do not report the PASS result.

### WARNING

A meaningful risk or uncertainty exists, but it can be handled conservatively without requiring a material user decision.

Behavior:

- report the warning clearly,
- explain the relevant risk,
- continue with the task.

If user confirmation is required before proceeding, the state is not WARNING; it is BLOCKED.

### BLOCKED

Proceeding requires one or more of:

- missing critical input,
- missing required evidence,
- unresolved material decision,
- unauthorized assumption,
- unavailable required capability.

Behavior:

- stop substantive execution,
- explain the blocker,
- request only the minimum information or decision required to continue.

For an Engineering Task, terminal Blocked Reason is limited to:

- `INPUT_REQUIRED`
- `DECISION_REQUIRED`
- `REVIEW_LIMIT_REACHED`

Complexity, test failure, debugging effort, refactoring needs, ordinary Git conflicts, or difficult Review Findings alone are intermediate engineering conditions, not Blocked Reasons.

Task Type is immutable and limited to `READ_ONLY` and `CHANGE`. Readiness does not convert between Task Types.

## Common Checks

Evaluate as applicable:

- Goal clarity
- Required inputs
- Evidence availability
- Constraints
- Decision maturity
- Agent suitability
- Execution feasibility
- Verification feasibility

## ChatGPT Profile

Pay particular attention to:

- goal clarity,
- required evidence,
- source reliability,
- source freshness when relevant,
- repository/baseline verification,
- architectural decision maturity,
- suitability for research/design/review,
- whether the requested outcome actually requires repository execution.

A better executor being available is normally WARNING.

An unavailable capability required to satisfy the requested outcome is BLOCKED.

## Codex Profile

Pay particular attention to:

- goal,
- scope,
- repository state,
- architecture and ADR constraints,
- dependencies,
- execution environment,
- verification feasibility,
- acceptance criteria,
- public-contract impact,
- version impact.

Do not infer architectural intent solely from implementation.

## Version Impact

Use:

- `NONE`
- `PATCH`
- `MINOR`
- `MAJOR`
- `UNKNOWN`

`MAJOR` does not automatically mean BLOCKED.

An unapproved breaking change is BLOCKED.

`UNKNOWN` does not automatically mean BLOCKED.

If version impact must be resolved before the current phase can proceed safely, unresolved `UNKNOWN` is BLOCKED.

## Hard Rules

- If a material user decision is required, use `BLOCKED`, not `WARNING`.
- `PASS` should normally be silent.
- Do not continue by silently inventing missing evidence or architectural intent.
- Do not bypass the gate merely because implementation appears straightforward.
