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
backend. The standalone KWS application provides its selected-target commands and full
manual acceptance sequence in
[`keyword_spotting_v1/README.md`](../vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/README.md).

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
config, Git, and `rg`. It runs structural BYOC tests; FSIM and TSIM gates; all
five standalone MLPerf Tiny application suites and selected-target matrices;
the cleanup/migration contracts; Python compilation; retired-reference checks;
and scoped repository checks. KWS and Streaming Wakeword VTA targets use their
documented CPU fallback because their exact int8 graphs produce no real VTA
partitions. Compilation may create ignored Python bytecode caches.

### MLPerf Tiny deployment schedules and tuning

Each migrated application owns its deployment and tuning interface. The five
standalone manuals provide independently executable acceptance commands:

- [Image classification V2](../vta/apps/mlperf_tiny_benchmark/image_classification_v2/README.md)
- [Visual Wake Words V1](../vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md)
- [Keyword Spotting V1](../vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/README.md)
- [Anomaly Detection V1](../vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/README.md)
- [Streaming Wakeword V1](../vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/README.md)

Image classification V2 has the same local `Makefile` entry points and the
same variables, with its large float model and first sample as defaults. Its
workflow is documented independently in
`vta/apps/mlperf_tiny_benchmark/image_classification_v2/README.md`; it owns a
separate `python/` implementation and `scripts/make_tasks.sh`. CPU targets
`c` and `llvm` need no VTA backend or geometry. VTA targets `vta,c` and
`vta,llvm` require the matching `SIMULATOR` and absolute `CONFIG`. Workload
export rejects zero real VTA coverage, and `make clean` preserves model,
samples, licenses, and persistent tuning evidence.

Visual Wake Words V1 now uses the standalone workflow documented in
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md`. It follows the
same four-target deployment contract as Image classification V2, with a local
96×96 RGB preprocessing and model-specific workload identity. Its Makefile
sets FSIM or TSIM per stage; do not set `VTA_BACKEND` to a different simulator
than `SIMULATOR`.

Keyword Spotting V1 uses the standalone workflow documented in
`vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/README.md`. Its original
int8 QNN arithmetic is preserved exactly. The current partitioner yields no
real VTA workloads, so requested VTA targets run the CPU fallback and report
zero coverage; export, schedule replay, and tuning stop without producing a
synthetic workload or winner.

Streaming Wakeword V1 uses the standalone workflow documented in
`vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/README.md`. It preserves
the imported QNN int8 arithmetic and validates exact output equality against
the canonicalized CPU graph on all three committed WAVs. The current
partitioner finds no real VTA workloads, so `vta,c` and `vta,llvm` execute
their CPU fallbacks without loading FSIM/TSIM; export, replay, and `make tune`
stop before publishing a workload or claiming a winner. Its manual acceptance
set covers all four selected targets, these rejection paths, report output,
and safe cleanup.

The streaming app's `Makefile` delegates `deploy`, `tune-fsim`, `tune-tsim`,
`tune`, and `clean` to its local `scripts/make_tasks.sh`. It accepts `CONFIG`,
`MODEL`, `INPUT`, `TARGET`, `SIMULATOR`, `PYTHON`, `SCHEDULE`, `OUTPUT_DIR`,
`REPORT`, `EXPORT_WORKLOADS`, `WORKLOADS`, `WORKLOAD`, `TRIAL_BATCH`,
`MIN_SUCCESSFUL`, `TIMEOUT`, `FSIM_TIMEOUT`, `TSIM_TIMEOUT`, `INPUT_LOGS`, and
`OUTPUT_LOGS`, using the same meanings as Image classification V1. Defaults are
the streaming int8 model, Marvin WAV, `TARGET=vta,llvm`, and `SIMULATOR=fsim`.
CPU targets do not initialize VTA. VTA targets require an absolute `CONFIG`
and matching simulator selection; this model reports zero actual VTA layers,
so workload export, schedule replay, and full tuning stop before publication.
Deployments write compiled graph bundles under `OUTPUT_DIR` and optional
reports/workloads at their specified paths. Tuning outputs use
`streaming_wakeword_v1/tune/<config-basename>/`. `clean` removes only local
`build/` and Python caches and preserves persistent tune evidence and model
assets. The app script uses the existing environment and built libraries; it
does not install or build dependencies.

Anomaly Detection V1 uses the selected-target workflow documented in
`vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/README.md`. It preprocesses
one WAV and executes the first feature vector once. The current topology has
nine real VTA partitions; its README gives the complete workload export,
bounded FSIM/TSIM tuning, replay, report, and cleanup acceptance commands.

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
.envs/tvm-vta-env/bin/python scripts/clean_mlperf_tiny.py \
  --model all --dry-run
```

`--model` accepts one of the five migrated application IDs or `all`; `all`
selects only those five applications. `--dry-run` lists recognized generated
files and byte totals without changing files. Without it, the script removes
only recognized, untracked outputs inside each selected application's local
`build/` directory. Unknown and tracked files, model/sample/license assets,
and saved `tune/<config-name>` schedules are retained. A symlink in a selected
build tree blocks the entire cleanup operation, and traversal never follows
external symlink targets. The script requires the initialized VTA submodule
for Git's tracked-file inventory and does not run a simulator.

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

Test scripts prepend `<TVM_PATH>/python`, `<VTA_PATH>/python`, and
`<VTA_PATH>/apps` to an existing `PYTHONPATH`. The BYOC runner also adds the
benchmark directory so spawned app test workers can import their test package.
`build_tvm_lib_macos.sh` accepts no path overrides.

Use the narrowest script that proves the requested behavior. Build TVM before
VTA, and build each required library before its tests. Update this file when a
maintained script's interface, prerequisite, output, or side effect changes.
