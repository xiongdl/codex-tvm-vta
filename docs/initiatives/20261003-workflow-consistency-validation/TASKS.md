# Tasks: Workflow consistency validation

Initiative: `20261003-workflow-consistency-validation`.
Approved Specify root OID: `ed4cc7ad785632cceb08732085ad3c3a1f08f1c6`.
See PLAN.md for the complete approved Specify map and original audit range.

## Checkpoint C1: Evidence collection

One fresh Default owns exactly T1 and T2, in order. Writable ownership is only
the two report files below. AGENTS.md, .agents/, .codex/, scripts/, tvm/, and vta/
are inspection/test inputs, not editable paths. Root owns lifecycle artifacts.
User approval of this checkpoint does not authorize workflow repairs.

### T1: Reproduce existing validation

- [ ] Inspect maintained workflow regression tests and their side effects.
- [ ] Run SPEC.md commands: baseline diff check, shell syntax, role contract,
  isolated Git workflow suite, and managed repository status.
- [ ] Parse the four relevant TOML files with the existing project interpreter
  when available. Resolve named role files and required referenced paths.
- [ ] Record exact commands, input OIDs, exits, useful output, and limitations
  in VERIFICATION.md. Test failures are audit results, not permission to repair.
- [ ] Verify report accuracy against captured results and commit this task alone.

Acceptance: every applicable check has a result or explicit reproducible blocker;
no workflow/configuration/test source file is changed. GREEN for this audit task
means evidence is complete and accurate; it does not mean the audited tests pass.

Verification: compare report with command output; `git diff --check`; ensure only
VERIFICATION.md is Git-visible before the workflow commit. Perform scoped report
simplification and recheck before commit.

Owned file: `docs/initiatives/20261003-workflow-consistency-validation/VERIFICATION.md`.
Dependencies: approved Plan/Tasks artifacts. Scope: one file.

### T2: Trace policy/configuration/test contracts

- [ ] Build CONTRACT-MATRIX.md covering all 13 changed files and consumers.
- [ ] Record exact source locations and expected transitions for role selection,
  candidate review/approval, checkpoint commits, ownership uncertainty,
  escalation/resumption, fix/re-review, and optional merge.
- [ ] Check renamed reviewer references, role/config names, required inputs,
  immutable review baselines, and test assertions against these transitions.
- [ ] Distinguish directly stated rules, observed discrepancies, coverage gaps,
  and unexercised runtime behavior. Do not redesign or deliver a formal Review
  verdict; this is evidence preparation for the independent reviewer.
- [ ] Verify matrix citations and completeness, simplify, recheck, and commit
  this task alone.

Acceptance: all changed files and named scenarios are represented with concrete
citations and evidence; no workflow repair occurs.

Verification: check citations against committed files and changed-file list;
`git diff --check`; ensure only CONTRACT-MATRIX.md is Git-visible before commit.

Owned file: `docs/initiatives/20261003-workflow-consistency-validation/CONTRACT-MATRIX.md`.
Dependencies: T1. Scope: one file.

### C1 verification and handoff

- [ ] Both reports are committed separately and reflect captured evidence.
- [ ] All managed repositories are clean on the delegated branch.
- [ ] Return GREEN with command results, full commit maps, and known limitations.

## Independent Review and repair decisions

Root dispatches an Implementation Reviewer after C1. Present resulting concrete
problems and solutions to the user before modifying workflow files. Record each
approval explicitly. Future fix checkpoints must specify the approved solution,
owned paths, regression verification, and current immutable commit maps; they
are not authorized by this evidence-only checkpoint.
