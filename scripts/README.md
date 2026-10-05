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
the standalone MLPerf Tiny ResNet V1 and V2 deployment checks, including V2's
complete app suite and CPU/FSIM/TSIM host-codegen matrix; plus anomaly
detection V1 asset, model, graph, HOST, FSIM, and HOST/TSIM coverage; Python
compilation; retired-reference checks; and scoped repository checks.
Compilation may create ignored Python bytecode caches.

### MLPerf Tiny deployment schedules and tuning

Image classification V1 provides a local Makefile with `deploy`, `tune-fsim`,
`tune-tsim`, and `tune` targets. It uses the existing project Python and
prebuilt TVM/VTA libraries; it does not install dependencies or build
libraries. From the repository root:

```bash
APP=vta/apps/mlperf_tiny_benchmark/image_classification_v1
make -C "$APP" deploy TARGET=llvm
make -C "$APP" deploy TARGET=vta,c SIMULATOR=tsim \
  REPORT=build/deployment-report.md
make -C "$APP" deploy EXPORT_WORKLOADS=build/workloads.json
make -C "$APP" tune-fsim WORKLOADS=build/workloads.json WORKLOAD=0 \
  TRIAL_BATCH=1 MIN_SUCCESSFUL=1
make -C "$APP" tune-tsim WORKLOADS=build/workloads.json \
  INPUT_LOGS=tune/vta_64mac/fsim.tmp WORKLOAD=0
make -C "$APP" tune
```

The application keeps its public Python entry points at the app root: `deploy.py`
for deployment and `tune.py` for the FSIM/TSIM command line. Implementation
modules live under `python/`: `model.py` owns model import, quantization,
partitioning and image input; `deployment.py` owns compilation, execution and
reports; `vta_workload.py` owns workload capture and serialization;
`autotvm_dispatch.py` binds per-occurrence configurations; `tuning.py` owns
search, measurement orchestration and candidate-log rules; `measurement.py`
owns isolated candidate processes; `schedule_io.py` owns schedule snapshots;
`tuning_storage.py` owns atomic tuning-file publication; and
`graph_artifacts.py` owns compiled bundles.

`image_classification_v1/scripts/make_tasks.sh` is the maintained shell
orchestrator called by the app Makefile. Its positional action is `deploy`,
`tune-fsim`, `tune-tsim`, or `tune`; its inputs are the Make variables
documented below (`CONFIG`, `MODEL`, `INPUT`, `TARGET`, `SIMULATOR`, `PYTHON`,
`SCHEDULE`, `OUTPUT_DIR`, `REPORT`, `EXPORT_WORKLOADS`, `WORKLOADS`,
`WORKLOAD`, `TRIAL_BATCH`, `MIN_SUCCESSFUL`, `TIMEOUT`, `FSIM_TIMEOUT`,
`TSIM_TIMEOUT`, `INPUT_LOGS`, and `OUTPUT_LOGS`). It requires the existing
project Python, initialized TVM/VTA checkouts and prebuilt libraries; VTA
actions also require a geometry config and the selected simulator library. It
sets `PYTHONPATH`, `VTA_CONFIG_FILE`, and the matching `VTA_BACKEND` for each
child process. Deployment writes bundles and optional reports/workloads under
`OUTPUT_DIR` or the requested paths. Tuning writes schedules and metadata under
`image_classification_v1/tune/<config-basename>/`; the full `tune` action also
writes ignored intermediates under `OUTPUT_DIR`. It does not install packages or
build libraries. Invoke it with one of its four actions; normal use is through
`make -C "$APP" <target>`.

The app's `make clean` action removes only its local `build/`, Python
`__pycache__/` directories, and `.pyc`/`.pyo` files. It preserves `tune/`,
`model/`, and `samples/`; custom `OUTPUT_DIR` paths outside the application are
not removed. It needs no project runtime, TVM/VTA libraries, config, or model,
and repeated runs succeed. Cache traversal does not follow directory symlinks;
a `build/` symlink is unlinked while its external target stays intact.

