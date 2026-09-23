# Plan: Fix TSIM Unknown-Instruction Blocking

## Objective

在不修改 MLPerf Tiny benchmark 模型、partition、topology 和断言的前提下，修复 VTA
Chisel 取指分发对真实指令字段的错误匹配，使 `vta_64mac.json` 下 TSIM 能完成完整
MLPerf Tiny 六项端到端验证。

## Execution order

按依赖顺序执行三个 checkpoint。每个 checkpoint 使用一个全新的 Default 执行边界；
checkpoint 内的实现、测试和提交必须在返回前完成。

### Checkpoint 1 — Instruction decode correctness

先用失败回归固定当前 unknown-instruction 行为，再修正公共 `FetchDecode` 契约。实现
必须只依赖规范的 opcode/子类型字段判断分发类别，同时把完整原始指令继续传给下游。

重点路径：

- `vta/hardware/chisel/src/main/scala/core/Decode.scala`
- `vta/hardware/chisel/src/main/scala/core/FetchVME64.scala`
- `vta/hardware/chisel/src/main/scala/core/FetchWideVME.scala`
- Chisel decode/fetch tests and test fixtures

验收：合法指令的非零字段不再触发 unknown；非法 opcode/subtype 仍被拒绝；64-bit 和
wide-VME 使用相同分类语义。

### Checkpoint 2 — TSIM artifact integration

基于 checkpoint 1 的已提交实现，使用共享 `vta_64mac.json` 重新生成 geometry、Chisel/
Verilator 硬件和 TSIM 动态库，验证新进程加载与初始化，排除 stale artifact 造成的假通过。

重点路径：

- `vta/hardware/chisel/**` 中与生成/构建相关的实现或测试
- `scripts/build_vta_lib.sh`、`scripts/test_vta_tsim.sh`（仅在必要时）
- `vta/CMakeLists.txt` 或运行时加载边界（仅在必要时）

验收：`libvta_tsim`、`libvta_hw` 与共享几何配置一致；TSIM smoke/focused gate 通过；
不存在旧 `TARGET`、`--target` 或 `VTA_PLATFORM` 依赖。

### Checkpoint 3 — MLPerf Tiny TSIM matrix

在新生成产物上按既有 runner 执行六项 MLPerf Tiny TSIM 端到端矩阵。此 checkpoint 只修复
属于 TSIM 硬件/runtime 的问题；不得通过修改 benchmark 模型、partition、topology、
样本或准确率断言来绕过失败。

重点路径：

- `scripts/test_vta_byoc.sh`（仅复用或修正 TSIM 验证入口）
- `vta/apps/mlperf_tiny_benchmark/**/run.py`（默认不修改）
- benchmark tests（默认不修改）
- 验证日志/报告（按项目约定保存）

验收：六项均完成真实混合执行并通过既有断言；逐项保留命令、exit status 和关键日志。

## Verification strategy

1. 运行 Chisel focused decode/fetch tests，确认输入字段变化和非法输入边界。
2. 运行 TSIM build 与 `test_vta_tsim.sh --smoke-only`，确认新产物实际被加载。
3. 运行完整 TSIM test/integration gate，再运行六项 benchmark matrix。
4. 对每个失败按“硬件解码、产物/环境、benchmark pipeline、结果断言”分类；只在批准范围
   内继续修复，不能把 FSIM 结果当成 TSIM 证据。

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| ISA 常量是 BitPat，直接改为低位 opcode 可能丢失 memory/ALU subtype | 先用字段级回归覆盖所有合法 subtype，再实现最小公共 decoder 变化 |
| ignored build output 仍是旧硬件 | 每次硬件修改后强制重新生成并检查库时间/geometry properties，使用新进程加载 |
| TSIM 长 benchmark 阻塞 | 使用项目既有 timeout/window budget；记录明确失败证据，不无限等待 |
| benchmark pipeline 存在与 TSIM 无关失败 | 保持 benchmark 内容不变，分层报告并在需要扩大范围时回到 Root 决策 |

## Completion condition

只有 Reviewer 对三个 checkpoint 的完整提交范围和六项 TSIM 证据均判定 Pass，才能完成本
initiative。完成后由用户自行执行：

```bash
./.agents/custom/scripts/git-workflow merge 20260923-fix-tsim-unknown-instruction
```
