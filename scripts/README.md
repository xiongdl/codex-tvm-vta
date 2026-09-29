# Repository Scripts

Run maintained scripts from the repository root. Use each script's `--help` as
the option contract. Scripts do not initialize submodules or download the
CIFAR-10 dataset. Test scripts do not build missing libraries.

## Required environment

The default Conda prefix is `.envs/tvm-vta-env`. Every Python command for this
repository, including one-off validation, must use one of:

```bash
.envs/tvm-vta-env/bin/python ...
conda run -p "$PWD/.envs/tvm-vta-env" ...
```

Do not use bare `python`, bare `python3`, or a system, Codex, or workspace
runtime. If the project environment is missing and the task does not authorize
creating it, stop and report the blocker.

The sole bootstrap exception is `.agents/custom/scripts/git-workflow`, which
uses host `python3` only for standard-library JSON processing before the project
environment is available; it does not import or execute project Python code.

The two required submodules must already be initialized before running
`git-workflow` or any maintained project script. If either is missing, stop and
ask the user to initialize the missing submodule. `tvm/` and `vta/` are the
default source paths. Host Git must exist before setup. Build and test commands
also require the tools and libraries listed below.

## Quick start

```bash
bash scripts/setup_tvm_vta_env.sh
conda activate "$PWD/.envs/tvm-vta-env"
bash scripts/build_tvm_lib_macos.sh
bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend all
bash scripts/test_vta_byoc.sh
```

`build_tvm_lib_macos.sh` supports only Apple Silicon macOS. On another
platform, build TVM separately into `$TVM_PATH/build`, then use the portable
VTA scripts when their prerequisites are available.

## Backend and geometry contract

`vta/config/vta_64mac.json` is the shared geometry configuration for every
simulator backend. It contains geometry only; backend selection is supplied at
the command boundary:

```bash
bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend fsim

bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend tsim
```

Runtime and test processes use the same absolute `VTA_CONFIG_FILE` and an
explicit matching `VTA_BACKEND=fsim` or `VTA_BACKEND=tsim`. MLPerf runners
currently expose `--simulator fsim|tsim` (and HOST where supported); that flag
must match `VTA_BACKEND`. HOST is a CPU reference mode, not a third VTA
backend. Use the project Python environment for runner commands:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py \
  --simulator fsim --host-codegen all
