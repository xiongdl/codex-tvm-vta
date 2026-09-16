# Spec: Unify Lifecycle Approval Flow

## Objective

Change the Root lifecycle so every task begins with an explicit, user-visible
execution process selected through `using-agent-skills`, and no repository
mutation starts until the user authorizes that process. When Define or Plan is
applicable, complete `interview-me` first, then let Root create the task branch,
generate or revise every applicable pre-Build lifecycle artifact, and commit
the complete artifact batch. Present that committed batch for one explicit
user approval before dispatching Build.

Root may modify only repository-resident Define/Plan lifecycle artifacts. A
Default remains the sole role allowed to modify implementation and verification
files. Reviewer remains read-only, and Ship remains a separate Root action that
requires explicit user authorization.

## Tech Stack

- Markdown role policy under `.agents/custom/`.
- Codex role routing from `AGENTS.md`.
- Local Git task branches and commits governed by
  `.agents/custom/version-control.md`.
- Addy workflow skills under `.agents/vendor/agent-skills/skills/`.

## Commands

Run from the repository root:

```bash
git status --short --branch --untracked-files=all
git diff --check
rg -n 'using-agent-skills|execution process|explicit user authorization|task branch|lifecycle artifact|single.*approval|Build|Ship' \
  .agents/custom/root.md
git diff -- AGENTS.md .codex .agents/custom
```

The change is policy-only; the TVM/VTA build is not relevant to its behavior.

## Project Structure

```text
AGENTS.md
  Role selection only; unchanged unless implementation finds a routing conflict.
.codex/
  Agent models, sandbox, and command approval rules; unchanged because the new
  gates are lifecycle policy rather than runtime permission changes.
.agents/custom/root.md
  Root lifecycle, approval, branching, artifact, delegation, and Ship policy.
.agents/custom/default.md
  Build/Fix/Verify implementation role; unchanged.
.agents/custom/reviewer.md
  Read-only review role; unchanged.
docs/initiatives/unify-lifecycle-approval-flow/
  Approved SPEC, PLAN, and TASKS for this change.
```

## Code Style

Keep the policy normative, role-specific, and chronological. Use direct
requirements rather than examples that could be mistaken for optional behavior:

```markdown
At task intake, use `using-agent-skills`, state the proposed execution process,
and obtain explicit user authorization before the first repository mutation.
```

Preserve the existing terminology: Root, Default, Reviewer, Define, Plan,
Build, Verify, Review, and Ship.

## Testing Strategy

- Static search proves all required gates and ownership terms are present.
- Focused diff review proves the implementation changes only the minimum Root
  policy text required by this specification.
- Candidate-integrity checks from `.agents/custom/version-control.md` bind the
  verification result to the staged candidate before every commit.
- A fresh Reviewer compares the implementation commit with this approved
  artifact batch and reports Pass, implementation findings, or Root escalation.

## Boundaries

- Always:
  - Use `using-agent-skills` at task intake and explicitly state the proposed
    execution process.
  - Obtain explicit user authorization before branch creation or any other
    repository mutation.
  - When `interview-me` applies, obtain explicit confirmation of intent before
    lifecycle artifacts are generated or revised.
  - Have Root create or safely reuse the task branch before Root writes any
    repository-resident lifecycle artifact.
  - Have Root generate or revise all applicable Define/Plan artifacts as one
    batch, candidate-check them, and commit them before presenting the batch.
  - Obtain one explicit user approval for the complete committed artifact batch
    before the first Build Default dispatch.
  - If the batch is revised, commit the complete revised batch and repeat the
    single batch-approval gate.
  - Keep implementation and verification file changes with Default and all
    review work with Reviewer.
- Ask first:
  - Any change to confirmed intent, scope, architecture, acceptance criteria,
    public interfaces, or release behavior.
  - Ship, integration, remote operations, or task-branch cleanup.
- Never:
  - Let Root modify implementation or verification files.
  - Dispatch Build before the committed lifecycle-artifact batch is explicitly
    approved.
  - Treat initial execution authorization as artifact approval or Ship
    authorization.
  - Modify `.codex`, `AGENTS.md`, Default policy, or Reviewer policy without a
    concrete conflict that this specification requires resolving.

## Success Criteria

1. Root explicitly states the skill-selected execution process at intake and
   waits for explicit user authorization before repository mutation.
2. Root owns task-branch creation before generating or revising lifecycle files.
3. A confirmed `interview-me` intent leads to one complete, committed batch of
   all applicable Define/Plan artifacts rather than sequential artifact gates.
4. The user approves that committed batch once before Build begins.
5. Root file mutation is limited to Define/Plan lifecycle artifacts; Default
   owns implementation and verification file changes.
6. The existing automatic Build -> Verify -> verified implementation commit ->
   Review and Fix -> Re-verify -> verified fix commit -> Re-review loop remains
   intact after batch approval.
7. Reviewer remains read-only and Ship still requires separate explicit user
   authorization.
8. No `.codex`, router, Default, or Reviewer change is made unless verification
   exposes an actual incompatibility.

## Open Questions

None. The user explicitly confirmed the role exception for Root-owned
lifecycle artifacts and authorized this Define/Plan execution process.
