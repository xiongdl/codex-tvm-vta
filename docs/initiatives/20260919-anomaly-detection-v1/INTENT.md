# Intent: MLPerf Tiny Anomaly Detection v1 Deployment

## Outcome

新增 `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1` 部署样例，参考现有 `image_classification_v1`、`image_classification_v2` 和 `visual_wake_words_v1` 的组织方式，将 `.envs` 中的 MLPerf Tiny anomaly detection v1 ToyCar 模型接入 TVM/VTA。

## User and purpose

该部署样例面向需要在 VTA 模拟器上验证 MLPerf Tiny anomaly detection v1 模型部署的开发者，用于确认模型导入、量化/分区、Graph Executor 产物导出和运行时执行链路完整可用。

## Inputs and constraints

- 模型使用 `.envs/tiny-v1.4/benchmark/training/anomaly_detection/trained_models/ad01_fp32.tflite`。
- 测试数据使用 `.envs/ToyCar/test/` 下固定选取的 5 条
  `normal_id_01_*.wav` 和 5 条 `anomaly_id_01_*.wav`。
- 需要提供主机侧部署入口，并支持 FSIM 和 TSIM 两套验证路径。
- 不修改现有 MLPerf Tiny benchmark，不引入外部数据集或新的运行时框架。

## Success criteria

- 新样例具备与现有 MLPerf Tiny 部署一致的模型流水线、图产物导出、运行时和测试结构。
- 模型输入/输出、音频特征预处理、10 条样本清单和部署路由均有明确、可自动验证的契约。
- FSIM 与 TSIM 均能构建并重新加载 reference/mixed Graph Executor 产物，执行正常/异常各 5 条、共 10 条输入并产生正向 VTA 活动。
- 文档提供从仓库根目录执行的完整命令，并清楚列出模型/数据来源和构建前置条件。

## Out of scope

- MLPerf Tiny 正式 accuracy、performance、energy 或 submission 报告。
- 重新训练模型、生成新的数据集或修改 `.envs` 内容。
- 修改现有 benchmark 的公共运行时接口。
