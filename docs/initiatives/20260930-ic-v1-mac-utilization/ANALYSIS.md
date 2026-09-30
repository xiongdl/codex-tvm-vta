# IC V1 TSIM cost 与指令分析

## 修正后的结论

先前报告把 TSIM 的累计 counter 当成了一次算子的周期数，导致裸 Conv 的 44.62% / 44.67%
以及完整融合 smoke 的 30.47% 都计算错误。原始日志、dump、JSON 和各自哈希保留；旧利用率、单次周期比较和从它们推导的优化差距均撤回。warmup 与正式测量调用之间的周期并不相同，所以将旧累计值除二只能给出算术平均，不能还原单次 cost。

修正 runner 在 warmup 后清零 TSIM profiler，再执行一次正式调用。config 32 的完整 IC V1
融合 task 在 AutoTVM 中得到 **60,492 cycles**；独立地对编译模块按“清零、warmup、读取、清零、正式调用一次、读取”执行，得到 warmup `60,491`、formal `60,492`，两种 cost 完全一致。按 `2,359,296 / (60,492 × 64)` 计算，单次有用 MAC 利用率是 **60.9403%**。61.62% 对应最多 59,824 cycles，当前 smoke 高 668 cycles。

这是已验证 config 的 bounded smoke，不是完整 tuning search 的最优值。分子只计 Conv MAC，周期包含真实模型的 bias、right shift、clip、cast ALU 后处理。真实模型常量权重下，FSIM 输出与 prepared Relay fusion 逐元素相等；TSIM dump 有 64 条 ALU。workload、配置、geometry、protocol、计数、dump 和哈希详见 [CONSISTENCY.md](CONSISTENCY.md) 及忽略目录 `build/autotvm/image_classification_v1/fusion-single-call/`。

因此，旧的 44.62% 不能作为当前模型融合利用率的基线。现有实测表明完整 fusion 的 config 32 smoke 已到 60.94%，距用户给出的 61.62% 参考值只有 0.68 个百分点；仍需单次协议下的完整 FSIM 搜索和有效候选复测，才能判断新最优是否达到该值。旧 rerank 的周期数字不足以证明历史上的最佳配置仍然最佳。

## NOP 是同步 token，不是等待周期

config 392 裸 Conv dump 中的 19 条 NOP 用于满足 compute、memory、store 队列间的依赖：两条启动 token、11 条 tile 之间的依赖提交，以及六条结束时的队列汇合。runtime 会优先把依赖位附加到兼容的真实指令；没有合适指令可承载时，`DepPush` 或 `CommitPendingPop` 生成零传输 NOP。位置与来源在 [CONSISTENCY.md](CONSISTENCY.md) 按指令编号列出。

dump 里的 queue balance 反映 token，不是时间戳。NOP 数量不能乘周期推算开销，也不能单独解释动态 stall；移除它们还会破坏缓冲区读写依赖。config 32 融合 dump 有 21 条 NOP，是另一 fusion/config 的 stream；它的 64 条 ALU 表明完整后处理已参与执行。两份 dump 的 NOP 数量不能直接当作同步成本对比。

## 复核边界

- 旧 config 392/393 的 `82,604` / `82,524` 是 warmup 与正式调用累计计数；没有逐调用 counter，不能从中提取单次数据。先前据此算出的利用率和 80-cycle 单次差距均无效。
- 旧 config 32 的 `120,983` 同样是两次调用累计计数；原 `30.47%` 结果已撤回。该 JSON 和运行日志没有被覆盖。
- 新协议是 `tsim_single_call` v1：`counted_invocations=1`、`warmup_excluded=true`。缺少或不匹配此 metadata 的旧 TSIM artifact 必须重新测量。FSIM 计时保持原样。
- 本次没有改硬件或调度，也没有评估数据复用方案。当前 dump 只能解释指令和依赖结构，不能分解每类指令占用的 cycles。

可复现命令与 oracle 方法见 [CONSISTENCY.md](CONSISTENCY.md)。裸 Conv dump 的静态指令、UOP、内存单位核算仍保留在 [EVIDENCE.md](EVIDENCE.md)，其中旧 cycle 相关结论已经标为历史累计口径。
