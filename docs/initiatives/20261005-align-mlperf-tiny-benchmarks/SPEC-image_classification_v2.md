# Specification: image_classification_v2

## Objective and model contract
Owns `vta/apps/mlperf_tiny_benchmark/image_classification_v2/`. Migrate this model to the
read-only reference deployment template for the confirmed workflow goal.
Default model: `model/pretrainedResnet_large_float.tflite`. Default input: `samples/00-airplane.png`.
Input/preparation: float32 NHWC (1,32,32,3), unchanged pixel convention; fixed global_scale=8, skip_conv_layers=[0].
Observable result: CIFAR-10 class and raw 10 output scores. Accept a custom model matching the supported
tensor/operator topology; default asset hashes remain provenance, not a blanket
custom-path rejection. Invalid shape/dtype/audio/image fails before compile.

## Tech stack
Existing pinned project Python, NumPy, tflite, TVM Relay/AutoTVM and VTA;
image apps retain Pillow, audio apps retain existing local numerical code.
No dependency installation or model/sample replacement is needed.

## Ownership, dependencies and local structure
`deploy.py` and `tune.py` own argument translation and startup validation.
`python/model.py` owns import, model contract, input preprocessing, fixed
quantization/normalization and optional real VTA partitioning. CPU preparation
must not import VTA or require geometry/backend/simulator libraries.
`python/deployment.py` owns selected compile, execution, result and Markdown
report; it compiles only the selected target, not a comparison graph.
Template-local `vta_workload.py`, `autotvm_dispatch.py`, `measurement.py`,
`schedule_io.py`, `tuning_storage.py`, `tuning.py`, and `graph_artifacts.py`
own respectively workload capture/snapshot, occurrence dispatch, isolated
candidate processes, schedule validation, transactional publication, search/
selection, and authenticated graph bundles. Adapt local copies only where
model-specific metadata/contracts require it; never import the reference app.
The CLI imports its own local package; tests use unique app package identities
so multiple applications do not collide on a package called `python`.
`Makefile` delegates orchestration to local `scripts/make_tasks.sh`.
Only TVM/VTA libraries and the pinned project environment are external runtime
dependencies. No common, benchmark registry/root code, neighboring app, dataset
archive, download, or original extraction/setup script dependency is allowed.

No registry, inheritance framework or shared runtime is introduced. Local
copies preserve independent ownership and make template exclusion enforceable.
Model changes stay in model code; tuning state stays in tuning/storage code.

## Public command contracts
- `deploy.py --model PATH --input PATH --target {c,llvm,vta,c,vta,llvm}`
  (target choices are four literal strings `c`, `llvm`, `vta,c`, `vta,llvm`),
  `--simulator fsim|tsim`, `--schedule PATH`, `--output-dir PATH`,
  `--deployment-report PATH`, `--export-workloads PATH`.
  Default target is `vta,llvm`, simulator FSIM, model/sample below, output
  local `build/`. Explicit relative paths resolve from invocation directory.
  CPU ignores simulator/schedule and rejects workload export before runtime
  startup. VTA requests require matching backend and absolute config.
- `tune.py --workloads PATH --workload -1|INDEX --simulator fsim|tsim`
  `--timeout SECONDS --output-logs PATH`, FSIM optional `--trial-batch N`
  `--min-successful N`; TSIM requires `--input-logs PATH` and rejects FSIM
  search options. Defaults: all occurrences, FSIM 100 trials/batch, 20 successes,
  60 seconds; TSIM 120 seconds. Tune never reopens model or source input.
- Make targets `deploy`, `tune-fsim`, `tune-tsim`, `tune`, `clean` and variables
  match the template, with app-specific model/input defaults. Full `tune`
  exports if WORKLOADS is absent, runs FSIM then TSIM, and does not redeploy.
- Retire old `run.py`, top-level runtime/model_pipeline/graph_artifacts modules,
  seed/alignment/resume/export ledger flags and old JSON report interface;
  update consumers in the same migration task. No compatibility wrapper.

## Real computation and zero coverage
Partition the real prepared computation only. Never attach dummy/no-effect
branches or claim probe activity is model acceleration. Unsupported operators
stay on CPU without altering model arithmetic for an offload claim. Derive
coverage from actual partitions, not hard-coded expected partition counts.
If no real partition exists, selected VTA target can execute the CPU fallback
without loading a simulator; print/report zero VTA coverage, no measured VTA
cycles/utilization, and the fallback reason. A supplied schedule or requested
workload export must fail clearly with `no real VTA workloads` before publishing
an export or claiming replay. There is no fake empty candidate log or winner.
Document this actual limitation and negative acceptance path rather than
inventing compiler support. Nonzero coverage requires real accelerator activity.

