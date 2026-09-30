# Spec: IC V1 NOP 诊断与 tuning / 推理计算一致性

## Latest revision: TSIM 单次周期测量

用户最新要求修正 TSIM AutoTVM 周期统计，FSIM 保持现状。下列要求补充并优先于本文原有周期结论；原功能范围和融合语义要求保持。

- Objective：TSIM runner 返回恰好一次成功算子执行的原生 cycle_count。若保留 warmup，warmup 必须在测量清零之前执行并排除；不得读两次累计值、除以二或用 wall time 换算周期。
- 已证实根因：ProfilerModuleLoader 在 time_evaluator 前 clear，TVM time evaluator 执行一次 warmup 和 number×repeat 次正式调用；TSIM Profiler::Update 使用累加，而 runner 直接将结束累计数写为 cost。当前 number=repeat=1 下为两次累计。
- 修复共享 `autotvm_tuner.py` 的 TSIM 路径，覆盖通用 TSIM tuning、IC V1 最终 TSIM measurement 和 direct runner 使用。FSIM 的 runner、RandomTuner/搜索策略、默认计时与任务计算不变；不改变 TOPI、runtime、硬件。
- 测量调用策略须明确单次 scope，拒绝或明确处理可能导致多次正式执行的 number/repeat/min_repeat_ms 配置；不能静默把多次累计作为单次 cost。
- TSIM 新产物记录测量协议和计数调用数。旧双次累计日志/sidecar/IC V1 result 不得静默作为新单次周期数据用于 resume、history-best、MAC 报告或 replay 的性能声明；旧 FSIM 产物与纯配置来源兼容性不应无故改变。
- IC V1 完整融合保持：model-derived bias/shift/clip/cast 的次序、参数、dtype 与部署融合一致；相同 selected config 在 tuning 与真实 lowering 路径下有效，负值/饱和输出验证不降低。isolated 测量不冒充整模型端到端 profile；不扩展到其他模型的融合重设计。
- 验证必须记录 warmup/clear/execute/status 的实际顺序和计数：回归用例应让 warmup 与正式执行贡献不同周期，以发现累计或简单平均的错误；用真实 TSIM 的同 task/config 单次调用 counter 作为 oracle，验证 AutoTVM cost 相同。
- 有界复测 IC V1 fusion config 32（已验证可运行），生成明确计数范围的 ALU dump，并核对 FSIM output/真实融合 output 一致性。更新 EVIDENCE/ANALYSIS/CONSISTENCY 以及涉及 cycle 含义的 README，撤回之前由双次累计导致的单次性能判断，保留原始输入与历史记录。
- 新报告区分“旧两次总和”“仅除以二所得均值估计”和“新实测单次周期”。单次 MAC 利用率必须使用新实测值；不能承诺达到 61.62%。

Success criteria：共享 TSIM 单次 cost、真实 oracle 和调用顺序验证通过；FSIM 回归不变；旧累计口径识别/拒绝与新协议验证有负例；完整融合正确性保留；相关报告更新并经独立审核。

## Revision and objective

本规格按用户后续指令修订，取代原来的 tile 复用建议方向。原 EVIDENCE.md / ANALYSIS.md 保留为裸 Conv 历史分析；新验证必须明确区分其计算口径。

解释当前 dump 的 19 条 NOP，并修正 IC V1 单 workload tuning：FSIM 搜索、TSIM 测量应执行真实推理融合算子的完整计算，包含适用的 bias、right_shift、clip、cast。真实图的属性与运算顺序是标准，不硬编码参考脚本的值。

## Current evidence and reference

- `image_classification_v1/tune.py` 经 `autotvm_tuner.extract_model_tasks` 取得独立 `conv2d_packed.vta` task；TOPI compute 只构建卷积与 identity output。
- 当前 config 392 dump 有 GEMM/reset、DMA、NOP，无 ALU；它不能作为包含后处理的真实融合层周期。
- `vta/python/vta/relay/transform.py` 的 `legalize_vta_function` 保留可选 bias → shift → clip → cast。
- `tvm/vta/scripts/tune_conv2d.py` 显式构建 conv → shift → bias → min/max → cast，可参考完整计算的组织方式，但其顺序与固定参数不能视为本模型语义。
- `vta/src/runtime/runtime.cc` 的 `DepPush`、`CommitPendingPop`、`PushNoop`、`Synchronize` 与 TIR coprocessor sync pass 共同决定 NOP；静态 token 余额不是等待周期。

