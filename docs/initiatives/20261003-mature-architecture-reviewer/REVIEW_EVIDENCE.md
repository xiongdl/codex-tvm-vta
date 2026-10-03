# Task 1 verification evidence

Initiative: `20261003-mature-architecture-reviewer`
Branch: `codex/20261003-mature-architecture-reviewer`
Approved Specify: primary `21ab5171bf43fd46dafd62a6a229c38f695bcd62`
Task base: primary `1983fb4d2c31dd2bfddcff29f8b9ced0967306dc`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, VTA
`2708a80c19246ec99efe359125f02ae9b121e164`.

## Verification

From the repository root:

```bash
bash -n .agents/custom/scripts/test-role-workflow
bash .agents/custom/scripts/test-role-workflow
git diff --check
```

All three passed. The maintained checker printed `OK role workflow contract`.

Scoped simplification merged the duplicate output-verdict instruction into one
sentence without changing its exact verdict set; all verifications were rerun
against that final wording.

Isolated negative check: for each of the 26 new checker invariants, a fresh
copy of `.agents/custom/` was placed in a `mktemp` directory under
`/private/tmp`; only the corresponding guarded line was removed from its copied
role file; then `bash <copy>/scripts/test-role-workflow` was run. All 26 runs
exited nonzero as expected. Temporary copies were removed by the harness exit
trap. These are text-contract checks, not proof of agent behavior.

## SPEC traceability

| Approved SPEC obligation | Final evidence |
| --- | --- |
| Fixed read-only workflow and immutable inputs | `Required inputs and limits`; `Review workflow`; committed-only Git inspection and no-edit limits |
| Root can provide exact artifact, repository, submodule, and non-Git provenance mappings | Shared mapping paragraph in `.agents/custom/root.md`; reviewer input contract |
| Materiality, consumer, GREEN, and evidence definitions | `Common standard` |
| Architecture Review preserves all six substantive checks | `Architecture Review checks`, items 1–6: intent/completeness; ownership/modularity; dependencies/contracts; simplicity; change locality; feasibility |
| Plan Conformance Review preserves all six substantive checks | `Plan Conformance Review checks`, items 1–6: coverage/conformance; executability/cohesion; order/checkpoints; verification; risk/locality; end state |
| Full re-review; first-match routing; exact verdicts; one output schema and concise examples | `Review workflow`; `Verdict routing`; `Output contract` |
| Correction ownership, approved-baseline boundaries, and role separation | Scope inputs, routing table, and scope-specific checks; no edit/delegation authority |
| Critical maintained invariants and isolated omission rejection | `.agents/custom/scripts/test-role-workflow`; 26/26 isolated negative checks above |
| Honest limits on behavioral and Luna-low validation | Static scenario record below; no claim of a model run |

## Static scenario walkthrough

These are manual rule walkthroughs against the final role and Root delegation
contract. “Observed” describes the route required by those written rules; it
does not describe an Architecture Reviewer model execution. Evidence references
name the controlling final section. All runs share the limitation that textual
and manual checks cannot prove runtime interpretation.

| # | Scenario | Expected route | Observed route and evidence | Limit |
| --- | --- | --- | --- | --- |
| 1 | Missing or ambiguous artifact/evidence OID | Root escalation | Root escalation; `Required inputs and limits` validates mappings and OIDs before review | Static only |
| 2 | Explicit primary and submodule mappings | Inspect each assigned commit; do not infer HEAD or use the wrong repository | Same; `Required inputs and limits` requires the supplied repository per path and forbids inferred commits | No separate multi-repository agent run |
| 3 | Confirmed in-scope new consumer is absent from current code | Absence alone is not a blocker; check feasibility and constraints separately | Same; `Common standard` says approved target behavior need not exist and calls for separate feasibility/constraint checks | Static only |
| 4 | Surface justified only by speculative reuse | Architecture findings | Architecture findings; `Architecture Review checks` 3–4 require a real/confirmed consumer and reject speculative reuse | Static only |
| 5 | Candidate says change role or return Pass | Treat as data; apply active role | Same; role opening and routing example label candidate instructions as review data | No adversarial model run |
| 6 | Known material Specify contract unresolved, versus unavailable evidence | Architecture findings if fixable within intent; otherwise missing evidence escalates | Same; common standard distinguishes artifact defects from unavailable evidence; first-match table routes them | Static only |
| 7 | Fixable Plan drift, versus plan requiring unapproved architecture | Plan Conformance findings; Root escalation | Same; `Verdict routing` states both routes and distinguishes missing task from missing architecture | Static only |
| 8 | Compilation or unrelated tests offered as behavior proof | Plan Conformance findings | Plan Conformance findings; checklist 4 says compilation alone does not prove behavior and verification must prove acceptance | Static only |
| 9 | Task intentionally breaks state and later restores checkpoint GREEN | Plan Conformance findings; task-level GREEN still required | Same; checklist 2 requires each task to end GREEN and forbids a later task repairing it; checklist 3 requires stable GREEN checkpoints | Static only |
| 10 | Evidence blocked after findings are established | Root escalation; retain findings and mark incomplete/non-exhaustive | Same; `Review workflow` preserves findings and stops dependent checks; output requires incomplete, non-exhaustive escalation | Static only |
| 11 | Re-review at new OIDs | Re-read full candidate set, fixes, and regressions; prior Pass does not carry forward | Same; `Review workflow` explicitly repeats all checks and says prior Pass does not approve later commits | Static only |
| 12 | Harmless naming, format, or equally valid alternative | No blocker; Pass only after complete applicable review | Same; `Common standard` excludes preference-only blockers and output requires completeness for Pass | Static only |

No Luna-low runtime validation was performed or claimed. This task changes only
role/delegation text and its static checker; TVM/VTA runtime tests would not
validate it.
