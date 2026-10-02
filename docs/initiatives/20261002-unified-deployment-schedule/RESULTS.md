# Unified deployment schedule results

This report records the verified unified `run.py --schedule PATH|none` and
model-local `tune.py` workflow across all six MLPerf Tiny models. Generated
search ledgers and temporary runtime outputs remain under ignored `build/`
directories; this committed report records the evidence needed to interpret
them. Historical saved schedules are retained separately and are not treated
as measurements of the unified path.

## Fresh maintained gate (2026-10-02)

`scripts/test_vta_byoc.sh --env-name tvm-vta-env` completed successfully with
the configured VTA 64-MAC FSIM and TSIM libraries. It ran the six runtime paths
with `--schedule none` on the documented sample sets and both host codegens for
TSIM deployments. It also ran the retained shared-provider and cleanup
contracts, Python compilation, retired-reference scans, and scoped repository
checks. No test failures occurred.

| Gate group | Result |
| --- | ---: |
| BYOC structural tests | 311 passed |
| Shared providers, tuning, measurement, cleanup | 45 passed |
| Actual deployment-compute capture | 2 passed |
| Schedule artifact contracts | 8 passed |
| Historical schedule migration | 11 passed |
| FSIM core | 40 passed |
| Image classification V1 model tests | 36 passed |
| Visual wake words model tests | 67 passed |
| Image classification V2 model tests | 65 passed |
| Keyword spotting model tests | 42 passed |
| Anomaly detection model tests | 54 passed |
| Streaming wakeword model tests | 43 passed |
| TSIM core | 21 passed |
| Keyword spotting TSIM unit tests | 9 passed |
| Anomaly detection TSIM unit tests | 10 passed, 1 skipped |
| Streaming wakeword TSIM unit tests | 7 passed |

The single skip is the existing `test_end_to_end_tsim_matrix_contract_has_ten_five_five_results` guard in `anomaly_detection_v1/tests/test_tsim_deployment.py`. It runs only when `ANOMALY_TSIM_RUN_INTEGRATION=1`; the maintained gate separately exercised the real TSIM deployment with the documented one-window-per-sample budget. No tests were disabled or weakened to obtain this result.

The fresh default-schedule runtime runs passed output/sample checks. TSIM whole-model profiler counters (cycles) were:

| Model | TSIM result and sample policy | Cycles |
| --- | --- | ---: |
| Image classification V1 | 10 reference-checked samples | 36,328,640 |
| Image classification V2 | 10 reference-checked samples | 212,264,130 |
| Visual wake words V1 | 10 samples | 68,621,090 |
| Keyword spotting V1 | 12 committed WAV samples | 28,253,328 |
| Anomaly detection V1 | 10 samples, one representative window per sample; normal=5, anomaly=5 | 1,887,730 |
| Streaming wakeword V1 | 3 samples: Marvin=0, Silence=1, Unknown=2 | 523,899 |

These are model-level TSIM profiler totals, not standalone operator costs.
Anomaly and streaming counters follow their documented bounded sample
protocols and should not be compared directly with other model totals. FSIM
and HOST comparisons passed; no claim is made that a tuned candidate is faster
than the default.

## Actual-compute tune evidence

Earlier implementation checkpoints exercised each model's deployment compute
capture and the unified runtime with defaults, partial coverage, candidate and
best snapshots, seed/alignment, bounded search, resume, and candidate/best
exports. These are checkpoint results, distinct from the fresh full gate above.
The generated files are in each model's ignored
`build/actual_compute_tuning/` directory. The selected bounded-search ledgers
below preserve the exported candidate's config identity and TSIM single-call
measurement; the selected occurrence is one real graph-resident layer and is
not represented as a full-model schedule.

| Model | Evidence run (UTC timestamp id) | Selected real occurrence / config identity | Measured selected-layer cost |
| --- | --- | --- | ---: |
| Image classification V1 | `20261002T085815.289760Z` | `tvmgen_mlperf_resnet_vta_main_0` / `8cba25c1b01fb04a95b750413107e00c0bad3f384f53eab65e9200639c8d596f` | 688,638 cycles |
| Image classification V2 | `20261002T083349.950971Z` | `tvmgen_mlperf_resnet_large_vta_main_0` / `9f25d2cf25e66dadf24e36657cf946307229b39eb3e67e4561ede838963d9747` | 3,967,001 cycles |
| Anomaly detection V1 | `20261002T093034.907306Z` | `tvmgen_mlperf_anomaly_vta_main_0` / `b36f0e8f19d9f3f4d07297e2ea9e1d8392a38d474f66bf23a2ce5400a854f25f` | 16,813 cycles |
| Keyword spotting V1 | `20261002T095611.486088Z` | `tvmgen_mlperf_kws_vta_main_0` / `45fd3486b7ece0eca147ce2d01f68d4461b753b83ae8bea89f8cb19e63dcf2` | 588,611 cycles |
| Streaming wakeword V1 | `20261002T101631.968384Z` | `tvmgen_mlperf_streaming_wakeword_vta_main_0` / `8f737c689e8c6a961006f65487d96eb2af329e9bbd468293c876bafd5a282ac6` | 174,633 cycles |
| Visual wake words V1 | `20261002T110129.770771Z` | `tvmgen_mlperf_vww_vta_main_0` / `2dfa656671f187adff27fc80d946ae33c9fd100289aac8abbc8e234ec8208b44` | 499,550 cycles |

Each listed ledger records one configuration (index 0) for the identified
actual occurrence and successful FSIM then `tsim_single_call_v1` measurement.
The exported best snapshot marks that occurrence measured and carries the same
record/configuration; its sidecar binds it to the model, geometry, compute and
config-space hashes. These identities prove schedule selection/application
inputs, not a cross-model performance ranking. Defaults, partial coverage,
candidate export, best export and full-coverage behavior are also covered by
the model integration tests and the earlier checkpoint runs; the fresh gate
specifically revalidates default `none` execution.

## Migration and cleanup

Historical full-fusion manifests were migrated for all six models with
`common.schedule.migrate_legacy_full_fusion`; converted per-occurrence costs
matched the retained reports. The migration, artifact and prior calculator
focused checks recorded 11 migration tests, 8 artifact tests, and 14
calculator tests plus 11 subtests. Migration validates provenance and does not
reinterpret historical reports as new-path measurements.

The cleanup fixture suite passed 15 tests. Its dry-run inventory contained
1,351 files (861,747,813 bytes), 178 unknown files, and zero retention errors;
173 tracked files were retained unchanged. No user outputs were deleted during
fixture verification.