```

The old `TARGET=sim` and `TARGET=tsim` configuration selectors are not
supported. Configurations containing those simulator target fields are
rejected with a migration error; set `VTA_BACKEND=fsim` or `VTA_BACKEND=tsim`
instead. The old `--target libvta_*` build interface is also rejected; use
`--config ABS_PATH --backend fsim|tsim|all`. FPGA backends such as `pynq` and
`zcu104` are deferred and are not implemented by these scripts.

## Commands

### `setup_tvm_vta_env.sh`

```text
--env-name NAME          default: tvm-vta-env
--python-version VERSION default: 3.11
```

Creates `.envs/<name>` with Conda from `conda-forge`. If that prefix already
exists, the script removes and recreates it. Requires Conda and access to
`conda-forge`.

Conda packages: `llvmdev=17`, `llvm-openmp`, `cmake>=3.24`, `git`, `verilator`,
`openjdk=11`, `sbt=1.5.5`, the selected `python`, and `pip`.

Pip packages: `attrs`, `numpy`, `cython`, `decorator`, `ml_dtypes`, `pytest`,
`tflite==2.10.0`, `Pillow==11.3.0`, `scipy`, `tornado`, `psutil`, `xgboost`,
`cloudpickle`, and `typing_extensions`.

The script does not activate the new environment.

### `build_tvm_lib_macos.sh`

```text
--env-name NAME      default: tvm-vta-env
--build-type TYPE    default: Release
--jobs N             default: logical CPU count minus 2, minimum 1
```

Requires macOS `arm64`, initialized `tvm/`, the selected environment,
`llvm-config`, and Apple Clang through `xcrun`. It configures `tvm/build/` with
LLVM and disables CUDA, Metal, Vulkan, and OpenCL. Outputs:

- `tvm/build/libtvm.dylib`
- `tvm/build/libtvm_runtime.dylib`

### `build_vta_lib.sh`

```text
--config ABS_PATH    required absolute path to one geometry JSON
--backend BACKEND    fsim | tsim | all; default: all
--env-name NAME      Conda environment under .envs/; default: tvm-vta-env
--build-type TYPE    CMake build type; default: Release
--jobs N             parallel CMake and Verilator jobs; default: detected
--trace MODE         none | vcd | fst for hardware generation; default: none
--skip-deps          skip Chisel dependency preload
--skip-tests         skip Chisel lint and unit tests
```

Requires initialized `tvm/` and `vta/`, the selected project environment,
built TVM libraries, CMake, and an absolute existing geometry config. `fsim`
requires no Verilator; `tsim` and `all` require Verilator for the TSIM shared
library. Hardware generation additionally requires SBT, Java, Make, and C++;
when those tools are unavailable, `tsim`/`all` build `libvta_tsim` and report
hardware generation as skipped. `VTA_PATH` must resolve to this repository's
`vta/` checkout. The old `--target libvta_*` interface is rejected with a
migration message.

Outputs selected libraries under `vta/build/`: `libtvm-vta-ext` is always
built, `fsim` adds `libvta_fsim`, and `tsim` adds `libvta_tsim`; available
hardware tools also produce `libvta_hw`. `all` selects both simulator
libraries. Darwin outputs `.dylib`; other platforms output `.so`.

The script configures the existing `vta/build/` directory, regenerates ignored
CMake/ABI files, and may regenerate ignored Chisel/Verilator artifacts. It
passes the same `--config` path to CMake and hardware validation/generation;
it does not download datasets or commit generated build output.

### Test scripts

| Command | Scope | Additional options |
| --- | --- | --- |
| `bash scripts/test_vta_fsim.sh` | FSIM unit and BYOC runtime tests | `--env-name NAME`, `--integration` |
| `bash scripts/test_vta_tsim.sh` | TSIM loading, initialization, and unit tests | `--env-name NAME`, `--smoke-only`, `--integration` |
| `bash scripts/test_vta_byoc.sh` | Complete BYOC validation gate | `--env-name NAME` |

All test scripts require the selected environment, built TVM, their VTA
libraries, and an absolute, existing `VTA_CONFIG_FILE`. Set
`VTA_BACKEND=fsim` for FSIM tests and `VTA_BACKEND=tsim` for TSIM tests.
`test_vta_tsim.sh` also requires `libvta_hw`; `--smoke-only` and `--integration`
cannot be combined.

The complete BYOC gate requires FSIM, TSIM, hardware, the shared geometry
config, Git, and `rg`. It runs structural BYOC tests; FSIM and TSIM gates;
MLPerf Tiny ResNet V1 and V2 plus anomaly detection V1 asset, model, graph,
HOST, FSIM,
and HOST/TSIM coverage;
Python compilation; retired-reference checks; and scoped repository checks.
Compilation may create ignored Python bytecode caches.

### MLPerf Tiny AutoTVM schedule tuning

All six benchmark applications support independent AutoTVM tuning runs for
FSIM and TSIM: `image_classification_v1`, `image_classification_v2`,
`anomaly_detection_v1`, `keyword_spotting_v1`, `streaming_wakeword_v1`, and
`visual_wake_words_v1`. Each model/backend run searches its supported VTA
schedule configuration spaces and writes a native AutoTVM log plus a JSON
sidecar under the ignored
`vta/apps/mlperf_tiny_benchmark/build/autotvm/` directory. The sidecar records
the model identity, backend, `vta_64mac.json` path and SHA-256, log hash,
supported and unsupported task-template report, task and trial counts, and
effective tuning options. By default the grid search
exhausts each extracted task's configuration space; `--trials-per-task` bounds
the search for a smoke run.

`--model all` tunes the six models sequentially in the order listed above. It
writes an aggregate JSON summary after each model completes, so completed log
pairs survive interruption and per-model failures remain visible. Pass a prior
summary back with `--resume-summary` to validate and reuse completed model/backend
pairs, then continue failed, interrupted, or invalid entries. Resume requires
the same backend, geometry file contents, and tuning options. Each model still
uses its own native log and sidecar; a failure does not cause a later model to
reuse another model's records. Aggregate exit status is nonzero if any model
failed, and the summary records each status and each successful artifact pair.

Run each backend in a separate process, with the same geometry file and an
explicit matching backend selector:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model image_classification_v2 --backend fsim

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model image_classification_v2 --backend tsim

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model all --backend tsim --trials-per-task 1
```

