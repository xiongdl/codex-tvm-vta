# IC V1 tuning 与真实融合计算一致性

## 口径修正

旧的 44.62% / 44.67% 数据来自独立 `conv2d_packed.vta` 裸 Conv。真实 IC V1
融合在 Conv 后还执行 `bias_add(64) -> right_shift(7) -> clip[-127,127] -> cast(int8)`。
旧 TSIM cycles 没包含这些计算，不能把新结果当作同一计算的前后对比，也不能用旧
44.62% 代表完整融合推理的 MAC 利用率。旧日志与 dump 保持原样；它们的适用范围已在
[EVIDENCE.md](EVIDENCE.md) 和 [ANALYSIS.md](ANALYSIS.md) 开头标明。

修订后的 workload 0 使用模板 `ic_v1_fused_conv2d.vta`，提取自实际 prepared VTA
composite，并从 Relay 函数读取 bias、shift、clip、dtype、符号和 occurrence。融合身份
SHA-256 为 `9009c9181d22e210e17db4f416f845204652b870fd1baf18d3ad421fd40aef92`；
AutoTVM workload SHA-256 为
`8ffe856231285ff3b7a28be6d65c09777b4288d55239088a3e673883939ea67d`。模型 SHA-256
是 `b5c0046d6e0328b4956afd6baa29555a29b1f1c65bdd45aaed75b7cd484d9f79`，几何配置
`vta/config/vta_64mac.json` 的 SHA-256 是
`23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa`。

## 正确性与有界 FSIM/TSIM 实测

项目环境下执行的 focused tests 全部通过：

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py
```

结果为 `15 passed`。测试从 prepared Relay 融合函数取出运算参数，在真实 Relay debug
executor 上计算结果，再和精确整数 reference 比较；样本覆盖负值和 clip 饱和边界。另有
两个配置通过真实 `LocalBuilder` 编译，且真实 Conv lowering 使用被选中的 Conv schedule
key。针对本次 smoke 的 config 32，我还用模型真实常量权重和确定性输入（NumPy seed
912）执行了编译后的 VTA FSIM 函数，将 packed 输出还原为 NHWC 后逐元素与 prepared
Relay 融合输出比较，结果完全相同；输出为 `(1,32,32,16)` 的 `int8`，含负值并达到
`-127` 与 `127` 饱和值。

在不超过 8 个候选配置的有界检查中，config 392 和 393 虽能编译，但 FSIM 执行分别在
`vta/src/runtime/runtime.cc::UopKernelMap::Get` 触发 `key=257`、`key=513` 超过现有
100 项限制；config 24 在 `UopKernel::VerifyDep` 因连续 UOP 写入相同 accumulator index
失败。这些是融合 ALU lowering 下实际不支持的候选，不能记录为有效 tuning 结果。config
0 和 config 32 的 FSIM 执行成功；选择 config 32 作为可工作的非默认 smoke 配置：

| 项目 | 结果 |
| --- | --- |
| 配置 index / entity | `32`; `tile_h=4, tile_w=32, tile_ci=1, tile_co=1, oc_nthread=1, h_nthread=1` |
| FSIM runner cost | `0.00130275 s`（本机 wall time，不是 cycles） |
| 同配置 TSIM `cycle_count` | `120,983` |
| logical Conv MAC | `2,359,296` |
| `2,359,296 / (120,983 * 64)` | `30.4703967%` |
| 完整融合身份 / 几何 | 上述 fusion SHA-256 / `vta_64mac.json` SHA-256 |

这个利用率以 Conv logical MAC 为分子，而分母 cycles 包含 ALU 后处理；它只描述该孤立
融合 task。它与旧裸 Conv 统计不可直接作优化增幅比较，也不是完整模型端到端 cycles。
它说明这次验证修复了计算语义，但没有证明 61.62% 可达。配置 32 的 FSIM、TSIM 和
debug dump 均使用同一 AutoTVM task 与同一配置实体。忽略的原始运行日志在
`vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/fusion-smoke/`，
其中 `config-32-debug-run.log` 保存了完整 VTA 指令输出，`config-32-debug.tar` 是生成的
debug 模块；文件 SHA-256 分别为
`51898f457ddbe272ef1045c65fd651265cabd41439415c4a17e60038b94e9eb8` 和
`d1d018bbace7696f7c1dac6e86c6f9eec16b39ad0c368acdfc2475f6cf2a4f5b`。旧 config 392 dump
SHA-256 仍为 `fcab0b7f885269ef7f5c826a6442939884d83f6d3eb844969b88096b982d41c0`。
被测 stream 已另存为 `config-32-instruction-dump.txt`（220 条、64 条 ALU、21 条 NOP，
SHA-256 `1fd2a1a82fd098d12432b43152b203b252f7dfafb08520a308d248eabccf0dff`）；汇总记录是
`result.json`（SHA-256 `6063b48aef4a01b04f9262e71a00ceb0c1e50d4554655627cb0b3abe18ec910b`）。

### 固定配置 FSIM/TSIM 复现

普通调参命令仍使用 RandomTuner；以下有界检查直接从实际融合 task 的 config space 取
已验证 config 32，不伪造 tuner record。FSIM 和 TSIM 分别在独立进程执行，selector 与
runner backend 保持一致：

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark" \
  ./.envs/tvm-vta-env/bin/python - <<'PY'
from tvm.autotvm.measure import MeasureInput
from image_classification_v1 import tune
from autotvm_tuner import measure_option

_, _, tasks = tune.prepare_v1_workloads()
task = tasks[0]
config = task.config_space.get(32)
measure = measure_option("fsim", timeout=120, number=1, repeat=1, cooldown_interval=0)
runner, builder = measure["runner"], measure["builder"]
try:
    runner.set_task(task)
    builder.set_task(task, runner.get_build_kwargs())
    item = MeasureInput(task.target, task, config)
    built = builder.build([item])
    result = runner.run([item], built)[0]
    print("config", config.to_json_dict(), "error", result.error_no, "cost", result.costs)
finally:
    tune._cleanup_runner(runner)
PY
```

