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
`vta/` checkout. The old `--target libvta_*` interface is rejected.

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

All test scripts require the selected environment, built TVM, and their VTA
libraries. `test_vta_tsim.sh` also requires `libvta_hw` and an absolute,
existing `VTA_CONFIG_FILE`; `--smoke-only` and `--integration` cannot be
combined.

The complete BYOC gate requires FSIM, TSIM, hardware, both VTA config files,
Git, and `rg`. It runs structural BYOC tests; FSIM and TSIM gates; MLPerf Tiny
ResNet V1 and V2 plus anomaly detection V1 asset, model, graph, HOST, FSIM,
and HOST/TSIM coverage;
Python compilation; retired-reference checks; and scoped repository checks.
Compilation may create ignored Python bytecode caches.

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
| `VTA_CONFIG_FILE` | TSIM test | `<VTA_PATH>/config/tsim_sample.json`; must be absolute and exist |
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