To continue an aggregate run, use the printed summary path:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model all --backend tsim --trials-per-task 1 \
  --resume-summary <autotvm-all-tsim-summary.json>
```

Add `--trials-per-task 1` for a bounded smoke run. FSIM defaults to a 120 s
per-measurement timeout and TSIM to 180 s; `--timeout` overrides that value.
Replay code should use the `history_best` helper in
`vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py` with the generated log and
sidecar. It validates backend, model, geometry, log integrity, supported task
coverage, and tuning options before applying history-best. Unsupported VTA
task templates are listed in the sidecar and are not represented as tuned.
TSIM AutoTVM record costs are simulator `cycle_count` values; FSIM record costs
are its runner measurements and should not be interpreted as TSIM cycles.
Use each model's own `run.py` with the corresponding log/sidecar from the
summary to replay its outputs; see
`vta/apps/mlperf_tiny_benchmark/README.md` for the six-model replay command
matrix and result interpretation.

For one IC V1 workload, use the V1-local `tune.py` command. The required
`--workload-index` is zero-based in supported task extraction order. It uses
AutoTVM RandomTuner with a local FSIM runner, 32 trials, and a 120-second
per-measurement timeout by default, then measures the best successful FSIM
record's exact configuration on TSIM. Begin with `VTA_BACKEND=fsim`; the
command changes the process-local selector to `tsim` for the final run. Both
FSIM and TSIM libraries must be built using the same absolute geometry file.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py \
  --workload-index 0
```

`--trials N` and `--timeout SECONDS` override the defaults; trials are capped
at the selected workload's configuration-space size. `--output-dir PATH`
changes the artifact location. The default native FSIM log, best-record log,
and result JSON are written below the ignored
`vta/apps/mlperf_tiny_benchmark/build/autotvm/image_classification_v1/`
directory. Output includes the task template and workload SHA-256, logical
MAC count, TSIM `cycle_count`, and artifact paths. FSIM wall-clock cost is not
reported as cycles. See the IC V1 README for the existing model-specific
command context.

### Per-layer useful-MAC utilization estimates

`vta/apps/mlperf_tiny_benchmark/mac_utilization.py` reports one row for every
VTA Conv/Dense occurrence in the prepared graph. It validates the TSIM log and
sidecar identities against the model and `vta_64mac.json`; `--model all` also
requires the existing successful six-model TSIM aggregate summary and checks
all six pairs before creating either report. It does not tune, compile, or run
the model. The default output directory is the ignored
`vta/apps/mlperf_tiny_benchmark/build/autotvm/mac-utilization/`.

The metric is
`logical_MACs / (best_successful_isolated_TSIM_task_cycles * peak_MACs_per_cycle)`.
AutoTVM's FLOP count is divided by two to obtain logical MACs; the geometry
peak is `2**LOG_BATCH * 2**LOG_BLOCK * 2**LOG_BLOCK` MAC/cycle (64 MAC/cycle for
`vta_64mac.json`). The CSV contains occurrence rows, so repeated workload
occurrences remain distinct. The JSON records formula and units, geometry and
hash, workload identities, artifact paths and hashes, unsupported task
coverage, and row counts. These cycles come from an isolated AutoTVM workload
measurement. They are a schedule estimate associated with a layer occurrence,
not per-layer profiling inside full-model execution or FPGA utilization.

