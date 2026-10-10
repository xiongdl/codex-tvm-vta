# VTA ALU 对齐 CMSIS-NN 双舍入与单舍入 requantize 路径

日期：2026-10-10

## 目标与范围

实现 CMSIS-NN `arm_nn_requantize` 的默认双舍入与单舍入路径。先实现并验收
FSIM，再实现并验收 Chisel TSIM。RMUL 和 RSFT 为独立 ALU 指令，二者
写回和读取的 accumulator 均为 INT32。单舍入采用ARM MVE的非舍入Q31乘法
加最终舍入RSFT序列。不增加64位 accumulator 或跨指令隐藏乘积状态。

参考：https://raw.githubusercontent.com/ARM-software/CMSIS-NN/main/Include/arm_nnsupportfunctions.h

## 指令定义

opcode定义：MIN=0、MAX=1、ADD=2、SHIFT=3、MUL=4、RMUL=5、RSFT=6。7保留。
SHIFT 的正移位量表示算术右移，负移位量表示左移。删除 Chisel 将负移位
转换为内部 opcode 4 的处理；直接根据实际移位操作数的符号选择方向。

在现有 ALU `imm` 字段之后追加独立rounding字段，不增加mul_q31字段：

| 字段 | 宽度 | 含义 |
| --- | --- | --- |
| rounding | 2 | 00不舍入；01最近舍入、半值向正无穷；10最近舍入、半值远离零；11非法 |

在当前 vta_64mac 配置下：rounding=[125:124]，bits[127:126]保留为零。
字段位偏移由配置计算，其他配置必须检查尾部至少剩余2位。保留128位指令
长度与原有字段位置。C位域、Chisel Bundle、编码工具和ABI标识必须同步。
旧编码在尾部字段为零时保留现有运算语义。

MIN/MAX/ADD/SHIFT/MUL要求rounding=00。RMUL和RSFT允许rounding=00/01/10。
RMUL是独立opcode，表示Q31格式的乘法，不表示总是舍入；是否舍入由
rounding字段决定。主指令opcode ALU=4、DWC=5保持不变；RMUL=5属于
独立的alu_opcode命名空间，不能与主指令DWC混淆。
非法组合在编码及模拟器入口检查，硬件拒绝非法编码，避免静默执行其他操作。

## 运算语义

### MUL 与 RMUL

普通MUL：有符号操作数相乘，输出低32位；用明确的位运算表达回绕，避免
C++有符号溢出。保留现有use_imm行为。

RMUL：内部生成完整有符号32×32乘积P，根据rounding将P右移31位后
写回INT32。乘法中的31位缩放是Q31格式转换的一部分，不使用imm编码缩放
量。默认requantize使用rounding=01，等价于`int32((P + 2^30) >> 31)`。
rounding=00/10分别使用相同的截断/半值远离零规则。内部完整乘积不写入SRAM。
RMUL支持现有use_imm：立即数符号扩展，但完整Q31 multiplier通常通过
源accumulator读取，因为imm只有16位。

不额外饱和。参考中的no_sat函数不处理两个乘数都为INT32_MIN的饱和特例；
量化测试使用非负Q31 multiplier，最大为INT32_MAX。

### SHIFT

保持现有SHIFT左右移行为不变，不增加舍入功能，rounding必须为00。
输入和输出均为INT32，移位量来自imm或源accumulator；正值算术右移，
负值左移并保留低32位，零直接返回。回归覆盖立即数及寄存器左右移。
Chisel内部左移编码调整只用于消除与MUL opcode的冲突，不改变外部语义。

### RSFT

输入和输出均为INT32，右移量来自imm或源accumulator，范围为[0,31]。
零直接返回；负数和大于31的右移量为非法操作，不截取低5位误执行。
RSFT不承担左移；预左移继续使用原有SHIFT。

对右移n>0，令q=v>>n、r=v-q*2^n、h=2^(n-1)：

- 00：q。
- 01：q+(r>=h)。
- 10：q+(r>h或(r==h且v>=0))。

