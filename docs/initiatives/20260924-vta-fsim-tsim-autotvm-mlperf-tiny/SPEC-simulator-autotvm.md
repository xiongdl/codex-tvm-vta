# Spec: FSIM/TSIM AutoTVM Schedule Search

## Objective

Provide a reproducible AutoTVM path that searches VTA schedules independently on FSIM and TSIM, applies the selected history-best records during compilation, and preserves separate logs and JSON sidecars for each backend. FSIM and TSIM must use the shared geometry file `vta/config/vta_64mac.json`.

## Assumptions

1. The existing pinned TVM/VTA checkouts and project environment remain the toolchain; no new package is required.
2. AutoTVM logs remain in the native AutoTVM record format. A sidecar JSON is the stable association between a log, the benchmark/model, backend, geometry config, and tuning options.
3. The TSIM run can expose the simulator `cycle_count` needed to compare candidate and baseline schedules. The implementation must verify this against the current simulator API before choosing the runner integration.
4. Search budget and early-stop controls will be configurable. The default should cover the supported search space unless the tuner API imposes a documented limit.

## Tech Stack

Python 3.11 project environment, TVM AutoTVM, Relay, VTA TOPI schedules, FSIM/TSIM native libraries, JSON, and the existing `vta_64mac.json` geometry configuration.

## Commands

Proposed tuning entry point (final CLI names are an implementation detail to settle in Plan):

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model image_classification_v1 --backend fsim

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model image_classification_v1 --backend tsim
```

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`: shared model/backend tuning entry point and AutoTVM task runner.
- `vta/python/vta/autotvm.py` and `vta/python/vta/top/`: existing VTA measurement and schedule registration APIs to reuse.
- `vta/config/vta_64mac.json`: the required geometry-only configuration.
- Each tuning output directory: backend-specific native AutoTVM log and a paired JSON sidecar.
- `vta/apps/mlperf_tiny_benchmark/`: tests for runner selection, log/sidecar pairing, and history-best replay.

## Code Style

Follow the existing benchmark Python modules: small helpers with explicit inputs, immutable result records where useful, path handling through `pathlib.Path`, and JSON written deterministically with sorted keys and a trailing newline. Keep simulator selection explicit through `--backend` plus matching `VTA_BACKEND`; do not revive the retired `TARGET=sim|tsim` interface.

```python
metadata = {
    "backend": backend,
    "model": model_id,
    "config_path": str(config_path),
    "config_sha256": config_sha256,
    "log_path": str(log_path),
    "tuning": tuning_options,
}
sidecar_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
```

## Testing Strategy

- Unit tests validate backend/config mismatch rejection, sidecar schema and log association, and tuner option validation.
- AutoTVM integration coverage confirms VTA tasks are extracted, the selected backend performs measurements, and history-best records are applied when building.
- A focused FSIM and TSIM tuning smoke run uses a bounded trial budget; full search is a user-invoked workflow.
- The benchmark integration module verifies TSIM cycle collection for tuned and baseline runs.

## Boundaries

- **Always:** Keep separate FSIM and TSIM records; include model/backend/config identity in the sidecar; fail clearly when the active backend does not match the requested simulator; preserve native AutoTVM logs for replay.
- **Ask first:** Add external tuning services, change dependency versions, or change geometry values in `vta_64mac.json`.
- **Never:** Silently substitute one backend's log for the other, drop failed measurement records without reporting them, or edit model weights/quantization as part of schedule tuning.

## Success Criteria

- FSIM and TSIM can independently run AutoTVM against `image_classification_v1` using `vta_64mac.json`.
- Each backend produces a native AutoTVM log and a valid sidecar that identifies the same model, backend, config content, and tuning options.
- The selected records can be replayed through AutoTVM history-best when compiling the model.
- TSIM tuning measurements expose cycle data usable by the model-level tuned-versus-baseline comparison.

## Open Questions

- Confirm the available VTA AutoTVM runner hooks for collecting TSIM `cycle_count` per trial; implement the narrowest supported adapter if the stock runner reports only wall-clock duration.
- Select the final tuner algorithm and default trial budget after inspecting task-space sizes for V1.
