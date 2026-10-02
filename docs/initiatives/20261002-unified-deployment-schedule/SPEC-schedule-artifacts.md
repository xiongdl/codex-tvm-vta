# Spec: schedule-artifacts
Inherits CAPABILITY_MAP.md shared contract.

## Objective
One schedule input represents any candidate, partial snapshot, or selected best snapshot, with deterministic loading and complete provenance.

## Format and interface
run.py accepts only --schedule PATH|none for task configuration selection. Omitted and literal none are equivalent defaults.
PATH identifies a native AutoTVM .log with same-stem .json metadata loaded automatically, never by a second required CLI argument.
Each exported snapshot has at most one selected record per layer occurrence; no implicit history-best selection over competing candidates.
A candidate can be unmeasured but must contain a valid configuration and identity; it cannot claim correctness or performance validation until measured.
Metadata schema includes version, model/content identity, computational identity per occurrence, geometry hash, schedule template/config-space identity, native record hash and occurrence mapping. Measurement backend/protocol/units are required where costs exist.
Evaluation backend and measurement provenance are distinct: a config may be evaluated on either matching-geometry simulator, but FSIM time is never treated as TSIM cycles.
Validated native records are the configuration authority; metadata and record configuration must agree.

## Coverage/error behavior
Absent layer entries use defaults; report every selected/default occurrence.
Unknown/duplicate occurrences, wrong model/geometry/compute identity, invalid config, missing metadata, corrupted logs or mismatched hashes fail before execution.
Partial means absent entries, not a damaged complete snapshot.
Aggregate candidate history and resume state are internal tuning artifacts; tune.py exports deployable snapshots for any requested candidate selection.
Do not auto-select newest files or guess a JSON file from directory contents.

## Commands
```bash
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/common/tests/test_schedule_artifacts.py -q
VTA_BACKEND=tsim ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --schedule /tmp/ic-v2-candidate.log --simulator tsim
```

## Testing strategy and success criteria
Test no input/none equivalence; one-layer partial selection; fully selected snapshots; repeated-workload occurrences with different configs; malformed, swapped, duplicate and tampered artifacts; atomic export and portable paired relative references.
No best-only or complete-only gate blocks a valid candidate. Candidate execution still undergoes normal output checks; “optimal” means best observed successful candidate, not proof of global optimum.

## Compatibility and boundaries
Remove --autotvm-log/--autotvm-sidecar and generic tuning workflow, updating callers/tests/docs together.
Preserve committed old artifacts and evidence. A validated migration/export helper may convert compatible complete-fusion artifacts; unverifiable old artifacts are rejected with a precise reason and remeasurement guidance.
Follow shared structure/style/boundaries. No open user choices.
