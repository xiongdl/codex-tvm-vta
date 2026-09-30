# Checkpoint C4 evidence

Initiative: `20260930-ic-v1-two-stage-mac-tuning`
Delegation: Default, C4 (T7 then T8)
Branch: `codex/20260930-ic-v1-two-stage-mac-tuning` in `.`, `tvm` and `vta`
Approved inputs: initiative `INTENT.md`, `CAPABILITY_MAP.md`, all three
`SPEC-*.md` files, `PLAN.md` and `TASKS.md`.

## C4 starting commit map

| Repository | Starting OID |
|---|---|
| `.` | `65bbeb24eb62f7573c9ec35534fe4f9c3d1da099` |
| `tvm` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| `vta` | `90cbe11210a6711393f09ce445f83d6f0abc9c42` |

## T7 — Full FSIM to TSIM tuning

The full search covered all eight ordered model fusion occurrences, using
100-trial FSIM increments, a quota of 20 distinct successful schedules,
60-second FSIM and 120-second TSIM timeouts. Every distinct FSIM success has a
TSIM measurement. All workloads reached the success quota; none exhausted its
valid search space. Each workload was measured over its entire last 100-trial
batch, including candidates after the quota was reached.

| Workload | Valid configs | FSIM attempts | FSIM successes | TSIM candidates | Stop reason | Selected config | Selected TSIM cycles |
|---:|---:|---:|---:|---:|---|---:|---:|
| 0 | 576 | 200 | 24 | 24 | success quota | 309 | 51,299 |
| 1 | 576 | 200 | 21 | 21 | success quota | 105 | 54,144 |
| 2 | 600 | 100 | 25 | 25 | success quota | 209 | 11,507 |
| 3 | 600 | 300 | 29 | 29 | success quota | 221 | 26,955 |
| 4 | 900 | 300 | 25 | 25 | success quota | 243 | 44,451 |
| 5 | 768 | 200 | 39 | 39 | success quota | 301 | 7,097 |
| 6 | 768 | 200 | 21 | 21 | success quota | 446 | 22,961 |
| 7 | 1,024 | 400 | 25 | 25 | success quota | 653 | 41,752 |

Workload 1's fastest TSIM candidate (config 106, 53,124 cycles) fails lowering
for the real fusion because its accumulator allocation exceeds VTA hardware
capacity. The exporter now validates TSIM candidates from lowest cycle count
upward against the real fusion and exports the fastest lowerable one. Config
105 is the next measured candidate and lowers successfully. The other seven
workloads retain their fastest measured TSIM candidate. The rejected config
and lowering reason are recorded in its result JSON. No FSIM/TSIM search data
was discarded or substituted.

The long-running search process survived an interruption while workload 4 was
in progress. Work resumed from the saved manifest and per-workload states;
completed candidate counts and native logs were reused rather than searched
again. All eight final manifest entries report complete TSIM measurements.
Malformed candidates that abort isolated FSIM child processes remain recorded
as candidate failures; each process recovered for the next candidate. The
search manifest records all worker return codes as zero, is `FULL_SEARCH`,
and is not bounded.

The export exposed two correctness gaps in the prior modules. Real occurrence
lowering now clears TECompiler state before and after each call, and its
multi-occurrence test verifies the per-call cache boundary. The exporter also
rejects a TSIM-measured candidate if it cannot lower against its actual VTA
fusion, then selects the next-fastest measured, lowerable configuration. Unit
tests first failed before the cache clear was added, and passed after the fix.

Raw per-trial and per-candidate data remains at
`vta/apps/mlperf_tiny_benchmark/image_classification_v1/build/two_stage_tuning/c4-full/20260930T120956.692567Z/`.
The self-contained selected native records and JSON manifest are at
`vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/optimal/c4-full/`.
The manifests include model/geometry/fusion identities, selected config and
record hashes, logical MACs, counts, stop reasons, and TSIM failures. Narrow
`.gitignore` exceptions retain these requested JSON/log artifacts in Git while
leaving other generated outputs ignored.

### T7 verification

Project Python: `.envs/tvm-vta-env/bin/python`.

- Full command: `python tune/tune.py --all --trial-batch 100 --min-successful 20 --fsim-timeout 60 --tsim-timeout 120`; completed all eight workloads. Export was resumed from the same complete manifest after fixes; candidate and native-record counts remained unchanged.
- `python tune/tune.py --replay-manifest tune/optimal/c4-full/best-manifest.json`: passed; all 8 self-contained results replayed and lowered.
- `pytest -q tests/test_fused_tuning.py tests/test_tune.py tests/test_two_stage_tuning.py`: 39 passed.
- Native TSIM selected-record checks and hash/identity replay validation passed for all 8 entries.
- Full tests, deployment comparisons, utilization report, and BYOC gate are recorded under T8 below after execution.

### T7 implementation and artifact commits

| Repository | T7 commit OID | Paths |
|---|---|---|
| `vta` | `98824287875053ddc7bd28617098ad9e6a00c651` | IC V1 TECompiler-cache correction and candidate validation; focused regression tests; full optimal manifest/results/native TSIM records; narrow `.gitignore` exceptions |
| `.` | `da4804af4f8bfe97f7e6dd4e2ac9afe8c8f358fd`, `aa307dadb6c2fe75147aac6dfd8dab629e9dc02b` | evidence and gitlink, then exact T7 commit-map update |
| `tvm` | unchanged | — |

## T8 — Final deployment and acceptance