The defaults are the float ResNet-8 model and first sample, `TARGET=vta,llvm`,
`SIMULATOR=fsim`, and `CONFIG=vta/config/vta_64mac.json`. Deployment also
accepts `MODEL`, `INPUT`, `SCHEDULE`, `OUTPUT_DIR`, `REPORT`, and
`EXPORT_WORKLOADS`. Split tuning requires `WORKLOADS`; TSIM also requires
`INPUT_LOGS`. `WORKLOAD=-1` selects all VTA occurrences. FSIM accepts
`TRIAL_BATCH`, `MIN_SUCCESSFUL`, and `TIMEOUT`; full `tune` accepts separate
`FSIM_TIMEOUT` and `TSIM_TIMEOUT` plus `OUTPUT_DIR` for ignored build
intermediates. The full target exports workloads when `WORKLOADS` is omitted,
then runs FSIM and TSIM in order; it stops at the best schedule and does not
deploy it automatically.

`CONFIG` selects both `VTA_CONFIG_FILE` and the saved schedule directory
`image_classification_v1/tune/<config-basename>/`. The directory contains an
exact `config.json` snapshot, `config.sha256`, grouped FSIM candidates in
`fsim.tmp` with `fsim.json`, and the TSIM-selected `best.log` with
`best.json`. These files are tracked deliverables; Make does not commit them.
The generated workloads and deployment bundles live under ignored `build/`.
Explicit relative paths are resolved from Make's working directory, including
when using `make -C`. See the app README for the direct Python CLI and report
details.

Image classification V2 has the same local `Makefile` entry points and the
same variables, with its large float model and first sample as defaults. Its
workflow is documented independently in
`vta/apps/mlperf_tiny_benchmark/image_classification_v2/README.md`; it owns a
separate `python/` implementation and `scripts/make_tasks.sh`. CPU targets
`c` and `llvm` need no VTA backend or geometry. VTA targets `vta,c` and
`vta,llvm` require the matching `SIMULATOR` and absolute `CONFIG`. Workload
export rejects zero real VTA coverage, and `make clean` preserves model,
samples, licenses, and persistent tuning evidence.

The four remaining MLPerf Tiny applications still use their existing direct
Python interfaces. Use the existing `.envs/tvm-vta-env`, initialized TVM/VTA
submodules, built libraries, and the same geometry in each process. Runner
`--simulator` must match `VTA_BACKEND`:

```bash
export VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json"
export PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps"

VTA_BACKEND=tsim ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py \
  --simulator tsim --host-codegen llvm --schedule none
```

For those applications, omitting `--schedule` or passing `none` uses the
default schedule. `--schedule PATH` loads a native AutoTVM `.log` plus the
same-stem `.json` metadata. Their metadata validates model, prepared
computation, geometry, occurrences, workload/configuration identities, and
native record hashes. Partial snapshots use defaults for uncovered occurrences.
Their deployment reports can include schedule provenance and TSIM evidence.

#### Seed and alignment gate for the other applications

Search measures real prepared deployment occurrences. First measure and export
the normal default configuration as a full seed snapshot on TSIM. Deploy it
with the one-sample performance check and all committed correctness samples to
produce the alignment report required by search:

```bash
MODEL=visual_wake_words_v1
MODEL_DIR="vta/apps/mlperf_tiny_benchmark/$MODEL"

VTA_BACKEND=tsim ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune.py" --seed --all
VTA_BACKEND=tsim ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/run.py" \
  --simulator tsim \
  --schedule "$MODEL_DIR/build/actual_compute_tuning/seed/seed.log" \
  --validate-schedule-evidence \
  --deployment-report "$MODEL_DIR/build/actual_compute_tuning/seed/deployment.json"
```

Seed log and same-stem metadata are written under
`<model>/build/actual_compute_tuning/seed/`. Seed records identify defaults;
their measured TSIM evidence uses one counted call after an excluded warmup,
`tsim_single_call_v1`, in cycles. The alignment gate requires the complete
layer set and enforces the strict per-layer deployment-to-measurement cycle
bound before search starts.

#### Search, resume, and export for the other applications

Search runs FSIM candidates and measures successful candidates on TSIM in
isolated workers. Defaults are 100 distinct candidates per batch, a quota of
20 successful candidates per occurrence, and timeouts of 60 seconds on FSIM
and 120 seconds on TSIM. Search stops at the quota or when the valid schedule
space is exhausted. `--workload-index N` selects an occurrence;
`--max-workloads N` bounds the selected occurrence count. Search state,
measurement records, failures, and `resume-manifest.json` are stored under
`<model>/build/actual_compute_tuning/<run-id>/`. Bounded searches are reported
as incomplete. Search requires the passing seed alignment report:

```bash
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune.py" \
  --all --alignment-report "$MODEL_DIR/build/actual_compute_tuning/seed/deployment.json"
```

