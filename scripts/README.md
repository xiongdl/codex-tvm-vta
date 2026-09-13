# Repository scripts

This directory contains the maintained setup, build, test, and data-extraction
entry points for this repository. Run them from the repository root. Read each
script's `--help` output before using it, pass `--env-name` when the default
environment is not appropriate, and do not assume that a build or downloaded
dataset already exists.

## Repository layout and prerequisites

The repository root contains the `scripts/` directory and two Git submodules:
`tvm/` and `vta/`. The scripts use those checkout locations by default. The
VTA scripts expect the TVM and VTA submodules to be initialized, and the build
and test scripts expect the libraries they consume to have already been
produced.

The setup script uses Conda and the `conda-forge` channel. It creates a
prefix environment under `.envs/` (by default `.envs/tvm-vta-env`) and then
installs Python packages with that environment's `pip`. The scripts invoke
Bash, CMake, Make, Python, and (for the hardware path) SBT, Java, Verilator,
and a C++ compiler. The Apple Silicon TVM script additionally requires macOS,
`arm64`, Apple Clang discoverable through `xcrun`, and `llvm-config` in the
Conda environment. The VTA build and test scripts select `.dylib` on Darwin
and `.so` otherwise.

The repository-provided TVM build entry point is therefore macOS/Apple Silicon
only. On non-macOS systems, build TVM separately using a compatible TVM build
configuration, then use the remaining scripts where their required tools,
paths, and library checks are satisfied. In particular, the portable VTA
build/test scripts expect the corresponding `.so` libraries and a working
`c++`, while the hardware path still needs its Chisel/Verilator toolchain.

## Quick start

From the repository root:

```bash
git submodule update --init --recursive
bash scripts/setup_tvm_vta_env.sh
conda activate "$PWD/.envs/tvm-vta-env"
```

The setup command accepts `--env-name NAME` and `--python-version VERSION`.
It removes an existing environment at the same `.envs/<name>` path before
creating the replacement; save any environment-local work first.

On Apple Silicon macOS, build TVM before VTA:

```bash
bash scripts/build_tvm_lib_macos.sh
bash scripts/build_vta_lib.sh --target all
bash scripts/test_vta_byoc.sh
```

`build_tvm_lib_macos.sh` writes `libtvm.dylib` and
`libtvm_runtime.dylib` under `tvm/build/`. The VTA `all` target builds FSIM,
TSIM, and hardware libraries under `vta/build/`; use
`--target libtvm-vta-ext` separately when that extension library is needed.
The BYOC command is the full validation gate and requires those built TVM,
FSIM, TSIM, and hardware libraries.

On non-macOS, replace the TVM build step with a compatible build performed
outside this repository, ensure its outputs are under the path selected by
`TVM_PATH`, and then run the VTA build/test scripts that are supported by the
available platform and toolchain.

## Environment setup

[`setup_tvm_vta_env.sh`](setup_tvm_vta_env.sh) creates the Conda prefix
`.envs/<env-name>`, after removing an existing prefix with that exact name.
Its defaults are environment name `tvm-vta-env` and Python `3.11`.

The exact Conda packages installed from `conda-forge` are:

| Package | Requested version |
| --- | --- |
| `llvmdev` | `17` |
| `llvm-openmp` | default channel version |
| `cmake` | `>=3.24` |
| `git` | default channel version |
| `verilator` | default channel version |
| `openjdk` | `11` |
| `sbt` | `1.5.5` |
| `python` | the `--python-version` value (default `3.11`) |
| `pip` | default channel version |

It then runs `python -m pip install` for:

```text
attrs numpy cython decorator ml_dtypes pytest tflite==2.10.0
Pillow==11.3.0 scipy tornado psutil xgboost cloudpickle typing_extensions
```

The script does not activate the environment for the current shell. Follow
its printed `conda activate <prefix>` command, or use `conda run -p
.envs/<env-name> ...` for an individual command.

## Script reference

All scripts derive the repository root from their own location, but commands
below are shown from the repository root. Outputs and side effects are those
implemented by the scripts; the scripts do not fetch submodules or perform a
TVM build on behalf of another platform.

