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
TSIM AutoTVM record costs are native simulator `cycle_count` values from one
formal invocation. The time evaluator performs one warmup, then the TSIM runner
clears the profiler through its reserved `f_preproc` and measures once
(`number=1`, `repeat=1`, `min_repeat_ms=0`). Warmup is excluded; do not divide
costs by two. Each TSIM sidecar/options identity records protocol
`tsim_single_call` v1 (`counted_invocations=1`, `warmup_excluded=true`).
Historical TSIM artifacts missing this protocol must be remeasured before
replay, resume, or MAC utilization reporting. FSIM timing and records are
unchanged and must not be interpreted as TSIM cycles.
Use each model's own `run.py` with the corresponding log/sidecar from the
summary to replay its outputs; see
`vta/apps/mlperf_tiny_benchmark/README.md` for the six-model replay command
matrix and result interpretation.

For IC V1 two-stage tuning, use the V1-local `tune/tune.py` command. It builds
one complete task per prepared-graph fusion occurrence, including model bias,
right shift, clip, and cast. The default `--all` run searches 100 distinct
configurations per FSIM batch until each workload has at least 20 distinct
successful schedules or its valid configuration space is exhausted. It then
measures every FSIM success on TSIM and selects the minimum positive native
`cycle_count`. FSIM and TSIM use separate processes and independent 60-second
and 120-second per-candidate timeouts. Use the same absolute geometry file for
both simulator libraries. The full fusion identity differs from bare
`conv2d_packed.vta` records; do not compare cycles across those scopes.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v1" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/tune.py --all
```

The command also supports `--workload-index N`, `--trial-batch N`,
`--min-successful N`, `--fsim-timeout SECONDS`, and `--tsim-timeout SECONDS`.
`--max-workloads N` and non-default search limits are bounded runs and the
manifest labels them `BOUNDED_SMOKE_INCOMPLETE`. To continue a run, provide its
`--resume-manifest PATH`; model, geometry, workload identities, search limits,
and timeout settings must match. Every full-search invocation, including
`--workload-index N` and bounded smoke runs, requires the complete passing
one-sample seed deployment report for all prepared occurrences. The controller
checks each positive integer cycle pair against the inclusive 10% bound and
validates the report's model, geometry, protocol, complete seed manifest, and
manifest hash before starting any search. Standalone replay rejects incomplete
or partial manifests before reading any candidate artifacts. Native backend logs, candidate failures,
progress, and resume state are written under
`vta/apps/mlperf_tiny_benchmark/image_classification_v1/build/two_stage_tuning/`.
Self-contained best native records and `best-manifest.json` are exported below
`vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/optimal/<run-id>/`
by default; `--artifact-dir PATH` changes that location. Replay with
`--replay-manifest PATH` validates the model, geometry, fusion, workload,
configuration, single-call TSIM protocol, and native record hashes without
reading intermediate build files.

The previous single-workload entry point
`image_classification_v1/tune.py --workload-index N` remains available with its
`--trials`, `--timeout`, `--output-dir`, and `--replay-result` options for
compatibility. Full two-stage tuning and self-contained artifact replay use
the new `tune/tune.py` entry point.

For IC V2, use the model-local
`vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/tune.py` entry
point. It requires the existing `.envs/tvm-vta-env`, the committed V2 model,
`vta/config/vta_64mac.json`, and built FSIM and TSIM simulator libraries. Run
the controller with absolute geometry, explicit FSIM selection, and Python
paths for TVM, VTA, the benchmark helpers, and the V2 app:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/tune.py --all
```

The CLI accepts `--workload-index`, `--max-workloads`, `--trial-batch`,
`--min-successful`, `--fsim-timeout`, `--tsim-timeout`, `--resume-manifest`,
`--artifact-dir`, and `--replay-manifest`. Defaults are 100 distinct FSIM
trials per batch, 20 successful configurations per occurrence, and 60/120
seconds per FSIM/TSIM candidate. FSIM and TSIM workers run in separate
processes. Bounded invocations are labeled incomplete. Search state, native
logs, and failures are written below the ignored V2
`build/two_stage_tuning/`; self-contained selected result JSON/native records
and `best-manifest.json` are exported below V2 `tune/optimal/`. The manifest
contains model and geometry hashes, all eight occurrence/workload identities,
the TSIM single-call protocol, candidate results, and native record hashes.
Resume rejects changed model, geometry, fusion identities, selected workload
set, or search limits. Standalone replay validates artifact coverage and
integrity, then checks real fusion lowering without reading intermediate
build files. Outputs under `build/` are ignored; `tune/optimal/` artifacts are
ordinary files and are committed only when the checkpoint requires their
delivery.