## Workloads, tuning state and reports
Export pre-schedule outlined Relay functions, constants and actual single-input
activations from default-schedule deployment, even if selected deployment has a
schedule. Snapshot binds model id/hash, compute/occurrence, input provenance,
preprocessing/quantization policy, hardware and raw configuration hash, TVM/VTA
compatibility and current config spaces. Adapt template hard-coded ResNet
metadata to this model; reject foreign-model snapshots/logs. Logs use native
AutoTVM records and same-stem JSON; FSIM candidates are not deployable winners.
TSIM selects minimum successful cycles per occurrence. Partial selection uses
validated selected configs and defaults elsewhere; report exact coverage.

Candidate worker compile/mismatch/timeout/native crash failures are isolated
and counted; initialization/configuration failures stop the stage. Quota or
space exhaustion with at least one success publishes verified candidates;
zero successes preserve prior validated files. Single-occurrence updates retain
other matching identities and invalidate only the updated occurrence winner.
Keep transactional validation/publication, writer exclusion, config.json and
config.sha256, occurrence-specific dispatch, and cleanup of failed temporary
files. Persistent results live in `tune/<config-name>/`; build intermediates are
ignored. Do not manufacture cycle measurements.

Graph bundles validate libraries, graph, params, sources and required symbols
before publication and reload. Reports contain model/input/config hashes,
selected target, CPU/VTA placement, raw outputs and model-specific result,
schedule coverage, logical MAC counts and available measurements. Count dense
MACs if present, not only convolutions. CPU/FSIM cycle data is N/A. TSIM
uses one counted invocation after warmup and individual real VTA-node cycles;
state whole-graph versus layer scope, peak MAC/cycle and utilization formula.
Zero-coverage fallback uses N/A, not measured zero cycles.

`make clean` removes only local build and Python caches, preserves model,
samples, licenses and persistent tune data; is idempotent and independent of
runtime prerequisites, does not follow directory symlinks or custom outside
OUTPUT_DIR. Match reference safe behavior.

## Commands and verification
Run from repository root using `.envs/tvm-vta-env/bin/python` only:
```
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" .envs/tvm-vta-env/bin/python -m pytest APP/tests
make -C APP deploy TARGET=llvm
make -C APP deploy TARGET=c
make -C APP deploy TARGET=vta,llvm SIMULATOR=fsim EXPORT_WORKLOADS=build/workloads.json
make -C APP tune-fsim WORKLOADS=build/workloads.json WORKLOAD=0 TRIAL_BATCH=1 MIN_SUCCESSFUL=1
make -C APP tune-tsim WORKLOADS=build/workloads.json INPUT_LOGS=tune/vta_64mac/fsim.tmp WORKLOAD=0
make -C APP deploy TARGET=vta,llvm SIMULATOR=tsim SCHEDULE=tune/vta_64mac/best.log REPORT=build/replay.md
```
Replace APP by this specification's owned application path. Use CONFIG as the
absolute shared vta_64mac geometry; each Make stage selects backend itself.
Verify both CPU codegens, both VTA host codegens and both simulators on the
committed default sample when real partitions exist. For zero real coverage,
verify successful truthful fallback plus explicit export/schedule rejection,
not fake successful tuning. Tests must exercise process isolation, metadata
validation/tamper rejection, CLI boundary errors, real activation roundtrip,
one bounded occurrence FSIM/TSIM/replay with output agreement and strict under
10% layer measurement alignment, and Make ordering/quoted paths/safe cleanup.
Functional equality to prepared CPU graph is a correctness check, not accuracy.
Do not require full configuration-space search or dataset accuracy evaluation.

## Manual Acceptance and documentation
This app README must provide a complete independently executable instruction
set: prerequisites/build commands, direct CLI and Make defaults/custom paths,
four selected targets, workload export, split stages with bounded occurrence,
full make tune, selected schedule replay, report/log/config checks, rejection
paths, and safe clean preservation. Spell out successful/expected failure
observations and actual unsupported capabilities. No reference-app manual run.

## Code style and boundaries
Use direct Python functions/dataclasses and template shell arrays; preserve
licenses. Example: `prepared = prepare_model(model_path, use_vta=use_vta)`.
Always validate I/O/metadata at boundaries and report actual measured behavior.
Never edit image_classification_v1, compiler/hardware or unrelated project
policy. No added dependency, abstract plugin framework, approximate int8 model
normalization, hidden zero-contribution probes, or skipped correctness tests.

## Success criteria
The app is self-contained and all implemented selected deployment/tuning/Make
contracts above are tested and documented with real runtime evidence. Its
model/sample assets are unchanged. Obsolete app entrypoints are removed with
callers updated. The reference app stays byte-for-byte unchanged.
