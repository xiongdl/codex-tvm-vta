# IC V1 软件优化分析

> Historical scope: this analysis used a standalone bare-Conv task and dump;
> it omitted the model's bias/right-shift/clip/cast work. Its cycle and MAC
> utilization figures therefore do not describe complete IC V1 fusion. The
> revised tuning contract, fused smoke result, and NOP analysis are recorded in
> [CONSISTENCY.md](CONSISTENCY.md). Tile reuse and hardware proposals below are
> historical and outside the revised scope.

## 结论

确认基线为 64 MAC/cycle、2,359,296 个 logical MAC。现有 TSIM rerank 的最优 config 393 用时 82,524 cycles，利用率 44.6706%；指令 dump 是 config 392，用时 82,604 cycles，利用率 44.6274%。达到用户确认的 61.62% 需要不超过 59,824 cycles，即比当前最佳至少减少 22,700 cycles（27.5%）。计算与完整 dump 核算见同目录已提交的 [EVIDENCE.md](EVIDENCE.md)。

从 dump 能确认的重点不是“DMA 已经拖慢了多少周期”，而是软件排程反复搬运可复用的数据：weight 读入量是唯一卷积权重的 8 倍；activation 也有高于唯一输入的重复读取。weight 全量能装入当前 16 KiB weight buffer，值得先尝试跨空间 tile 保留；activation 全量超过 8 KiB input buffer，需用滚动窗口或更合适的空间 tile 复用行数据。静态读量只给出可减少的数据上限，TSIM dump 没有周期分解，不能换算成可节省周期。

已有 79 个成功 TSIM 配置中，最优仍是 82,524 cycles。392 与 393 的已解析调度实体除 `tile_h` 由 4 变 8 外相同，周期只差 80（约 0.10%）。这说明只在当前已测 AutoTVM 空间调参，无法覆盖 61.62% 目标；它不排除重新设计调度后通过消除搬运冗余获益。现有证据不足以判断重排后能否节省所需的 22,700 cycles，因此软件优化“有明确试验价值，但目标可达性未证实”。目前也没有证据把剩余差距归因于硬件吞吐限制，暂不给硬件改造建议。

## 可确认的开销与边界

config 392 的 88 条指令中，有 16 条 INP LOAD、16 条 WGT LOAD、4 条 UOP LOAD、8 条 STORE、8 条 reset GEMM，以及 19 条零字节依赖 NOP。16 条非 reset GEMM 各执行 `32 × 3 × 24 = 2,304` 个 UOP，总计 36,864 个 UOP、2,359,296 个 MAC；reset GEMM 执行 2,048 次 accumulator 清零迭代，不执行乘加。reset 次数正好对应 2,048 个输出向量，因每个累加向量在首次累加前必须为零，不能把这 2,048 次当成可直接删除的冗余 MAC 工作。[EVIDENCE.md](EVIDENCE.md) 给出 dump 编号、字节单位和来源交叉核验。

DMA 指令的依赖字段及 dump 内 `l2g_queue/g2l_queue/s2g_queue/g2s_queue` 是运行时维护的依赖 token 余额。它们能指出 load、compute、store 之间存在顺序约束，却不是时间戳或 stall 计数。19 条 NOP 也不能直接乘一个周期数估算收益。当前只知道整段 TSIM 测量周期，不知道 GEMM、reset、DMA 和同步各自占多少周期，也不知道搬运和计算实际重叠程度。

## 软件优化路线

