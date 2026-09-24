# Spec: Extend AutoTVM Tuning to All MLPerf Tiny Models

## Objective

After the `image_classification_v1` FSIM/TSIM tuning loop is verified, extend the same AutoTVM schedule-search, history-best replay, tuning-log/JSON-sidecar, and performance-reporting contract to every MLPerf Tiny model currently included in `vta/apps/mlperf_tiny_benchmark/`.

## Assumptions

1. The repository's current benchmark applications define the rollout set: anomaly detection V1, image classification V1 and V2, keyword spotting V1, streaming wakeword V1, and visual wake words V1.
2. Each model's existing preprocessing, quantization, partitioning, samples, and output-comparison contract remains unchanged.
3. Model-specific tasks that do not lower to a registered VTA AutoTVM schedule are reported explicitly; the rollout must not fabricate tuning records or claim every operator is accelerated.
4. Each model/backend pair receives a distinct native log and paired JSON sidecar tied to the same `vta_64mac.json` contents.

## Tech Stack

Shared AutoTVM tuner from `simulator-autotvm`, existing model-specific MLPerf Tiny Relay pipelines and simulator runners, per-model tests, and the project Python environment.

## Commands

The proposed shared entry point selects any supported repository model and one simulator backend:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model all --backend tsim
```

The corresponding FSIM invocation uses `VTA_BACKEND=fsim --backend fsim`. The final `all` expansion and CLI behavior will be specified in Plan after V1 establishes the reusable interface.

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`: shared model enumeration, AutoTVM task extraction, and backend dispatch.
- `vta/apps/mlperf_tiny_benchmark/<model>/model_pipeline.py`: existing model contracts and supported VTA subgraphs.
- `vta/apps/mlperf_tiny_benchmark/<model>/runtime.py` and `run.py`: apply matching history-best records and report simulator results.
- Each model's `tests/` and `README.md`: model-specific tuning, replay, and correctness coverage/documentation.
- `scripts/README.md`: document maintained command entry points, prerequisites, outputs, and side effects.

## Code Style

Reuse the common tuner and metadata schema rather than copying per-model AutoTVM logic. Keep model-specific extraction behind explicit adapters that consume existing prepared Relay modules. Report unsupported task families and skipped tuning candidates with their reasons; do not hide partial coverage.

## Testing Strategy

- Per-model structural tests confirm task extraction and log/sidecar identity without invoking a long search.
- A bounded tuning/replay smoke run exercises at least one supported VTA schedule per model/backend where the model has such a task.
- Existing model pipeline, FSIM, and TSIM correctness tests remain unchanged and pass.
- Aggregate coverage reports the model set, tunable task count, best-log path, sidecar path, output-equivalence result, and TSIM cycle count where supported.

## Boundaries

- **Always:** Add models in the confirmed repository set; retain model-specific accuracy/output and routing checks; make partial AutoTVM coverage visible; use the shared geometry config and sidecar schema.
- **Ask first:** Add new benchmark models beyond the current repository set or change an existing model's quantization, preprocessing, weights, or expected routing.
- **Never:** Treat missing AutoTVM tasks as successful tuning, reuse another model's log, or report simulator cycles as board latency/official MLPerf results.

## Success Criteria

- Every current repository model can be enumerated by the tuner and independently reports tunable versus unsupported tasks.
- Supported tasks can be tuned/replayed separately under FSIM and TSIM, with one native log and matching JSON sidecar per model/backend.
- Existing model correctness checks continue to pass when a matching tuned log is applied.
- TSIM cycle counts are reported for each model with available TSIM runtime coverage; no model is claimed faster without a tuned-versus-baseline comparison.

## Open Questions

- Some existing model runtimes use different graph and profiler contracts; rollout should add only adapters supported by evidence from the V1 loop.
- The aggregate `--model all` command should remain interruptible and resume-safe; exact per-model failure handling is a Plan decision.
