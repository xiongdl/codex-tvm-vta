# VTA DwC acceptance - 2026-10-10

Source chat: `01a11fd5-19fe-7ee2-9364-74e05b40a5a3`.
VTA branch: `codex/dwc-implementation`, matrix acceptance commit: `8cd0356`; final cleanup commit: `162b91f`.

## Implementation

Opcode 5 reuses GEMM instruction fields, array and pipeline. DwC uses only multiplier zero, consumes signed low packed weights once per valid tap, and reloads at each real kernel range. Input DMA retains BLOCK_IN vectors; each bank is min(BI,BO)*INP_BITS wide and the parallel read is BATCH*max(BI,BO)*INP_BITS. The default TOP loads complete input rows, using 1344 bytes per KWS tile, and executes nine actual taps.

## Same real KWS layer

The first quantized DwC corresponds to TFLite operator 1. Input/output NHWC is [1,25,5,64]; actual Relay weights are HWOI [3,3,64,1], stride 1, four-side padding 1, multiplier 1. Independent integer convolution equals Relay exactly. All six runs use the same logical sample hashes and reconstruct complete signed int32 through four ordinary byte stores.

| BI x BO | FSIM outputs | TSIM outputs | FSIM DwC per byte | TSIM four byte-run cycles |
|---|---|---|---:|---|
| 8x8 | 8000 exact | 8000 exact | 9000 | 35893, 43755, 43755, 43755 |
| 8x16 | 8000 exact | 8000 exact | 4500 | 20753, 24712, 24712, 24712 |
| 16x8 | 8000 exact | 8000 exact | 9000 | 35559, 43718, 43718, 43718 |

Every geometry/backend also passes the established GEMM numerical benchmark and 31 backend/ISA tests. Opcode 5, bridged queue tokens and four FINISH records are retained; actual TSIM completion with correct outputs proves the tiled queue path runs. Reference range is -8205 to 6860. All real input/weight channels contain nonzero data, including expanded upper channels and both reverse subblocks.

## Verification and reproduction

- Complete VTA Python unit suite: 412 passed in 86.56 seconds.
- Complete Chisel suite: 83 passed, 39 suites, zero failed/aborted.
- Default TOP/sample focused suite: 10 passed.
- Controller fresh final check: 41 TOP/sample/backend/ISA tests passed in 21.30 seconds.
- Default 8x8 compiler extension, FSIM and TSIM libraries restored; generated BI/BO are both 8.
- Bare whole-project pytest has 46 previously recorded collection errors. It is not claimed green; the final phase did not repeat it.

Run the complete matrix from the project root:

```sh
./scripts/test_vta_dwc.sh
```

[Stable detailed report](../../../vta/build/dwc-acceptance/task-6-report.md) includes exact commands, model/WAV/data hashes and intermediate failure diagnoses. `vta/build/dwc-acceptance` retains per-geometry NPZs, library/source fingerprints, RTL, instruction traces, numerical summaries and test logs. Build artifacts are ignored by Git.

## Limits

The TOP supports this BATCH=1, int8 operands, int32 accumulation, depth multiplier 1 and dilation 1 scope. `dwc_kernel(weight,(KH,KW))` carries unambiguous kernel metadata. Build with the documented `vta.build_config(disabled_pass={"tir.CommonSubexprElimTIR"})`. SRAM keeps its fixed-latency protocol; randomized bubble tests cover the weight consumer, not arbitrary response backpressure. Full-graph routing and performance tuning are outside this request.

## Execution rulings, in original order

All recorded interface/environment decisions and their rework costs follow. The early patch-tile ruling was superseded by the later complete-row tile ruling.

- Ruling: Task 1 tests runtime generation and lowering structurally; numerical DwC tests become executable in task 2 — opcode 5 has no execution backend yet — cost if wrong: missed cross-layer issue until task 2.

- Ruling: Reuse original TVM checkout and environment, with independent VTA checkout/build — TVM itself is not an implementation target — cost if wrong: need additional TVM checkout if integration requires TVM edits.

- Ruling: DwC uop mode is 2, preserving GEMM=0 and ALU=1, using existing push entry — avoids unnecessary ABI additions — cost if wrong: generated/runtime mode mismatch requiring recompilation.

- Ruling: DwC input uop indices address BATCH×min(BLOCK_IN,BLOCK_OUT) lane channel units; DMA and GEMM retain BLOCK_IN vector units — reverse configuration must distinguish both BLOCK_OUT subblocks — cost if wrong: address contract changes across runtime, RTL and TOP. Task 3 validates depth/index capacity and physical mapping.