计算舍弃位、阈值和增量时避免INT32溢出。FSIM使用明确宽度的中间量，
Chisel使用完整乘积、算术右移及舍弃位判断，最后转换为32位。

## 默认 requantize 指令序列

给定INT32累加值x、非负Q31 multiplier m、shift s∈[-31,30]：

1. 若s>0：普通SHIFT将x左移s位。
2. RMUL：乘m，rounding=01，输出INT32 b。
3. 若s<0：RSFT将b右移-s位，rounding=10；否则b为结果。
4. ADD输出zero point，MIN/MAX按融合激活与INT8范围裁剪。

默认CMSIS C路径的预左移使用有符号INT32乘法；溢出没有可移植确定语义。
CMSIS一致性用例限制x*2^max(s,0)在INT32范围内。VTA自身对普通左移明确
定义低32位回绕，并独立测试。输出转换不隐式饱和。

## 单舍入指令序列与范围

单舍入使用RMUL、rounding=00，输出算术右移31位后的INT32，
第一次Q31格式转换不舍入。最终RSFT使用rounding=01，仅在这里舍入。

- s<0：RMUL输出b=floor(x*m/2^31)，RSFT将b右移-s位并舍入。对非负
  Q31 multiplier和全部INT32输入，这与当前标量单舍入公式一致。即使
  丢弃乘积低31位，最终右移至少1位，其舍入判断需要的位仍保留在b中。
- s>=0：先用SHIFT将x左移s+1位，再使用不舍入RMUL，最后用RSFT右移1位并舍入。
  该序列要求预左移x*2^(s+1)能由INT32表示；生成器和测试检查此前提。
  超出此前提不得宣称与64位标量单舍入一致，也不得静默使用回绕结果。

本次量化模型的所有CONV_2D通道shift均为负。首层16个通道的shift为
[-8,-10,-9,-8,-9,-9,-9,-8,-9,-9,-10,-9,-8,-11,-10,-7]，
因此真实模型的单舍入无需预左移，也不受上述正shift范围限制。
实现时再次从模型生成参数并校验，不能将这些数值作为计算参数硬编码。

## 软件接口与硬件

保持现有VTAUopPush接口对旧调用的行为，增加显式支持rounding和RMUL/RSFT opcode的
ALU构建入口，复用现有uop/loop/runtime队列。rounding与opcode纳入kernel缓存键，
避免不同舍入模式错误复用指令。Python常量与测试编码器同步。

更新FSIM执行、Chisel ISA/Decode/TensorAlu两条执行路径及相关解码测试。
用户要求32位乘法按一个cycle实现：32×32乘积与Q31格式转换/舍入使用
一个计算cycle，不额外增加乘法流水stage；现有SRAM访问与控制周期仍保留。
必须同步valid/opcode/rounding及写回控制，验证依赖指令连续执行，并通过
Chisel测试确认计算延迟。该要求不是一次完整ALU指令含SRAM访问总共一个cycle，
也不是未经综合验证的目标频率保证。现有其他后端不能静默执行带新字段的指令；
本次实现和数值验收目标为FSIM与Chisel TSIM。

## 模型样例与验收

新增测试内容统一位于`vta/tests/qconv2d/`，不得修改`vta/apps`。
该目录包含：

- `extract_conv_fixture.py`：从.envs量化模型及固定CIFAR-10输入提取卷积样例。
- `fixtures/`：保存固定输入、权重、bias、逐通道参数、TFLite输出与版本/hash元数据。
- `reference/`：独立CMSIS-NN参考程序和版本/编译宏信息。
- `test_alu_requantize.py`及`test_conv_requantize.py`：驱动真实FSIM/TSIM指令测试。
- `reports/`：运行时生成差异定位报告，加入忽略规则，不提交重复生成的运行日志。

Chisel自身的单元测试继续位于现有`vta/hardware/chisel/src/test/scala/`，
测试入口脚本可以扩展现有`scripts/test_vta_fsim.sh`和`test_vta_tsim.sh`。
提取过程仅读取.envs模型，不向apps复制模型、样例或生成文件。

