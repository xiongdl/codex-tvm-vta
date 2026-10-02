# Spec: artifact-cleanup
Inherits CAPABILITY_MAP.md shared contract.

## Objective
Offer one explicit way to inspect and remove temporary generated application files, separately from resumable tuning state and saved evidence.

## Command contract
Repository-root wrapper scripts/clean_mlperf_tiny.py:
```bash
./.envs/tvm-vta-env/bin/python scripts/clean_mlperf_tiny.py --model all --cache --dry-run
./.envs/tvm-vta-env/bin/python scripts/clean_mlperf_tiny.py --model image_classification_v2 --cache
./.envs/tvm-vta-env/bin/python scripts/clean_mlperf_tiny.py --model all --tuning-runs --dry-run
```
--model accepts the six exact ids or all. An explicit category is required; --cache and --tuning-runs may be combined.
--cache removes regenerable model compilation/debug output and scoped Python/test caches.
--tuning-runs separately removes generated search logs/checkpoints/candidate exports within owned build paths; users are told these cannot subsequently resume.
Dry run prints categorized resolved paths and byte totals without mutation. Real deletion reports removed paths and failures.

## Structure and safety
Implementation uses apps/common artifact inventory; wrapper contains no duplicate model registry.
Inventory covers shared benchmark build and all model build paths with explicit category ownership; unknown files are reported and retained, not guessed.
Reject symlink escapes; do not follow symlinked roots; ensure targets are beneath allowed generated roots.
Never delete Git-tracked files, model/sample assets, tune/seed, tune/optimal, saved evidence, .envs, TVM/VTA libraries, or unrelated applications.
Do not invoke git clean or blanket deletion of ignored files.
No cleanup runs automatically during this initiative; verify using temporary fixture trees.

## Testing strategy and success criteria
```bash
./.envs/tvm-vta-env/bin/python -m pytest scripts/tests/test_clean_mlperf_tiny.py -q
```
Verify dry-run immutability, category separation, model scoping/all, nested files, missing targets, tracked files, symlink escape rejection, saved-result preservation and accurate reporting.
Docs classify generated vs saved output and provide recovery implications.
Follow shared style/boundaries. No open user choices.
