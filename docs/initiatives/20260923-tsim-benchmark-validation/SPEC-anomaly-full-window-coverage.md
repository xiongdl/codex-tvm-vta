# Spec: Anomaly Detection Full-Window TSIM Coverage

## Objective

Replace the current representative-window-only anomaly detection TSIM evidence with a complete run over every model input window for every checked-in validation sample. The report must show that all expected windows were executed and that the resulting scores match the established reference behavior.

## Assumptions

1. The current CLI/runtime supports a positive `--tsim-window-budget`; the current validation used a budget of one and reported `score_scope=representative_windows`.
2. Full coverage means every window derived from each record in the checked-in validation manifest, not only one window per record.
3. The required budget will be derived from actual record lengths and window geometry. Validation must fail if the executed count differs from the expected count; it must not silently fall back to a smaller budget.

## Tech Stack

Python 3.11 project environment, the existing anomaly detection runtime/model and validation manifest, VTA TSIM, and pytest. No new dependency is expected.

## Commands

Run from the repository root with the built project environment and TSIM libraries. Calculate the total expected window count from the checked-in validation records using the runtime's existing windowing contract, then pass that exact count as `--tsim-window-budget`:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --simulator tsim --host-codegen all --tsim-window-budget <expected-total-window-count>
```

Run the focused anomaly deployment tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_tsim_deployment.py
```

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/runtime.py` defines input window selection, scoring, and execution summaries.
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py` exposes the TSIM window budget and output matrix.
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/` verifies window counts, scores, and CLI/runtime contracts.
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/` contains the checked-in validation manifest and inputs.

## Code Style

Use the existing window-selection and summary structures. Keep the expected total derived from actual validation inputs rather than hard-coding an observed run count.

## Testing Strategy

- Add a deterministic contract test proving the full expected window count is selected when the budget equals that count and that the result reports complete coverage.
- Run the full anomaly TSIM CLI matrix for all checked-in validation samples with no windows omitted.
- Require the result summary to identify full-window scope and every per-sample result to report `executed_window_count == total_window_count`; aggregate those fields and require the totals to match as well.
- Preserve existing score/reference checks and positive simulator-cycle evidence.

## Boundaries

- **Always:** Execute and account for every window in every checked-in validation record; preserve output/reference and simulator-cycle checks.
- **Ask first:** Change the model, validation manifest, window definition, or scoring semantics.
- **Never:** Call a budgeted subset a complete run, weaken score checks, or report full-window coverage when executed and expected counts differ.

## Success Criteria

- The TSIM run covers all windows for all validation records in both host-codegen variants.
- The result explicitly reports full-window scope, and per-sample plus aggregate executed/expected window totals match.
- Focused anomaly deployment tests pass with no skips masking the full-window contract.

## Open Questions

- The exact total window count must be measured from the checked-in manifest and runtime window geometry before the final command is recorded.
