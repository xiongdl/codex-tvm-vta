# Capability map
Initiative: 20261002-unified-deployment-schedule

| Module id | Responsibility | Depends on |
|---|---|---|
| deployment-compute | Actual deployment-layer computation capture and shared lowering | — |
| schedule-artifacts | One validated schedule snapshot format and selection interface | deployment-compute |
| model-workflow | Six-model tuning and deployment consolidation | deployment-compute, schedule-artifacts |
| artifact-cleanup | Scoped cleanup of generated application files | model-workflow |

Build order: deployment-compute → schedule-artifacts → model-workflow → artifact-cleanup.

## Shared specification contract
All module specs inherit the following project structure, style, verification, and boundaries.

### Stack and environment
Use existing TVM 0.17-era Relay/TE/AutoTVM, VTA BYOC, pytest, and repository Python environment. No dependency installation or environment recreation.
Every project Python command uses ./.envs/tvm-vta-env/bin/python.
Geometry: absolute VTA_CONFIG_FILE pointing to vta/config/vta_64mac.json.
FSIM/TSIM run in separate processes with matching VTA_BACKEND and CLI backend.
TSIM costs use native cycle_count, tsim_single_call v1, one measured invocation with warmup excluded. FSIM timings are not cycles.

### Project structure
Proposed implementation locations:
- vta/apps/common/: importable, model-independent schedule, compute, measurement, artifact and evidence helpers.
- vta/apps/common/tests/: meaningful shared contract tests.
- vta/apps/mlperf_tiny_benchmark/: model registry and aggregate benchmark orchestration.
- Each model: run.py, tune.py, runtime.py, model_pipeline.py, model-specific graph/asset adapters, tests/, model/ and existing sample assets.
- Each model's tune/ directory: saved seed/optimal records and evidence; no second deployment command.
- Each model's build/: regenerable build/cache output and explicitly categorized resumable search state.
- scripts/: repository-level command wrappers, including cleanup.
Existing committed evidence paths remain available. Moving saved evidence is unnecessary.

### Commands
Run from repository root:
```bash
export VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json"
export PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps"
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/common/tests -q
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/tests --import-mode=importlib -q
bash scripts/test_vta_byoc.sh
```
New paths/commands describe the target implementation, not currently available entry points. Model test commands use the same environment and add the selected model path when required.

### Code style
Explicit typed identities and normal package imports; avoid cross-model sys.path mutation and dynamic loading where ordinary imports suffice.
```python
selection = load_schedule(path, expected_identity=deployment.identity)
for layer in deployment.layers:
    config = selection.config_for(layer.identity)
    lowered = deployment.lower_layer(layer, config=config)
```
Here config=None explicitly selects the normal default path. Do not mutate an already-scheduled TIR to manufacture a new candidate.

### Testing and boundaries
Always: Verify output correctness, identity binding, cache isolation and selection coverage; preserve strict existing deployment gates and exact TSIM protocol; run relevant tests before task commits.
Escalate: Changes to approved intent/specs, unavailable external prerequisites, or policy conflicts, per Root rules.
Never: Remove quality checks to make tests pass; silently fall back on corrupt records; delete assets/saved evidence; mix backend timing units; use direct Git mutation.
No arbitrary coverage percentage or performance target is invented. A passing functional test alone does not prove tuning/deployment computation equivalence.
