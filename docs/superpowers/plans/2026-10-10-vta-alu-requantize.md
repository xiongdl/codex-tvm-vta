# VTA ALU requantize Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增加MUL硬件支持及RMUL/RSFT指令，以真实量化卷积证明CMSIS-NN、FSIM、TSIM一致，并确认TFLite差异来源。

**Architecture:** 保留INT32 accumulator和现有SHIFT，新增RMUL=5、RSFT=6及独立2位rounding。MUL/RMUL一个计算cycle，双舍入与单舍入通过不同RMUL/RSFT模式组合实现。先以独立CMSIS参考验收FSIM，再更新Chisel并使用完全相同的样例验收TSIM。

**Tech Stack:** C++17、Python/pytest/NumPy/TFLite、CMSIS-NN标量C、Chisel 3.5、chiseltest、Verilator。

**Spec:** `docs/superpowers/specs/2026-10-10-vta-alu-requantize-design.md`（用户已确认）。

## Global Constraints

- MIN=0、MAX=1、ADD=2、SHIFT=3、MUL=4、RMUL=5、RSFT=6；7保留。
- 独立rounding字段：00不舍入、01最近舍入半值向正无穷、10最近舍入半值远离零、11非法；当前64mac偏移[125:124]。
- 不增加mul_q31字段、64位accumulator或隐藏乘积状态；保持128位指令与原有字段偏移。
- 原有SHIFT行为不变；只有RMUL/RSFT允许非零rounding；RSFT移位量[0,31]。
- 32×32乘法/Q31转换使用一个计算cycle，不额外增加乘法流水stage。
- multiplier和shift均为per-output-channel；不得共享一个通道的参数代替其他通道。
- 单舍入s<0覆盖全部INT32输入；s>=0要求预左移s+1位不溢出，超范围显式拒绝。默认路径预左移也必须满足CMSIS有效输入范围。
- FSIM/CMSIS和FSIM/TSIM零差异；TFLite仅接受已经证明来源为舍入且尝试对齐失败的±1差异。
- 测试、样例、参考及报告位于`vta/tests/qconv2d/`；不得修改`vta/apps`。
- 输入模型为`.envs/tiny-v1.4/benchmark/training/image_classification/trained_models/pretrainedResnet_quant.tflite`；输入取.envs固定CIFAR-10样例。
- 最终whole-branch reviewer使用`gpt-6.1-sol`、`high`；其他代理如采用SDD，遵循AGENTS.md的模型映射。

## Review Focus

1. runtime kernel缓存遗漏rounding或出现同一kernel混合模式，必须拒绝/正确区分（Task 1）。
2. 负数半值、RSFT=31、RMUL的高位及转换回绕不能因C++溢出或Scala Int乘法改变结果（Tasks 2、4）。
3. 输入zero point=-128、边界padding、三输入通道及输出通道参数顺序不能造成伪舍入差异（Task 3）。
4. 同一量化模型不能识别其运行时舍入配置；旧CMSIS单舍入INT32中间值不能冒充当前标量参考（Tasks 2、3）。
5. opcode/rounding与valid错周期、连续RMUL→RSFT依赖、重建后残留旧ABI库必须检查（Tasks 4、5）。

---

### Task 1: 指令编码、ABI与runtime扩展

**Files:** 修改`vta/include/vta/hw_spec_const.h`、`hw_spec.h`、`runtime.h`、`vta/src/runtime/runtime.cc`、`vta/config/vta_config.py`、`vta/python/vta/environment.py`；新增`vta/tests/qconv2d/test_encoding.py`、`runtime_probe.cc`、`conftest.py`、`run_tests.sh`、`.gitignore`。

**Interfaces:**
- 产生常量`VTA_ALU_OPCODE_RMUL=5`、`VTA_ALU_OPCODE_RSFT=6`、`VTA_ALU_ROUND_NONE=0`、`VTA_ALU_ROUND_UP=1`、`VTA_ALU_ROUND_AWAY=2`。
- `VTAAluInsn.rounding`为imm之后的2位字段。
- 新C入口`void VTAUopPushEx(uint32_t mode, uint32_t reset_out, uint32_t dst_index, uint32_t src_index, uint32_t wgt_index, uint32_t opcode, uint32_t use_imm, int32_t imm_val, uint32_t rounding)`。
- 旧`VTAUopPush`参数和符号保持不变，等价于新入口rounding=0；新入口只对ALU使用非零rounding。
- `run_tests.sh --backend fsim|tsim [--alu-only] [--encoding-only]`设置独立进程所需TVM_PATH、VTA_PATH、VTA_CONFIG_FILE、PYTHONPATH，使用.envs/tvm-vta-env运行pytest；输出目录为被忽略的reports。

