# Plan: IC V1 NOP 与融合 tuning 一致性

## Latest active plan: TSIM 单次 cycle cost

此前 Checkpoints 1–4 已完成，融合与 replay 修复经 Reviewer Pass。当前 root 为 `2cf608910d37c7c01ab94eadc7acf6f36a5d739d`，VTA 为 `4dba1e8eb75f9ed76fc270f9eff6c2df179176bb`，TVM 为 `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`。以下是新审批范围，后文保留为已完成工作的计划记录；发生冲突以本段为准。

### Decisions and sequence

1. 最小修改共享 TSIM runner/loader。保留标准 AutoTVM RPC 流程；优先使用 TVM time_evaluator 的 `f_preproc` hook：其调用位于 warmup 之后、正式执行之前，可调用已注册的 `vta.tsim.profiler_clear`。用 TSIM 专用 module adapter 或等价局部方式注入，不修改 TVM/runtime。若 hook 不适合，允许在同一 Python runner 局部实现等价的 warmup→clear→一次执行→status；不添加二次除法。
2. TSIM 保持恰好一次计数调用，明确固定/校验 number=1、repeat=1、min_repeat_ms=0，并处理冲突 f_preproc/CPU cache flush，避免静默多次计数或覆盖用户 hook。FSIM 完全保持现有计时行为。
3. 新 TSIM 测量协议包含版本、计数调用数 1、warmup 排除策略，作为共享侧 metadata 和 IC V1 result 的明确契约。TSIM artifact validator 的统一检查让 resume、history-best、MAC 报告拒绝缺少该契约的旧累计数据；不重写旧文件，不默认除以二。FSIM metadata 兼容维持。
4. IC V1 保留当前真实融合 task 及 FSIM search/best 选择，只修正最终 TSIM cost 与结果验证。新 result 保存协议，加载/replay 拒绝旧累计周期性能身份，继续校验日志和配置。可以继续使用 FSIM record 作为配置来源；其 cost 不是 TSIM cycles。
5. 先验证不等 warmup/正式周期的回归测试与共享/IC V1兼容测试，再做真实融合 config32 的有界 TSIM oracle。记录 warmup cycles、清零、正式单次 cycles、AutoTVM cost；期望 cost 等于正式单次 oracle，而非两次总和或平均。除必要复核外不做随机搜索。
6. 更新历史报告：82524/82604 与120983属于旧累计计数，原44.62%/30.47%单次利用率及基于其得出的优化周期差撤回；只能将除二值标为均值估计。最终利用率以新实测单次周期计算，原数据/hash保留。NOP结构事实保留，不再把warmup与正式dump一起统计。

### Checkpoint 5: Runner 和数据口径修复

Fresh Default 执行 Tasks 6、7、8，逐任务验证、分别提交。

- Task 6 owns shared `autotvm_tuner.py` 的 TSIM runner/loader 及 `tests/test_autotvm_tuner.py` 的计数回归；实际时间评估流程中验证 warmup 排除。
- Task 7 owns shared metadata/validator 和对应 tests，以及 MAC report 的协议消费/测试（若 validator 已统一覆盖则不作无必要修改）。FSIM行为与旧FSIM身份保留。
- Task 8 owns IC V1 `tune.py`、`tests/test_tune.py`；新 TSIM 协议与融合/replay校验。`fused_tasks.py`及真实pipeline只读，除非局部验证显示测量一致性需要最小修复，且不改计算契约。

### Checkpoint 6: 实测与文档纠正

Fresh Default 执行 Task 9。复用 config32 实际完整融合、同一 geometry；FSIM output 对照可复用已记录正确性并运行 focused tests，新 TSIM 单次 output/oracle必须验证。产物写入 ignored `fusion-single-call/`，不能覆盖旧 fusion-smoke。保存真实计数范围、dump和可复现命令。只修改 EVIDENCE、ANALYSIS、CONSISTENCY、IC V1 README、scripts README；必要 scoped measurement bugfix限定 Tasks6–8路径并重新验证。

