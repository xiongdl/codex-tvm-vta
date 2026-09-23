# Specification: TSIM Artifact Integration

## Functional requirements

1. 使用 `vta/config/vta_64mac.json` 作为唯一几何配置，重新生成 Chisel geometry
   properties、硬件模型和 TSIM 动态库。
2. TSIM build 必须通过现有构建入口，并生成与当前平台命名规则一致的
   `libvta_tsim` 及所需 `libvta_hw` 产物。
3. 新进程必须能加载 TSIM 库、注册 runtime functions、初始化 simulator，并在相同
   `VTA_CONFIG_FILE`/`VTA_BACKEND=tsim` 下运行 focused tests。
4. 产物不得依赖旧的 `TARGET=sim/tsim`、`--target` 或 `VTA_PLATFORM` 选择逻辑。
5. 生成物中的几何字段必须与 JSON 一致；不得通过手工编辑 ignored build artifacts
   伪造通过结果。

## Verification

- 运行项目维护的 TSIM build/test 命令，并保留 exit status 与关键产物检查结果。
- 至少验证：库存在、动态加载成功、`vta.tsim.init` 成功、TSIM 基础测试通过。
- 若 Chisel/Verilator/Java 环境不可用，应明确报告环境阻塞，不将未构建状态记为通过。

## Non-goals

- 不处理 FPGA backend。
- 不改变 backend/config 解耦设计。
- 不把 benchmark 失败改写为单纯库加载成功。
