# Specification: Application organization

## Objective and success
Implement the confirmed cleanup without changing computation, tuning selection, output formats, simulator protocols, defaults, or persistent tuning data. Root contains deploy.py/tune.py; python/ is a package with relative internal imports; scripts/make_tasks.sh owns shell orchestration. Old in-repository references are migrated, without legacy shim modules or run.py.

## Structure and ownership
- python/model.py: existing model_pipeline.py import/quantization/partition/input responsibilities.
- python/deployment.py: runtime.py plus existing deployment.py lowering and cycle comparison. Fix asset roots to the application parent.
- python/vta_workload.py: deployment_compute.py plus workloads.py capture and serialization. Resolve duplicate/private names carefully, retain existing serialized formats and validations; remove merged self-imports.
- python/autotvm_dispatch.py: dispatch.py occurrence bindings.
- python/tuning.py: tuning.py search/log contracts plus tune.py orchestration. Root tune.py owns argument parsing, argument validation and main boundary; internal tuning owns FSIM/TSIM workflow. Preserve lazy imports and CPU-only startup behavior. Remove merged self-imports.
- python/measurement.py: existing isolated measurement.
- python/schedule_io.py: schedule.py schedule snapshots.
- python/tuning_storage.py: publication.py persistent file transactions.
- python/graph_artifacts.py: existing compiled graph bundles.
- python/__init__.py: package marker without eager imports.

Dependencies: CLI -> internal owners; deployment -> model/workload/schedule/artifacts; tuning -> workload/measurement/schedule/storage; measurement -> dispatch/workload and lazy deployment simulator facilities as currently necessary; workload capture and serialization stay one owner. No internal imports from root CLI. No new abstraction or compatibility layer. External model/image and graph I/O stays with current owners; tuning file mutation stays with storage. Preserve errors, locks, rollback, multiprocessing importability, lazy VTA initialization and schedule identity. Internal symbol names can remain where clear; consolidate duplicate equivalent routines only with caller and behavior evidence. Tests migrate to package imports and patch the actual owning module.

## Make contracts
Retain all existing targets, variables, defaults, prerequisite/error behavior. Move shell script with corrected application/repository roots. Add phony clean that requires no compiled libraries, model imports or VTA backend. It deletes only application-local build/ and __pycache__/pyc caches under application source/tests, including root caches. It must not follow directory symlinks to delete external contents or delete tune/model/samples. Custom output locations remain outside its scope; document this. Repeated clean succeeds.

## Code style
Use existing Python style and explicit package imports, e.g. `from .model import prepare_model`. No sys.path compatibility hacks in production entries. No eager package imports. No algorithm rewrites.

## Commands and testing
Use repository .envs/tvm-vta-env/bin/python with PYTHONPATH=$PWD/tvm/python:$PWD/vta/python, VTA_CONFIG_FILE=$PWD/vta/config/vta_64mac.json, and VTA_BACKEND=fsim for relevant tests. Focused command, from the repository root: `.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests`. Run CLI --help, shell syntax, make workflow regression tests, clean negative/preservation/idempotence tests, and existing application suite. Exercise real LLVM deployment and small FSIM/TSIM/two-stage smoke using available prebuilt libraries and exported workloads; report unavailable runtime prerequisites honestly. Do not download assets, install dependencies, or rebuild libraries. Update all affected references found in repository searches, including scripts/test_vta_byoc.sh and scripts/README.md. Document new structure, module responsibilities, CLI migration, and clean side effects.

## Boundaries
Always preserve tracked tuning records and meaningful existing tests; update callers atomically. Never alter policy files, unrelated applications, generated committed output, algorithms or tuning strategy. No open requirements questions.
