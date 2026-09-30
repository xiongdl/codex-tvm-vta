# Tasks: IC V1 MAC 利用率诊断

## Checkpoint 1 — 基线与指令证据

### Task 1: 核对输入并建立指令开销证据

- Deliverable: `EVIDENCE.md`，列出输入 identity/hash、MAC 数、geometry、配置、周期；完整 dump 的指令统计及源代码语义依据。
- Acceptance:
  - 核实 workload 0 的 2359296 MAC、64 MAC/cycle、392/393 周期和利用率；计算达到 61.62% 的周期预算及需减少的周期。
  - 统计 GEMM 非 reset 工作量和 reset 迭代、LOAD/STORE/UOP 类型与数据量、依赖链；区分 logical MAC 与 padded 工作量，并标注数据单位。
  - 每项推论可追溯到 dump 编号和源码位置；保留可复现计算，不声称静态队列状态等于运行时 stall。
- Verify: 项目环境计算利用率；统计与原文、硬件/运行时语义交叉核验；输入 hash 前后相同；git-workflow status 清洁后交接。
- Dependencies: approved lifecycle artifacts。
- Owned files: initiative `EVIDENCE.md`；必要临时/ignored 分析产物。Root 文档、功能源码和原始输入只读。
- Commit: 验证通过后单独提交 Task 1。
- Checkpoint verification: 所有 Task 1 acceptance 成立，报告已提交且 managed repositories clean。

## Checkpoint 2 — 软件优化路线与限制

### Task 2: 交付证据支持的优化建议

- Deliverable: `ANALYSIS.md`，中文结论与按优先级排列的软件优化路线。
- Acceptance:
  - 解释可确认的当前开销与不能分离的开销，评估现有调度空间是否覆盖候选方向；引用 committed EVIDENCE。
  - 每项软件建议含 dump/源码依据、作用机制、buffer/依赖/正确性约束、验证方式；可估算的收益给范围或下界，不能实测的注明假设。
  - 判断 61.62% 所需周期缩减是否可能由软件候选覆盖，证据不足则明确；只在软件限制有证据时给硬件候选，不承诺找到历史修改。
- Verify: 独立复核目标周期计算、源码引用、配置差异及建议约束；必要时有界重放并记录结果；输入不变；managed repositories clean。
- Dependencies: Task 1 committed OIDs and EVIDENCE。
- Owned files: initiative `ANALYSIS.md`；必要临时/ignored 分析产物。Root 文档、EVIDENCE、功能源码和原始输入只读。
- Commit: 验证通过后单独提交 Task 2。
- Checkpoint verification: 所有 Task 2 acceptance 成立，报告已提交且 managed repositories clean。

## Final review

Fresh Reviewer 对 initiative 全部已提交改动、approved artifacts、验证证据和各仓库精确 base-to-tip range 审核；Required/Critical implementation findings 由 fresh Default 修复后 fresh Reviewer 再审。Root-owned 文档变更需要 Root escalation。
