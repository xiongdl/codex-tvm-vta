# Specification: MLPerf Tiny TSIM Verification

## Scope

验证仓库当前 MLPerf Tiny deployment matrix 中的六个 benchmark，使用每个 benchmark 已有
的 runner、模型资产、Relay partition、topology、输入样本和结果断言；本 capability 不
允许通过削弱 benchmark 验收来得到绿色结果。

## Functional requirements

1. 每个 benchmark 必须使用 `--simulator tsim`，并在进程环境中显式设置：
   - `VTA_CONFIG_FILE=<repo>/vta/config/vta_64mac.json`
   - `VTA_BACKEND=tsim`
2. 每项必须完成真实的 host/VTA 混合执行，而不仅是导入、编译或库加载 smoke test。
3. 每项必须使用既有 benchmark 断言验证执行成功和输出契约；不能只检查进程退出或日志中
   出现“built”。
4. 验证记录必须按 benchmark、host codegen/runner 变体、命令、exit status 和关键日志
   摘要组织，能区分硬件解码失败、环境失败、模型/partition 失败和结果失败。
5. 六项全部通过才可将本 initiative 标记为完成；任一项失败必须保留可复现证据并回到
   实现/诊断阶段。

## Benchmark matrix

矩阵以仓库当前 `scripts/test_vta_byoc.sh` 和各 benchmark runner 为准，至少覆盖：

- image classification v1
- visual wake words v1
- image classification v2
- anomaly detection v1
- streaming wakeword v1
- keyword spotting v1

如果仓库入口实际定义的六项名称与上述列表不同，实施阶段以维护脚本和 runner 的当前
清单为准，并在验证报告中说明映射；不得静默减少矩阵。

## Verification evidence

- 先运行 TSIM focused gate，确认基础环境和解码回归通过。
- 再按矩阵逐项执行，必要时使用项目已有的 TSIM window budget/超时约束，避免无限阻塞。
- 对每项保留可复现命令及结果；只有六项均为成功状态才报告“TSIM 全部部署正确”。

## Constraints

- 不修改 benchmark model/partition/topology、输入资产或 accuracy assertions。
- 不把 FSIM 通过推断为 TSIM 通过。
- 不把 Java/SBT/Verilator 缺失归因于硬件解码修复，也不以跳过 TSIM 代替验证。