- Ruling: A DwC uop range is the actual KH×KW taps for one output/channel block; existing instruction loops repeat the full range. Reload marker is uop_idx==uop_begin on every rewind — provides a kernel boundary without new ISA fields — cost if wrong: TOP folding must be adjusted and unsupported hand-written uop schedules rejected/documented.

- Ruling: DwC bypasses legacy VerifyDep repeated-destination rejection, retaining other modes' checks — consecutive taps require accumulator bypass already present in the pipelined RTL — cost if wrong: RTL numeric regression exposes a bypass deficiency to fix in Task 4.

- Ruling: Fall back to original /Users/xdl/Projects/codex-tvm-vta/vta checkout after managed worktree writes remained sandbox-blocked — using-git-worktrees explicitly permits in-place sandbox fallback, original VTA clean and branch is not main/master — cost if wrong: changes need transfer into isolated checkout later. Earlier managed VTA worktree has no edits and remains attached.

- Ruling: Preserve wide VME beats using additional row-interleaved physical bank stripes F=max(1,VMEbits/(BATCH*max(BI,BO)*INP_BITS)), BATCH*R*F banks, each min(BI,BO)*INP_BITS; compute read width remains BATCH*max(BI,BO)*INP_BITS — minimum BATCH*R bank count cannot receive existing512bit beat without multiwrite conflicts, user fixed width not count — cost if wrong: extra bank routing needs revision; test512bit compatibility and64bit three-config paths. Select stripe then rotate withinR to avoid crossing rows.

- Ruling: TOP uses explicit dwc_kernel(packed_weight,(KH,KW)) metadata identity wrapper, preserving packed4Dweight and requested compute signature — entry count alone cannot identify kernel geometry — cost if wrong: callers need wrapper/interface adjustment.

- Ruling: Default TOP schedule conservatively tiles one output/channel group with BI-aligned kernel patch — complete padded KWS input exceeds8KiB SRAM and no tuning requested — cost if wrong: performance may be lower and later schedule tuning needed.

- Ruling: Refine default TOP tile to load complete kernel-height rows/all channels, rather than discontiguous3x3patch — existingDMA rejects two simultaneous noncontiguous spatial strides; KWS three padded rows use1344bytes and fitSRAM — cost if wrong: higherDMA volume, later schedule tuning.

- Ruling: Bridge nonadjacent LOAD/STORE dependency through existingCOMPUTE queue in VTAtransform — tiledTOP CoProcSync emits directSTORE→LOAD rejected byruntime and hardwareadjacentqueues — cost if wrong: synchronization deadlock or reorder; focused paired-token tests and realTSIM numerical acceptance required. TVM source andISA unchanged.

- Ruling: Accept final-review scope exclusions: fullgraph/otherFPGAbackends, TOPbatch>1, partialchannels/multiplier>1/dilation>1/otherdtypes, arbitrarySRAMbackpressure, unsupportedhandwrittenkernelranges/unalignedgroups, performancetuning/CSE-oncallbacks, unrelatedbarepytestcollection — approved independent-layer specification and documented existing protocol/publicTOP limits govern these behaviors — cost if wrong: future feature/schedule/ABI work or separate test-infrastructure repair is required; no exclusion hides an observed acceptance failure.

## Review status

All six task-level specification and quality reviews passed. Whole-branch review approved merging with no Critical/Important findings. The two minor diagnostics were fixed in one final wave; scoped re-review confirmed both addressed with no new breakage. The controller freshly ran 41 TOP/sample/backend/ISA tests on the committed VTA source: all passed.

## Final diagnostic cleanup

Portable DPI PRIu64 formatting and DwC TE alignment declarations were reconciled in `162b91f`. Physical SRAM rounding, full entry transfer, strides and offset factors remain unchanged. A warning regression first failed in two asymmetric geometries, then all 50 focused tests passed. Fresh TSIM16x8 and restored-default TSIM8x8 both compared 8000 exact outputs, without alignment/format warnings. Default8x8 all-backend libraries remain restored. [Cleanup report](../../../vta/build/dwc-acceptance/final-fix-report.md) and `final-fix-*` logs preserve the commands and new numerical evidence.

Final source: VTA `162b91f`, root branch `codex/vta-dwc-support`. All review findings are addressed. Parent final verification after cleanup: ten TOP/sample tests passed (see `controller-final.log`). Integration has not been performed; both local branches are preserved pending the user selection.
