# Specification: Workflow consistency validation

## Objective

Audit the committed workflow changes between `470b501dcc7e2b1a51baad5968f75e68efeb6848`
and `e1d9589cd4b5a9b3bac58d50c04823e640c98aac`. Produce evidence-backed findings
and verify approved repairs. This is one capability: workflow validation.

Assumptions: the local baseline commit is the requested GitHub commit; current
committed behavior is the candidate, not an automatically approved design;
isolated workflow tests are appropriate, while simulator tests are unrelated.

## Commands

From the repository root:

```bash
git diff --check 470b501dcc7e2b1a51baad5968f75e68efeb6848 e1d9589cd4b5a9b3bac58d50c04823e640c98aac
bash -n .agents/custom/scripts/git-workflow .agents/custom/scripts/test-git-workflow .agents/custom/scripts/test-role-workflow
bash .agents/custom/scripts/test-role-workflow
bash .agents/custom/scripts/test-git-workflow
./.agents/custom/scripts/git-workflow status
```

Parse configuration and perform any Python validation only with
`.envs/tvm-vta-env/bin/python`. No new environment or package installation.
Inspect test scripts before execution; Git mutations in the regression suite
are confined to its temporary fixture repositories, not managed project repos.

## Project structure and scope

- `AGENTS.md`: selects the role and its policy.
- `.agents/custom/{root,default,architecture-reviewer,implementation-reviewer}.md`:
  lifecycle, execution, design review, and implementation review contracts.
- `.agents/custom/{architecture,version-control,automation}.md`: shared rules.
- `.codex/config.toml`, `.codex/agents/*.toml`: runtime configuration.
- `.agents/custom/scripts/`: workflow automation and regression tests.
- `docs/initiatives/20261003-workflow-consistency-validation/`: owned audit
  artifacts, findings, proposed fixes, approval records, and verification.

Unchanged shared scripts and referenced skills may be inspected for contracts;
historical initiative artifacts are context, not new obligations to migrate.

## Style and reporting

Preserve existing Markdown, TOML, and Bash conventions. Each finding uses:

```text
ID: F1
Location: repository-relative file and one-based line
Evidence: exact conflicting rules or reproducible command/result
Impact: concrete workflow failure or ambiguity
Proposal: smallest coherent correction and affected files
Verification: test or scenario proving the correction
Approval: pending / user-approved / user-rejected
```

Distinguish proven failures, textual contradictions, coverage gaps, and runtime
limitations. Do not claim agent behavior is verified by substring tests.

## Testing strategy

Run existing role-contract and isolated Git-workflow suites, shell syntax and
diff checks, and configuration parsing when the project interpreter exists.
Trace end-to-end scenarios: role selection, candidate review and approval,
checkpoint commits, ownership uncertainty, escalation and resumption, fix and
re-review, and optional merge. Check role/config naming and referenced paths.
If runtime semantics require outside documentation, use authoritative sources
and distinguish documented behavior from actual execution evidence.

Write focused regression tests only for approved behavioral repairs or agreed
coverage gaps. No weakening checks, removing failing assertions, or rewriting
policy to make a test green. Record command exits and practical limitations.

## Boundaries

- Always: preserve user edits, use Git workflow for project Git mutations,
  report complete concrete evidence, and independently review approved fixes.
- Ask first: every workflow repair, including policy, configuration, or test
  changes. Present evidence, impact, solution, and validation before requesting
  approval. An approved audit plan alone does not authorize these edits.
- Never: implement an unapproved repair, alter unrelated TVM/VTA functionality,
  push, merge, install dependencies, or claim tests prove untested semantics.

Audit reports and lifecycle documents may be written and committed under the
initiative directory. Pending findings can be recorded without fixing them.
After findings are available, update proposed repair artifacts with concrete
solutions and obtain the required reviews/approvals before implementation.

## Success criteria

1. All 13 changed files are checked against their consumers and shared rules;
   relevant existing tests are run with reproducible results or explicit blockers.
2. Every actionable finding has evidence, impact, a minimal solution, and an
   individual approval state. No workflow repair precedes user approval.
3. Approved repairs pass affected verification and independent review; rejected
   or deferred problems remain clearly recorded as residual risks.

## Architecture and simplification

This audit introduces no runtime module, public interface, or abstraction.
Root owns approval decisions; execution agents own delegated verification and
approved repairs; independent reviewers judge committed evidence/artifacts.
The initiative directory holds reports, not a second workflow implementation.
Keep existing ownership and dependencies unless the user approves a concrete
correction. A single specification is sufficient for this cohesive audit.

## Open questions

None for audit scope. Per-finding repair decisions remain with the user.