将上面命令中的两个 `fsim` 分别替换为 `tsim`，并将 `VTA_BACKEND=fsim` 改为
`VTA_BACKEND=tsim`，会测出同一 task/config 的 cycle count。要生成带 ALU 指令的 runtime
dump，可用以下同配置 debug build。运行时会把完整指令流打印到 stdout：

```python
import vta
from tvm.autotvm.measure.measure_methods import BuildResult
from tvm.autotvm.utils import get_const_tuple
from tvm.contrib import tar

with task.target:
    schedule, args = task.instantiate(config)
with vta.build_config(debug_flag=2):
    module = vta.build(schedule, args, target=task.target, target_host=task.target_host)
path = "vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/fusion-smoke/config-32-debug.tar"
module.export_library(path, fcompile=tar.tar)
arg_info = tuple((get_const_tuple(x.shape), x.dtype) for x in args)
measure = measure_option("tsim", timeout=180, number=1, repeat=1, cooldown_interval=0)
runner = measure["runner"]
try:
    runner.set_task(task)
    item = MeasureInput(task.target, task, config)
    result = runner.run([item], [BuildResult(path, arg_info, None, 0.0)])[0]
    print("config", config.to_json_dict(), "error", result.error_no, "cycles", result.costs)
finally:
    tune._cleanup_runner(runner)
```

这里的 `task`, `config`、`MeasureInput`、`measure_option` 与上面的 pinned-config
命令相同。`VTA_DEBUG_DUMP_INSN` 为 runtime debug flag bit 1，runtime 在
`CommandQueue::Synchronize` 打印真实队列，不应手工拼接 ALU 或 NOP。

### Native FSIM result 保存、加载与 replay

验证 replay validator 时，用已知可运行的 config 32 做了一次单配置 FSIM
测量，并将真实 `MeasureResult` 通过 `autotvm.record.encode` 写为 native FSIM
记录；best log 是同一条成功记录（此次有界测量只有一个候选）。结果随后经
正式 replay 入口加载。FSIM 返回 `error_no=0`，cost 为 `0.001243333 s`；
AutoTVM 从文件解码出 config index 32。Replay CLI 成功验证模型、几何、完整
融合和 task workload 的 identities，校验 FSIM/best log 的文件 SHA-256，并将
配置应用到 prepared model 的真实 outlined fusion lowering；`lower_with_fused_config`
确认 lowering 使用了对应 Conv schedule key。

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py \
  --replay-result vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/replay-config-32/config-32-result.json