- [ ] 写`test_encoding.py`：检查128位布局、RMUL/RSFT所有合法rounding、原有字段不移动、rounding之外高位为零、至少两种几何配置。以C实际位域编码为参考，避免Python/Chisel共享错误偏移。
- [ ] 写runtime probe：新旧入口混合、每个kernel一致的模式、缓存签名含rounding，以及rounding=3、旧opcode非零rounding被拒绝；分进程检查预期错误。
- [ ] 运行`bash vta/tests/qconv2d/run_tests.sh --backend fsim --encoding-only`，确认新增字段/符号缺失引起失败。
- [ ] 实现上述常量、位域、入口、kernel.rounding保存及指令赋值。新旧入口复用内部Push逻辑；检查kernel内控制参数一致。将rounding放入新增调用的缓存signature，禁止外部缓存复用错误模式。更新ABI_SCHEMA_VERSION以使旧二进制被检测拒绝。
- [ ] 运行编码测试及`test_abi_fingerprint.py`、`test_backend_contract.py`、`test_dwc.py`中的runtime编码回归；确认旧API调用仍产生rounding=0。
- [ ] 提交：`feat(vta): encode RMUL RSFT and ALU rounding`。

### Task 2: CMSIS独立算术参考与真实FSIM ALU

**Files:** 新增`vta/tests/qconv2d/reference/build_reference.py`、`reference/cmsis_reference.c`、`alu_probe.cc`、`test_alu_requantize.py`；修改`vta/src/sim/sim_driver.cc`及`scripts/test_vta_fsim.sh`。

**Interfaces:**
- `build_reference.py --cmsis-root PATH --output-dir PATH`生成双舍入/单舍入两份参考库及source hash/version/build macro清单；采用支持宿主标量编译的官方源文件，不手写替代CMSIS函数。
- 参考C导出`int32_t cmsis_requantize(int32_t x, int32_t multiplier, int32_t shift)`。
- 同一参考wrapper预留Task 3使用的`int cmsis_conv2d(const char *fixture_dir, const char *output_dir)`，实现时对应真实`arm_convolve_s8`。
- ALU probe从文件加载opcode/rounding/输入/操作数序列，执行真实driver，并导出完整INT32结果；FSIM/TSIM使用相同输入格式。
- 完整INT32观测通过scratch accumulator复制与四次低字节store重建，不允许INT8 store掩盖高位差异。

- [ ] 写算术用例：x=1,m=2^30,s=-1双舍入1/单舍入0；负半值及邻值、INT32_MIN/MAX、零、移位0/1/31、乘积高位、普通MUL回绕、立即数和逐lane寄存器参数。
- [ ] 写范围用例：单舍入正shift合法输入匹配、非法预左移拒绝；RSFT=-1/32拒绝；旧SHIFT合法范围左右移回归；不把RMUL的INT32_MIN×INT32_MIN变为饱和输出。
- [ ] 构建官方参考。记录本地旧版本单舍入中间值为INT32的差异；当前参考必须使用真正的INT64版本源码，不能只把手工修改旧头文件作为最终参考。以固定版本/hash及保留许可证的最小源码集实现可复现构建。
- [ ] 运行`bash vta/tests/qconv2d/run_tests.sh --backend fsim --alu-only`，确认RMUL/RSFT尚未实现时失败。
- [ ] 实现FSIM MUL明确回绕、RMUL完整内部乘积及31位舍入、RSFT；验证opcode/rounding组合及RSFT操作数范围，避免有符号溢出。保留SHIFT外部语义。
- [ ] 重建：`bash scripts/build_vta_lib.sh --config "$PWD/vta/config/vta_64mac.json" --backend fsim`。
- [ ] 运行ALU测试，对CMSIS双/单路径至少各10万组固定seed随机样例逐元素零差异；运行`bash scripts/test_vta_fsim.sh`检查旧ALU和BYOC回归。
- [ ] 提交：`feat(vta): align FSIM RMUL and RSFT with CMSIS rounding`。

