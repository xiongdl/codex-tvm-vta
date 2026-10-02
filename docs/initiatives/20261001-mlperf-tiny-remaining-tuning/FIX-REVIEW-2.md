# Review 2 fixes: gate dispatched tuning workers

Initiative: `20261001-mlperf-tiny-remaining-tuning`

Branch: `codex/20261001-mlperf-tiny-remaining-tuning`

## Finding addressed

The hidden `--worker-backend` entry point previously bypassed the parent
process's seed alignment check, and parent dispatch did not pass the report to
workers. Full-search FSIM and TSIM workers now require and independently
validate the complete seed deployment report against the freshly prepared
model, all occurrence/workload/fusion identities, active geometry, bound seed
manifest/native records, and the `tsim_single_call` protocol before entering
backend measurement code. Parent dispatch passes the validated report to both
workers. Seed workers receive an explicit `--seed` marker; the seed path stays
separate and cannot use an alignment report. Setting `--min-successful 1`
alone does not enter seed mode.

Added regressions for all four model adapters. They cover direct FSIM and TSIM
worker rejection without a report, malformed/foreign/incomplete report
rejection before backend dispatch, actual valid parent validation and report
propagation to both backend workers, and explicit seed worker dispatch.

## Verification

Each of the four focused model-local tuning suites passed: **14 passed** for
AD V1, **14 passed** for KWS V1, **14 passed** for Streaming Wakeword V1, and
**14 passed** for VWW V1. Commands used `.envs/tvm-vta-env/bin/python`, the
shared absolute `vta_64mac.json` configuration, explicit `VTA_BACKEND=fsim`,
and the matching model-local Python path. For example:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_two_stage_tuning.py
```

The four committed seed deployment reports were revalidated against freshly
prepared model graphs: AD **9/9**, KWS **4/4**, Streaming Wakeword **1/1**,
VWW **13/13**, totaling **27/27** occurrences. All committed optimal manifests
were independently replayed under TSIM: **9 + 4 + 1 + 13 = 27** artifacts,
each labeled `FULL_SEARCH`. No search, deployment measurement, or ten-sample
run was repeated.

`py_compile` passed for all four adapters and their focused test files.
`git diff --check` passed in root and VTA repositories.

## Commit maps

The fix began from root `6732081271a6cec07ae30621c18259ad106ac562`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`94587832a6406dc1596c8b9220fdd2f72eb093cd`.

| Change | Root commit | TVM commit | VTA commit | Committed paths |
| --- | --- | --- | --- | --- |
| Worker gate and regressions | `37273cea0110ba5bf93d2ee686cb17dc354c9066` | unchanged | `a24152a6875b4fe09d3d43a150bac3727b435688` | Four model-local `tune.py` adapters and `tests/test_two_stage_tuning.py` files |
| Review evidence | recorded after this file is committed | unchanged | unchanged | `docs/initiatives/20261001-mlperf-tiny-remaining-tuning/FIX-REVIEW-2.md` |

The source-fix commit updates the root VTA gitlink to the committed worker
changes. This evidence file is committed separately so its verification and
source commit map remain attributable.

## Limits

The regression tests stop before simulator candidate execution after proving
that each worker's gate admits or rejects the intended request. The completed
seed reports and optimal artifacts were validated/replayed without rerunning
FSIM searches or deployment measurements.
