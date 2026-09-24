# Spec: Combined Pipeline Test Collection

## Objective

Make the three routing-invariant pytest modules for VWW, image classification V2, and anomaly detection collect and run together from one documented command. The command must exercise the same tests as the three individual module commands and exit successfully without duplicate-module import errors.

## Tech Stack

Python 3.11 project environment and the repository's existing pytest installation. Do not add a test dependency solely to solve module collection.

## Commands

The combined command is the acceptance check. The implementation may use pytest's supported import mode or a small repository-level test configuration if evidence shows that is the narrowest maintainable fix:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q --import-mode=importlib vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py
```

## Project Structure

- Each benchmark owns its existing `tests/test_model_pipeline.py` module.
- A shared pytest configuration may live at repository root only if the chosen solution applies consistently and does not change unrelated test discovery semantics.
- The initiative's `VALIDATION.md` records the canonical combined command and its result.

## Code Style

Prefer a command-line pytest option when it solves the collision without repository-wide behavioral changes. If configuration or module naming changes are needed, follow existing repository conventions and keep benchmark tests independently runnable.

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

- None. The known collision is duplicate `test_model_pipeline` basenames; pytest `importlib` mode will be evaluated first.
