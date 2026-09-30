# Checkpoint C3 evidence

Initiative: `20260930-ic-v1-two-stage-mac-tuning`
Delegation: Default, C3 (T5 then T6)
Branch: `codex/20260930-ic-v1-two-stage-mac-tuning` in `.`, `tvm` and `vta`
Approved inputs: initiative `INTENT.md`, `CAPABILITY_MAP.md`, all three
`SPEC-*.md` files, `PLAN.md` and `TASKS.md`.

## C3 starting commit map

| Repository | Starting OID |
|---|---|
| `.` | `69fadb59125adf3e24adfe289c3f47da24e22196` |
| `tvm` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| `vta` | `59d6b2abf12d368d5b4d33c2ea615412f27d7aa4` |

## T5 — Selected schedules and real deployment profile

`tune/deployment.py` validates the self-contained best manifest against the
prepared IC V1 model, geometry, occurrence identities, TSIM protocol and native
records. It applies each selected configuration at the existing VTA
Relay-to-TIR callback, scoped by the fusion's global symbol. The TE compiler
cache is cleared between occurrence lowerings, so repeated Conv shape keys do
not silently reuse another occurrence's schedule. The original compiler
callback is restored after build.

The selected build and baseline build both run as real deployed mixed graphs.
All ten committed outputs matched the pure HOST reference. Full-model cycle
counts come from ordinary, uninstrumented Graph Executor runs. Per-occurrence
counts come from executing the matching VTA graph node with graph-resident
inputs in the debug executor. A debug full-graph run matched the ordinary
single-sample cycle count exactly; summed per-occurrence cycles also matched
the one-sample tuned full-model count, leaving zero residual for this graph.
Per-occurrence comparisons use `abs(deployment - AutoTVM) / AutoTVM`.

Bounded FSIM search (`trial-batch=1`, quota 1) visited 1, 12, 2, 3, 39, 8, 7
and 2 candidates for occurrences 0–7. Each found one distinct valid schedule;
TSIM measured each selected schedule once. Valid configuration spaces ranged
from 576 to 1,024. The run is explicitly `BOUNDED_SMOKE_INCOMPLETE`; it is not
the full tuning run assigned to C4. Candidate simulator child crashes were
recorded as FSIM failures and subsequent candidates continued successfully.

The versioned report is generated at
`vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/deployment-c3-bounded.json`
and is ignored generated output. The bounded selected manifest and intermediate
native records are under the IC V1 `tune/optimal/c3-bounded-all/` and
`build/c3-bounded-tuning/` directories respectively.

| Occurrence | Selected AutoTVM cycles | Deployed cycles | Relative difference |
|---:|---:|---:|---:|
| 0 | 102,907 | 112,475 | 9.2977% |
| 1 | 57,280 | 59,545 | 3.9543% |
| 2 | 12,832 | 13,911 | 8.4087% |
| 3 | 33,299 | 34,540 | 3.7268% |
| 4 | 45,073 | 46,529 | 3.2303% |
| 5 | 72,709 | 79,314 | 9.0842% |
| 6 | 36,625 | 38,006 | 3.7706% |
| 7 | 120,412 | 123,190 | 2.3071% |

On ten committed samples, uninstrumented full-model TSIM cycles were
**38,757,180 baseline** and **5,075,100 tuned**. The matching single-sample
tuned deployment was 507,510 cycles. Per-occurrence logical MAC counts and
cycles, config/workload hashes, geometry, full-model counts, and profiling
scope are included in the JSON contract.

### T5 verification

Project Python: `.envs/tvm-vta-env/bin/python`.

- `py_compile tune/deployment.py`: passed.
- `pytest -q tests/test_deployment_profile.py`: 4 passed.
- `pytest -q tests/test_deployment_profile.py tests/test_tsim_deployment.py -k 'not end_to_end_tsim_matrix_with_reloaded_graph_bundles'`: 11 passed, 1 deselected.
- Real `tune/deployment.py --best-manifest ... --output ... --build-dir ...`: passed; 8/8 occurrence comparisons were at or below 10%; all ten output comparisons passed; debug and ordinary full-model cycles matched.
- The existing `test_end_to_end_tsim_matrix_with_reloaded_graph_bundles` passed alone in 57.11s. Running the full `test_tsim_deployment.py` file in one process reproducibly segfaulted in Graph Executor on its final end-to-end test. The crash also occurs with only the existing test file and is absent in the bounded deployment command above. The full-file failure remains a known TSIM test-process risk.

T5 implementation commit OIDs are recorded in the C3 handoff.
