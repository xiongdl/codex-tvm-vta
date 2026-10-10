# VTA DwC 支持设计

## 目标与范围

新增原生 DwC 指令和 TOP，复用 Chisel GEMM 阵列及流水线，以 KWS 真实 DwC 层依次跑通 FSIM、TSIM。使用默认 schedule 参数，不依赖调优。此次验收为独立层，不要求把完整 KWS 图的全部 DwC 自动路由到 VTA，也不扩展其他 FPGA 后端。

## ISA 与运行时

定义 VTA_OPCODE_DWC=5，采用 GEMM 指令布局，包括 reset、uop 范围、循环和索引因子；不新增指令位宽或修改既有 opcode。DwC 进入 compute 队列，遵守原有依赖同步。runtime、指令打印、FSIM 执行和 profiler 均识别 DwC，TOP lowering 使用专用 DwC intrinsic 发出该 opcode。

## 计算阵列

DwC 与 GEMM 使用同一阵列。每个 batch、输出通道的 dot-product 在 DwC 模式下，仅第一个乘法器计算该通道输入与对应权重 bank 的最低位权重，其余乘法器输入置零以停止数据相关切换。归约树和寄存器级数不变，mode 与数据保持周期对齐。累加、reset 和输出行为沿用 GEMM；GEMM 的全部 BLOCK_IN 乘法器正常工作。

## 输入缓冲

输入缓冲的并行数据宽度为 BATCH × max(BLOCK_IN, BLOCK_OUT) × INP_BITS；软件输入仍按 BLOCK_IN 向量化。RTL tensor 参数、Load/DMA、ISA 派生尺寸、runtime、FSIM 和 Python environment 必须一致区分 BLOCK_IN 向量的逻辑寻址与缓冲的并行读取宽度，不能将扩宽直接解释为重新按 BLOCK_OUT 打包输入。存储容量、bank 组织和索引范围按实际实现一致推导。

输入缓冲每个 bank 的位宽为 min(BLOCK_IN, BLOCK_OUT) × INP_BITS，不包含 BATCH 因子。总并行宽度由多个 bank 提供；每个 batch 对应 max(BLOCK_IN, BLOCK_OUT) / min(BLOCK_IN, BLOCK_OUT) 个 bank 的并行宽度，所有 batch 合计为 BATCH 倍。本次三组配置的每个 bank 均为 64 bit：默认配置每 batch 一个 bank，扩宽和反向配置每 batch 两个 bank。软件地址映射必须配合此 bank 组织，保证所需向量无冲突并行访问。

每个 DwC 计算周期需要每个 batch 的 BLOCK_OUT 个输入数据。当 BLOCK_OUT > BLOCK_IN 时，软件通过输入缓冲的布局、地址分配和加载调度，保证所需的多个 BLOCK_IN 向量能无冲突并行提供 BLOCK_OUT 个输入数据。当 BLOCK_IN > BLOCK_OUT 时，DwC 选择当前输出通道分块对应的 BLOCK_OUT 个输入，其余 lanes 保留真实输入数据，不要求补零。输入数据不因 BLOCK_IN 与 BLOCK_OUT 的大小关系在 lanes 上补零；空间卷积 padding 按算子语义另行处理。GEMM 仍按 BLOCK_IN 向量读取。

## 权重布局与移位语义

保持 dot-product 与权重 bank 的对应关系。每通道按 (kh, kw) 行优先展开核，连续 BLOCK_IN 个权重打包为一个 entry，末尾补零。最低位元素对应当前分组第一个核位置。

权重从 weight memory 读取后存入对应 bank 的权重寄存器。uop 仍按实际 KH、KW 执行；每个有效 DwC 计算周期消耗 BLOCK_OUT × 1 个权重数据，各 dot-product 使用对应权重寄存器最低位的一个 WGT_BITS 元素，按有符号值计算，消费后将寄存器右移 WGT_BITS 更新。仅在有效消费时移位，等待或停顿周期不推进权重。

