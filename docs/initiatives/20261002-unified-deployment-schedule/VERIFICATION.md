# Unified deployment schedule verification

## Fresh verification

Run from the repository root with the VTA FSIM and TSIM libraries built and
`.envs/tvm-vta-env` available:

```bash
bash scripts/test_vta_byoc.sh --env-name tvm-vta-env
```

Result: passed (`VTA BYOC validation passed`). This command invokes BYOC
structural tests; common schedule/tuning/measurement/cleanup tests; actual
compute, artifact and migration tests; FSIM and TSIM suites; all six model
workflows; Python compilation; retired Relay and MLPerf command-reference
audits; and scoped diff/status checks. The detailed fresh counts and model
output/cycle evidence are in `RESULTS.md`.

The only skipped test was the anomaly TSIM end-to-end matrix unit guard because
`ANOMALY_TSIM_RUN_INTEGRATION` was unset. The gate then ran the real anomaly
TSIM deployment explicitly with `--tsim-window-budget 1`; this preserves the
intended bounded integration protocol. No other test skips, suppressions, or
expectation relaxations were introduced.

Focused T31 checks also passed:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" \
VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps" \
./.envs/tvm-vta-env/bin/python -m pytest -q --import-mode=importlib \
  vta/apps/common/tests/test_deployment_evidence.py \
  vta/apps/common/tests/test_tuning_controller.py
bash -n scripts/test_vta_byoc.sh
git diff --check
git -C vta diff --check
```

The focused tests reported 17 passed. The two updated shared modules retain
coverage for occurrence identity and errors, one-time graph-resident profiling,
strict deployment evidence thresholds, all six model CLI defaults, and tuning
candidate/best/resume option contracts.

## Earlier checkpoint evidence

Before C11, implementation checkpoints exercised each model's default,
partial, candidate, and best schedule paths; seed and alignment gates; bounded
search and resume; and candidate/best exports. For every model, those runs
verified the model's documented outputs/sample contract. The selected
actual-compute run ids, occurrence symbols, config identities, and measured
single-call layer cycles are recorded in `RESULTS.md`. Those checkpoint results
are historical relative to the fresh full gate and are based on generated
ignored `build/actual_compute_tuning/` ledgers and snapshots.

Migration verification converted each historical full-fusion manifest and
matched the converted occurrence costs to its retained report. Migration does
not promote the old evidence to proof of the unified path. Cleanup verification
used fixtures and a dry-run inventory only; it retained tracked and saved
outputs and deleted no user results.

## Commit map

The root repository base is `7416243c22d59300c22e6c222c364d155a7fb7e8`, TVM
base is `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA base is
`a24152a6875b4bfe09d3d43a150bac3727b435688`.

| Task | Root commit | VTA commit | TVM |
| --- | --- | --- | --- |
| T29 | `63828e9a9f2a30e6cf3299a00c6019bf2ad62eff` | `427a3fd4fd0a63966f8a781766992c98d019dced` | unchanged |
| T30 | `03bdf064b63420dbfa34b534039dd33c27a7f544` | `314bcdb199e09078223a17affcd6b17caece06a8` | unchanged |
| T31 | `eedf6469ab9334a1e6a126b3339684b45788d40b` | `8c23e027c69cb694333ff3b64913d665cc015c0a` | unchanged |
| T32 | recorded after its evidence commit | recorded after its evidence commit | unchanged |

The cumulative root and VTA tips are the final T32 commit ids reported with this
checkpoint. This task does not edit approved design artifacts or advance the
initiative beyond C11.
