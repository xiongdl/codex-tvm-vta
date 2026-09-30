# Tasks: IC V1 NOP 与融合 tuning 一致性

## Completed checkpoints

- [x] Checkpoint 1 / Task 1: EVIDENCE.md，root e1c8f1689ad521369dad59e939802804f6f7065c。
- [x] Checkpoint 2 / Task 2: ANALYSIS.md，root fd89ec389e54cb38d71843413c6b29a209f80024；review fix 8c7817bb0a15f206ec5841c16acb6f0ec6713031 后 Pass。

这些文件说明旧裸 Conv 计算，不重复执行原任务；下面按修订 SPEC 执行。

## Checkpoint 3 — 完整融合任务与 tuning 接入

### Task 3: 从真实融合算子构建可测任务

- Deliverable: IC V1 `fused_tasks.py` 与 `tests/test_fused_tuning.py`。
- Acceptance:
  - 从真实 prepared VTA fusion 获取正确顺序、bias/shift/clip/cast/dtype 和常量；融合 task 在所选 Conv ConfigEntity 下使用真实计算与 schedule，MAC 分子只计 Conv。
  - 完整 identity 可序列化重建、子进程可注册；相同 Conv 但不同后处理不会静默合并，保留 occurrence/symbol 与旧 Conv key 映射。
  - 代表性及负值/饱和边界输入与真实融合 reference 比较通过，ALU lowering 存在；两个配置能正确传递，避免 cache 忽略 config。
- Verify: focused fusion tests；实际 LocalBuilder 的小规模编译验证；一致性验证不能仅由 mocks 或检查字符串替代。
- Dependencies: approved revised INTENT/SPEC/PLAN/TASKS。
- Owned: fused_tasks.py、test_fused_tuning.py；必要只增 helper 的 shared autotvm_tuner.py/test_autotvm_tuner.py（若实际需要）。其余功能路径只读。
- Commit: Task 3 验证后 workflow 单独提交；不改 Root 文档。

### Task 4: 单 workload tuning 全程测量融合语义

- Deliverable: IC V1 tune.py 接入，tests/test_tune.py 更新，fusion 测量身份及配置应用/回放校验。
- Acceptance:
  - FSIM 搜索与 TSIM 最终测量为同一完整 fusion；保留 random/local/defaults 与 runner failure recovery；新 workload-index 顺序和 occurrence 明确。
  - 结果元数据识别完整计算、model/geometry/log hash、Conv key/config、MAC 与周期；同 Conv 不同 fusion 不静默共享性能身份，新融合结果校验拒绝不匹配和旧裸 Conv 口径。
  - 新 artifact 的选定 schedule 可映射到真实模型 Conv key，验证真实 lowering 使用该配置；其他模型默认提取/测量/旧回放行为不受无关影响。
- Verify: test_tune.py、test_fused_tuning.py 与受影响 shared tests；成功/失败路径与身份失配负例；实际 builder/runner bounded 预验证。
- Dependencies: committed Task 3。
- Owned: tune.py、fused_tasks.py、test_tune.py、test_fused_tuning.py，必要 shared helper/其 focused tests。
- Commit: Task 4 单独验证并提交。

Checkpoint verification：Tasks 3/4 acceptance 成立，focused tests 通过，两任务各自已提交，managed repositories clean；返回 GREEN 和精确 commit map。

## Checkpoint 4 — 实测、NOP 原因与文档

### Task 5: 验证完整计算并交付可复现证据

- Deliverable: CONSISTENCY.md；IC V1 README 和 scripts/README 更新；旧 EVIDENCE/ANALYSIS 顶部明确裸 Conv 历史口径；ignored build 下 fusion smoke artifacts、dump。
- Acceptance:
  - 有界 workload 0 smoke，最多 8 次候选测量，至少一个成功 fusion FSIM 候选及其精确配置 TSIM cycles；输出 correctness 对比真实融合，dump 包含适用 ALU；新 identity 与 old 44.62% 口径不同明确记录。
  - 解释原 19 条 NOP 的初始化、分块依赖、收尾来源；逐组编号、TIR/runtime 源码依据，区分结构 token 与真实等待；如新 dump 的 NOP 改变，说明变化来源，不仅比较数量。
  - 文档覆盖新任务顺序、融合计算范围、身份与回放契约、命令/产物；不给达到 61.62% 保证，不实施 tile 复用或硬件改动。
- Verify: focused correctness tests；实际 FSIM/TSIM smoke、dump 和 profiler；input/output 校验与原产物 hash 不变；git diff --check 与 clean workflow。
- Dependencies: committed Tasks 3/4。
- Owned: CONSISTENCY.md、EVIDENCE.md、ANALYSIS.md 的范围标注、IC V1 README、scripts/README；必要 task-scoped correctness/measurement bug fixes限 Tasks3/4路径，修复须额外验证。Root lifecycle docs、TOPI/TVM/硬件/其他模型功能路径只读。
- Commit: 验证完成后单独 workflow 提交 Task 5。

Checkpoint verification：Task 5 acceptance 成立，实测/正确性/ALU 证据记录齐全，managed repositories clean，返回 GREEN 和 commit map。

## Final review

Fresh Reviewer 对完整最新 initiative committed range、approved artifacts、各任务验证/commit maps 审核。Required/Critical implementation findings 由 fresh Default Fix/Verify 后 fresh Reviewer 重审；改变 Root-owned 决策需 escalation。