The selected-config deployment validator is the separate V2-local
`image_classification_v2/tune/deployment.py` entry point. It requires a
complete-coverage exported best manifest, the project Python environment, the
matching absolute geometry, and built TSIM libraries. It applies each selected
configuration to its matching VTA symbol during lowering, then builds and
reloads baseline and selected mixed graphs. The first committed sample is used
for baseline and selected full-run cycles, debug and ordinary counter
agreement, and all eight selected VTA node measurements. Each node measurement
uses one cleared/read counter window and one counted invocation, with warmup
excluded. After all eight cycle comparisons pass, all ten committed samples
run with the selected graph for output correctness only. Its exact strict gate is
`10 * abs(deployment_cycles - autotvm_cycles) < autotvm_cycles`; missing,
invalid, or exactly-10-percent rows fail. Bundles go under the ignored V2
`build/selected_deployment/` directory.
The JSON report defaults to V2 `tune/deployment.json`; failures write a
separate `.failure.json` diagnostic and do not publish a passing report. Run
it in a fresh TSIM process using the full command in the V2 README.

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
measurement under the single-call TSIM protocol above. They are a schedule estimate associated with a layer occurrence,
not per-layer profiling inside full-model execution or FPGA utilization.

### Real deployment MAC utilization

The repository-level `scripts/mac_utilization.py --deployment-report PATH`
consumes a versioned report from an actual mixed-model deployment. It is
independent of model names, graph loaders, TVM imports and tuning logs. It
validates geometry and selected-manifest hashes, occurrence-to-config identity,
positive invocation/cycle counts and the 10% operator-cycle threshold. Repeated
workloads remain separate occurrence rows. Operator utilization uses measured
per-occurrence TSIM cycles; whole-model utilization uses the report's measured
full-model cycles and the same invocation count as its logical MAC total.
Baseline and tuned whole-model values are both reported. Host operations remain
outside the VTA MAC total.

IC V1 creates the report after a bounded or complete selected-schedule
deployment. Its `--best-manifest` must cover every deployed fusion occurrence;
the command writes the versioned artifact below the app's `tune/` directory and
keeps graphs and raw deployment builds in `build/`:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v1" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/deployment.py \
  --best-manifest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/optimal/<run-id>/best-manifest.json \
  --output vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/deployment.json

./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py \
  --deployment-report vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/deployment.json \
  --output-json vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/mac-utilization.json
```

The report command is read-only unless `--output-json PATH` is provided. It
rejects mixed deployment/scalar input. The scalar `--macs`, `--cycles`, and
`--config` interface remains available for explicit calculations; scalar
values are labeled user inputs, not verified model measurements.

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

### Shared two-stage tuning controller

`vta/apps/mlperf_tiny_benchmark/tuning_controller.py` contains the shared
state, seed-gate, replay, and worker-process contracts used by model-local
tuning adapters. It does not prepare a model or start simulator searches on its
own. Adapters provide the prepared-graph occurrence identities and native
AutoTVM measurement callbacks.

Seed schedules are exported separately with `write_seed_manifest`. Before
creating full-search state, adapters call `validate_seed_gate` with the seed
manifest, its one-sample deployment report, the expected model/geometry
identity, and the complete prepared-graph occurrence list. It returns a
`SeedGateBinding`; `create_state` requires that validated binding, so full
search cannot be initialized from free-form hashes. This checks the
manifest and report hashes, each FSIM seed record, positive AutoTVM and
deployment TSIM cycles, exact occurrence/config identities, the inclusive 10%
cycle bound, and `tsim_single_call` v1. The seed manifest and report hashes
from the binding are part of every full-search state identity.

`create_state`, `record_fsim_result`, and `next_batch_size` maintain distinct
FSIM attempts until the successful-schedule quota or valid search-space
exhaustion. `pending_tsim_configs` enumerates every FSIM success not yet tried
on TSIM. `record_tsim_result` retains failed attempts and lowering failures;
`select_best_tsim` only selects a positive-cycle candidate that lowers through
the real deployment path after every FSIM success has a TSIM attempt. State
files are written atomically and carry a content hash checked during resume.
`validate_replay_manifest` checks model/search identity, complete occurrence
coverage, the single-call protocol, and hashes of exported result/native files.

`vta/apps/mlperf_tiny_benchmark/deployment_evidence.py` validates selected
symbol/config pairs against prepared-graph occurrences, lowers each config
through the supplied real-lowering callback, checks ordinary/debug counter
agreement, maps symbols to reloaded graph nodes, and profiles one cleared
resident-node invocation. Its one-sample reference callback and exact integer
cycle gate preserve failure diagnostics through `write_failure_report`. Passing
reports use `occurrence_base: 0`; `scripts/mac_utilization.py` accepts this
zero-based form alongside its existing one-based report form. The independent
IC V2 deployment command keeps its strict threshold and ten-sample default.

The Visual Wake Words V1 complete-fusion adapter uses the same controller and
deployment contracts for its thirteen prepared VTA Conv occurrences. Its
model-local commands, including the seed-before-search gate, are documented in
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md`.
The model-local `tune/deployment.py --best-manifest PATH --output PATH`
command validates a complete VWW seed or selected manifest, builds the exact
dispatch, checks one committed image against the HOST reference and manifest
label, and writes the versioned deployment report; intermediate graph bundles
and debug data stay under the model's ignored `build/` directory.

