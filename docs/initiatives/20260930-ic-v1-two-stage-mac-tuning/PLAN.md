# Plan: IC V1 two-stage MAC tuning

## Initiative and approved inputs
Initiative: 20260930-ic-v1-two-stage-mac-tuning.
Branch for all managed repositories: codex/20260930-ic-v1-two-stage-mac-tuning.
Inputs: INTENT.md, CAPABILITY_MAP.md and all three SPEC-*.md files in this directory; user approved specifications on 2026-09-30.

Original bases:
- .: c1050b8a048f1b028b009fbb7e05ea7840cb4ae2
- tvm: 9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca
- vta: d91fdae82c2cc98f1b090791dc1efaf0937da112

## Approach
Build and verify the risky computation/measurement path first, then adaptive search, deployment validation and generic reporting. Run actual full tuning only after bounded smoke verification establishes that candidate failures do not corrupt runner state. Use fresh Default agents sequentially at the checkpoint boundaries in TASKS.md; each task is independently verified and committed. Root does not implement or take over delegated tasks. A fresh Reviewer evaluates the full committed range after all checkpoints; findings proceed through automatic Fix/Verify/Re-review.

## Architecture decisions
- Reuse model preparation and real fusion lowering. Compare task computation against deployed fusion including postprocessing, tensor ordering and logical MAC accounting. Avoid creating a second approximate model implementation.
- Tune per real occurrence by default. Sharing searches is optional only with proven identical semantic and schedule identities. Distinct occurrence mappings survive reporting.
- Place maintained tuning code and exported optimal artifacts under IC V1/tune/. Keep native intermediate logs, resume manifests, raw profile data and builds in IC V1/build/. Best exports must replay without build/ inputs.
- Separate FSIM and TSIM processes, retain search visited state across batches and resume, use a local runner lifecycle that recovers from candidate failures and cleans owned RPC resources. Record infrastructure failures separately; do not count them as valid search progress or successful schedules.
- Dispatch every distinct FSIM success for TSIM AutoTVM measurement. Select by positive native TSIM cycles, not FSIM elapsed time. Conflicting occurrence choices for the same deployment dispatch key require a correct occurrence-specific application mechanism, not silent last-record wins.
- Collect operator cycles from actual full-model execution with validated instrumentation and compare to the selected candidate. Whole-model cycles come from an uninstrumented complete inference with warmup excluded; operator sum and residual are separate values.
- Export a versioned deployment measurement contract for scripts/mac_utilization.py. The calculator treats model IDs as data and uses no model loader/allowlist. Preserve scalar CLI compatibility.
- Default validation host codegen is the existing deployment default (LLVM). Keep existing C deployment behavior usable and run affected tests; tuning need not be duplicated for host codegen.

## Ordered execution
1. Checkpoint C1: computation/RPC measurement foundation (T1–T2).
2. Checkpoint C2: adaptive all-workload search and optimal export (T3–T4).
3. Checkpoint C3: real deployment profiling and generic reporting (T5–T6).
4. Checkpoint C4: complete real search, deployment acceptance and final evidence (T7–T8).

TASKS.md is the authoritative checklist and task/commit granularity. Execution agents record completion and exact per-repository commit maps in checkpoint evidence files under this initiative directory; approved PLAN.md/TASKS.md are Root-owned and are not rewritten by executors.

## Environment and verification
Use only .envs/tvm-vta-env/bin/python for project Python. Existing Python, TVM libraries and FSIM/TSIM/hardware libraries are present; validate loading/ABI in the smoke rather than assuming file existence proves compatibility. Every simulator process gets absolute VTA_CONFIG_FILE and explicit matching VTA_BACKEND. Reuse documented build/test entry points if repair is needed. No environment recreation or model downloads are planned.

All task tests precede commits. Run the relevant unit/structural tests and real bounded smoke early, then full search and deployment once tooling is ready. Run affected IC V1 deployment regression checks and required project BYOC gate at final verification. If required infrastructure or permissions are unavailable, return evidence and escalate; do not mark acceptance complete.

## Risks and mitigations
| Risk | Mitigation |
|---|---|
| Many invalid configurations or simulator aborts | Preserve visited state, fresh/recoverable owned RPC lifecycle, distinct failure classification, checkpointed resume. |
| Local sockets/subprocess restrictions | Reproduce exact operation, request supported sandbox escalation, retain logs; never silently replace the requested runner. |
| Task differs from real fusion or dispatch config leaks | Structural/runtime equivalence tests, explicit occurrence mapping, cache clearing and verification of applied configurations. |
| Profiling changes cycles or aggregate counters hide operators | Collect counters at real invocation boundaries, verify profile sum/residual and full inference equivalence; fix discrepancies before acceptance. |
| Long search with no fixed trial cap | Save progress after batches and measurements, report counts/space sizes and exhaustion; duration depends on actual invalid candidates. |
| Optimal exports depend on intermediates | Package selected native records plus validated metadata, test replay with build artifacts unavailable. |
| Tuning gives little or no improvement | Report actual baseline/tuned values and best measured schedules; no fabricated gain or lowered cycle threshold. |

## Boundaries and open questions
No unresolved product questions. Exact artifact schema/filenames are implementation details constrained by approved specs. Preserve model assets, quantization, hardware geometry, existing unrelated commands and quality gates. Changed approved decisions require Root escalation. Permission/credential/external-state blockers are escalated with exact evidence. Reviewer Pass ends implementation; user performs optional merge manually.
