# Specification: repository integration and shared-code retirement

## Objective and ownership
After all five apps own their implementation, remove tracked code under
vta/apps/common (including obsolete shared tests), and benchmark root
model_registry.py, tuning_controller.py, deployment_evidence.py and obsolete
root tests. Keep benchmark README/pytest configuration when needed, all six
application directories, licenses, model/sample assets and saved tune evidence.
Never modify image_classification_v1, TVM, compiler/hardware or policy.

## Dependencies and surface
Integration owns scripts/test_vta_byoc.sh, scripts/clean_mlperf_tiny.py,
scripts/tests/test_clean_mlperf_tiny.py, scripts/README.md, benchmark README,
needed pytest configuration/.gitignore and repository tests for this migration.
Update maintained runners and docs to deploy.py/new selected-target interface
in the same app migration task; do not leave broken references at checkpoint.
A complete live consumer search beyond these paths is required before deletion.
All removal/update scope must be attributable to retiring these interfaces.

The central clean_mlperf_tiny.py entrypoint remains maintained: replace its
common.artifacts import by script-owned cleanup of selected migrated apps'
local build/cache outputs, preserving tracked files, saved tune directories,
models/samples/licenses and unknown files. Retire old ledger category options
whose feature was removed; document the new CLI and update callers/tests.
Keep image_classification_v1 untouched; do not use its code at runtime or
change its cleanup behavior. Support `--model` migrated model id or `all`,
`--dry-run`; all means the five migrated apps. Safety includes no external
symlink traversal, no deletion of tracked files, deterministic inventory and
path containment. Ownership is maintenance cleanup, not deployment logic.

Do not simply relocate common into a renamed shared application library.
Small script-local functions are sufficient for the remaining maintenance task.
Repository test runner invokes app-owned tests/new entrypoints; remove tests
of retired seed/resume/shared helper contracts and replace with meaningful
local workload/selected deployment/tuning/cleanup coverage. Preserve core VTA
BYOC tests. Root tests enforce no app common/neighbor/root imports, no obsolete
callers, and unchanged reference contents by Git diff.

## Commands, verification and success
Use the existing project environment and scripts documented in scripts/README.
Run `bash scripts/test_vta_byoc.sh` with documented options for applicable
coverage after updating its entrypoints; targeted per-app tests and real bounded
workflow evidence remain required. Run pinned pytest on scripts/tests for
cleanup plus migration assertions. Read-only `git -C vta diff BASE --
apps/mlperf_tiny_benchmark/image_classification_v1` must be empty.
Check all five imports/startup without apps/ on PYTHONPATH and with CPU env
VTA_BACKEND/VTA_CONFIG_FILE removed. Search active scripts/runtime callers of
removed paths; history under docs/initiatives is provenance, not an active caller.

## Documentation and manual acceptance
Update benchmark index and scripts/README for new commands, environment,
inputs/outputs/options/side effects of maintained scripts. Link each of the
five app-owned complete manual acceptance sets, covering actual implemented
features. Document streaming zero-VTA limitation explicitly; never label its
unsupported tune path as a successful winner. No manual acceptance or edits
for image_classification_v1. Final handoff provides exact reviewed OIDs,
automated evidence and five separate command sets/links. User accepts and
merges manually.

## Style, testing and boundaries
Prefer clear local cleanup functions and explicit shell arguments; no new
framework. Test dry-run/non-dry-run, tracked/unknown/persistent asset safety,
symlinks and model selection. Always verify replacement consumers before
shared deletion. Never delete an unknown/ownership-uncertain file, assets,
reference app content or checks needed for retained functionality.
