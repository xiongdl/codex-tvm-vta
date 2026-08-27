# Project Versioning

## Version Format

Projects use:

```text
MAJOR.MINOR.PATCH
```

## Core Principle

> Task determines Version Impact.  
> Release determines Version Number.

A task does not automatically bump `VERSION`.

## Version Impact

Every material task may be classified as:

- `NONE`
- `PATCH`
- `MINOR`
- `MAJOR`
- `UNKNOWN`

### NONE

The work does not require a new project release.

### PATCH

Backward-compatible fixes or internal improvements that do not add a new public capability.

Typical examples:

- bug fixes,
- compatible correctness fixes,
- internal refactoring,
- documentation corrections.

### MINOR

Backward-compatible new public capability.

Typical examples:

- new API,
- new component,
- new optional configuration,
- backward-compatible feature.

### MAJOR

A breaking change to a public contract.

Public contracts may include:

- API,
- ABI,
- CLI,
- configuration schema,
- persistent data/file/model format,
- hardware/software interface,
- ISA,
- register interface,
- externally relied-upon runtime behavior,
- integration contracts.

### UNKNOWN

Current information is insufficient to classify the impact reliably.

`UNKNOWN` must be resolved before a formal release.

## AI Responsibilities

### ChatGPT

During requirements, design, or task-definition work, provide:

```text
Preliminary Version Impact:
NONE / PATCH / MINOR / MAJOR / UNKNOWN
```

This is a design assessment, not the final release decision.

### Codex

Before implementation:

- inspect the actual repository,
- verify the expected version impact,
- raise `BLOCKED` if a required compatibility decision is unresolved.

After implementation and verification:

- report `Final Version Impact` based on the actual change.

If final impact differs from preliminary impact, explain why.

## Interaction with Task Readiness

`MAJOR` does not automatically mean `BLOCKED`.

A breaking change is `BLOCKED` only when required authorization or compatibility decisions are missing.

`UNKNOWN` does not automatically mean `BLOCKED`.

It becomes `BLOCKED` when the current phase cannot safely continue until impact is resolved.

## Release Aggregation

Multiple task impacts may be accumulated into one release.

Priority:

```text
MAJOR > MINOR > PATCH > NONE
```

`UNKNOWN` cannot enter a formal release.

## Release Consistency

For a formal release:

```text
VERSION
CHANGELOG.md
Git tag
```

must agree.

Example:

```text
VERSION = 1.4.0
CHANGELOG contains 1.4.0
Git tag = v1.4.0
```

## Project Initialization

For a brand-new project, the default initial version is:

```text
0.1.0
```

For an existing project, do not overwrite existing versioning.

Inspect available version sources such as:

- existing `VERSION`,
- Git tags,
- package metadata,
- release metadata,
- existing `CHANGELOG.md`.

If authoritative version sources conflict materially, report:

```text
BLOCKED — Version Source Conflict
```

and request the minimum decision needed to establish the authoritative version source.
