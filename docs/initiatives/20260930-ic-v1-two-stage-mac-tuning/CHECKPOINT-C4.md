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
| `.` | `da4804af4f8bfe97f7e6dd4e2ac9afe8c8f358fd` | this evidence file and VTA gitlink |
| `tvm` | unchanged | — |

## T8 — Final deployment and acceptance

Pending execution after T7 is committed.
