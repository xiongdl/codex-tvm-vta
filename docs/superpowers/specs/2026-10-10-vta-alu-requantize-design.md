# VTA ALU 对齐 CMSIS-NN 默认 requantize 路径

日期：2026-10-10

## 目标与范围

实现 CMSIS-NN `arm_nn_requantize` 的默认双舍入路径。先实现并验收
FSIM，再实现并验收 Chisel TSIM。MUL 和 SHIFT 为独立 ALU 指令，二者
写回和读取的 accumulator 均为 INT32。不实现 `CMSIS_NN_USE_SINGLE_ROUNDING`，
不增加64位 accumulator 或跨指令隐藏乘积状态。

参考：https://raw.githubusercontent.com/ARM-software/CMSIS-NN/main/Include/arm_nnsupportfunctions.h

## 指令定义

保留 opcode：MIN=0、MAX=1、ADD=2、SHIFT=3、MUL=4。5–7保留。
SHIFT 的正移位量表示算术右移，负移位量表示左移。删除 Chisel 将负移位
转换为内部 opcode 4 的处理；直接根据实际移位操作数的符号选择方向。

在现有 ALU `imm` 字段之后追加两个独立字段：

| 字段 | 宽度 | 含义 |
| --- | --- | --- |
| rounding | 2 | 00不舍入；01最近舍入、半值向正无穷；10最近舍入、半值远离零；11非法 |
| mul_q31 | 1 | 0普通乘法；1定点Q31乘法 |

在当前 vta_64mac 配置下：rounding=[125:124]、mul_q31=[126]，bit127保留为零。
字段位偏移由配置计算，其他配置必须检查尾部至少剩余3位。保留128位指令
长度与原有字段位置。C位域、Chisel Bundle、编码工具和ABI标识必须同步。
旧编码在尾部字段为零时保留现有运算语义。

MIN/MAX/ADD要求新字段为零。SHIFT要求mul_q31=0。普通MUL要求rounding=00。
非法组合在编码及模拟器入口检查，硬件拒绝非法编码，避免静默执行其他操作。

## 运算语义

### MUL

普通MUL：有符号操作数相乘，输出低32位；用明确的位运算表达回绕，避免
C++有符号溢出。保留现有use_imm行为。

Q31 MUL：内部生成完整有符号32×32乘积P，根据rounding将P右移31位后
写回INT32。乘法中的31位缩放是Q31格式转换的一部分，不使用imm编码缩放
量。默认requantize使用rounding=01，等价于`int32((P + 2^30) >> 31)`。
rounding=00/10分别使用相同的截断/半值远离零规则。内部完整乘积不写入SRAM。
Q31模式支持现有use_imm：立即数符号扩展，但完整Q31 multiplier通常通过
源accumulator读取，因为imm只有16位。

不额外饱和。参考中的no_sat函数不处理两个乘数都为INT32_MIN的饱和特例；
量化测试使用非负Q31 multiplier，最大为INT32_MAX。

### SHIFT

输入和输出均为INT32，移位量来自imm或源accumulator。支持移位量[-31,31]。
零直接返回。负移位量左移并保留低32位，要求rounding=00。正移位量按
rounding指定的规则处理。不得将移位量简单截取低5位而将31以外输入误执行。

对右移n>0，令q=v>>n、r=v-q*2^n、h=2^(n-1)：

- 00：q。
- 01：q+(r>=h)。
- 10：q+(r>h或(r==h且v>=0))。

计算舍弃位、阈值和增量时避免INT32溢出。FSIM使用明确宽度的中间量，
Chisel使用完整乘积、算术右移及舍弃位判断，最后转换为32位。

## 默认 requantize 指令序列

给定INT32累加值x、非负Q31 multiplier m、shift s∈[-31,30]：

1. 若s>0：普通SHIFT将x左移s位。
2. Q31 MUL：乘m，rounding=01，输出INT32 b。
3. 若s<0：SHIFT将b右移-s位，rounding=10；否则b为结果。
4. ADD输出zero point，MIN/MAX按融合激活与INT8范围裁剪。

默认CMSIS C路径的预左移使用有符号INT32乘法；溢出没有可移植确定语义。
CMSIS一致性用例限制x*2^max(s,0)在INT32范围内。VTA自身对普通左移明确
定义低32位回绕，并独立测试。输出转换不隐式饱和。

## 软件接口与硬件

保持现有VTAUopPush接口对旧调用的行为，增加显式支持rounding和mul_q31的
ALU构建入口，复用现有uop/loop/runtime队列。新字段纳入kernel缓存键，
避免不同舍入模式错误复用指令。Python常量与测试编码器同步。

更新FSIM执行、Chisel ISA/Decode/TensorAlu两条执行路径及相关解码测试。
TSIM可以增加定点乘法流水周期，但必须同步valid/opcode/rounding及写回
控制，验证依赖指令连续执行。现有其他后端不能静默执行带新字段的指令；
本次实现和数值验收目标为FSIM与Chisel TSIM。

## 模型样例与验收

使用仓库根目录下的：
`.envs/tiny-v1.4/benchmark/training/image_classification/trained_models/pretrainedResnet_quant.tflite`。
不使用apps目录中的浮点模型。

提取首个CONV_2D：输入INT8[1,32,32,3]，权重INT8[16,3,3,3]，bias INT32[16]，
输出INT8[1,32,32,16]，权重逐通道scale共16个。记录模型SHA256、算子参数、
量化参数、输入和输出，以及TFLite运行时版本。使用.envs中的CIFAR-10固定
样例输入，保留可复现的提取脚本；禁用delegate并保留中间tensor以获得参考输出。

量化multiplier/shift使用TFLite兼容的生成规则。VTA实际执行卷积累加、bias、
requantize及裁剪，考虑输入zero point、padding及3通道输入的硬件对齐。
先独立验证INT32累加，再逐元素比较最终输出。不能仅在Python计算卷积后宣称
硬件卷积路径通过。

测试包括：两种舍入的正负半值及邻值；零、INT32边界；移位0/1/31；正负
shift；高位乘积；立即数和寄存器操作数；编码往返；旧ALU回归；非法字段；
定点MUL紧接SHIFT的流水和依赖。CMSIS默认标量函数为独立算术参考。

真实TFLite结果为最终模型验收依据；如运行时使用其他算术路径，必须报告并
确定使用默认双舍入参考内核，不能通过调整容差掩盖差异。FSIM通过后，重建
TSIM并使用同一组固定样例，最终要求输出零差异。环境缺失导致的未执行检查
应明确报告，不把跳过测试作为通过。
