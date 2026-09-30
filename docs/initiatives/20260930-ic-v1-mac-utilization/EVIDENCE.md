# Baseline and instruction evidence

## Findings

The approved workload is IC V1 AutoTVM workload index 0, template
`conv2d_packed.vta`, workload SHA-256
`30ae9c31b72c78f8dfb84ba3cc10c6c192c2ad7a8e1365bdaf0213c85b2627fd`.
The matching result JSON reports 2,359,296 logical MACs. Its task signature is
input `[1, 2, 32, 32, 1, 8]` and weight `[2, 2, 3, 3, 8, 8]` in `int8`,
with stride `[1, 1]`, padding `[1, 1, 1, 1]`, layout `NCHW1n8c`, and `int32`
accumulation. These shapes imply 16 input and 16 output channels, 32 by 32
outputs, and a 3 by 3 reduction:

```text
1 * 16 * 32 * 32 * 16 * 3 * 3 = 2,359,296 MACs
```

The geometry file is `vta/config/vta_64mac.json`: batch is 1 and both input
and output blocking are 8, so peak throughput is `1 * 8 * 8 = 64 MAC/cycle`.
The workload's channels are exact multiples of the 8-lane blocks; this dump
does not show channel-tail GEMMs. Spatial boundary padding is present in the
activation loads, as described below.

| Evidence | Config | TSIM cycles | Useful-MAC utilization |
| --- | ---: | ---: | ---: |
| Rerank best | 393 | 82,524 | 44.670641% |
| Dumped instruction stream | 392 | 82,604 | 44.627379% |

Both percentages use `2,359,296 / (cycles * 64)`. Thus the dump's config 392
result is approximately 44.63% (44.62% if truncated to two decimals); the
rerank best is approximately 44.67%. Config 393 is 80 cycles faster than 392,
about 0.097% fewer cycles. The compared FSIM schedule entities differ only in
`tile_h` (4 for 392; 8 for 393); `tile_w=32`, `tile_ci=1`, `tile_co=2`,
`oc_nthread=1`, and `h_nthread=2` are the same. The instruction dump is for
392, so its instruction statistics must not be represented as a dump of the
best config 393.

At 61.62%, the cycle budget is
`2,359,296 / (64 * 0.6162) = 59,824.732...`; an integer cycle count must be at
most 59,824. Relative to config 393 this requires at least 22,700 fewer cycles
(27.51% of its measured cycles); relative to config 392 it requires 22,780
fewer. This is a target budget, not an attribution of removable cycles.

## Complete dump accounting (config 392)

`image_classification_v1-workload-0-config-392-instruction-dump-once.txt`
contains all 88 instructions. The full, timestamped runtime dump ends with
`CONFIG_INDEX 392`, `FSIM_COST_SECONDS 0.001244`, `TSIM_ERROR_NO 0`, and
`TSIM_RESULT (82604,)`, tying the decoded stream directly to the rerank result.

| Instruction class | Count | Meaning / evidence |
| --- | ---: | --- |
| `GEMM` | 24 | 8 accumulator-reset instructions and 16 dot-product instructions |
| `LOAD INP` | 16 | Activation vectors |
| `LOAD WGT` | 16 | Weight matrix vectors |
| `LOAD UOP` | 4 | Micro-operations |
| `STORE` | 8 | Output vectors |
| `NOP-COMPUTE-STAGE` | 7 | Compute-queue dependency markers; zero transfer size |
| `NOP-MEMORY-STAGE` | 9 | Load-queue dependency markers; zero transfer size |
| `NOP-STORE-STAGE` | 3 | Store-queue dependency markers; zero transfer size |
| `FINISH` | 1 | End marker |
| **Total** | **88** | |

For each non-reset GEMM, the dump has loop extents 32 and 3 and a UOP range of
24. The runtime's GEMM loop therefore executes
`32 * 3 * 24 = 2,304` UOPs per instruction, or `16 * 2,304 = 36,864` UOP
executions across these 16 instructions. One UOP multiplies an 8-element
input vector by an 8-by-8 weight matrix, yielding `1 * 8 * 8 = 64` scalar
MACs. The result is `36,864 * 64 = 2,359,296` MACs, exactly the task's logical
MAC count. This is the logical dot-product work encoded in this dump; the
dump does not evidence extra GEMM executions for a channel tail.