The final T7 selected manifest was applied as a real baseline and tuned TSIM
deployment over all ten committed samples. Every tuned output exactly matched
the pure HOST output. Debug and ordinary Graph Executor cycle counts matched.
The tuned VTA occurrence sum is 275,137 cycles per sample and the matching
ordinary full-model count is 275,137, leaving zero residual. The uninstrumented
ten-sample whole-model counts are 38,757,180 baseline and 2,751,370 tuned.

The first deployment run rejected two minimum-cycle schedules at the fixed
10% comparison limit:

| Occurrence | First selected TSIM cycles | Real cycles | Difference | Final measured config | Final TSIM cycles | Final real cycles | Difference |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 11,507 | 12,961 | 12.6358% | 64 | 14,338 | 15,573 | 8.6135% |
| 5 | 7,097 | 7,833 | 10.3706% | 111 | 7,980 | 8,547 | 7.1053% |

These replacements came from the already TSIM-measured candidates; the complete
search was not repeated. The final selected result JSON records both the
minimum observed TSIM cycles and the deployment-qualified selected cycles.
All eight final comparisons are 1.7436%–8.6135%.

| Occurrence | MACs / invocation | Final TSIM cycles | Deployed cycles | Difference | Deployed MAC utilization |
|---:|---:|---:|---:|---:|---:|
| 0 | 2,359,296 | 51,299 | 54,229 | 5.7116% | 67.9784% |
| 1 | 2,359,296 | 54,144 | 56,301 | 3.9838% | 65.4766% |
| 2 | 131,072 | 14,338 | 15,573 | 8.6135% | 13.1510% |
| 3 | 1,179,648 | 26,955 | 28,411 | 5.4016% | 64.8763% |
| 4 | 2,359,296 | 44,451 | 45,907 | 3.2755% | 80.3015% |
| 5 | 131,072 | 7,980 | 8,547 | 7.1053% | 23.9616% |
| 6 | 1,179,648 | 22,961 | 23,689 | 3.1706% | 77.8083% |
| 7 | 2,359,296 | 41,752 | 42,480 | 1.7436% | 86.7797% |

The generic deployment calculator reports 12,058,624 logical MACs per sample,
whole-model utilization of 4.8614% baseline and 68.4808% tuned, 63.6193
percentage-points gain, and 14.0865× cycle speedup. Its JSON output uses actual
uninstrumented full-model cycles; it does not infer whole-model utilization
from the sum of VTA node counts. The readable result is
`vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/REPORT-C4-FULL.md`;
versioned deployment and calculator output are
`tune/deployment-c4-full.json` and `tune/mac-utilization-c4-full.json`.

The required same-process TSIM regression was fixed. `SimulatorSession` now
validates the backend through the pure `vta.backend.normalize_backend`
selector, not the `vta.testing.simulator` module whose import eagerly loads the
environment-selected native simulator. Previously the wrong-environment test
could load FSIM, after which the final real TSIM graph test loaded TSIM in the
same process and Graph Executor aborted. A fresh-process regression test fails
if backend mismatch validation imports the simulator module. The root-cause
test first failed and then passed after the change; the complete TSIM profile
and deployment suite now passes in one process.

The HOST/FSIM suite also exposed that the older single-workload `tune.py`
left `VTA_BACKEND=tsim` in its caller after measurement, making following FSIM
tests fail their backend check. It now restores the prior selector (including
when TSIM setup or cleanup raises). The tuning test verifies FSIM is restored;
it first failed before the fix and passed after it.

### T8 verification

Project Python: `.envs/tvm-vta-env/bin/python`.

- Final `tune/deployment.py --best-manifest tune/optimal/c4-full/best-manifest.json`: passed; all ten outputs matched HOST, 8/8 per-occurrence errors stayed below 10%, and debug/full-model profiling agreed.
- `scripts/mac_utilization.py --deployment-report tune/deployment-c4-full.json --output-json tune/mac-utilization-c4-full.json`: passed; whole-model, utilization, MAC counts and gains reconcile with the deployment artifact.
- `tune/tune.py --replay-manifest tune/optimal/c4-full/best-manifest.json`: passed; all 8 results replayed after deployment-qualified candidates were selected.
- Full IC V1 HOST/FSIM group (`test_fused_tuning.py`, `test_tune.py`, `test_two_stage_tuning.py`, `test_model_pipeline.py`, `test_host_deployment.py`): 70 passed.
- Full IC V1 TSIM/profile group (`test_deployment_profile.py`, `test_tsim_deployment.py`): 13 passed in one process, including the formerly aborting end-to-end matrix test.
- JSON syntax validation passed for deployment and utilization reports. BYOC gate is pending.

The first complete BYOC attempt stopped during its structural suite with 20
failures in two older test modules: channel near-misses and packed output
shapes assumed a fixed block width of 16, while the documented `vta_64mac.json`
geometry uses 8. The fixtures now derive invalid channel counts and packed
tensor dimensions from `vta.get_env()`. With the unchanged approved geometry,
`pytest -q vta/tests/python/unittest/test_byoc_partition.py vta/tests/python/unittest/test_byoc_lowering.py`
passes all 202 tests. The complete gate is being rerun on a clean committed
tree.

After that correction, the full gate passed the BYOC structural suite (311),
standalone FSIM suite (40), and ResNet V1/VWW V1/ResNet V2 HOST/FSIM suites
(38/66/62). It then exposed a gate-command environment mismatch: the anomaly
detection TSIM-only unit file had been run in the earlier FSIM phase with
`VTA_BACKEND=fsim`, and correctly rejected this. The command now runs the same
TSIM test file in the TSIM phase with `VTA_BACKEND=tsim`; its direct focused run
passes 9 tests with 1 documented skip. The complete gate is being rerun after
this environment-routing correction.

T8 implementation, deployment-qualified results, README and report await the
verified task commit; final BYOC results will be appended afterward.