Resume with the saved manifest and the same seed/report, model, geometry,
compute, occurrence selection, timeouts, and search options:

```bash
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune.py" \
  --all --alignment-report "$MODEL_DIR/build/actual_compute_tuning/seed/deployment.json" \
  --resume-manifest "$MODEL_DIR/build/actual_compute_tuning/<run-id>/resume-manifest.json"
```

A successful search writes `best.log` and same-stem metadata. Explicit exports
require `--resume-manifest` and `--output-log PATH`; choose `--export-candidate CANDIDATE` with `--workload-index OCCURRENCE` for one ledger candidate, or `--export-best` for
best successful TSIM candidates. Either export is a regular schedule snapshot
for `deploy.py --schedule PATH`; candidate exports can cover just one occurrence.
Metadata preserves provenance and measured/unmeasured status.

Compatible historical complete-fusion manifests can be migrated through
`common.schedule.migrate_legacy_full_fusion` against the actual prepared
computation. It checks model, geometry, occurrence and compute identity,
configuration validity, native record integrity, and the historical TSIM
single-call protocol. It rejects incomplete/incompatible artifacts and creates
no measurements. This is a migration helper, not a second deployment flow.

#### Clean generated files

The maintained `clean_mlperf_tiny.py` script classifies generated build output
before removal. Start with a dry run:

```bash
.envs/tvm-vta-env/bin/python scripts/clean_mlperf_tiny.py \
  --model all --cache --tuning-runs --dry-run
```

`--model` accepts one model ID or `all`. At least one category is required:
`--cache` for recognized compiler/debug outputs and `--tuning-runs` for search
ledgers, logs, and checkpoints. Remove `--dry-run` to delete only recognized,
untracked files. Unknown files, tracked files, saved schedules, models,
samples, and evidence are retained. Saved `tune/<config-name>`
schedules remain outside the cleaner's build roots and are preserved even when
untracked. The cleaner recognizes the ResNet V1 `build/tune/workloads.json`
snapshot and `build/tune/deploy` bundle as generated intermediates. Removing
tuning runs discards those workloads and the other applications' resume state.
The cleaner does not run a simulator.

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

### `mac_utilization.py`

```bash
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py \
  --macs 123456 --cycles 7890
```

Use either deployment-report mode or the compatible scalar mode. Scalar mode
requires positive integer `--macs` (logical multiply-accumulates) and `--cycles`
(TSIM cycles). `--config PATH` selects a VTA geometry JSON; by default it reads
`vta/config/vta_64mac.json`. The JSON must be an object with
non-negative integer `LOG_BATCH` and `LOG_BLOCK` fields. Peak throughput is
`2**LOG_BATCH * 2**LOG_BLOCK * 2**LOG_BLOCK` MAC/cycle (64 MAC/cycle for the
shared configuration), and utilization is
`MACs / (TSIM cycles * peak MACs/cycle)`. Output reports the supplied MAC and
cycle counts, peak MACs/cycle, utilization ratio, and percentage. Invalid
numbers, unreadable or malformed JSON, and missing or invalid geometry fields
return a nonzero error before printing a result. Deployment mode validates a
versioned real-measurement artifact and reports operator occurrences,
baseline/tuned whole-model cycles, actual whole-model utilization, cycle gain,
and the operator sum/residual. `--output-json PATH` atomically writes the same
result in JSON for either mode. The calculator uses only the Python standard
library, has no model or TVM dependency, and never runs a simulator.

### `clean_mlperf_tiny.py`

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps" \
  ./.envs/tvm-vta-env/bin/python scripts/clean_mlperf_tiny.py \
  --model all --cache --dry-run
```

`--model` is required and accepts one of the six MLPerf Tiny model directory
IDs or `all`. At least one category is required: `--cache` selects known
compiler/debug outputs and `--tuning-runs` selects generated search ledgers,
logs, and checkpoints; both categories may be selected together. `--dry-run`
prints categorized absolute file paths and byte totals without changing files.
Without it, the script removes only recognized, untracked files under the
shared and model `build/` directories. Unknown files are reported and retained;
tracked files, samples, models, and saved `tune/<config-name>` schedules are
preserved even when untracked. Symlinked build roots
or entries stop cleanup for safety. Removing `--tuning-runs` output discards
ResNet V1's exported workloads and older applications' resume state. Empty
parent directories are left in place. The script uses the project Python
environment and initialized VTA submodule; it does not run a simulator.

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