The other 8 GEMMs have `reset_out=1`, ranges of four UOPs, and loop extents 32
and 2. They represent `8 * 32 * 2 * 4 = 2,048` reset-UOP iterations. Per the
TSIM implementation, reset iterations clear accumulator vectors and do not
perform dot products; the reset loop is excluded from the simulator's
`gemm_counter`. Do not count those as MACs.

### Nominal GEMM UOP issue rate

The checked-in Chisel implementation establishes a nominal one-UOP-per-active-
cycle issue schedule. `TensorGemmIndexGenerator` drives `valid` from its
`running` state and increments `uop_idx` on each running cycle
(`vta/hardware/chisel/src/main/scala/core/TensorGemm.scala:238-269`). The
configured compute block instantiates `new TensorGemm`
(`vta/hardware/chisel/src/main/scala/core/Compute.scala:61-64`);
`TensorGemm` extends `TensorGemmPipelinedSplit`, which connects the generator's
valid signal to the UOP index stream (`TensorGemm.scala:547-563, 588-593,
748`). Therefore, 36,864 useful UOPs require at least 36,864 active GEMM issue
cycles in this nominal architecture. At 64 MAC/UOP, that is the useful-compute
lower bound for the dump's workload. This does not establish measured TSIM
cycles attributable to GEMM, queue stalls, DMA overlap, or command setup and
drain; those remain unpartitioned by the dump.

### Transfer sizes and units

The 2D memory instruction sizes are in memory elements, with each element a
vector for the corresponding block. For this geometry, an input vector is
`1 batch * 8 input lanes * 8 bits = 8 bytes`; a weight vector is
`8 output lanes * 8 input lanes * 8 bits = 64 bytes`; a UOP is 32 bits or
4 bytes; and an output vector is `1 * 8 * 8 bits = 8 bytes`. These widths
follow `hw_spec_const.h` and `vta_64mac.json`.

| Dump operations | Encoded elements (`x_size * y_size`) | Element size | Encoded data |
| --- | ---: | ---: | ---: |
| 16 `LOAD INP` | 2,944 input vectors | 8 B/vector | 23,552 B read |
| 16 `LOAD WGT` | 288 weight vectors | 64 B/vector | 18,432 B read |
| 4 `LOAD UOP` | 56 UOPs | 4 B/UOP | 224 B read |
| 8 `STORE` | 2,048 output vectors | 8 B/vector | 16,384 B written |

The activation loads specify 320 additional vector slots from explicit
`x_pad`/`y_pad` fields; these become 2,560 bytes of zero-filled on-chip input
storage. They are not DRAM-read bytes and do not add GEMM loop iterations.
This separates the input halo padding from the logical MAC accounting. Data
volume counts above are derived from the encoded 2D extents and element sizes;
they do not estimate transfer latency or overlap.

### Dependency chain and what the dump can establish

`runtime.cc::DumpInsn()` prints a software-maintained dependency-token balance
while it walks the queued instruction words. The dependency bits indicate
ordering between load, compute, and store queues; they are not timestamps or
runtime stall measurements. Representative chains in this dump are:

1. `INSTRUCTION 7` pushes a load-to-compute dependency; `INSTRUCTION 10`
   (the next UOP load on the compute queue) pops a load-to-compute token.
2. `INSTRUCTION 11` pushes compute-to-load; `INSTRUCTION 14` consumes that
   dependency before the next activation/weight buffer use.
3. `INSTRUCTION 19` pushes compute-to-store; `INSTRUCTION 22` consumes it
   before storing the accumulator result.
4. `INSTRUCTION 22` pushes store-to-compute; `INSTRUCTION 24` consumes it
   before the next accumulator-reset/GEMM group.

The exact flags are visible in the cited instruction numbers in the original
dump. `l2g_queue`, `g2l_queue`, `s2g_queue`, and `g2s_queue` are updated by
adding or removing encoded dependency tokens as the dump is printed. Their
values do not establish whether DMA overlaps GEMM in a given cycle, how long a
queue waited, or how many cycles stalls consumed. TSIM's recorded cycle counts
are dynamic measurements for a complete isolated task; this static dump does
not decompose those cycles by instruction class.