```

这条命令打印 `Real outlined model fusion lowering: verified`。忽略目录中的
FSIM 与 best log SHA-256 均为
`8c32b1ece9212e4c04d7e82a427be7dd9abd46be1ea489c5895801678bdf8610`；result JSON
SHA-256 为 `d00c6217af1ea5ea6ae454ecf1c41fd11e884b560fb42918b74c6fff598f9828`。
该 replay 检查配置身份与实际 lowering，不会重新测量 TSIM，也不代表完整搜索。

## 真实 fusion dump 与 NOP 解释

旧 config 392 dump 共 88 条指令，含 19 条 NOP（7 compute、9 memory、3 store）。编号和
其位置对应三组来源：

| 编号 | 角色与源码依据 |
| --- | --- |
| `0–1` | 两条开头的 `NOP-STORE-STAGE` 都只 push prev dependency，没有数据搬运。TIR `CoProcInstDepDetector::MatchFixEnterPop` 在 device program 开头补齐首次使用队列依赖；runtime `DepPush` 若没有可附加的前一条 store 指令就调用 `PushNoop`。它们是启动 token，不代表 store 工作或 stall 周期。 |
| `20–21`, `39–40`, `58–59`, `77–78` | 每个输出 GEMM tile 之后的 compute/memory 队列 token。`20/39/58/77` 是 GEMM 已携带 push 后仍需额外提交的 compute push；相邻 memory NOP 提交挂起的 pop。其后两条 STORE 分别消费 compute-to-store token；这组边界维持输出写回和下一 tile 对输入/权重的复用顺序。 |
| `26`, `45`, `64` | `NOP-MEMORY-STAGE` 位于 accumulator reset 后、下一 `LOAD INP` 前；它提交 compute-to-load 队列的 pending pop，使下一次 SRAM/input tile 生命周期在正确依赖后开始。 |
| `81–86` | 最后一组 tile 之后的 drain/queue join。runtime `CommandQueue::Synchronize` 在 FINISH 前建立 store/load 到 compute 的收尾依赖并提交 pending pops；`DepPush`、`CommitPendingPop` 在现有指令不能携带对应 flag 时发出这些空 NOP。 |

这些判断同时参考旧 dump 每条指令的 dep flag 与 queue balance，以及
`tvm/src/tir/transforms/coproc_sync.cc::CoProcInstDepDetector` 的 enter/exit/loop-carry
token 匹配逻辑。`runtime.cc::DepPush` 会优先把 push flag 附加到兼容的上条指令，否则
`PushNoop` 生成 `x_size=y_size=0` 的结构性指令；`CommitPendingPop` 也以零传输 NOP
提交 pop。`Synchronize` 会在 FINISH 前执行队列汇合。因此 NOP 数量不是 stall 周期数，
queue balance 也不是时间戳；不能按 19 条乘周期估算，也不能直接删掉 token。

新的 config 32 融合 dump 每次调用有 64 条 ALU：对应真实的四个后处理操作在每个输出
tile 上运行。`debug_flag=2` 下 AutoTVM 时间评估器打印了 warmup 和测量两次指令流；
`config-32-debug-run.log` 分别报告 219 和 220 条指令（第二次多一个起始队列 pop），每个
流有 64 条 ALU，NOP 分别为 20 和 21 条。第二条流中编号 `0–1` 是启动依赖，`21,34,...,203`
是重复的 memory-stage tile 间同步，`214–217` 是收尾队列汇合。与裸 Conv 的 19 条相比，
新 dump 的变化来自完整后处理产生的 compute 队列工作和配置 32 的 tile/缓冲区生命周期；
由于 fusion 身份和 schedule entity 不同，NOP 数量不能单独归因 ALU，也不能据此推断动态
等待增减。完整 stream 可在忽略日志中按 `There are 220 instructions` 定位。

### 源码定位

- `tvm/src/tir/transforms/coproc_sync.cc`: `CoProcInstDepDetector::InjectSync` 生成跨队列依赖；`VisitStmt_(ForNode)` 处理 loop-carry token；`MatchFixEnterPop` / `MatchFixExitPush` 补齐程序入口与出口。
- `vta/python/vta/transform.py`: `InjectCoProcSync` 调用 TVM `CoProcSync`；`InjectALUIntrin` 将 add、shift、min、max lowering 为 VTA ALU micro-op。
- `vta/python/vta/top/vta_conv2d.py`: EWISE consumers 在 accumulator scope 中，标注 ALU pragma 并按输出 tile `compute_at`。
- `vta/src/runtime/runtime.cc`: `DepPush` 优先复用已有指令的 dependency bit；`CommitPendingPop` 与 `PushNoop` 创建零传输 token 指令；`Synchronize` 在 FINISH 前做最终队列同步并按 debug flag dump。