## Structure and ownership boundary

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py`：单 workload tuning 与输出。
- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`：共享提取、builder/runner、history-best；仅在一致性需要时调整，保留其他模型兼容性。
- `vta/python/vta/relay/` 与 TOPI：真实推理计算和调度来源；优先复用现有路径，最小范围变更。
- 对应 `tests/`：计算与属性一致、ALU 生成、日志身份与回放验证。
- IC V1 README 与 `scripts/README.md`：记录口径、命令和旧产物兼容规则。
- initiative 文档：新增 `CONSISTENCY.md` 记录 NOP 依据、修复机制、验证与周期，更新历史报告的适用范围说明。

## Required behavior

1. 从 prepared IC V1 图识别对应真实 VTA 融合 occurrence，建立 Conv workload 与完整融合计算的对应关系。相同 Conv shape 但后处理不同的 occurrence 不能被默默去重为一个完整任务。
2. 复用真实图属性和计算路径。bias 的有无、值或参数化契约、shift、clip 边界、输出 dtype、运算顺序与真实推理相同；适用的计算留在 VTA ALU 而非 host。
3. FSIM tuning 和 TSIM 最终比较测量同一完整任务；单算子 isolated 测量边界明确，不要求包含模型 host 前后处理或把 isolated cycles 当整模型 profile。
4. 正确性验证使用代表性输入、负值、溢出/饱和边界，并与真实融合计算比较；不能只检查编译成功或 ALU 指令存在。
5. tuning 身份/元数据包括融合语义，旧裸 Conv 产物必须能明确识别。旧数据不得静默用于新完整计算的性能声明；需要兼容的 Conv schedule key 与新测量 identity 分开处理。
6. 逐类解释 NOP：起始空闲 token、分块间数据就绪/覆盖保护和结束队列汇合；给出具体编号与生成源码。不能仅凭 NOP 数宣称瓶颈或直接删依赖。
7. 产出有界 smoke tuning、对应 ALU dump 和 TSIM cycle 结果；不做完整配置穷举。不把新周期与旧裸 Conv 周期当同计算的优化前后。

## Commands and environment

从仓库根目录执行，全部项目 Python 使用 `.envs/tvm-vta-env/bin/python`，geometry 为同一绝对 `vta/config/vta_64mac.json`。

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py --workload-index 0 --trials 1 --timeout 120
```

新增一致性测试和指令 dump 命令在计划中按实际入口列出；相关共享提取/回放变更需增加受影响兼容性检查。重建仅在实现确实需要且已有项目脚本支持时进行，不安装依赖或修改硬件。

## Style and testing strategy

遵循现有 Python 模块、测试命名和显式 backend/geometry 校验风格。报告每项结论提供指令编号、源码位置与验证命令，例如“INSTRUCTION 20 的 compute→store push 为第二条 store 提供 token；等待周期未知”。

测试先覆盖已发现的语义不一致，再实现修复；核对完整计算输出与真实融合函数，验证 ALU lowering。共享代码变更检查其他模型提取和现有 log/sidecar 的兼容规则，避免单 workload 修复改变无关应用行为。

## Boundaries

- Always：真实推理语义为准；保留原产物；记录测量计算范围；软件优先；依赖与缓冲区正确性不降标准。
- Ask first：改变已批准规格/计划、扩大至其他模型的功能重设计、需要用户独有信息或外部权限。
- Never：权重/输入 tile 复用优化；硬件改造；删除必要 token；伪造 ALU 以通过检查；用旧裸 Conv 周期表示真实融合推理性能。

## Success criteria

- NOP 说明可追溯到 dump 与 runtime/TIR 生成机制，明确其数量不等于真实 stall 周期。
- IC V1 tuning 与对应真实模型融合算子语义和输出一致，适用 ALU 出现在生成指令中，FSIM/TSIM 测的是同一计算。
- 新旧任务与性能口径可辨别，日志或回放不会静默混用不同融合语义。
- 有界 smoke 与相关测试通过，文档记录命令、指令、周期及限制，经独立审核。

## Open questions

实现路径、融合 occurrence 去重方式和 schedule-key 兼容方式由计划阶段根据代码机制确定；不需要用户指定技术方案。
