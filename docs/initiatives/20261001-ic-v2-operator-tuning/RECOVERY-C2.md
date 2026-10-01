# Approved C2 recovery

Initiative: 20261001-ic-v2-operator-tuning.

The user explicitly approved a fresh Default taking over the unfinished, uncommitted T4 deployment.py modification after Root reported project-not-clean and the committed-handoff restriction. This is a one-time exception to Default clean-start and committed-only handoff for C2 recovery; preserve the existing diff as task input, inspect it, and correct it rather than resetting or discarding it. Root has also updated approved lifecycle artifacts for the user-authorized one-sample performance gate followed by ten-sample correctness-only execution. The recovery Default may verify and commit these authorized documentation changes with its attributable T4 recovery commit. No further approval is needed for in-scope fixes.

Committed map: root 31094bf6c351660bcbba8a876a840172d7e52bcf, tvm 9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca, vta 8fe1032a92f872109c491f5545d128624e9b3a60; branch codex/20261001-ic-v2-operator-tuning. Unfinished input: vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/deployment.py plus these authorized documentation edits.

T3 was committed but actual T4 verification exposed artifact-field/import mistakes and 7/8 cycle mismatches. Existing bounded records: /tmp/ic-v2-c2-artifacts/best-manifest.json; failure evidence: /tmp/ic-v2-c2-deployment.failure.json. Keep failure evidence.

Root inspection shows V2 deployment passes a native log containing ic_v2_fused_conv2d.vta records to HistoryBest; actual deployed Conv lowering queries conv2d_packed.vta. V1 instead uses _selected_occurrence_lowering and per-symbol ApplyConfig with cleared TECompiler cache. Establish the actual cause and adopt occurrence-scoped dispatch with verifiable config attribution, rather than assuming HistoryBest finds a different workload key.

The uncommitted run_individual_node counter /2 approach violates the approved warmup-excluded single-call protocol. Replace it with genuine single-node, single-counted-invocation measurement (the proven V1 direct _execute_node path is a reference); do not divide a two-invocation count. Verify ordinary/debug complete-run agreement on the one sample.

Complete T4 with the existing valid bounded records if they remain protocol/identity-valid; there is no need to rerun searches solely for the validation-order clarification. First make all eight comparisons pass on one sample; only then execute ten samples for correctness. Complete focused meaningful regressions and command docs, write CHECKPOINT-C2.md, verify then commit via git-workflow and return GREEN with exact OIDs and clean state. If fixes require lowering/compiler changes within approved model arithmetic/routing and C2 paths, fix and test them rather than treating ordinary bugs as user gates.
