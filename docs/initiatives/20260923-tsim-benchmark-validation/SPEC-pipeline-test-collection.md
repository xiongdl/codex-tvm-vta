# Spec: Combined Pipeline Test Collection

## Objective

Make the three routing-invariant pytest modules for VWW, image classification V2, and anomaly detection collect and run together from one documented command. The command must exercise the same tests as the three individual module commands and exit successfully without duplicate-module import errors.

## Tech Stack

Python 3.11 project environment and the repository's existing pytest installation. Do not add a test dependency solely to solve module collection.

## Commands

The combined command is the acceptance check. Use pytest's importlib mode together with the scoped `vta/apps/mlperf_tiny_benchmark/pytest.ini`; the configuration keeps the collection root within the benchmark subtree so test module names do not shadow the repository's top-level `vta` package:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q --import-mode=importlib vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py
```

## Project Structure

- Each benchmark owns its existing `tests/test_model_pipeline.py` module.
- `vta/apps/mlperf_tiny_benchmark/pytest.ini` scopes root discovery to this benchmark subtree and avoids shadowing the top-level `vta` package.
- The initiative's `VALIDATION.md` records the canonical combined command and its result.

## Code Style

Keep the pytest configuration scoped to the MLPerf Tiny benchmark subtree and preserve standalone module execution. The `--import-mode=importlib` option avoids duplicate test-module names; the scoped config prevents the top-level `vta` package from being shadowed during collection.

## Testing Strategy

- Run all three files in one pytest process using the documented command.
- Confirm normal collection, all expected tests executed, and exit status 0.
- Run each module independently to ensure the combined fix preserves standalone behavior.
- Do not reduce the selected test set or mark tests skipped to avoid the collision.

## Boundaries

- **Always:** Keep the exact three focused modules in the combined invocation and preserve their assertions.
- **Ask first:** Add a dependency or change unrelated repository-wide pytest behavior.
- **Never:** Report separate module runs as proof that the combined invocation works, or omit a module from the command.

## Success Criteria

- The documented combined command collects and runs all three modules in one process with exit status 0.
- Each module remains independently runnable and passes.
- No tests are skipped or removed to obtain a successful collection.

## Open Questions

- None. The duplicate basenames are handled by importlib mode, and the scoped pytest config prevents namespace shadowing during combined collection.