每消费完 BLOCK_IN 个核位置，读取下一权重 entry 到寄存器，然后继续实际 KH、KW 对应的 uop。末尾补零仅用于权重存储对齐，不增加核位置或要求执行补齐到 BLOCK_IN 的计算。开始新的输出位置或通道分块时，重新建立对应的权重寄存器状态，即使复用同一 memory 地址也不得沿用已移位的数据。复用 GEMM uop 和循环字段，通过实际核位置及权重 entry 切换管理加载与消费，保持既有计算流水线不变。

3×3 核、BLOCK_IN=8 时为两个 entry：第一个存前八个核位置，第二个存 (2,2) 和七个零；BLOCK_IN=16 时为一个 entry，存九个核位置和七个零。

## TOP

新增 packed DwC compute、tensor intrinsic 和默认 schedule，支持此次真实层所需的 depth multiplier=1、int8 输入/权重及 int32 累加。输入按 BLOCK_IN 向量化，输出按 BLOCK_OUT 分块通道；权重按 BLOCK_IN 分组存储，uop 按实际 KH、KW 执行。软件确保每周期所需 BLOCK_OUT 个输入无冲突并行可用。正确处理空间 padding、stride 和边界。根据模型实际属性确定测试 padding 和 stride，不猜测。输出可复用既有 ALU 后处理，核心数值验收使用 int32 累加结果。

## KWS 样例与配置矩阵

已直接解析仓库 kws_ref_model_float32.tflite：四个 DwC 位于 TFLite operator 索引 1、3、5、7，输入和输出均为 NHWC [1,25,5,64]，权重为 [1,3,3,64]。选第一个 DwC，提取现有 KWS 量化流程中的对应权重和该层激活，保存来源、operator 索引及数据哈希，使其可复现。

同一份逻辑输入、权重和 CPU 参考输出运行三组配置，仅打包格式变化：

| 配置 | BATCH | BLOCK_IN | BLOCK_OUT | 输入缓冲并行宽度 | 输入 bank 位宽 | 每通道权重 entry 数 |
|---|---:|---:|---:|---:|---:|---:|
| 默认 | 1 | 8 | 8 | 64 bit | 64 bit | 2 |
| 扩宽 | 1 | 8 | 16 | 128 bit | 64 bit | 2 |
| 反向 | 1 | 16 | 8 | 128 bit | 64 bit | 1 |

三组分别构建匹配的 simulator/runtime/RTL，不能用旧库运行新几何配置。CPU 参考使用独立逐通道卷积，并逐元素精确比较 int32 结果。

## 验证与验收

1. ISA 编解码、compute dispatch、依赖同步和 reset 覆盖 opcode 5。
2. 权重打包测试确认核顺序、低位元素、有符号取值及补零。
3. RTL 检查输入 bank 位宽为 min(BLOCK_IN, BLOCK_OUT) × INP_BITS、总并行宽度符合定义、按 BLOCK_IN 向量加载的真实输入数据，扩宽配置下 BLOCK_OUT 个输入无 bank 冲突并行供给，以及 DwC 乘法器 gating、mode 对齐、有效消费移位、停顿保持、跨 entry、重复地址重载和流水线延迟。3×3 核仅执行九个实际核位置。
4. 同一 KWS 层在三组配置下先全部通过 FSIM，再全部通过 TSIM。
5. 定向数据使通道 8～15 输出非零且各不相同，检测扩宽时跨 BLOCK_IN 向量的截断、bank 冲突和通道混用；反向配置所有输入 lanes 保留真实非零数据，检测 BLOCK_OUT 子块选择及多输出分块，不能通过 lanes 补零掩盖错误。
6. 三组配置下运行 GEMM 回归，确认扩宽与 DwC mode 不改变既有计算。

完成报告记录命令、配置、样例来源和结果。任何尚未执行或失败的验证明确列出，不将库加载成功等同于计算通过。
