# Intent: Fix TSIM Unknown-Instruction Blocking

## Confirmed outcome

修复当前 `vta/config/vta_64mac.json` 配置下 TSIM 在真实 MLPerf Tiny 混合执行中因
`FetchVME64.scala` 报 `Fetch: Unknown instruction type` 而阻塞的问题，并确认六个
MLPerf Tiny benchmark 的 TSIM 端到端部署均可运行。

## Scope

- 允许修改 VTA Chisel 硬件模型、取指/指令解码、指令编码边界、TSIM runtime 以及
  对应测试。
- 优先检查并修复 `FetchDecode` 与实际 VTA 指令格式/运行时 opcode 解码之间的不一致。
- 保持 `vta/config/vta_64mac.json` 的几何配置语义不变。
- benchmark 的模型、partition、topology、输入数据和准确率断言不作为修复手段，除非
  后续发现仅为测试适配所必需且另行获得批准。
- FPGA 平台（如 `pynq`、`zcu104`）不在本次范围内。

## Success criteria

1. 带有真实字段值的合法 VTA 指令不会在 TSIM 取指分发阶段被误报为 unknown。
2. 非法 opcode/非法指令仍能被拒绝或以现有诊断方式失败，不能通过放宽匹配吞掉错误。
3. TSIM 硬件构建、TSIM 单元/运行时测试通过。
4. 六个 MLPerf Tiny benchmark 在 TSIM 下按既有 runner 和既有模型/partition/topology
   完成端到端执行；任何剩余失败必须被明确记录为阻塞，而不能声称部署完成。

## Explicit non-goals

- 不恢复旧的 `TARGET=sim/tsim` 兼容映射。
- 不重新引入 `VTA_PLATFORM`。
- 不以修改 benchmark 模型、partition、topology 或断言来绕过 TSIM 硬件问题。
