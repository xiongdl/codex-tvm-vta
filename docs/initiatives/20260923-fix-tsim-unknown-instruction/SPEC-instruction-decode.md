# Specification: Instruction Decode Correctness

## Problem

`FetchDecode` 当前以 `ListLookup(io.inst, ...)` 对完整 `INST_BITS` 指令匹配。VTA
指令的低位包含 task opcode，而其余字段由 load/store/GEMM/ALU 的具体参数组成；真实
运行时会为这些字段填入非零值。因此，使用完整指令常量做精确匹配可能把合法指令误判为
unknown，触发 `FetchVME64.scala` 的断言。此处是待验证的根因假设，实施阶段必须用回归
测试先固定行为，再修改实现。

## Functional requirements

1. `FetchDecode` 必须依据 VTA ISA 的规范字段识别指令类别：
   - load input/weight → Load queue；
   - load uop/acc、GEMM、FINISH、ALU → Compute queue；
   - store output → Store queue。
2. 合法指令的参数字段、依赖字段、尺寸字段、地址字段或立即数字段变化，不得改变其
     分发类别。
3. 下游 `LoadDecode`、`ComputeDecode`、`StoreDecode` 必须继续收到完整的原始指令，不能
   通过只保留 opcode 的方式破坏参数解码。
4. 非法 task opcode、未知 memory subtype 或不属于支持 ISA 的编码不得被静默归类为合法
   queue；必须保持 unknown/invalid 的可观测失败路径。
5. `Fetch64Bit` 与 `FetchWideVME` 使用的公共分发契约必须一致。

## Behavioral examples

| 输入 | 期望分发 |
| --- | --- |
| `LINP`，`xsize=0` 或非零，其他字段任意合法值 | Load |
| `LWGT`，`xsize=0` 或非零，其他字段任意合法值 | Load |
| `LUOP` 或 `LACC`，字段含真实非零地址/尺寸/依赖值 | Compute |
| `GEMM`，循环边界/寄存器/依赖字段非零 | Compute |
| `FNSH` 或支持的 ALU 指令，合法字段值 | Compute |
| `SOUT`，字段含真实非零地址/尺寸/依赖值 | Store |
| 未知 opcode 或未知指令 subtype | 不进入任何 queue，并触发既有诊断/失败路径 |

## Verification requirements

- 新增或调整 Chisel 单元测试，至少覆盖每个合法类别的“常量编码”和“带非零字段的
  实际样式编码”。
- 覆盖非法 opcode/subtype，证明修复没有把 default invalid 变成 valid。
- 测试必须在当前 `vta_64mac.json` 几何配置下运行，并通过项目指定的 Java/SBT/Chisel
  环境执行。
- 若实现需要修改 ISA 常量或公共 decoder，必须同时验证取指宽度 64-bit 和 wide-VME
  两条路径。

## Constraints

- 不修改 MLPerf Tiny benchmark 的模型、partition、topology、样本或断言。
- 不修改 `vta_64mac.json` 的几何数值来规避解码问题。
- 不恢复旧 target 名称兼容映射。