### Verification commands

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py
```

TSIM oracle 使用既有测量入口或任务 scoped 可复现 harness，不安装依赖；命令和完整步骤写进 CONSISTENCY。本地 RPC bind 如被沙箱限制可针对同一有界命令请求 escalation。共享变更只拓展到受影响检查；不全量调优、不改硬件、真实模型计算或 tile 复用策略。

### Risks and checks

- f_preproc 若调用次序错误仍会累计 warmup：用不等周期顺序断言、真实 oracle 对照。
- repeat/min_repeat_ms 可自动追加调用：TSIM显式约束，并测试拒绝或确定单次语义。
- 旧 sidecar 被误复用：统一协议验证及 resume/history-best/MAC report负例；FSIM不受影响。
- 持久化 result身份不完整：真实 JSON 往返、新协议校验、旧累计口径负例。
- 新周期不完全等于旧总和一半：报告 warmup/正式初始化差异，直接使用单次实测。

完成后 fresh Reviewer 审核完整最新 committed range；继续自动 Fix/Verify/Re-review。Root lifecycle docs只由Root维护。

## Revision and completed work

原 Checkpoint 1 / Task 1 已提交 EVIDENCE.md；Checkpoint 2 / Task 2 已提交 ANALYSIS.md，经修订后 Reviewer Pass，root tip 为 8c7817bb0a15f206ec5841c16acb6f0ec6713031；TVM/VTA 功能代码未变。保留这些历史文件，新任务编号从 3 开始。

本轮按已批准修订 SPEC 修正当前 IC V1 单 workload `tune.py`。排除权重/输入 tile 复用和硬件修改。依赖顺序为真实融合任务构建 → 单 workload 测量与身份/回放契约 → FSIM/TSIM 有界验证与 NOP 报告 → 独立 Review。

## Implementation decisions

1. 增加 IC V1 局部融合任务模块 `fused_tasks.py`。从 prepared.mixed_module 的真实 VTA outlined functions 取得完整融合计算，优先复用现有 legalization/packed-core 与调度逻辑，避免手写固定 shift/bias 顺序。模块必须在 AutoTVM builder 子进程中可导入并注册任务，不能仅依赖父进程临时对象。
2. 完整任务身份包含 Conv 属性、后处理结构与常量身份，序列化可重建。Conv shape 相同但融合语义不同的 occurrence 不合并；相同完整语义可合并且保留 occurrence/symbol 映射。workload-index 为新的明确完整任务顺序，并记录与旧 Conv task 的映射，不能暗中承诺旧编号含义完全不变。
3. 保留现有 Conv 调度 knobs，不进行数据复用优化。融合 task.instantiate 在所选 ConfigEntity 下生成真实融合输出 schedule；直接或通过定向 DispatchContext 将所选配置作用到真实 Conv schedule key。
4. IC V1 tune 搜索与最终 TSIM 使用同一融合 task，并按现有进程可恢复方式运行。默认 random/local/32trials/120s 保持；新结果记录 schema、measurement_scope、model/geometry/log hash、完整融合身份、occurrences、Conv schedule key、MAC 数和周期。旧裸 Conv 结果保留，不能静默用于融合测量声明。
5. 增加 IC V1 局部配置应用/回放校验接口：新 artifact 验证融合 identity、model、geometry 和 log；在真实模型 lowering 的 Conv key 上应用选定配置。旧裸 Conv logs 可仍用作旧 schedule 搜索记录，但新融合性能验证必须拒绝把其结果当新测量。无需更改其他五个模型的默认 tuning。
6. correctness oracle 使用真实 outlined fusion 的 CPU/reference 计算或等价 Relay 路径；对同一输入比较 fusion tuning 输出与真实 VTA fusion 输出，包含负值、shift 与 clip 饱和边界。检查 ALU lowering，不能仅断言指令存在。
7. 只通过现有 debug API/运行方式输出一次 smoke dump；必要时为 tune 增加可选 `--dump-instructions`，保持默认行为。dump 必须来自被测融合候选，记录配置与输出验证。不能拼接 ALU 或复制旧 dump。

## Checkpoint 3: 构建与接入

Fresh Default 执行 Tasks 3、4，逐任务验证和独立提交。

- Task 3：建立融合任务、语义与可重建 identity、配置传递及 correctness tests。
- Task 4：接入 tune 搜索与 TSIM、artifact 元数据、配置应用/回放验证，保留必要兼容性，增加对应 tests。

Ownership：IC V1 `fused_tasks.py`、`tune.py`、`tests/test_fused_tuning.py`、`tests/test_tune.py`；仅若需复用才允许给 shared `autotvm_tuner.py` 加局部辅助能力并在 `tests/test_autotvm_tuner.py` 验证默认兼容。不要修改 VTA TOPI、真实模型 pipeline、硬件或 TVM 核心。

## Checkpoint 4: 有界实测与 NOP 报告

Fresh Default 执行 Task 5。运行融合 task smoke；默认目标 workload 0，最多 8 次候选测量，至少一个成功后做相同配置 TSIM。优先预先核实 config 可编译避免随机失败浪费。若 8 次内无成功，查找局部失败根因、修复后重跑 bounded smoke，不扩大到穷举；需要改变 approved decisions 时 escalation。

对代表输入核验真实融合输出与 tuning 输出；一次 dump 必须包含适用 ALU，记录新周期。修改 README/scripts 文档与历史报告适用范围，新增 CONSISTENCY.md 按编号解释 NOP。所有生成产物在 ignored build 路径，原日志保持原样。

## Verification commands

从仓库根目录执行：

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py --workload-index 0 --trials 1 --timeout 120
```

若增加 dump flag，Task 5 使用实际 `--help` 确认后记录精确命令。融合 correctness FSIM/TSIM 检查由 test_fused_tuning.py 的集成用例或专用可复现验证入口执行；TSIM 用 fresh process/正确 backend 初始化。测试只 broadening 到被共享改动影响的范围，功能路径不改则不跑无关全量模型矩阵。

## Risks and mitigation

| Risk | Mitigation |
| --- | --- |
| Relay compiler cache 未应用所选 config | 每次 instantiate 明确配置上下文；跨两个配置检查 schedule/指令变化及真实模型应用 |
| 子进程无法重建 task | 任务模块可导入，语义与常量可序列化；用真实 LocalBuilder smoke 验证 |
| 相同 Conv 不同后处理被合并 | fused identity 与 occurrence 映射测试，保留 Conv key 与完整 measurement key 区别 |
| 融合日志无法回放 Conv schedule key | 定向配置应用校验，真实模型 lowering 检查，拒绝不同融合语义的测量身份 |
| 新周期看似变差 | 明确新周期包含 ALU，与旧裸 Conv 数值不是同计算的提升/回退 |
| NOP 数被误读为 stall | 仅说明依赖生成机制；无动态 trace 不分摊等待周期 |

## Coordination

Root owns lifecycle docs。Default 按 checkpoint 顺序执行，逐任务提交；不并行。完成后 fresh Reviewer 审核完整 initiative committed range；Required/Critical findings 进入 fresh Default fix / fresh Reviewer re-review。所有 Git mutation 通过 workflow。
