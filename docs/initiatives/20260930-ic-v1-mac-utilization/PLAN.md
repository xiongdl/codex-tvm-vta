# Plan: IC V1 MAC 利用率诊断

## Scope and decisions

按已批准 SPEC 交付分析报告，不修改软件或硬件功能。使用现有 workload 0、config 392 dump 和完整 TSIM rerank。将静态指令分析与真实周期证据分开；61.62% 作为用户确认的同口径对照值，不能推断其历史改动已被复原。

依赖顺序：输入身份与周期核对 → 指令与源码语义核算 → 软件候选和上限评估 → 独立 Review。

## Checkpoint 1: 基线与指令证据

一个 fresh Default 完成 Task 1。核实 MAC 数、配置、geometry 和测量来源；统计完整 dump，核对 UOP/loop、reset、DMA 和同步语义。记录现有输入 SHA-256 和可重现统计命令，产出 `EVIDENCE.md`。不把 queue dump 当成周期级 trace。

## Checkpoint 2: 优化路线

一个 fresh Default 完成 Task 2，消费已提交证据。分析调度与运行时如何生成这些指令，评估数据复用、搬运与计算重叠、buffer 生命周期、UOP/指令开销及 reset 的优化可能性。结合现有成功配置结果排序建议，产出 `ANALYSIS.md`。只有软件限制有证据时列出硬件方向。没有真实测量时不给提升保证。

## Verification

- 所有项目 Python 使用 `.envs/tvm-vta-env/bin/python`；环境不存在则返回 Root escalation。
- 复算利用率：`./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs 2359296 --cycles 82524`，并核对该 MAC 数的 workload 来源。
- dump 原文、统计与源码引用交叉核验；标明 config 392 的 82604 cycles 与 best config 393 的 82524 cycles 区别。
- 临时统计脚本可放 `/private/tmp/`，报告保存完整命令或必要代码以便复现；不添加无关维护脚本。
- 允许使用现有构建进行有界、同 workload 的重放来解决关键不确定性，但不修改功能源码、不做全量重调优或硬件重建。执行前查已有入口、记录命令和输出；没有安全可用入口时仅报告验证建议。
- 每任务独立验证和提交；最终 fresh Reviewer 对完整提交范围审核证据、计算与建议。

## Risks

| Risk | Mitigation |
| --- | --- |
| dump 与最佳配置不同 | 明确对应关系，用 392 解释指令，用 393 表示最优实测基线，必要时有界重放 |
| 静态统计无法分摊真实 stall | 报告下界、结构事实与待验证假设，不虚构周期百分比 |
| 旧环境不可获取 | 只提出候选历史差异，不能宣称找到唯一改动 |
| 估计节省互相重叠 | 不直接相加；每项注明是否需要动态验证 |

## Ownership

Root owns INTENT.md、SPEC.md、PLAN.md、TASKS.md。Default 1 owns EVIDENCE.md；Default 2 owns ANALYSIS.md。两者可在 ignored build 或临时目录保存必要分析产物。源代码与原始 dump/log/result 只读。所有 Git mutation 通过 git-workflow，agents 顺序执行，不并行。