### Setup and builds

| Script | Key options | Prerequisites | Outputs and side effects |
| --- | --- | --- | --- |
| [`setup_tvm_vta_env.sh`](setup_tvm_vta_env.sh) | `--env-name NAME`; `--python-version VERSION` | Conda with access to `conda-forge` | Removes and recreates `.envs/<name>`, installs the exact Conda and pip dependencies listed above, and prints an activation command. |
| [`build_tvm_lib_macos.sh`](build_tvm_lib_macos.sh) | `--env-name NAME`; `--build-type TYPE`; `--jobs N` | macOS `arm64`; initialized `tvm/`; existing `.envs/<name>` with `llvm-config`; Apple Clang via `xcrun` | Creates/configures `tvm/build/`, then builds and checks `tvm/build/libtvm.dylib` and `tvm/build/libtvm_runtime.dylib`. It disables CUDA, Metal, Vulkan, and OpenCL in its CMake invocation. |
| [`build_vta_lib.sh`](build_vta_lib.sh) | `--target TARGET`; `--env-name NAME`; `--build-type TYPE`; `--jobs N`; `--trace MODE`; `--skip-deps`; `--skip-tests` | Initialized `tvm/` and `vta/`; built TVM and TVM runtime libraries; executable CMake and Verilator; hardware targets additionally need SBT, Java, Make, and C++ | Configures/builds `vta/build/`. Depending on target, checks `libtvm-vta-ext`, `libvta_fsim`, `libvta_tsim`, and/or `libvta_hw`; hardware builds may preload Chisel dependencies and run Chisel lint/unit tests. |

`build_vta_lib.sh --target` accepts `libtvm-vta-ext`, `libvta_fsim`,
`libvta_tsim`, `libvta_hw`, or `all`. The CMake target for `libvta_tsim` and
`libvta_hw` is `vta_tsim`; `libvta_hw` also runs the Chisel hardware build.
`all` builds the FSIM and TSIM CMake targets and then the hardware path. The
selected target chooses `vta/config/vta_config.json` for the TVM extension and
FSIM, and `vta/config/tsim_sample.json` for TSIM/hardware.

The `--trace` value is `none`, `vcd`, or `fst`, and is used only by the
hardware path (`libvta_hw` or `all`) to set the Chisel trace flags. `--skip-deps`
skips Chisel dependency preloading. `--skip-tests` skips Chisel `lint` and
`unittest`; it does not skip the CMake build or the hardware library build.

### Tests and validation

| Script | Key options | Prerequisites | Outputs and side effects |
| --- | --- | --- | --- |
| [`test_vta_fsim.sh`](test_vta_fsim.sh) | `--env-name NAME`; `--integration` | Environment Python; built TVM and `libvta_fsim` | Runs FSIM unit tests (`test_environment.py`, `test_vta_insn.py`, `test_byoc_runtime.py`); `--integration` adds `vta/tests/python/integration`. Prints verbose pytest results. |
| [`test_vta_tsim.sh`](test_vta_tsim.sh) | `--env-name NAME`; `--smoke-only`; `--integration` | Environment Python; built TVM, `libvta_tsim`, and `libvta_hw`; an absolute existing `VTA_CONFIG_FILE` (default `vta/config/tsim_sample.json`) | Loads TSIM registry functions and initializes the simulator. `--smoke-only` stops there; otherwise runs TSIM unit tests and optionally integration benchmarks. The smoke and integration flags cannot be combined. |
| [`test_vta_byoc.sh`](test_vta_byoc.sh) | `--env-name NAME` | Environment Python; built TVM, FSIM, TSIM, and hardware libraries; both VTA config files | Runs structural BYOC tests, the FSIM gate, MLPerf ResNet host/FSIM tests, the TSIM gate, Python compilation, retired-reference checks, and scoped repository checks. Compilation may create ignored Python bytecode caches. |

The test levels are intentionally distinct:

- **Smoke:** `test_vta_tsim.sh --smoke-only` checks library loading,
  registry functions, and simulator initialization only.