Use the matching V1 TSIM log and sidecar, then use the TSIM aggregate summary
for all six models:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/mac_utilization.py \
  --model image_classification_v1 --backend tsim \
  --log vta/apps/mlperf_tiny_benchmark/build/autotvm/<v1-tsim-log>.log \
  --sidecar vta/apps/mlperf_tiny_benchmark/build/autotvm/<v1-tsim-sidecar>.json

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/mac_utilization.py \
  --model all --backend tsim \
  --summary vta/apps/mlperf_tiny_benchmark/build/autotvm/<autotvm-all-tsim-summary>.json
```

An alternate report location can be selected with `--output-dir PATH`.
Output names use a stable stem derived from the selected model set and validated
artifact identities. Re-running with the same inputs replaces the same paired
CSV and JSON paths.

### `extract_mlperf_resnet_samples.py`

```bash
.envs/tvm-vta-env/bin/python scripts/extract_mlperf_resnet_samples.py \
  --test-batch <cifar-10-batches-py/test_batch> \
  --output-dir <output-directory>
```

Both arguments are required. The input must be the official CIFAR-10 Python
`test_batch` with SHA-256
`f53d8d457504f7cff4ea9e021afcf0e0ad8e24a91f3fc42091b8adef61157831`.
The script authenticates the bytes before unpickling, validates the 10,000
records, and writes the first sample for labels 0 through 9 as ten PNG files
plus `manifest.json`. NumPy is required even for `--help`.

### `extract_mlperf_vww_samples.py`

```bash
.envs/tvm-vta-env/bin/python scripts/extract_mlperf_vww_samples.py \
  --dataset-root <vw_coco2014_96-directory> \
  --output-dir <output-directory>
```

Both arguments are required. The input must contain `non_person/` and
`person/` directories with at least five readable 96x96 RGB JPEGs each. The
script selects the first five JPEG filenames in lexical order from each class,
copies their bytes to the output directory, and writes the VWW `manifest.json`
with class labels, source-relative paths, and SHA-256 hashes. The output must
not be the dataset directory or any path below `.envs`; the source dataset is
never modified. Invalid roots, class directories, image files, or output
locations fail before any output is created.

## Environment overrides

| Variable | Used by | Default or constraint |
| --- | --- | --- |
| `TVM_PATH` | VTA build and all tests | `<repo>/tvm`; built TVM libraries must be under `build/` |
| `VTA_PATH` | VTA build and all tests | `<repo>/vta`; the build script rejects another checkout |
| `VTA_CONFIG_FILE` | build and simulator tests | `<VTA_PATH>/config/vta_64mac.json`; must be absolute and exist |
| `VTA_BACKEND` | runtime and simulator tests | `fsim` or `tsim`; explicit backend selector |
| `CMAKE` | VTA build | `<env>/bin/cmake` |
| `SBT` | VTA hardware build | `<env>/bin/sbt` |
| `VERILATOR` | VTA build | `<env>/bin/verilator` |
| `JAVA_HOME` | VTA hardware build | `<env>/lib/jvm`; must contain `bin/java` |
| `CXX` | VTA hardware build | Apple `clang++` on macOS; `c++` elsewhere |

Test scripts prepend `<TVM_PATH>/python` and `<VTA_PATH>/python` to an existing
`PYTHONPATH`. `build_tvm_lib_macos.sh` accepts no path overrides.

Use the narrowest script that proves the requested behavior. Build TVM before
VTA, and build each required library before its tests. Update this file when a
maintained script's interface, prerequisite, output, or side effect changes.
