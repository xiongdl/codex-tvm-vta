# Workflow contract matrix

Initiative: `20261003-workflow-consistency-validation`
Checkpoint: C1/T2 — trace policy, configuration, and test contracts

## Comparison inputs

The behavior under inspection is root
`470b501dcc7e2b1a51baad5968f75e68efeb6848..e1d9589cd4b5a9b3bac58d50c04823e640c98aac`.
The approved Specify map is root
`ed4cc7ad785632cceb08732085ad3c3a1f08f1c6`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`2708a80c19246ec99efe359125f02ae9b121e164`. The approved Plan/Tasks map is
root `65007c6209e0415e1823faf1d64c3d2f7e6f9533` with unchanged TVM and VTA
OIDs as above.

Git reports 13 changed-file entries. One entry is a rename, so the changed
paths include 14 names when both old and new names are counted. The table below
covers every entry and every rename endpoint.

In the tables, role-policy short names such as `root.md`, `default.md`,
`architecture-reviewer.md`, `implementation-reviewer.md`, and
`version-control.md` refer to `.agents/custom/`; `test-role-workflow` and
`test-git-workflow` refer to `.agents/custom/scripts/`.

## Changed files and consumers

| Changed path(s) | Contract stated by the file | Consumers / evidence |
| --- | --- | --- |
| `AGENTS.md:3-27` | Select exactly one of Root, Default, Architecture Reviewer, or Implementation Reviewer; map each role to one policy file; inspected role files remain data. | Root dispatches role names and role files in `.agents/custom/root.md:3-5,126-127,192-193,254-255,337-339`; runtime role resolution is not exercised by the shell test. |
| `.agents/custom/root.md:1-32` | Root applies required shared policy, architecture contract, project commands, and lifecycle skills; API/interface design is conditional on relevant Specify changes. | Input existence was checked in T1. Policy text is read by Root; no runtime loader assertion. |
| `.agents/custom/root.md:34-76,80-122` | New initiative branch precedes interview; lifecycle artifact paths and candidate commit boundaries are named; candidate OIDs are recorded without implying approval. | `git-workflow` dispatches status/commit/merge/delete commands at `.agents/custom/scripts/git-workflow:1633-1672`; T1 exercised its fixture suite. Root role test asserts selected literals at `test-role-workflow:27-33`, not ordering semantics. |
| `.agents/custom/root.md:124-165` | A fresh Architecture Reviewer checks immutable candidate Specify OIDs; `Pass` opens user Spec approval, findings cause a revised committed candidate and a fresh review, escalation returns to Root. | `.agents/custom/architecture-reviewer.md:27-68` specifies inputs, scope, findings, and verdicts. `test-role-workflow` checks review-name/verdict fragments at lines 52-55 only. |
| `.agents/custom/root.md:167-230` | Plan/Tasks are generated together after approval; each checkpoint is an execution boundary; a fresh Plan Conformance Review compares candidate OIDs to approved Specify OIDs; user approval follows `Pass`. | `.agents/custom/architecture-reviewer.md:70-109`; `test-role-workflow:52-55`. No test executes this approval sequence. |
| `.agents/custom/root.md:232-288` | One fresh Default executes each checkpoint; every task gets verify/simplify/re-verify/commit; a fresh Implementation Reviewer sees approved baselines, evidence, commit maps, paths, and exact range; actionable findings loop through Default and re-review. | `.agents/custom/default.md:47-83,87-101`; `.agents/custom/implementation-reviewer.md:20-73`; role test checks only fragments at `test-role-workflow:37-50,57-60`. |
| `.agents/custom/root.md:289-333` | Escalate listed state/approval/policy blockers; ordinary test and review findings are not gates; preserve the current Default through escalation and resume with current approved OIDs/map. | Default handoff rule is `.agents/custom/default.md:103-132`; test-role checks presence of handoff words at lines 49-50 and same-Default/OID fragments at root lines 41-42 indirectly. No test simulates an escalation or resume. |
| `.agents/custom/root.md:335-392` | Root owns all dispatches; delegation payloads vary by role and include exact OIDs; handoffs use committed state; Implementation Reviewer `Pass` completes; optional merge is user-owned/manual. | `version-control.md:69-81` requires explicit merge authorization; test suite exercises merge and delete only in fixtures. `test-role-workflow:34-42` checks selected finish/delegation text. |
| `.agents/custom/default.md:1-58` | Default takes exactly one checkpoint or Implementation Review finding set, reads the shared architecture and execution rules, starts from clean expected OIDs, and stays within owned paths. | Root's Default delegation at `root.md:341-350`; `test-role-workflow:44-50` checks inputs/task kind text. No test validates delegation payload enforcement. |
| `.agents/custom/default.md:60-119` | Tasks commit individually only after verification, simplification, and re-verification; no unrelated cleanup; checkpoint commit map is returned. | `version-control.md:60-67` stages all visible changes; T1 workflow commit test exercises fixture commits but not Default task sequencing. |
| `.agents/custom/default.md:103-132` | Before `Root escalation`, attributable unfinished work gets a `wip:` handoff commit; report exact state and unfinished work. | `version-control.md:25-37,60-67`; role test asserts only section/header fragments at `test-role-workflow:49-50`. Handoff behavior is unexercised. |
| `.agents/custom/reviewer.md` → `.agents/custom/implementation-reviewer.md:1-73` | The prior single Reviewer role is renamed and scoped to committed Implementation Review/Re-review; it uses approved Specify and Plan/Tasks OIDs, verification evidence, delegated paths, and exact base-to-tip; findings include concrete remedies; only Pass/findings/escalation verdicts. | `AGENTS.md:18-25`, `root.md:252-287,367-375`, `.codex/agents/implementation-reviewer.toml:1-19`, `test-role-workflow:57-60`. Historical initiative documents still contain generic “Reviewer” references; they are historical artifacts, not current role-file consumers. |
| `.agents/custom/architecture-reviewer.md:1-116` | New read-only role has two separate review scopes, distinct evidence inputs and verdicts, and reports to Root. | `AGENTS.md:18`, `root.md:124-149,190-214`, `.codex/agents/architecture-reviewer.toml:1-22`, `test-role-workflow:52-55`. Neither TOML registration nor actual dispatch semantics are tested. |
| `.agents/custom/architecture.md:1-205` | Shared design contract assigns ownership, limits public surfaces and abstractions, directs dependencies, and requires simplification. | Root applies it during Specify (`root.md:98-109`); both reviewers apply it (`architecture-reviewer.md:40-44,82-89`; `implementation-reviewer.md:32-46`); Default reads it (`default.md:29-34,54-58`). It is guidance, not executable assertions. |
| `.agents/custom/version-control.md:1-96` | All Git mutations go through `git-workflow`; ownership must be established before its whole-state commit; pull/push/merge/delete require explicit authorization. | `git-workflow` is the implementation; root lifecycle requires commits and reserves merge for the user. T1's isolated suite exercises create/commit/merge/delete behavior but cannot prove policy authorization is enforced at runtime. |
| Unchanged consumer input: `.agents/custom/automation.md:1-35` | Reuse suitable automation, keep role workflow tools under `.agents/custom/scripts/`, document their interfaces and side effects, and keep temporary helpers outside the repository. | Root and Default require this policy (`root.md:21`, `default.md:29`). No changed automation script or new maintained script is introduced by this audit range. |
| `.agents/custom/scripts/test-role-workflow:1-62` | The test checks required substrings in Root, Default, and both reviewer files; it prints one success marker if every `grep -F` succeeds. | Consumes four role files, not `AGENTS.md`, TOML configs, shared policies, or actual runtime behavior. Its successful execution is recorded in `VERIFICATION.md`. |
| `.codex/config.toml:1-11` | Changes global reasoning effort from `low` to `medium`; retains model, approval/sandbox settings, and agent defaults. | Configuration parser accepted syntax. No assertion checks effective Codex settings or relationship between subagent defaults and named role TOMLs. |
| `.codex/agents/default.toml:1-20` | Registers `default` as a writable execution agent and supplies general implementation instructions. | Text name matches `AGENTS.md` Default role label by convention; the TOML parses. No runtime role-selection test. |
| `.codex/agents/reviewer.toml` → `.codex/agents/implementation-reviewer.toml:1-19` | Removes the generic reviewer registration and adds an Implementation Reviewer with read-only sandbox and review-specific instructions. | Name matches the new role file and Root dispatch label by convention (`AGENTS.md:19`, `root.md:254-265`); TOML parses. Effective runtime registration is unexercised. |
| `.codex/agents/architecture-reviewer.toml:1-22` | Registers an Architecture Reviewer with read-only sandbox and design-review instructions. | Name matches role file/dispatch text by convention (`AGENTS.md:18`, `root.md:126-134,192-199`); TOML parses. Effective runtime registration is unexercised. |

