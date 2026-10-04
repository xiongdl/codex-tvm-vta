# Implementation plan

Initiative: `20261004-standalone-resnet8-app`.
Approved Specify: main repository `463aa703d816dee95244164445290960f49504c2`, INTENT.md and SPEC.md in this directory; explicit human approval in conversation. Evidence baselines: vta `59bdf646d49ff01a8699738ab19bfdcab3577d87`, tvm `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`.

## Implementation order

1. Localize the existing app dependencies without changing external behavior, establish one local dispatch authority and migrate app tests to local imports. This makes later slices independent without disrupting other models.
2. Ship the single-target deployment CLI, CPU import isolation and single-image model preparation, updating its tests/callers and report output together.
3. Add deploy-time workload serialization and recovery tests with real captured activations; no separate extractor CLI.
4. Replace tuning entrypoint with independent FSIM and TSIM modes, publication/identity contracts and roundtrip tests as one coherent slice.
5. Add Make targets and saved-config directory conventions, migrate ignored/legacy assets, update narrow existing integration/cleanup callers and documentation, then validate the complete application.

No architecture change: local computation/schedule contract code remains provider to both runtime and tuning; VTA compiler remains legalization/lowering owner. Workloads is authoritative for tune. Make performs process orchestration with fixed backend values. No new public service, duplicated model pipeline or new dependency.

## Checkpoints

- C1: independent existing application and shared local dispatch, retained deployment and tuning behavior GREEN.
- C2: approved deployment and optional reports/workloads, new CPU/VTA flows GREEN.
- C3: approved independent FSIM/TSIM CLI and durable schedule publication GREEN.
- C4: Make workflow, caller/docs migration and final integration GREEN.

Each checkpoint is executed by one fresh Default, sequentially; tasks within each checkpoint commit separately after verification, simplification and re-verification. Root-owned approved artifacts are immutable execution inputs. Architecture review after this batch checks plan conformance. Human approves PLAN/TASKS before implementation. Final implementation review includes complete base-to-tip maps and all verification evidence. Root never merges automatically.

## Verification approach

Use existing .envs/tvm-vta-env/bin/python and built libraries. Initial read-only inventory found libtvm/libtvm_runtime, libtvm-vta-ext, libvta_fsim, libvta_tsim and libvta_hw dylibs; availability is not proof of ABI compatibility, verify loading before integration. Do not install/build as a hidden workaround. Commands below run from repository root unless Make changes cwd explicitly.

Define command prefix in task reports (not a maintained executable): VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" .envs/tvm-vta-env/bin/python. TSIM tests run in a separate process with VTA_BACKEND=tsim. Pure CPU checks unset VTA_BACKEND and test imports without simulator load. All tests use --import-mode=importlib. Existing tests must be migrated to new contracts rather than blindly deleted; preserve asset/source integrity and candidate/graph correctness coverage. Do not allow large skips to substitute for required actual-runtime checks.

Fast tests prove boundaries, malformed input rejection, selection and publication. Actual-runtime tests prove c/llvm CPU and both VTA host codegens, activation/IR recovery, FSIM/TSIM config selection and replay. Use one-layer bounded candidates for early checks and one successful candidate per occurrence for full roundtrip. Avoid the costly default 20-success search in validation. Finish with the repository required complete BYOC script once, after integration migration; failures in delegated code are fixed, environment blockers are escalated with exact evidence. Other model coverage stays intact.

## Risks

- CPU startup currently imports vta eagerly: delay imports and compare same quantized outputs in tests without rebuilding a CPU reference in normal deployment.
- TVM serialization/version sensitivity: validate format/runtime contract before IR recovery, then requery portable config space; no pickled objects.
- Different hosts/backends and repeated workloads: use one per-occurrence dispatch authority and explicit candidate grouping; never identify a fusion by conv shape alone.
- Several output files: staged validation, lock and caught-failure rollback; hashes detect crash-interrupted publication. No crash-proof atomicity claim.
- Single-layer search can stale earlier best: publication invalidates only replaced layer winners; full changed config invalidates all.
- Markdown graph measurement can alter cycle accounting: separate uninstrumented whole graph invocation and graph-node measurements, report residual/N/A honestly.
- Existing integration runner and cleanup know old layout: migrate only IC V1 uses, retain other model contracts and saved logs. Legacy evidence kept explicitly, not treated as current schedule.

## Completion evidence

Record each task OID map and commands/results. After C4, review complete committed range against approved Specify/Plan. Required resulting behavior includes standalone app imports, CPU without backend, explicit paths, accurate reports, actual workloads handoff with model removed from tuning access, persistent files/config validation and Make orchestration from both cwd conventions. No open architectural questions.
