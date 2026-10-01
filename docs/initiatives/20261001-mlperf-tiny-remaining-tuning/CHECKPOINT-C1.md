# Checkpoint C1: shared infrastructure

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## Completed tasks

- **T1:** Added `vta/apps/mlperf_tiny_benchmark/fused_tasks.py` for deterministic
  complete VTA Conv fusion extraction, exact Conv packing identity, scalar and
  vector bias constants, right shift, clipping and cast arithmetic. Extraction
  requires exact agreement between routed symbols and prepared VTA functions;
  unsupported composite arithmetic fails with the offending symbol. The host
  inventory preserves the counts exposed by each model pipeline.
- **T2:** Added `tuning_controller.py` for seed manifest/report gating,
  seed-bound and integrity-checked resume state, distinct FSIM batching to the
  success quota or valid-space exhaustion, per-success TSIM attempt tracking,
  deployable positive-cycle selection, replay file-hash validation and
  explicit isolated-worker environments. Seed artifacts remain separate from
  full-search state.
- **T3:** Added `deployment_evidence.py` for exact selected-config identity and
  lowering callbacks, one-sample reference checks, ordinary/debug counter
  agreement, graph-resident single-call node profiling, inclusive integer
  10% checks, compatible deployment reports and atomic failure diagnostics.
  `scripts/mac_utilization.py` now accepts an explicit zero-based occurrence
  report form while preserving its existing one-based form.

## Prepared graph inspection

Tests prepared the actual committed models and extracted every routed VTA
fusion. Counts were anomaly detection **9**, keyword spotting **4**, streaming
wakeword **1**, and visual wake words **13**. Every routed VTA composite in
these graphs is Conv arithmetic with bias/add (scalar or channel vector),
right shift, clip and cast. No Dense occurrence is routed to VTA; Dense work
remains in the host inventory. The KWS tensor-bias task was instantiated into
an AutoTVM schedule to verify the vector-bias template path.

## Verification

All commands used `.envs/tvm-vta-env/bin/python` with repository TVM/VTA
`PYTHONPATH`, explicit `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json"`,
and an explicit backend.

- Shared focused suite:
  `./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/tests/test_fused_tasks.py vta/apps/mlperf_tiny_benchmark/tests/test_tuning_controller.py vta/apps/mlperf_tiny_benchmark/tests/test_deployment_evidence.py vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py -q`
  — **53 passed**. This covers all four prepared graphs, 100-trial batching,
  20-success stopping, exhaustion, duplicate rejection, seed gating, TSIM
  failures, tamper/foreign-identity rejection, deployment boundary cases,
  graph-node counters, calculator report integration and failure diagnostics.
- IC regressions:
  `./.envs/tvm-vta-env/bin/python -m pytest --import-mode=importlib vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_fused_tuning.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_deployment_profile.py -q`
  — **33 passed**. IC V2's strict `<10%` policy remains covered.
- `git diff --check` — passed before commits.
- `./.agents/custom/scripts/git-workflow status` — clean after task commits.

No simulator search or real-model deployment was started in C1. The model
adapters and real seed alignment checks belong to the following checkpoints.

## Commit maps

Original commit map: root `863bb1c32251c7dd779ad450d6e4ed2df5928e98`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, VTA
`71b80f2892bcb446fc9cb73e62220012af1a5869`.

| Task | Root commit | VTA commit | Committed paths |
| --- | --- | --- | --- |
| T1 | `e3c1744d13a599f25f422bd6b0303bc3cab341d9` | `545d96cb6e1279430e8d7cc67e894b35e1679081` | `vta/apps/mlperf_tiny_benchmark/fused_tasks.py`; `vta/apps/mlperf_tiny_benchmark/tests/test_fused_tasks.py` |
| T2 | `c32b543e4c1291f944808bfe68e651154ec1cbe9` | `90a6b12498a80a55acff875bb373b8376313cd38` | `vta/apps/mlperf_tiny_benchmark/tuning_controller.py`; `vta/apps/mlperf_tiny_benchmark/tests/test_tuning_controller.py`; `scripts/README.md` |
| T3 | `f8d705781e5cbf2fa9e08183470f0af015d9d98b` | `02eecf8e693a1e02c8d4e01648485e94456e1770` | `vta/apps/mlperf_tiny_benchmark/deployment_evidence.py`; `vta/apps/mlperf_tiny_benchmark/tests/test_deployment_evidence.py`; `vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py`; `scripts/mac_utilization.py`; `scripts/README.md` |

TVM had no source changes and remains at `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`.
Before the checkpoint evidence commit, the clean final source map was root
`f8d705781e5cbf2fa9e08183470f0af015d9d98b`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`02eecf8e693a1e02c8d4e01648485e94456e1770`.

## Known limits

This checkpoint verifies shared contracts and schedule instantiation; it does
not provide FSIM/TSIM search counts, real deployment cycle pairs or per-model
MAC reports. Those require the model-local seed and deployment tasks in C2 and
later checkpoints. The inspected prepared graphs have no VTA-routed Dense task,
so Dense stays explicitly inventoried on host rather than being represented as
a VTA workload.
