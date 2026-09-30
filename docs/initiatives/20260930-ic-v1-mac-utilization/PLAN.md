# Plan: IC V1 NOP 与融合 tuning 一致性

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
