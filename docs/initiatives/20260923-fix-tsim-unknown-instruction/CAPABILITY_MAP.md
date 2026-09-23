# Capability Map

本次修复拆为三个可独立验证的 capability。依赖方向为：指令解码契约 → TSIM 构建/运行时
产物 → MLPerf Tiny 端到端矩阵。

| Capability | 责任边界 | 独立验收 |
| --- | --- | --- |
| Instruction decode correctness | Chisel 取指分发依据规范的 opcode/子类型字段识别合法指令，保留完整指令给下游 decode，并拒绝非法编码 | Chisel decode/fetch 回归测试覆盖带非零字段的合法指令与非法 opcode |
| TSIM artifact integration | 用共享几何配置重新生成硬件模型和 TSIM 动态库，确保运行时加载与配置一致 | TSIM build、库加载、初始化、TSIM focused tests 通过 |
| MLPerf Tiny TSIM verification | 使用既有 benchmark runner、模型、partition、topology 和断言跑完整六项矩阵 | 六个 benchmark 的 TSIM 端到端结果均成功，或输出逐项可审计的失败证据 |

## Dependency and change boundary

- `Instruction decode correctness` 是主要实现能力；它不得改变 benchmark 代码。
- `TSIM artifact integration` 只负责构建链和产物验证，不修饰 benchmark 行为。
- `MLPerf Tiny TSIM verification` 只消费既有 benchmark 部署路径；若发现 benchmark 自身
  与 TSIM 的独立缺陷，必须先报告而不是扩大本 initiative 的实现范围。