| 优先级 | 建议与 dump / 源码依据 | 作用机制及约束 | 收益边界与验证 |
| --- | --- | --- | --- |
| 1 | **跨空间 tile 保留并复用 weight。** dump 中 16 条 WGT LOAD 各搬 18 个 64 B weight vectors，总计 288 vectors / 18,432 B；该 workload 的完整 kernel 只有 `2 × 2 × 3 × 3 = 36` vectors / 2,304 B，且反复出现相同 DRAM 地址（例如 INSTRUCTION 7/9、15/17、28/30）。schedule 在 `vta/python/vta/top/vta_conv2d.py:162` 建立 weight cache，并在 `:213` 附近将其放在 GEMM 的 `k_o` 循环内生成。 | 把 weight cache 的载入范围提升到包含多个空间 tile 的循环外，或显式安排整个 36-vector kernel 驻留后再计算。配置 weight buffer 为 16 KiB，容纳 2.3 KiB 的完整 kernel。需要确认 UOP 的 `wgt_idx` 与新的 SRAM 排布一致；保持 input/output channel reduction 次序和累加结果不变，并保证任何下一次覆盖 weight SRAM 的 load 不早于最后一个使用它的 GEMM。依赖 token 必须覆盖真实 buffer 生命周期。 | 按 dump 读量计算，理论上最多避免 252 个重复 vectors，即 16,128 B / 当前 WGT 读量的 87.5%；这是字节上限，不是周期收益。修改后生成同 workload 指令 dump：核验逻辑 MAC、UOP 索引、依赖 token、权重值与输出正确，再用 TSIM 比较 cycles。若 TSIM 周期不降，说明该数据搬运当前被重叠或不是关键路径。 |
| 2 | **用滚动 input 窗口减少相邻空间 tile 重读。** dump 的 INP LOAD 搬入 2,944 个 8 B vectors / 23,552 B，唯一逻辑输入是 `2 × 32 × 32 = 2,048` vectors / 16 KiB；另有 320 个明确 pad vector slots 在本地置零，不是 DRAM 读。当前 INP LOAD 带有 `y_size=5/6` 和 x 边界 pad，呈现卷积窗口 halo。schedule 在 `vta/python/vta/top/vta_conv2d.py:184-190` 定义空间 tile 和 compute_at 位置。 | 调整行 tile / 遍历次序，让相邻输出行共享还驻留在 input SRAM 的重叠输入行。整张逻辑输入 16 KiB，大于 8 KiB input buffer，因此不可简单整图缓存；必须考虑 3 行卷积窗口、上下边界 padding、两组输入 channel block 及 load/compute 交叠时的 buffer 占用。 | 唯一输入与当前 DRAM 读量的差是 896 vectors / 7,168 B，等于当前 INP 读量的 30.4%，是可消除 payload 的上限；padding slots 不应误算成 DRAM 节省。生成 dump 复核 input 地址、pad、每个逻辑输出仅计算一次及 buffer 无覆盖，再用相同 TSIM 配置和 workload 测量。当前 config 392→393 的 `tile_h=4→8` 只快 80 cycles，不能据此承诺更大行 tile 会节省显著周期。 |
| 3 | **在 buffer 生命周期允许时合并相邻小任务与同步边界。** dump 有 16 条正常 GEMM、8 条 reset GEMM 和 19 条零字节依赖 NOP；`vta/src/runtime/runtime.cc:600-692` 会根据跨队列依赖插入/合并 token，`vta/src/runtime/runtime.cc:1208-1240` 将 UOP kernel 转成 GEMM 指令。 | 提高 tile 批量可能减少指令提交、重复 UOP LOAD、reset/GEMM 分段和 barrier，但扩大 tile 会增加 accumulator/input/weight SRAM 活跃区。当前 32 KiB accumulator buffer 深度为 1,024 个 output vectors；全 workload 有 2,048 个 output vectors，因此不能同时驻留所有输出，也不能越过 store-before-overwrite 的依赖。reset 逻辑初始化的是结果输出，不能仅因它不计 MAC 就省略。 | 静态的指令数只能显示可检查的位置，不能量化周期下界。尝试前后需对比指令数、每类搬运量和动态 TSIM cycles，并以 VTA 模拟结果与 CPU reference/output 比较确认结果一致；不得直接删除 NOP 或依赖 token。 |

## 61.62% 目标判断与后续决策

Chisel 中的 `TensorGemmIndexGenerator` 每个 running cycle 前进一个 UOP，`TensorGemmPipelinedSplit` 将其 valid 信号驱动到 UOP 索引流，且 `TensorGemm` 继承该实现；`Compute` 实例化的正是 `TensorGemm`。因此，对 36,864 个有用 UOP，名义架构下 GEMM 至少需要 36,864 个 active issue cycles。这是源码支持的计算下界，不是 TSIM 测出的 GEMM 周期拆分，也不证明 DMA、同步或流水线实际用了多少周期。要满足 59,824-cycle 目标，reset、搬运、同步、命令开销及其他非有用计算时间合计预算约为 22,960 cycles；现有 dump 不能把该预算分摊到这些类别。源码引用和边界见 [EVIDENCE.md](EVIDENCE.md)。

相对该理想参考，当前最佳实测比它多 45,660 cycles；达到目标需要削减这部分约一半。weight 和 input 重复 payload 提供了值得验证的软件机会，但是否落在关键路径、能节省多少 cycles 均未知。因此结论是：**软件方向还没有被证伪，但基于已测配置调参无法达到目标；对调度结构做数据驻留/复用实验后才能判断 61.62% 是否可由软件覆盖。**

下一步先实现并单独测量 weight 驻留，再评估 input 滚动窗口；每次只改变一个调度机制，使用同一 workload identity、64MAC geometry 和 TSIM 口径，记录生成 dump、正确性和 cycles。若两项实测降低搬运量但周期仍远高于目标，再对有周期级证据的关键路径决定是否需要硬件方向。没有旧环境的 dump 或变更记录，本分析不能识别历史上究竟改过什么。

## 复核与复现

以下命令从仓库根目录运行。利用率计算使用仓库项目 Python 环境；config 392/393 的 FSIM 配置差异由 AutoTVM 记录解码核验。输入 dump、rerank、log 以及源码在本 checkpoint 前后保持只读。

```bash
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs 2359296 --cycles 82524
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs 2359296 --cycles 82604
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -c 'from tvm import autotvm; p="vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/image_classification_v1-workload-0-20260930T021628.757343Z-fsim.log"; rows=list(autotvm.record.load_from_file(p)); print("\n".join(f"id={i.config.index} config={i.config}" for i,r in rows if i.config.index in (392,393)))'
```

本次未另行重放 workload：已有 rerank 已在相同 workload/geometry/backend 下测完 79 个成功配置；尚未实现新的调度，不存在可供重放比较的候选指令流。优化收益均作为待测假设，未冒充实测周期改善。
