# Spec: remaining Tiny operator tuning

## Objective and fixed inputs
Cover every deployed VTA MAC operator occurrence in AD V1, KWS V1, Streaming Wakeword V1 and VWW V1. Inspect the actual prepared graphs to enumerate coverage; preserve repeated occurrences even when workloads match. Use committed models, existing quantization, HOST/VTA routing, sample preprocessing and vta/config/vta_64mac.json. Record model bytes, geometry, prepared graph and fusion hashes. HOST-only nodes are explicitly inventoried outside VTA tuning coverage.

## Stack and structure
Use .envs/tvm-vta-env, repository TVM/VTA, AutoTVM and existing simulator libraries. Reuse IC V1/V2 algorithms through the smallest safe shared helper boundary. Model adapters and tune/tune.py live under each model application in vta/apps/mlperf_tiny_benchmark/. Focused tests live in each application's tests/ and shared helper tests where applicable. Document maintained interfaces in scripts/README.md and model READMEs. No new dependencies are required.

## Provider contract and behavior
- Extract the actual deployed complete arithmetic, including Conv/Dense, bias, activation, shift, clipping and casts where present, with exact shapes, dtypes, constants and layouts. Do not substitute bare convolution measurements. Unsupported fusions fail with diagnostics.
- Preserve deterministic occurrence/symbol/workload/config identities. Validate that configurations lower through the actual deployment path before accepting them for selection.
- Seed phase finds one successful FSIM schedule for every occurrence, measures each on AutoTVM TSIM and exports complete seed coverage. A success requires successful build, execution and expected output validation. Seed evidence is separate from full-search completion.
- Full search cannot begin for a model until its complete seed deployment gate passes under SPEC-deployment-evidence.md. Seed configurations may count toward the full search when identities, settings and measurements match; never count them twice.
- Default FSIM batches contain 100 distinct configurations (the last exhausted batch may be smaller). After a batch, stop if at least 20 distinct successful schedules exist; otherwise add another 100 until the valid configuration space is exhausted. Record attempts, successes, invalid configurations, execution failures and exhaustion separately. Exhaustion with fewer than 20 is an explicit permitted result, never a claim of meeting the quota.
- Measure every FSIM success with AutoTVM TSIM and choose the minimum positive successful native cycle_count among deployment-lowerable configurations. Record TSIM failures; require at least one selectable configuration per occurrence. Do not choose a slower schedule solely to conceal alignment failures.
- Separate backend processes, matching absolute geometry and explicit backend selection. Use tsim_single_call v1: warmup excluded, profiler cleared, one formal invocation, number=1, repeat=1, min_repeat_ms=0; never divide costs by two. Reuse 60-second FSIM and 120-second TSIM candidate timeouts unless evidence requires a documented infrastructure adjustment.
- Provide seed, full-search, resume and standalone replay operations with explicit model selection, trial-batch/min-successful settings and artifact directories. Bounded smoke runs remain incomplete. Resume validates model/geometry/fusion identity, options, unique candidate indices and the seed-gate report hash. Persist state atomically and keep infrastructure failures distinct from candidate failures.
- Intermediate builds/logs/state belong under model/build/two_stage_tuning/. Export self-contained seed and selected native records, result JSON and manifests under model/tune/. Manifests bind model, geometry, occurrence coverage, exact config, record hashes and protocol; reject incomplete, foreign-model or tampered artifacts before replay. Exported artifacts must replay without intermediate build state.

## Commands
These are implementation target interfaces, executed from repository root. MODEL is one of the four directory names listed above:

```bash
MODEL=anomaly_detection_v1
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/$MODEL" ./.envs/tvm-vta-env/bin/python "vta/apps/mlperf_tiny_benchmark/$MODEL/tune/tune.py" --seed
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/$MODEL" ./.envs/tvm-vta-env/bin/python "vta/apps/mlperf_tiny_benchmark/$MODEL/tune/tune.py" --all --alignment-report <seed-deployment.json>
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/$MODEL" ./.envs/tvm-vta-env/bin/python -m pytest "vta/apps/mlperf_tiny_benchmark/$MODEL/tests" -q
```

## Code style
Follow existing Python conventions, explicit validation and canonical hashes:

```python
if manifest["model_sha256"] != prepared.imported.model_sha256:
    raise ValueError("schedule model identity mismatch")
```

## Testing and success criteria
Verify extraction against actual prepared graph arithmetic, repeated occurrence mapping, Dense/Conv coverage, seed gating, distinct batching and exhaustion, positive TSIM selection, failures/resume, artifact integrity and standalone replay. Run bounded simulator integration followed by full searches for all four models. Each occurrence must meet the quota or prove exhaustion, have all FSIM successes attempted on TSIM, and have an attributable minimum-cycle selected schedule. Run affected IC regressions for shared changes. Mock evidence cannot replace simulator runs.

## Boundaries
Always preserve complete semantics, durable failures and model-specific records. Ask Root on unavailable environment/data/permissions or approved-contract changes. Never skip occurrences, weaken quotas, fabricate cycles or retune IC V1/V2. No unresolved user choices.