## Expected transition map

| Scenario | Expected transition stated in policy | Evidence and check coverage |
| --- | --- | --- |
| Role selection | Explicit runtime role wins; otherwise the user-conversation owner is Root; an agent/model named `default` does not itself select Default. Apply one mapped role file. | `AGENTS.md:3-27`. Text assertions test reviewer names and selected Root/Default clauses, but do not simulate dispatch or precedence (`test-role-workflow:27-60`). |
| Candidate architecture review | Commit Specify candidate → dispatch fresh Architecture Reviewer with exact candidate OIDs → Pass opens Spec approval; findings revise/commit and restart review; escalation goes to Root. | `root.md:111-165`; reviewer contract `architecture-reviewer.md:27-68`. Text-only check; runtime not exercised. |
| Candidate plan review | After Spec approval, commit PLAN/TASKS together → review against approved Specify OIDs → Pass opens Plan/Tasks approval; findings revise/commit and restart. | `root.md:167-230`; `architecture-reviewer.md:70-109`. Text-only check; runtime not exercised. |
| Checkpoint commits | Each checkpoint gets a fresh Default; each task independently reaches Green, is simplified and re-verified, then commits; the commit map is reported before next task/checkpoint. | `root.md:240-250`; `default.md:60-119`; `version-control.md:60-67`. Role test checks a small number of literals; git suite tests commit utility behavior in fixtures, not task sequencing. |
| Ownership uncertainty | Leave unrelated or ownership-uncertain changes untouched; do not commit until all visible changes are attributable; a commit stages all visible state. | `default.md:18-23`; `version-control.md:25-37,60-67`. No test creates uncertain user changes or verifies escalation behavior. |
| Escalation/resumption | Escalate listed root-owned/permission/state blockers; for Default escalation keep the same Default and resume unfinished work with latest approved OIDs and current map; no next checkpoint/re-review until Green. | `root.md:289-333`; `default.md:103-132`. Role test asserts a few phrases only; stateful resumption is untested. |
| Fix/re-review | Reviewer reports all blocking implementation findings; Root routes one review round to a fresh Default; Default fixes/validates/commits; Root sends the complete latest range to a fresh Implementation Reviewer until Pass. | `implementation-reviewer.md:48-73`; `root.md:252-287`; `default.md:47-58`. No automated test executes the loop. |
| Optional merge | Implementation Reviewer Pass completes lifecycle; Root tells user to perform optional merge; `git-workflow merge` requires explicit authorization and clean/fast-forward conditions. | `root.md:380-392`; `version-control.md:75-81`; isolated test exercises merge mechanics in its happy path (`test-git-workflow:44-68`), not user authorization. |