使用仓库根目录下的：
`.envs/tiny-v1.4/benchmark/training/image_classification/trained_models/pretrainedResnet_quant.tflite`。
不使用apps目录中的浮点模型。

提取首个CONV_2D：输入INT8[1,32,32,3]，权重INT8[16,3,3,3]，bias INT32[16]，
输出INT8[1,32,32,16]，权重逐通道scale共16个。记录模型SHA256、算子参数、
量化参数、输入和输出，以及TFLite运行时版本。使用.envs中的CIFAR-10固定
样例输入，保留可复现的提取脚本；禁用delegate并保留中间tensor以获得参考输出。

量化multiplier/shift使用TFLite兼容的生成规则，均为per-output-channel，
不能将任一参数简化成per-tensor。multiplier按lane加载；对于不同shift，
按channel对应关系调度RSFT及必要的预左移SHIFT，不能因分组改变输出通道顺序
或padding lane结果。
VTA实际执行卷积累加、bias、
requantize及裁剪，考虑输入zero point、padding及3通道输入的硬件对齐。
先独立验证INT32累加，再逐元素比较最终输出。不能仅在Python计算卷积后宣称
硬件卷积路径通过。

测试包括：两种舍入的正负半值及邻值；零、INT32边界；移位0/1/31；正负
shift；高位乘积；立即数和寄存器操作数；编码往返；旧ALU回归；非法字段；
RMUL紧接RSFT的流水和依赖。CMSIS默认标量函数与当前版本单舍入标量
函数分别为独立算术参考。覆盖s<0全INT32范围、s>=0合法预左移范围与
超范围显式拒绝；包括x=1、m=2^30、s=-1时双舍入1/单舍入0的区分样例。

## 数值验收优先级与差异归因

用户规定以下三个独立验收条件：

1. FSIM与CMSIS-NN必须逐元素完全一致，无任何容差。分别对双舍入和单舍入
   验证相应路径；参考版本、编译宏与有效输入范围必须记录。量化卷积也必须
   运行实际CMSIS-NN卷积实现作为参考，而不只比较手写Python算术公式。
2. TSIM与FSIM必须逐元素完全一致，使用相同指令、输入和逐通道参数；
   两种舍入模式都覆盖，不因TFLite存在差异放宽这项要求。
3. TFLite Python输出应尽可能对齐。如果只有正负1差异，必须逐项确认是
   舍入造成的，并尝试使用支持的舍入策略对齐。若无法对齐，可接受已经证明
   来源为舍入的正负1差异；其他原因或超过1的差异均不得以容差通过。

归因时逐层比较：卷积INT32累加（含bias）、逐通道multiplier/shift、
RMUL前后、RSFT前后、输出zero point及激活裁剪，定位第一个不同的步骤。
必须排除输入预处理、padding、布局、scale生成、累加溢出及融合激活等因素。
对于每个输出差异，保存坐标、输出通道、累加值、multiplier、shift、完整
乘积、舍入商与余数、两边输出，并用独立CMSIS参考及运行时算术实现解释。
仅观察差值为正负1不能证明其来源为舍入。

先运行双舍入和单舍入参考卷积，查找两者输出不同的位置，再与TFLite实际
输出比较以识别其舍入路径；真实样例不能区分时补充能区分的确定性输入。
仍无法区分时检查对应运行时源码/构建设置并报告证据，不凭模型量化参数
猜测，不将两种结果相同当作识别成功。

尝试对齐TFLite时使用RMUL/RSFT的受支持舍入组合；不能改变已经定义的
CMSIS舍入模式来掩盖差异。若TFLite需要与CMSIS不相同的策略，应保存为
独立明确命名的指令序列，CMSIS基准序列继续满足零差异。单舍入仍遵守
前述正shift有效范围约束。

最终报告分别列出CMSIS/FSIM、FSIM/TSIM的差异数（必须为0），以及
TFLite/FSIM的差异数、最大绝对差值、来源证据和尝试过的策略。FSIM通过
CMSIS验收后再重建TSIM，以同一固定样例验证。环境缺失导致的未执行检查
应明确报告，不把跳过测试作为通过。
