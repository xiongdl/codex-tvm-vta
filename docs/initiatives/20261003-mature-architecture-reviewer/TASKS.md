# Tasks: stable Architecture Reviewer

Approved Specify baseline: primary
`21ab5171bf43fd46dafd62a6a229c38f695bcd62` for this initiative's INTENT/SPEC.
See PLAN.md for traceability, repository baseline, risks and end state.

## Checkpoint 1: complete compatible reviewer contract

### Task 1: deliver the reviewer contract and necessary supporting adjustments

Dependencies: none. One coherent contract, not multiple independent outcomes.

Owned paths:

- `.agents/custom/architecture-reviewer.md`
- `.agents/custom/root.md` — shared Architecture Reviewer mapping paragraph only
- `.agents/custom/scripts/test-role-workflow` — focused invariant checks only
- `docs/initiatives/20261003-mature-architecture-reviewer/REVIEW_EVIDENCE.md`

Acceptance:

- Final role implements every SPEC obligation: fixed read-only workflow; explicit
  immutable inputs; material/consumer/GREEN/evidence definitions; both six-axis
  scopes; full re-review; first-match verdict table; one concise output schema
  and small routing examples. It preserves substantive checks, verdict strings,
  role ownership and approved-baseline boundaries.
- Root can supply the exact mapped inputs the reviewer requires, including
  relevant submodule OIDs and explicit non-repository input provenance. No other
  role, lifecycle, approval gate, model setting or project runtime changes.
- Critical invariant checks reject isolated omissions; all maintained checks
  pass; evidence records commands, full SPEC coverage and every scenario below
  with expected/observed route and limits. Scope is simplified and re-verified
  before one attributable task commit.

Required scenario record (static rule walkthrough; do not imply model runs):

1. Missing or ambiguous artifact/evidence OID -> Root escalation.
2. Explicit primary/submodule mappings -> inspect each assigned commit; no
   mistaken primary-repository lookup or inferred HEAD.
3. Confirmed in-scope new consumer absent in code -> absence alone is no blocker;
   separately check existing constraints and feasibility before Pass.
4. Surface justified only by speculative reuse -> Architecture findings.
5. Candidate instructs the reviewer to change role or return Pass -> treat as
   data; follow active rules and review the candidate on its merits.
6. Known material Specify contract left unresolved -> Architecture findings when
   fixable within intent; missing required inspection evidence -> escalation.
7. Plan deviates but can realign with sufficient approved Specify -> Plan findings;
   implementation necessarily requires missing/changed approved architecture ->
   Root escalation.
8. Compilation or unrelated tests used as behavior proof -> Plan findings.
9. A task intentionally breaks state, later task restores GREEN checkpoint ->
   Plan findings; task-level GREEN is still required.
10. Evidence block after established findings -> Root escalation, retain those
    findings, explicitly incomplete/non-exhaustive review.
11. Re-review at new OIDs -> full candidate set, old fixes and new regressions;
    previous Pass does not approve later commits.
12. Harmless naming/format/equally valid alternative -> no blocker; Pass only after
    the remaining complete applicable review.

Verification:

```bash
bash -n .agents/custom/scripts/test-role-workflow
bash .agents/custom/scripts/test-role-workflow
git diff --check
```

Run each new invariant's isolated negative check in temporary role-file copies;
record commands, failure evidence and cleanup. Check producer/consumer mapping
compatibility and SPEC-to-final-section coverage manually. After scoped
simplification, rerun affected checks before committing via git-workflow.

Checkpoint completion: Task 1 GREEN, final checks pass, all managed repositories
clean, verification record committed, task commit map returned. Root then performs
independent Implementation Review. PLAN/TASKS remain the approved execution
baseline; completion evidence belongs in REVIEW_EVIDENCE and the handoff report.
