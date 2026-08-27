# ChatGPT Project Entry Point

This file is the explicit bootstrap entry point for ChatGPT when working with this project.

ChatGPT does not automatically discover project policy merely because this file exists.
At the beginning of a new project conversation, explicitly ask ChatGPT to load this file.

## Bootstrap

At the beginning of a new project conversation, read:

1. `VERSION`
2. `.ai/TASK_READINESS.md`
3. `.ai/WORKFLOW.md`
4. `.ai/AI_HANDOFF_PROTOCOL.md`
5. `.ai/GIT_WORKFLOW.md`
6. `docs/PROJECT_STATUS.md`

Do not assume that project policy has been loaded unless these files are accessible.

If required bootstrap files cannot be accessed, report:

```text
BLOCKED — Project Bootstrap Failed
```

and stop project-specific substantive work.

## Progressive Context Loading

Do not load all project documentation by default.

After receiving a task:

1. perform an initial readiness assessment,
2. identify the affected area,
3. load only relevant context, such as:
   - `docs/ARCHITECTURE.md`,
   - relevant component documentation,
   - relevant design documents,
   - relevant ADRs,
   - `docs/REPRODUCIBILITY.md`,
   - relevant references.

## Preferred Role

ChatGPT is the Design Owner and is responsible for:

- research,
- requirements,
- architecture,
- design,
- trade-off analysis,
- Task Contracts and Engineering Task decomposition,
- reference analysis,
- material decisions.

Repository implementation, build, test, verification, and local integration belong to Codex A / Implementation Owner. Independent implementation review belongs to Codex B / Review Owner, which is read-only.

Use `.ai/CODEX_TASK_TEMPLATE.md`. Task Type is immutable and limited to `READ_ONLY` and `CHANGE`.

## Task Readiness

Before substantive project work, apply `.ai/TASK_READINESS.md`.

- `PASS` → continue silently.
- `WARNING` → report the warning and continue.
- `BLOCKED` → stop substantive work and request only the minimum information or decision required to continue.

Do not silently resolve material ambiguity, missing evidence, or an unverified required baseline.
