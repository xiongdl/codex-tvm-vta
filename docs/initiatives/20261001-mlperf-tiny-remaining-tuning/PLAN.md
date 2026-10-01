# Plan: remaining MLPerf Tiny tuning

Initiative: 20261001-mlperf-tiny-remaining-tuning
Branch: codex/20261001-mlperf-tiny-remaining-tuning
Intent confirmed and Specify batch approved by user on 2026-10-01.

## Execution design
Build a focused shared implementation for the four remaining models, reusing proven IC fusion extraction, native AutoTVM measurement and selected-symbol lowering where compatible. Keep existing IC interfaces and policies unchanged. Implement Dense as well as Conv using actual prepared fusion arithmetic. Each model adapter records its own identities, routing, sample and reference semantics.

Seed and full search are separate phases. Full search requires a complete passing seed deployment report bound to model, geometry, workload, configuration and measurement identities. Each model proceeds through seed → deployment alignment → FSIM full search → TSIM candidate selection → optimal deployment → utilization. No full search starts before that model's seed gate. Simulator processes and checkpoint agents run sequentially.

## Task index and dependency order
C1 (T1–T3): shared complete-fusion tuning and gate-capable deployment infrastructure.
C2 (T4–T6): AD adapter and real seed gate.
C3 (T7–T8): AD full search and selected deployment.
C4 (T9–T11): KWS adapter and real seed gate.
C5 (T12–T13): KWS full search and selected deployment.
C6 (T14–T16): Streaming Wakeword adapter and real seed gate.
C7 (T17–T18): Streaming Wakeword full search and selected deployment.
C8 (T19–T21): VWW adapter and real seed gate.
C9 (T22–T23): VWW full search and selected deployment.
C10 (T24–T25): four-model summary and final regression evidence.
TASKS.md is the authoritative task list.

## Verification
Use only the project environment and commands in the approved specs/scripts README. Test behavioral contracts with focused pytest tests, then real seed and full simulator runs. Seed and selected deployment both use one sample, exact <=10% comparison and debug/ordinary counter agreement. Full search evidence must enumerate unique attempts, successes, TSIM outcomes and space exhaustion. All exported selected artifacts must replay without build intermediates. Record exact commands, counts, identities, cycles, MACs and per-repository commit maps in checkpoint evidence.

Each task is a separate verified commit; each checkpoint gets a fresh Default agent. After all checkpoints, a fresh Reviewer assesses the complete committed ranges; findings go to a fresh Default and then a fresh Reviewer. Approval of this plan authorizes this automatic lifecycle. Root does not merge.

## Ownership and scope
Implementation: benchmark-local shared helpers, four model apps and their tests; scripts/mac_utilization.py and its focused tests for compatibility if needed; scripts/README.md and model READMEs. Existing IC helpers may be narrowly reused or adjusted with regressions. TVM/VTA compiler changes are permitted only when necessary to preserve the approved real-arithmetic/config-lowering contract and are verified with scoped regressions; no unrelated runtime redesign.
Root owns approved lifecycle artifacts. Default may write checkpoint evidence but must not revise approved decisions. Generated native record/result batches are deliverables, not source task sizing; keep raw builds/logs ignored. Small source tasks below have at most five primary maintained files. If an implementation needs a larger independent source change, return Root escalation rather than silently combine tasks.

## Risks and mitigations
| Risk | Mitigation |
| --- | --- |
| Dense or a different fusion is unsupported by IC helpers | Test actual prepared extraction early; implement faithful template, fail explicitly if impossible within scope |
| Model imports collide | Isolate adapters/import identities; test foreign-model rejection |
| TSIM cost differs due to measurement scope or state | Compare complete arithmetic, exact configuration and cleared single-call windows; preserve state initialization; retain failure evidence |
| FSIM search has few successes | Add 100 distinct trials until quota or proved exhaustion; never lower quota |
| Long-running searches or RPC infrastructure failure | Persist state and logs atomically; resume with identity checks; classify infrastructure errors separately |
| Model/data/library unavailable | Check existing assets/environment before simulator work; escalate user-only missing state |
| MAC report rejects new schema | Emit compatible versioned report or narrowly extend validator with regression tests |
| Regression in IC V1/V2 | Run affected extraction/tuning/deployment tests, preserving their threshold and sample defaults |

## Open questions
None. No parallel agents or simulator jobs. Final reviewed artifacts and commit maps are delivered; user owns optional merge.
