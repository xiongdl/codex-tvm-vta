# Checkpoint C2 evidence

Initiative: `20261001-ic-v2-operator-tuning`\
Branch: `codex/20261001-ic-v2-operator-tuning`

## T3 recovery and T4 implementation

- The earlier T3 deployment used `HistoryBest` on the fused AutoTVM records.
  Those records did not dispatch to the deployed bare Conv lowering key. V2
  deployment now applies each validated native record's configuration to its
  matching VTA global symbol while lowering, with the TECompiler cache cleared
  around each function. Selected configurations are checked against the full
  prepared VTA symbol set, and the native record's cycle count must match the
  manifest entry.
- Per-node measurement now clears TSIM counters and executes the reloaded graph
  node once with `_execute_node`. Warmup is excluded; two invocations are no
  longer combined and divided.
- The one-sample performance stage now runs first: it verifies the first
  selected output, baseline and selected full-model counters, debug/ordinary
  counter agreement, and all eight strict cycle pairs. Only after that gate
  passes does the selected graph run the ten-sample output check. The latter
  does not collect per-node or full-model performance counters.
- Both READMEs now document occurrence-scoped configuration application,
  single-counted node measurement, the one-sample strict gate and the
  ten-sample correctness stage.

## Verification commands

The existing complete-coverage bounded manifest was retained and replayed:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/tune.py \
  --replay-manifest /tmp/ic-v2-c2-artifacts/best-manifest.json
```

Result: all eight entries replayed and lowered; manifest label remains
`BOUNDED_SMOKE_INCOMPLETE`.

The real TSIM deployment command used the same manifest:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/deployment.py \
  --best-manifest /tmp/ic-v2-c2-artifacts/best-manifest.json \
  --output /tmp/ic-v2-c2-artifacts/deployment.json \
  --output-dir /tmp/ic-v2-c2-deployment
```

Result: deployment passed with the bounded manifest. Performance used exactly
one sample (`00-airplane.png`); debug and ordinary complete-run counters both
reported `5,478,352` cycles. All ten selected outputs passed after the strict
gate. Baseline full-model cycles for the performance sample were `21,226,413`.

| Occurrence | Config | AutoTVM cycles | Deployed cycles | Difference | Result |
| ---: | ---: | ---: | ---: | ---: | :--- |
| 0 | 0 | 3,950,572 | 3,967,001 | 0.415864% | pass |
| 1 | 103 | 306,272 | 306,273 | 0.000327% | pass |
| 2 | 18 | 88,368 | 88,553 | 0.209352% | pass |
| 3 | 403 | 311,161 | 311,161 | 0.000000% | pass |
| 4 | 812 | 276,295 | 276,295 | 0.000000% | pass |
| 5 | 451 | 85,764 | 85,764 | 0.000000% | pass |
| 6 | 143 | 154,089 | 154,090 | 0.000649% | pass |
| 7 | 876 | 289,215 | 289,215 | 0.000000% | pass |

The report at `/tmp/ic-v2-c2-artifacts/deployment.json` records these rows,
the single-call protocol, selected configuration hashes, one-sample full-model
counters, and ten output passes. Earlier failure diagnostics remain preserved
at `/tmp/ic-v2-c2-deployment.failure.json`.

Focused V2 strict-gate, occurrence-dispatch and TSIM contract tests passed:
`23 passed, 1 deselected`. The deselected test is the separate full TSIM matrix;
the actual eight-node selected deployment and ten-sample correctness run above
were executed directly. Python compilation and `git diff --check` passed.

The V2 HOST/FSIM deployment test file also produced `20 passed, 1 failed`.
The failure is an existing contradictory source assertion: it forbids
`from tvm import autotvm`, while that exact import is already present in the
T4 starting commit's `image_classification_v2/runtime.py`. This recovery does
not change that pre-existing HOST/FSIM AutoTVM replay path.

## Scope and status

The bounded manifest is integration evidence only and is not represented as a
completed full tuning run. No model bytes, quantization, routing, trial budget,
or strict threshold changed. T4 is complete; C3 remains responsible for the
default full search and full-search final evidence.