## Source basis

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py:94-102`
  converts AutoTVM's FLOP count to logical MACs by dividing by two. The
  IC V1 README describes the matching workload result and metric.
- `vta/config/vta_64mac.json` supplies the geometry; `vta/config/pkg_config.py:71-78`
  sets output width equal to input width. `vta/include/vta/hw_spec_const.h:31-88`
  defines UOP widths, matrix-vector widths, and bytes per memory element.
- `vta/include/vta/hw_spec.h:75-115` defines the strided 2D memory sizes and
  padding fields. Its GEMM pseudocode at lines 117-140 defines the nested
  loops over output iteration, input iteration, and UOP range.
- `vta/src/runtime/runtime.cc:762-882` prints the instruction fields and
  software queue balances. `runtime.cc:1020-1098` maps UOP/INP/WGT/OUT memory
  element sizes and constructs 2D memory instructions; lines 1200-1240 build
  GEMM instructions from UOP loop metadata.
- `vta/src/sim/sim_driver.cc:399-450` distinguishes normal GEMM work from
  reset work. Normal work performs the 8-by-8 dot product; reset work writes
  zeros to accumulator lanes.
- `vta/hardware/chisel/src/main/scala/core/Compute.scala:61-64` instantiates
  `TensorGemm`; `TensorGemm.scala:238-269,547-563,588-593,748` shows the
  generator's one-UOP-per-active-cycle nominal schedule and the pipelined
  implementation selected by that instance. This is an architectural issue
  rate, not a TSIM cycle attribution or a measurement of realized stalls.
- `vta/apps/mlperf_tiny_benchmark/README.md:92-105` defines the useful-MAC
  utilization formula and 64 MAC/cycle peak for this geometry.

## Reproduction

Run from the repository root. Both utilization commands use the repository
Python environment and checked-in metric script:

```bash
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs 2359296 --cycles 82524
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs 2359296 --cycles 82604
```

The instruction counts and byte totals can be independently recalculated from
the dump using `x_size * y_size` and these element sizes: INP 8 B, WGT 64 B,
UOP 4 B, OUT 8 B. For GEMM, multiply each non-reset instruction's two loop
extents by `uop_end - uop_bgn`; multiply its resulting UOP count by 64 MAC/UOP.
For reset instructions apply the same extent calculation but count reset-UOP
iterations separately from MACs. Source definitions above give each unit and
loop meaning.

The 61.62% budget can be reproduced with the formula
`floor(2359296 / (64 * 0.6162)) = 59824 cycles`.

## Input identity and immutable-source check

SHA-256 of original evidence inputs at analysis start and before commit:

| Input | SHA-256 |
| --- | --- |
| Approved TSIM rerank JSON (`...025152.937603Z-tsim-rerank.json`) | `9072f755088ef98fd50c6aec4c14a86d114253149a8f85bcd1381abd2032276e` |
| Config 392 decoded dump (`...config-392-instruction-dump-once.txt`) | `fcab0b7f885269ef7f5c826a6442939884d83f6d3eb844969b88096b982d41c0` |
| Config 392 full runtime dump (`...config-392-instruction-dump.log`) | `2572fae002195501df056c585dce45979c51cc90935401c560fbb632f8ce3fda` |
| Workload 0 result JSON (`...021628.757343Z-result.json`) | `d7d1d438269d2704f0078e4749a2dfa67298113018669c15815ef3677d2635bd` |
| FSIM tuning log (`...021628.757343Z-fsim.log`) | `8411cb0d7a0c46d6890572293f61d4a85cd645308a1d6029b538d973b0d7429e` |
| Paired FSIM best record (`...021628.757343Z-best.log`) | `eff4399d173aae2fefcfd41d08a710b0c574b60ae2888dfb3ee61c5f7b940500` |
| Geometry (`vta/config/vta_64mac.json`) | `23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa` |

The older paired `result.json` is a separate standalone verification reporting
83,066 cycles; it is not the complete rerank best and is not used for the
44.67% baseline above. The approved rerank contains 79 successful TSIM
measurements, identifies 393 at 82,524 cycles as its best, and lists 392 at
82,604 cycles. Config records 392 and 393 were read from the paired FSIM log.
The original input hashes matched at the final check. No source or original
log/dump/result file was modified.
