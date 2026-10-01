# Checkpoint C4: KWS adapter and seed gate

Initiative: `20261001-mlperf-tiny-remaining-tuning`<br>
Branch: `codex/20261001-mlperf-tiny-remaining-tuning`<br>
Status: **GREEN**

## T9: complete-fusion adapter

The KWS adapter prepares the committed model through its existing model
pipeline, maps all four routed VTA symbols to distinct complete fused tasks,
and retains KWS HOST operators in the host inventory. AutoTVM tasks include
Conv, per-channel bias, right shift, clipping and cast. The KWS model identity
is bound into all durable states and manifests; foreign-model replay is
rejected. The CLI exposes seed, full search, resume and standalone replay.

Prepared-graph tests found four VTA occurrences. Every occurrence has the same
logical MAC count of 512,000 per invocation; repeated workloads remain bound to
their own symbols and identities.

## T10: deployment evidence adapter

The deployment adapter validates the seed manifest and native records, applies
the exact configs during real VTA lowering, and uses KWS's existing mixed
CPU/VTA device plan and WAV-to-MFCC preprocessing. It executes one committed
sample, requires exact HOST output and top-1 agreement, profiles graph-resident
VTA nodes, and compares ordinary with debug full-model counters. Failures are
written using the shared versioned failure-report format.

An initial build attempt exposed that KWS needs the device plan returned by its
runtime, and its graph executor needs both CPU and ext-dev devices. Both
selected and baseline builds now follow that runtime contract. A focused
follow-up deployment fix commit records the change.

## T11: complete seed alignment gate

The seed run used the approved absolute `vta_64mac.json` geometry, separate
FSIM and TSIM processes, and `--trial-batch 1` to stop each occurrence after its
first successful FSIM schedule. All four schedules built and ran on FSIM, then
received one successful AutoTVM TSIM single-call measurement.

| Occurrence | FSIM attempts | FSIM successes | AutoTVM TSIM cycles | Deployment TSIM cycles | Difference |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 5 | 1 | 211,054 | 208,364 | 1.2746% |
| 1 | 15 | 1 | 138,023 | 138,025 | 0.0015% |
| 2 | 11 | 1 | 61,175 | 61,180 | 0.0082% |
| 3 | 8 | 1 | 52,445 | 52,446 | 0.0019% |

All four pairs pass the inclusive 10% gate. Deployment correctness passed for
the single manifest-first sample, `down-00176480_nohash_0.wav` (SHA-256
`68d8077e68d9c2c02a9eb744061e934f514fc523aa90ee63fd56bfec0227e65d`). The
ordinary and debug full-model measurements both report 460,015 cycles; the
untuned baseline reports 2,354,444 cycles. The report has `sample_count: 1` and
four covered VTA occurrences.

The self-contained seed manifest replayed **4 artifacts** successfully. The
final native records, best manifest and deployment report are under
`keyword_spotting_v1/tune/seed/20261001T191431.265469Z/` and
`keyword_spotting_v1/tune/deployment-seed.json`.

The first sandboxed FSIM attempt failed to bind the loopback RPC tracker; this
is preserved in
`keyword_spotting_v1/build/two_stage_tuning/20261001T190229.251554Z/manifest.json`
as an infrastructure failure. An early post-fix exploratory batch was stopped
after identifying excess seed-batch work; its FSIM candidate errors remain in
the separate ignored build state. The completed seed run records candidate
failures separately from infrastructure errors and has zero infrastructure
errors. These attempts were not used as seed evidence.

## Verification

- KWS focused suite after adapter changes:
  `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests -q`
  — **45 passed**.
- Shared task and affected IC/AD regression suite after the blocked-bias fix:
  **59 passed, 1 skipped** using pytest `--import-mode=importlib`.
- Seed command completed with `status=complete`, `completion_label=SEED_COMPLETE`,
  four FSIM successes and four TSIM measurements.
- Standalone seed replay validated and replayed **4 artifacts**.
- Real TSIM deployment report: `status=passed`, `sample_count=1`, 4/4
  occurrence gates passed, exact KWS HOST output correctness, and ordinary/debug
  cycle agreement.
- `git diff --check` and final managed-repository status passed.

## Commit maps

C4 began from root `5c3a780fa69b6d34000a2aeb601bc932a7903720`, TVM
`9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, and VTA
`65d4f358edbc9a992098a5f828d37a7f6d68bc4d`.

| Change | Root commit | TVM commit | VTA commit |
| --- | --- | --- | --- |
| T9 KWS tuning adapter | `2c2d8b96941a9c5b2d8f58b61a5ff8820b40830d` | unchanged | `2173bedd42ceaff9990a55937e358e554b710413` |
| T10 KWS deployment adapter | `74cefcabde31a3488a78f20fb217da3582e83f2f` | unchanged | `364f5be747daa6e626bb66713f05c297edfd6667` |
| KWS blocked vector-bias semantics fix | `b36029b5ac016eef4948aa34e359071d916bafcc` | unchanged | `b8532fa6a2c6bf21b577330b9e3ba29fd884c95d` |
| KWS deployment device-planning fix | `56b85a1b7086a70a61ba2ee9eefdf841c10e87a8` | unchanged | `0f2e8d669d1f02a850536d57966bddfe1d9f22fa` |
| T11 seed artifacts and deployment report | `11b8cb2637003412e92a50ae92098ae2d323e16e` | unchanged | `1a84af5e74d01f4ad7d64aa92dc1b3153f58bd41` |

The checkpoint evidence commit completes this document. T11 is seed alignment
only; C5 remains responsible for the full search quota and optimal deployment.
