# Tasks: Per-Layer VTA MAC Utilization

## Checkpoint 1: Single-Model Report Core

Fresh Default execution boundary: complete Task 1, verify it, then commit it.

### Task 1: Calculate validated per-layer utilization rows

**Description:** Add the reporting core that validates a model's TSIM AutoTVM
log/sidecar pair, resolves each supported VTA Conv/Dense layer occurrence to a
matching workload, selects the minimum successful best-trial cycle cost,
derives the configured peak MACs/cycle, and calculates useful-MAC utilization.

**Acceptance criteria:**

- [ ] MAC count, peak throughput, ratio, and percentage use the confirmed
  formula and documented units.
- [ ] A deterministic row is emitted for each VTA Conv/Dense layer occurrence;
  repeated workload occurrences remain separate and reference the same
  workload record.
- [ ] Model/backend/config/hash/workload/trial mismatches, missing records,
  invalid cycles, unsupported templates, and ambiguous mappings fail clearly.
- [ ] The implementation does not modify model preparation, weights,
  quantization, runtimes, or TVM core.

**Verification:** Run focused tests for MAC/FLOP conversion, the
`vta_64mac.json` 64-MAC/cycle peak, best successful cycle selection, repeated
workload rows, and malformed/mismatched artifacts.

**Dependencies:** None.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/mac_utilization.py`
- `vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py`

**Estimated scope:** Small.

## Checkpoint 2: CLI and Six-Model Reports

Fresh Default execution boundary: complete Task 2 and commit it separately.

### Task 2: Add CLI, report outputs, and usage documentation

**Description:** Add single-model and six-model CLI inputs, emit CSV detail and
JSON summary under ignored build output, document commands and interpretation,
then exercise the report with existing V1 and aggregate TSIM artifacts.

**Acceptance criteria:**

- [ ] Single-model mode requires a matching TSIM log and sidecar; `all` mode
  requires the existing TSIM aggregate summary and validates every model pair.
- [ ] The six-model output contains all supported Conv/Dense occurrences with
  paired artifact identities and no fabricated utilization for unsupported
  task types.
- [ ] CSV and JSON output are deterministic in schema and identify the metric
  as an isolated AutoTVM task estimate rather than full-model per-layer
  profiling.
- [ ] Default outputs go under ignored build output and no generated reports
  are committed.

**Verification:** Run CLI contract tests; generate and inspect one-model V1 and
six-model reports from existing TSIM artifacts; confirm model row counts,
config hashes, paired log identities, cycles, and utilization calculations.

**Dependencies:** Task 1.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/mac_utilization.py`
- `vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py`
- `scripts/README.md`
- `vta/apps/mlperf_tiny_benchmark/README.md`

**Estimated scope:** Medium.

## Checkpoint 2 Verification

- [ ] Both CLI modes validate their inputs and create the documented paired
  outputs.
- [ ] Every current benchmark model has rows for each supported VTA Conv/Dense
  occurrence.
- [ ] The script labels estimates and units accurately and leaves simulator,
  model, and TVM core code unchanged.