### Task 3: 真实卷积样例、逐通道调度与FSIM验收

**Files:** 新增`vta/tests/qconv2d/extract_conv_fixture.py`、`fixture.py`、`conv_probe.cc`、`test_conv_requantize.py`、`analyze_rounding.py`、`fixtures/`、`README.md`；扩展Task 2的CMSIS wrapper。

**Interfaces:**
- `extract_conv_fixture.py --model PATH --cifar-batch PATH --sample-index N --output-dir PATH`提取首个CONV_2D；固定样例index=0。使用TFLite解释器禁用delegate并保留中间tensor。
- `fixture.py`提供`load_fixture(path: Path) -> dict`、`quantize_multiplier(scale: float) -> tuple[int,int]`、`check_requantize_range(acc: ndarray, shifts: ndarray, mode: str) -> None`。
- 固定输出为`fixture.npz`及`metadata.json`：input、weight、bias、multiplier、shift、tflite_output；元数据含模型/输入hash、tensor索引、padding/stride/dilation/激活、scale/zero point及运行时版本。
- `conv_probe --fixture DIR --mode double|single --output-dir DIR`执行实际GEMM及ALU，导出accumulator和output；driver backend由独立进程选择。
- `analyze_rounding.py --fixture DIR --fsim-dir DIR --cmsis-dir DIR --output PATH`生成差异坐标、中间值、策略与归因JSON。

- [ ] 写提取检查：INT8[1,32,32,3]、INT8[16,3,3,3]、INT32[16]、输出INT8[1,32,32,16]，两个量化参数数组均长度16；scale生成和通道顺序必须与schema一致。
- [ ] 确认现有.envs是否提供TFLite推理，若缺失仅补齐独立测试环境依赖，记录安装及版本。先生成固定真实输出，不用手写公式冒充解释器输出。
- [ ] 写实际CMSIS卷积调用与手工INT64累加交叉检查，双/单宏分别编译；捕捉其INT32累加及输出。遵守正shift范围约束。
- [ ] 写失败用例：完整卷积FSIM/CMSIS零差异、3输入通道padding、图像四边padding、不同逐lane shift、单/双结果分歧，以及差值为1但累加/参数错误时报告必须拒绝归因舍入。
- [ ] 实现host im2col及硬件布局；host只准备数据，不执行待验收卷积。对input zero point=-128，用显式边界值-128及bias修正`bias-input_zero_point*sum(weight)`，补齐输入lane的weight为零；对CMSIS累加逐元素验证此等价变换。
- [ ] 按64个输出位置分tile、16输出通道分两个BLOCK_OUT块，检查当前64mac SRAM容量；GEMM处理9个tap并加载修正bias。逐lane加载multiplier/shift向量，RMUL和寄存器RSFT直接读取每个通道参数；保持输出通道顺序。
- [ ] 在真实driver上读回INT32累加，随后执行指定模式的RMUL/RSFT、zero point和激活裁剪。执行`bash vta/tests/qconv2d/run_tests.sh --backend fsim`，要求CMSIS/FSIM累加和最终输出均零差异。
- [ ] 对比TFLite并运行归因报告。尝试受支持的舍入组合；真实样例不能识别时加固定seed输入或核查实际内核源码/构建。仅接受逐项证明由舍入导致且无法对齐的±1差异；如策略不同，保存独立命名序列并保持CMSIS基准不变。
- [ ] 提交：`test(vta): validate per-channel qconv2d against CMSIS and TFLite`。

### Task 4: Chisel解码与一个cycle的MUL/RMUL/RSFT

**Files:** 修改`vta/hardware/chisel/src/main/scala/core/ISA.scala`、`Decode.scala`、`TensorAlu.scala`；修改`src/test/scala/unittest/FetchDecodeTest.scala`、`AluTest.scala`、`TensorAluTest.scala`；新增`AluRequantizeTest.scala`。

**Interfaces:**
- ALU_OP_NUM=7，C_ALU_ROUND_BITS=2；AluDecode增加`alu_rounding`，扣减高padding，要求非负布局。
- Alu/AluReg/AluVector增加2位rounding输入；TensorAlu及TensorAluPipelined按原valid/opcode时序传递该字段。
- opcode3由真实操作数符号执行SHIFT；opcode4为普通MUL，不再充当内部SHL。RMUL/RSFT分别为5/6。

