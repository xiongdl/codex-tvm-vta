# Project Initialization

Use this process when applying the template to a new or existing project.

The goal is to discover the real project and establish a maintainable engineering baseline.

Do not implement new product features during initialization unless explicitly requested.

## Phase 1 — Inspect

Inspect repository structure, source layout, build systems, tests, configuration, environment requirements, dependencies, generated artifacts, scripts/tools, documentation, CI, and major subsystems.

## Phase 2 — Establish Boundaries

Determine whether the project is naturally single-component or multi-component.

A component may be justified by several of:

- distinct responsibility,
- meaningful public interface,
- independent implementation,
- independent build/test behavior,
- distinct dependencies,
- independent evolution.

Do not create components only for visual neatness.

## Phase 3 — Identify Dependencies and Integration Boundaries

Map important dependencies and cross-component contracts.

Document stable shared contracts under `docs/integration/`.

## Phase 4 — Establish Project Documentation

Create or update:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/PROJECT_STATUS.md`
- `docs/REPRODUCIBILITY.md`

## Phase 5 — Discover Existing Workflows

Determine how the project performs setup, dependency installation, build, test, verification, cleanup, and diagnostics/status.

Prefer preserving working tools rather than replacing them without reason.

## Phase 6 — Establish Automation Entry Points

Where practical, provide:

```bash
./scripts/project setup
./scripts/project build
./scripts/project test
./scripts/project verify
./scripts/project clean
./scripts/project status
```

## Phase 7 — Establish Verification Levels

```text
components/<component>/tests/
        └── Component-local tests

integration/tests/
        └── Cross-component tests

tests/
        └── Project-level / End-to-End tests
```

Use the narrowest level that fully proves the intended behavior.

## Phase 8 — Establish Reproducibility

Ensure the repository can answer:

1. What environment is supported?
2. What dependencies are required?
3. Which versions matter?
4. How is setup performed?
5. How is the project built?
6. How are tests run?
7. How are important artifacts/results reproduced?
8. Which state is generated versus source-controlled?

## Phase 9 — Establish Traceability

Create ADRs only for decisions whose rationale should survive.

## Phase 10 — Verify Baseline

Run relevant build/test/verify commands where practical.

Record commands, pass/fail status, skipped checks, and constraints.

## Phase 10A — Establish AI Task Git Workflow

Define the repository `Default Base Branch`. Use `main` as the template default, while preserving an instantiated project's explicitly chosen project-defined long-lived branch when appropriate. Ensure each `CHANGE` Task resolves one immutable Base Branch, creates exactly one short-lived `task/*` Task Branch from it, and integrates the approved commit back into that same Base Branch using ff-only integration as defined by `.ai/GIT_WORKFLOW.md`.

Do not invent additional branch taxonomies during initialization.

## Phase 11 — Summarize

Report structure, components, dependencies, integration boundaries, engineering entry points, verification coverage, reproducibility status, documentation gaps, risks, and the recommended first engineering task.

Update `docs/PROJECT_STATUS.md`.


## Phase 12 — Establish Versioning

Inspect whether the project already has an authoritative versioning scheme.

Check, as applicable:

- existing `VERSION`,
- Git tags,
- package metadata,
- release metadata,
- existing `CHANGELOG.md`.

For a new project with no prior versioning, initialize:

```text
VERSION = 0.1.0
```

and establish `CHANGELOG.md` plus `docs/VERSIONING.md`.

For an existing project, preserve the existing authoritative versioning scheme.

Do not reset an existing project to `0.1.0`.

If version sources conflict materially, report:

```text
BLOCKED — Version Source Conflict
```

and request the minimum decision needed to identify the authoritative version source.
