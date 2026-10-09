# VTA DwC 支持设计

## 目标与范围

新增原生 DwC 指令和 TOP，复用 Chisel GEMM 阵列及流水线，以 KWS 真实 DwC 层依次跑通 FSIM、TSIM。使用默认 schedule 参数，不依赖调优。此次验收为独立层，不要求把完整 KWS 图的全部 DwC 自动路由到 VTA，也不扩展其他 FPGA 后端。

## ISA 与运行时

定义 VTA_OPCODE_DWC=5，采用 GEMM 指令布局，包括 reset、uop 范围、循环和索引因子；不新增指令位宽或修改既有 opcode。DwC 进入 compute 队列，遵守原有依赖同步。runtime、指令打印、FSIM 执行和 profiler 均识别 DwC，TOP lowering 使用专用 DwC intrinsic 发出该 opcode。

## 计算阵列

DwC 与 GEMM 使用同一阵列。每个 batch、输出通道的 dot-product 在 DwC 模式下，仅第一个乘法器计算该通道输入与对应权重 bank 的最低位权重，其余乘法器输入置零以停止数据相关切换。归约树和寄存器级数不变，mode 与数据保持周期对齐。累加、reset 和输出行为沿用 GEMM；GEMM 的全部 BLOCK_IN 乘法器正常工作。

## 输入缓冲

输入 entry 宽度为 BATCH × max(BLOCK_IN, BLOCK_OUT) × INP_BITS。RTL tensor 参数、Load/DMA、ISA 派生尺寸、runtime、FSIM 和 Python environment 使用一致定义，索引位宽按实际 entry 数推导。固定字节容量下，entry 数可随位宽变化；禁止保留旧深度造成容量或寻址不一致。

DwC 每个 entry 的有效通道数为 BLOCK_OUT，按输出通道顺序存放。BLOCK_IN > BLOCK_OUT 时，剩余输入 lanes 补零。GEMM 每个 entry 的前 BLOCK_IN lanes 有效，额外 lanes 补零。两种布局均由软件打包，DMA 按扩展后的 entry 大小传输。

## 权重布局与移位语义

保持 dot-product 与权重 bank 的对应关系。每通道按 (kh, kw) 行优先展开核，连续 BLOCK_IN 个权重打包为一个 entry，末尾补零。最低位元素对应当前分组第一个核位置。

每组首先读取原始权重 entry，随后每个有效 DwC 计算步使用最低位元素，再逻辑右移 WGT_BITS；按有符号 WGT_BITS 解释取出的元素。组内计算读取移位寄存器，不重复恢复原始 entry。完成 BLOCK_IN 个位置后读取下一组；同一个权重地址被用于新输出位置时必须重新加载。新指令、reset 或组切换不得继承上一组的移位状态。

TOP 每个权重分组生成明确的计算边界，复用 GEMM uop 和循环字段。每组执行 BLOCK_IN 个核位置，Padding 位置输入和权重均为零；该分组边界用于初始化移位状态，不能仅凭地址变化判断，因为不同输出位置会复用同一地址。

3×3 核、BLOCK_IN=8 时为两个 entry：第一个存前八个核位置，第二个存 (2,2) 和七个零；BLOCK_IN=16 时为一个 entry，存九个核位置和七个零。

## TOP

新增 packed DwC compute、tensor intrinsic 和默认 schedule，支持此次真实层所需的 depth multiplier=1、int8 输入/权重及 int32 累加。按 BLOCK_OUT 分块通道，按 BLOCK_IN 分组核位置；正确处理空间 padding、stride 和边界。根据模型实际属性确定测试 padding 和 stride，不猜测。输出可复用既有 ALU 后处理，核心数值验收使用 int32 累加结果。

## KWS 样例与配置矩阵

已直接解析仓库 kws_ref_model_float32.tflite：四个 DwC 位于 TFLite operator 索引 1、3、5、7，输入和输出均为 NHWC [1,25,5,64]，权重为 [1,3,3,64]。选第一个 DwC，提取现有 KWS 量化流程中的对应权重和该层激活，保存来源、operator 索引及数据哈希，使其可复现。

同一份逻辑输入、权重和 CPU 参考输出运行三组配置，仅打包格式变化：

| 配置 | BATCH | BLOCK_IN | BLOCK_OUT | 输入 entry | 每通道权重 entry 数 |
|---|---:|---:|---:|---:|---:|
| 默认 | 1 | 8 | 8 | 64 bit | 2 |
| 扩宽 | 1 | 8 | 16 | 128 bit | 2 |
| 反向 | 1 | 16 | 8 | 128 bit | 1 |

三组分别构建匹配的 simulator/runtime/RTL，不能用旧库运行新几何配置。CPU 参考使用独立逐通道卷积，并逐元素精确比较 int32 结果。

## 验证与验收

1. ISA 编解码、compute dispatch、依赖同步和 reset 覆盖 opcode 5。
2. 权重打包测试确认核顺序、低位元素、有符号取值及补零。
3. RTL 检查 Load 后扩宽输入全部 lanes，DwC 乘法器 gating、mode 对齐、移位、跨 entry、重复地址重载和流水线延迟。
4. 同一 KWS 层在三组配置下先全部通过 FSIM，再全部通过 TSIM。
5. 定向数据使通道 8～15 输出非零且各不相同，检测高位截断和通道混用；反向配置检测输入额外 lanes 不污染结果及多输出分块。
6. 三组配置下运行 GEMM 回归，确认扩宽与 DwC mode 不改变既有计算。

完成报告记录命令、配置、样例来源和结果。任何尚未执行或失败的验证明确列出，不将库加载成功等同于计算通过。
