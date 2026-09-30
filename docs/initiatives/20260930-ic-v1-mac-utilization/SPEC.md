# Spec: IC V1 MAC 利用率诊断

## Objective

交付面向用户的证据报告，解释当前 workload 0 约 44.62% 利用率的开销来源，提出软件优先的优化路线。61.62% 是同 workload、调度、统计口径的用户提供参考结果；无该环境产物，不声称已识别其历史改动。

## Inputs and structure

- `vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/`：现有日志、结果、TSIM rerank 和指令 dump，保持原始文件。
- `image_classification_v1-workload-0-20260930T025152.937603Z-tsim-rerank.json`：79 个成功配置已测量，best config 393 为 82524 cycles，config 392 为 82604 cycles。
- `image_classification_v1-workload-0-config-392-instruction-dump-once.txt`：88 条指令，分析前核对其 workload、geometry 和周期出处。
- `vta/python/`、`vta/src/`、硬件源码及 `tvm/`：只读追溯调度、指令生成、依赖与执行语义。
- 本 initiative 目录：生命周期文件和最终 `ANALYSIS.md`；必要的生成数据放 ignored build 目录或临时目录。

## Commands

从仓库根目录运行；读文件无需项目环境，所有项目 Python 使用 `.envs/tvm-vta-env/bin/python`。

```bash
rg --files --hidden --no-ignore vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1
cat vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/image_classification_v1-workload-0-20260930T025152.937603Z-tsim-rerank.json
sed -n '1,180p' vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/image_classification_v1-workload-0-config-392-instruction-dump-once.txt
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs <核实后的逻辑MAC数> --cycles 82524
```

最后一条中的 MAC 数为待核实参数，必须替换为结果中的整数后执行。若需重放 dump，仅使用现有构建与同一 geometry/backend，具体命令在计划中依据入口确定；本次不进行大规模重新调优或重建硬件。

## Analysis style

结论分为已证实事实、估计和待验证假设；每项优化必须给出指令编号或源码位置、影响机制、约束和验证方法。例如：

> 观察：指令 N 使用某依赖 token。假设：该依赖限制搬运与计算重叠。验证：核对 buffer 生命周期，并用相同 workload 的 TSIM cycles 比较候选指令序列。

静态 dump 的逻辑队列状态不直接当作真实周期级 stall；无法从现有证据分离的开销明确标注，不给出虚假的精确分摊。

## Verification strategy

1. 关联 workload identity、geometry、MAC 数、配置和 TSIM cycles；重算 44.62% 及达到 61.62% 所需周期预算。
2. 对指令统计计算迭代、reset、DMA 类型与大小、UOP 加载、store 和同步；结合源码核实语义，检查总工作量与逻辑 MAC 的关系。
3. 分析软件候选的 buffer、依赖与正确性约束，记录其可验证步骤；只有证据表明软件限制时提出硬件候选。
4. 独立审核报告与证据，不要求无功能改动的全量功能测试。重放若执行，记录命令、配置和结果。

## Boundaries

- Always：保留输入产物；优先软件；遵循角色与 git-workflow 规则；使用项目 Python；报告证据局限。
- Ask first：扩大到功能修改、改变确认意图或已批准产物；缺少用户独有信息或环境条件导致无法继续。
- Never：修改原始日志伪造提升；直接 Git mutation；改统计口径来提高利用率；从静态 dump 断言真实 stall 周期。

## Success criteria

- 报告能解释 dump config 392 与当前 best config 393 的对应关系和差距，核实约 44.62% 基线。
- 至少给出有证据支撑的软件瓶颈候选及优先级，量化目标周期预算；不可量化项注明理由。
- 每项建议包含源码/指令依据与验证方法，区分软件可改进部分与硬件潜在限制。
- 不将 61.62% 历史实现或达成目标描述为已验证事实。

## Open questions

没有需要用户补充才能开展的范围问题。具体时间开销与可实现提升由分析决定；旧环境产物不可获取是已知限制。