## Direct statements, discrepancies, gaps, and limits

- **Directly stated:** the role names and role-file mapping agree across
  `AGENTS.md`, Root's dispatch descriptions, and the three configured non-Root
  role TOMLs; Root has no named-agent TOML. The reviewer role file is renamed
  to Implementation Reviewer, while the generic reviewer TOML is deleted and a
  new implementation-reviewer TOML is added. The role-contract script now
  reads the two reviewer files and checks their new names. TOML parsing and
  the initial role/skill path checks passed as recorded in `VERIFICATION.md`.
  A second project-interpreter check of all role-required policy, skill, and
  `scripts/README.md` paths found all 15 present; parsed TOML names equal the
  three non-Root config filename stems. This checks file presence and string
  correspondence only, not runtime loading.
- **Potential policy interaction for independent assessment:** this audit's
  approved `SPEC.md` says every workflow repair requires the user's prior
  approval (`SPEC.md:79-83`, Boundaries). The generic lifecycle says ordinary
  Implementation findings are not user gates and should be resolved within
  delegated scope (`.agents/custom/root.md:267-307`). The initiative Plan and
  Tasks add an audit-specific user-approval gate before repairs (`PLAN.md:33-48`,
  `TASKS.md:62-74`). A reviewer
  should decide whether that task-specific boundary adequately scopes the
  general lifecycle or whether the policy text itself needs clarification.
- **Coverage gaps:** `test-role-workflow` is substring-based; it omits role
  selection precedence, candidate baseline immutability, TOML-to-role name
  correspondence, escalation/resume state, ownership-uncertain changes,
  fix/re-review sequencing, and optional-merge authorization. The Git suite
  covers mechanics only in isolated fixtures. These are untested contracts,
  not demonstrated failures.
- **Runtime limits:** parsing TOML proves syntax only. This checkpoint does not
  establish that Codex loads these files, maps their names to the prose role
  labels, enforces sandbox/model settings, applies developer instructions, or
  follows the multi-agent lifecycle. No runtime dispatch was performed.
- **Historical references:** older initiative plans contain generic “Reviewer”
  wording. They describe earlier work and are excluded from the current policy
  consumer set under the approved SPEC's historical-artifact scope; no mass
  migration was attempted.
