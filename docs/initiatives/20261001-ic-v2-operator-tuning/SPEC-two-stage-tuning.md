# Spec: IC V2 two-stage tuning

## Objective
Implement IC V1-equivalent complete fusion tuning for image_classification_v2, then run the full search. Current prepared routing requires eight distinct VTA Conv fusion occurrences; identical shapes must not collapse occurrence identities.

## Assumptions and fixed inputs
Use the committed ResNet-8 Large model, SHA-256 fb17ae9c1b6d0e5bd97f0f35024f207556261d7310b249716c87cc0628214b0e. Preserve its global_scale=8.0 quantization, skip_conv_layers=[0], eight VTA partitions and host boundaries. Geometry is vta/config/vta_64mac.json. Reuse V1 algorithms where appropriate, with explicit model identity and import isolation; no V1 records may masquerade as V2 records.

## Stack and structure
Existing project Python 3.11 environment, repository TVM v0.17.0, VTA and AutoTVM. Add IC V2 complete-fusion extraction and tune/ entry points, focused tests under image_classification_v2/tests/. Shared helpers may be factored within mlperf_tiny_benchmark if necessary; preserve V1 interfaces. Document maintained entry points in scripts/README.md and the V2 README.

## Behavior and provider contract
- Extract actual prepared fusion arithmetic, tensor shapes, dtypes, constants, layouts and occurrence/symbol identity. Include bias when present, right shift, clip and cast; unsupported fusions fail explicitly.
- Default full search mirrors V1: distinct valid configurations in 100-trial FSIM batches until at least 20 distinct successes per occurrence or valid space exhaustion; measure every FSIM success on TSIM. Separate backend processes and default per-candidate timeouts of 60 s FSIM and 120 s TSIM.
- Select minimum positive successful TSIM cost among valid configurations that lower for the actual fusion. Record any lowering rejection with its reason. Do not substitute a slower configuration to hide measurement discrepancies.
- Preserve TSIM single-call v1 protocol: one formal counted invocation, warmup excluded, profiler cleared, number=1, repeat=1, min_repeat_ms=0. Native cycle costs are not divided by two.
- Support --all, --workload-index, --trial-batch, --min-successful, --fsim-timeout, --tsim-timeout, --max-workloads, --resume-manifest, --artifact-dir and --replay-manifest equivalent to V1. Bounded runs remain visibly incomplete.
- Persist intermediate native logs, failure details and resume state under V2/build/two_stage_tuning/. Export best native records, result JSON and best-manifest.json under V2/tune/optimal/<run-id>/.
- Self-contained replay and deployment consume only exported artifacts. Validate model, backend, geometry hash, fusion/workload/config identity, occurrence coverage, native record hashes and measurement protocol. Reject mismatched, tampered, incomplete or foreign-model artifacts before applying schedules.

## Commands
All commands run from repository root. Full implementation target:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/tune.py --all
```
Focused verification:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests -q
```
For backend-specific integration tests, use a separate process with VTA_BACKEND=tsim and the same geometry. A smoke run may precede the full search but cannot satisfy final acceptance.

## Code style
Follow existing Python naming and explicit validation, e.g.:

```python
if result["model_sha256"] != prepared.imported.model_sha256:
    raise ValueError("selected record does not match the prepared IC V2 model")
```
Use deterministic canonical identities and atomic durable state updates. No new dependencies.

## Testing strategy and success criteria
Test extraction against actual prepared V2 routing and complete arithmetic; configuration uniqueness, batching, exhaustion, failures and resume; record selection and integrity checks; cross-model rejection and self-contained replay. Run actual bounded backend smoke, then complete all eight occurrences using the default full-search criteria. Export complete replayable artifacts and record measured counts/cycles and failures. Run affected V1 regressions if helpers are shared.

## Boundaries
Always preserve model arithmetic, V1 compatibility, full candidate evidence and backend separation. Never lower the success target, omit occurrences, label a bounded search complete or fabricate measurements. Escalate missing permissions/environment or changes to approved scope under Root policy. Implementation and verification are delegated after Plan/Tasks approval.

## Open questions
None. Implementation may determine the smallest safe sharing boundary without changing this contract.
