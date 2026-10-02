# Review 1 fixes: seed gates and replay coverage

Initiative: `20261001-mlperf-tiny-remaining-tuning`

Branch: `codex/20261001-mlperf-tiny-remaining-tuning`

## Findings addressed

- Every full-search invocation now validates the full one-sample seed report,
  including `--workload-index` and bounded runs. The shared gate checks exact
  model and geometry hashes, the TSIM single-call protocol, complete occurrence
  and seed-manifest coverage, bound manifest and native-record hashes, matching
  config/workload/fusion identities, positive integer cycle counts, and the
  inclusive 10% deployment cycle limit.
- Standalone replay now validates complete model occurrence coverage, status,
  model and geometry identity, protocol, config hashes, positive cycles, and
  local native-record hashes before replaying selected records.
- Added regression coverage for per-workload gate bypass, empty/partial and
  incomplete replay manifests, invalid or over-limit cycles, foreign report
  identities, and tampered or incomplete seed-manifest bindings.

## Verification

Commands ran from the repository root with the required project environment:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_two_stage_tuning.py
# 6 passed

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_two_stage_tuning.py
# 6 passed

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_two_stage_tuning.py
# 6 passed

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_two_stage_tuning.py
# 6 passed

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/tests/test_deployment_evidence.py
# 28 passed

./.envs/tvm-vta-env/bin/python -m py_compile \
  vta/apps/mlperf_tiny_benchmark/deployment_evidence.py \
  vta/apps/mlperf_tiny_benchmark/{anomaly_detection_v1,keyword_spotting_v1,streaming_wakeword_v1,visual_wake_words_v1}/tune/tune.py
git diff --check
git -C vta diff --check
# All passed
```

The committed seed reports and seed manifests were validated against freshly
prepared model occurrences with this project-environment command; it passed
for AD 9/9, KWS 4/4, Streaming Wakeword 1/1, and VWW 13/13 occurrences:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python - <<'PY'
import importlib.util
from pathlib import Path
root = Path('vta/apps/mlperf_tiny_benchmark').resolve()
models = ('anomaly_detection_v1', 'keyword_spotting_v1',
          'streaming_wakeword_v1', 'visual_wake_words_v1')
for model in models:
    app = root / model
    spec = importlib.util.spec_from_file_location(
        f'{model}_audit_tune', app / 'tune' / 'tune.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prepared, identities, tasks = module.legacy.prepare_v1_workloads()
    module._validate_alignment_report(
        app / 'tune' / 'deployment-seed.json', prepared, identities, tasks)
    print(f'{model}: committed seed alignment validated ({len(identities)} occurrences)')
PY
```

Standalone TSIM artifact replay passed for every committed full-search manifest:

| Model | Run ID | Replay result |
| --- | --- | --- |
| AD V1 | `20261001T174411.872234Z` | 9 artifacts validated |
| KWS V1 | `20261001T192416.141960Z` | 4 artifacts validated |
| Streaming Wakeword V1 | `20261001T205934.834798Z` | 1 artifact validated |
| VWW V1 | `20261001T220401.514781Z` | 13 artifacts validated |

Each replay used the model-local `tune/tune.py --replay-manifest` command with
`VTA_BACKEND=tsim`, the absolute shared geometry path, and the matching
model-local `PYTHONPATH`. All manifests reported `FULL_SEARCH`; total replay
coverage was 27/27 occurrences. Search and deployment measurements were not
rerun.

## Commit maps

The review-fix source commit began from root
`573521bfd7c8feb484b73baaae12cd6ec41b3c92`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`9e4935eda0ef229792218a7d02f60fda00531114`.

| Commit | Root | TVM | VTA | Scope |
| --- | --- | --- | --- | --- |
| Source fixes | `bb1dd66b5053da0273d7d5774f1fc50a7fc67a4b` | unchanged | `94587832a6406dc1596c8b9220fdd2f72eb093cd` | Shared gate/replay validation, four model adapters and regressions, command documentation |

The source-fix commit is clean. This evidence file is committed separately so
the source verification results and source commit map remain tied to the
reviewed implementation.
