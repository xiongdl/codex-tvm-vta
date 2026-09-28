# Implementation Plan: Per-Layer VTA MAC Utilization

## Overview

Add a read-only reporting command for the six MLPerf Tiny models. It will
validate TSIM AutoTVM log/sidecar pairs, map supported VTA Conv/Dense workload
records to each layer occurrence in the prepared model graph, calculate useful
MAC utilization from logical MACs and best-trial cycles, and write CSV plus
JSON reports under ignored build output.

## Architecture Decisions

- Keep the implementation in one benchmark-local script. Reuse
  `autotvm_tuner.py` model selection, prepared graph, task extraction, workload
  identity, and sidecar contracts where practical; do not add AutoTVM imports to
  `model_pipeline.py`.
- Read trial records from native AutoTVM logs and use the minimum successful
  integral TSIM cycle cost for each workload. Validate sidecar and log hashes,
  model identity, backend, geometry identity, and task coverage before writing
  any output.
- Preserve each graph occurrence as its own CSV row, including repeated
  workloads; use a deterministic ordinal and workload hash when the graph does
  not retain a source-level layer name.
- Compute logical MACs as `task.flop / 2` for VTA templates that record FLOPs,
  and compute peak MACs/cycle as `BATCH * BLOCK_IN * BLOCK_OUT` from the
  selected geometry. Label the result useful-MAC utilization to distinguish it
  from physical lane occupancy and end-to-end profiling.
- For one model, accept a native log and its sidecar. For all models, accept the
  existing TSIM aggregate summary and validate each referenced pair. This
  avoids new tuning or runtime instrumentation.
- Default generated files to the ignored benchmark build directory; do not
  commit report output.

## Task List

### Phase 1: Per-Workload Calculation

- Task 1: Build validated artifact loading, workload best-cycle selection,
  geometry peak derivation, MAC utilization math, and deterministic layer-row
  construction with focused tests.

### Checkpoint 1: Single-Model Report Core

- Formula and unit conversions have focused tests.
- Single-model log/sidecar validation rejects mismatches and incomplete data.
- Repeated layer occurrences remain separate and resolve to a workload record.

### Phase 2: CLI and Six-Model Reports

- Task 2: Add single-model and `all` CLI modes, CSV/JSON writing, documentation,
  and bounded report-generation verification using existing TSIM artifacts.

### Checkpoint 2: Usable Script

- One-model and six-model commands produce paired CSV/JSON reports.
- All six models' supported VTA Conv/Dense layer occurrences are represented.
- Report metadata identifies model, workload, log, sidecar, config, cycles,
  MAC count, peak MACs/cycle, and utilization units.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| AutoTVM records are keyed by workload rather than graph layer name. | Layer rows may be difficult to associate or could silently merge repeated operations. | Traverse extracted supported tasks in graph order, assign deterministic ordinals, retain workload hashes, and fail on ambiguous mapping. |
| A best trial's isolated workload cycle cost differs from that layer's cost in full graph execution. | The result could be misread as a per-layer profiler reading. | Name the field and CLI documentation as a task-level estimate; state clearly that it is not end-to-end per-layer cycle profiling. |
| Some task FLOP counts include non-MAC operations or differ by template. | Utilization could be overstated. | Support only explicitly recognized VTA Conv/Dense templates and validate their MAC-count conversion. Reject unknown forms. |
| The geometry JSON encodes log2 dimensions. | A wrong peak-throughput formula would invalidate every row. | Derive dimensions using powers of two and test the `vta_64mac.json` result is 64 MAC/cycle. |
| Aggregate summary paths can point at stale or mismatched artifacts. | Wrong cycles could be paired to a model. | Verify all model/backend/config/log hashes from each sidecar before report generation. |

## Open Questions

- None; requirements are confirmed in `INTENT.md` and `SPEC.md`.