- **Unit:** `test_vta_fsim.sh` runs the FSIM unit set; non-smoke
  `test_vta_tsim.sh` runs the TSIM unit set. Add `--integration` to either
  script to include the relevant integration benchmarks.
- **Full gate:** `test_vta_byoc.sh` composes structural, FSIM, MLPerf,
  TSIM, compilation, retired-reference, and repository checks.

### MLPerf sample extraction

[`extract_mlperf_resnet_samples.py`](extract_mlperf_resnet_samples.py) takes
two required arguments:

```bash
python scripts/extract_mlperf_resnet_samples.py \
  --test-batch <path-to-cifar-10-batches-py/test_batch> \
  --output-dir <output-directory>
```

The input must be the official CIFAR-10 Python `test_batch` bytes authenticated
by SHA-256
`f53d8d457504f7cff4ea9e021afcf0e0ad8e24a91f3fc42091b8adef61157831`.
The script rejects a different hash, validates the expected 10,000-record
shape and keys, and only then unpickles the authenticated bytes. It selects
the first test-batch occurrence of each numeric label 0 through 9. The output
directory is created if needed and receives ten `NN-class.png` RGB images plus
`manifest.json` containing selection metadata and PNG/raw-RGB SHA-256 hashes.
Python with NumPy is required for extraction; `--help` can be run with any
available Python that can import the script's dependencies.

## Environment-variable overrides

The shell scripts use these overrides only where noted. Paths supplied to
scripts must exist when the script resolves them; `VTA_CONFIG_FILE` must be an
absolute path for the TSIM test script.

| Variable | Used by | Default and behavior |
| --- | --- | --- |
| `TVM_PATH` | `build_vta_lib.sh`, `test_vta_fsim.sh`, `test_vta_tsim.sh`, `test_vta_byoc.sh` | `<repo>/tvm`; build VTA requires the TVM headers and both built TVM libraries under `TVM_PATH/build`. Tests prepend its `python/` directory to `PYTHONPATH`. |
| `VTA_PATH` | `build_vta_lib.sh`, `test_vta_fsim.sh`, `test_vta_tsim.sh`, `test_vta_byoc.sh` | `<repo>/vta`; `build_vta_lib.sh` additionally requires it to resolve to this workspace's VTA checkout. Tests prepend its `python/` directory to `PYTHONPATH`. |
| `VTA_CONFIG_FILE` | `test_vta_tsim.sh` | `<VTA_PATH>/config/tsim_sample.json`; must be an absolute existing file. The BYOC gate sets its own FSIM/TSIM config per child command, and `build_vta_lib.sh` selects its CMake config from `--target`. |
| `CMAKE` | `build_vta_lib.sh` | `<env>/bin/cmake`; executable used for the VTA CMake configure/build. |
| `SBT` | `build_vta_lib.sh` | `<env>/bin/sbt`; checked and passed to the Chisel hardware Makefile only for `libvta_hw`/`all`. |
| `VERILATOR` | `build_vta_lib.sh` | `<env>/bin/verilator`; executable used for the VTA build and to discover `VERILATOR_ROOT`. |
| `JAVA_HOME` | `build_vta_lib.sh` | `<env>/lib/jvm`; must contain `bin/java` for `libvta_hw`/`all`, and its `bin/` is added to `PATH` for that path. |
| `CXX` | `build_vta_lib.sh` | macOS: Apple `clang++` found with `xcrun`; non-macOS: `c++`. Passed to the Chisel hardware Makefile only for `libvta_hw`/`all`. |

The test scripts also preserve an existing `PYTHONPATH` after their TVM/VTA
entries. `build_tvm_lib_macos.sh` has no environment-variable path overrides;
use its `--env-name`, `--build-type`, and `--jobs` options.

## Choosing a command

Use the narrowest maintained script that matches the task. Initialize the
submodules and create the environment before building, build TVM before VTA,
and build the libraries required by a test before invoking that test. Use
`--help` for the current option contract, and keep project-specific command,
dependency, and environment decisions documented here when those interfaces
change.