- [ ] 写FetchDecode测试：与Task 1的C位域golden一致，rounding=0/1/2均正确，旧偏移及128位长度保持。
- [ ] 写AluRequantize测试：复用CMSIS生成的golden向量；Scala使用BigInt参考完整乘积；逐lane不同移位量、负半值及31位移位均覆盖。
- [ ] 写AluReg周期测试：连续输入MUL/RMUL/RSFT且每拍改变rounding，验证输入寄存后一个计算cycle产生相应输出，不多插stage；valid空洞不能导致结果错配。
- [ ] 写TensorAlu测试：两条执行路径均覆盖负寄存器SHIFT、MUL opcode4、连续依赖RMUL→RSFT、SRC=DST及src/dst loop factor。非法rounding/RSFT量不得静默提交写回。
- [ ] 使用现有Makefile的SBT_ENV/cache与.envs工具运行新增suite，确认新接口缺失导致失败；沿用构建脚本管理的Java/cache配置，不改机器全局设置。
- [ ] 实现组合乘法及Q31格式转换、RSFT舍弃位/阈值判断和字段流水；更新旧Alu参考中opcode4=SHL的假设。禁止为乘法增加流水stage。
- [ ] 用`bash scripts/build_vta_lib.sh --config "$PWD/vta/config/vta_64mac.json" --backend tsim`运行现有Chisel lint/unit tests并重建RTL/Verilator库。新增suite必须实际运行，不仅elaborate通过。
- [ ] 提交：`feat(vta): implement single-cycle RMUL RSFT in Chisel`。

### Task 5: TSIM同样例验收、入口与最终报告

**Files:** 扩展`vta/tests/qconv2d/test_alu_requantize.py`、`test_conv_requantize.py`、`run_tests.sh`、`README.md`及`scripts/test_vta_tsim.sh`；仅在确有新字段误执行路径时修改非目标后端的拒绝检查。

**Interfaces:**
- 每个backend使用独立进程加载其库，结果保存reports/fsim和reports/tsim；共同fixture hash和指令hash必须一致。
- 最终JSON至少包含cmsis_fsim_mismatch_count、fsim_tsim_mismatch_count、tflite_fsim_mismatch_count、tflite_max_abs_diff、rounding_evidence及source/runtime/build metadata。

- [ ] 写跨backend检查：相同fixture/指令运行单双路径，完整INT32 ALU结果、卷积累加及最终INT8输出全部精确比较；错ABI旧库必须拒绝，不能当作运行成功。
- [ ] `bash vta/tests/qconv2d/run_tests.sh --backend fsim`保存基准；随后`bash vta/tests/qconv2d/run_tests.sh --backend tsim`生成对应结果并比对FSIM，所有差异数必须0。
- [ ] 扩展现有两个测试脚本纳入qconv2d；执行`bash scripts/test_vta_fsim.sh`和`bash scripts/test_vta_tsim.sh`，旧SHIFT、GEMM、DwC与runtime依赖回归不得失败。
- [ ] 检查Xilinx/Intel等非目标路径，对于无法实现的新opcode/非零rounding增加明确拒绝；不能误执行普通乘法或忽略rounding。
- [ ] README记录重建、提取、参考、测试命令、数据来源及合法范围；最终报告明确TFLite是否零差异，如接受±1则附全部归因证据及尝试策略。
- [ ] 核对`git diff --check`及`git diff --name-only`，确保无vta/apps修改、报告日志未提交、固定fixture能由脚本重建。
- [ ] 提交：`test(vta): require exact FSIM TSIM qconv2d parity`。
- [ ] 按选定执行方式完成独立whole-branch review（gpt-6.1-sol/high），修复有效问题并仅重跑受影响检查；全部验收完成后总结实际证据及任何未执行项。

## Self-review

- spec各节已映射至Tasks 1–5；未扩展完整模型BYOC自动识别，验收使用真实driver指令序列。
- FSIM先于TSIM实现；独立官方CMSIS与真实TFLite解释器均为必需，环境缺失不得跳过后声称完成。
- API签名、fixture格式、参考接口及probe输出由上游任务定义，下游复用。
- rounding缓存、32位观测、padding/通道参数、旧CMSIS版本、流水/ABI五项风险均有相应测试。