For backend isolation, `run_isolated_worker` takes an argument-list command,
`fsim` or `tsim`, an existing geometry file, and optional Python paths. It
starts one subprocess with explicit `VTA_BACKEND`, an absolute
`VTA_CONFIG_FILE`, and the requested backend; it returns the subprocess status
without interpreting candidate failures as infrastructure failures.

### Remaining four-model complete-fusion workflow

The model-local commands support AD V1, KWS V1, Streaming Wakeword V1, and
VWW V1. Run from the repository root, selecting exactly one model directory
per run. These commands use the existing `.envs/tvm-vta-env`, built simulator
libraries, and absolute shared VTA geometry. FSIM search and TSIM deployment
or replay must use separate processes.

```bash
MODEL=anomaly_detection_v1 # or keyword_spotting_v1, streaming_wakeword_v1, visual_wake_words_v1
MODEL_DIR="vta/apps/mlperf_tiny_benchmark/$MODEL"
export MODEL MODEL_DIR
export PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/$MODEL_DIR"

# One seed schedule for every VTA occurrence.
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune/tune.py" --seed --all

# Apply the exported seed manifest to one committed sample. This report gates full search.
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
  ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune/deployment.py" \
  --best-manifest "$MODEL_DIR/tune/seed/<seed-run-id>/best-manifest.json" \
  --output "$MODEL_DIR/tune/deployment-seed.json"

# Full FSIM search (100 trials per batch, quota 20 by default).
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune/tune.py" --all \
  --alignment-report "$MODEL_DIR/tune/deployment-seed.json"

# Resume an interrupted run with its matching manifest and options.
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune/tune.py" \
  --resume-manifest "$MODEL_DIR/build/two_stage_tuning/<run-id>/manifest.json"

# Replay exported selected artifacts without intermediate build state.
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
  ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune/tune.py" \
  --replay-manifest "$MODEL_DIR/tune/optimal/<run-id>/best-manifest.json"

# Deploy the selected schedules to one sample and calculate real deployment utilization.
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
  ./.envs/tvm-vta-env/bin/python "$MODEL_DIR/tune/deployment.py" \
  --best-manifest "$MODEL_DIR/tune/optimal/<run-id>/best-manifest.json" \
  --output "$MODEL_DIR/tune/deployment-full.json"
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py \
  --deployment-report "$MODEL_DIR/tune/deployment-full.json" \
  --output-json "$MODEL_DIR/tune/mac-utilization-full.json"
```

Replace `MODEL` with one of the four exact directory names and replace each
`<run-id>` with the ID printed by that model's prior command. Seed and selected
deployment each run exactly one committed sample; do not substitute the
separate ten-sample model integration suites for these commands. Resume accepts
only the original search identity. The initiative result table and committed
per-model evidence links are in
`docs/initiatives/20261001-mlperf-tiny-remaining-tuning/RESULTS.md`.

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
