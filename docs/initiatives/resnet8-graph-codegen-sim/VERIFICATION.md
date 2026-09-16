# ResNet-8 Graph LLVM/C Verification Evidence

This document records the current verification of the approved Graph Executor
LLVM/C deployment on the fixed MLPerf Tiny v1.4 ResNet-8 model. It records
build, reload, execution, and structural evidence only; it does not claim
accuracy, performance, energy, MAC utilization, or traffic analysis.

## Repositories and scope

The verification ran on `codex/resnet8-graph-codegen-sim` with these recorded
implementation states:

| checkout | original branch/base | verified HEAD |
| --- | --- | --- |
| parent | `dev` / `e2e271f5f15df9a26e7e4e944af3fbe3eff27b44` | `3a490e454a40d7b0191efe7665e2c904b4ee48a8` |
| `vta/` | `vta_v0.0.2` / `e6443ae67fa28877476e5af954f652a4c2dfeccc` | `7add5bf069cde2172e0b70592a549e854c293f66` |
| `tvm/` | `tvm_v0.17.0` / `eeebcfa0ad4a6e9d49cce3ee6718ecbef0ee018f` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |

The parent contains only the expected untracked generated files under
`OUTDIR/` and `test.o`; they were not edited, staged, or removed. The VTA and
TVM worktrees had no tracked or untracked changes. Generated deployment
bundles under VTA's ignored application `build/` directory were inspected but
were not staged.

## Verification commands

All commands completed with exit status 0.

| command | result |
| --- | --- |
| `PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q tvm/tests/python/codegen/test_target_codegen_c_host.py tvm/tests/python/codegen/test_target_codegen_static_init.py` | `26 passed in 10.61s` |
| `VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" bash scripts/test_vta_fsim.sh` | `24 passed in 27.44s` |
| VTA structural pytest set from `scripts/test_vta_byoc.sh` (`test_target_extension.py`, `test_target_hooks.py`, `test_abi_fingerprint.py`, `test_byoc_contract.py`, `test_byoc_partition.py`, `test_byoc_lowering.py`, `test_byoc_codegen.py`, `test_byoc_graphpack_retirement.py`) | `308 passed in 42.47s` |
| FSIM application suite (`test_assets.py`, `test_model_pipeline.py`, `test_host_deployment.py`) under `vta_config.json` | `36 passed in 21.55s` |
| `VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" bash scripts/test_vta_tsim.sh` | `TSIM library loading and initialization passed`; `12 passed in 11.10s` |
| `test_tsim_deployment.py` under `tsim_sample.json` | `8 passed in 52.61s` |
| `bash scripts/test_vta_byoc.sh` | structural `308 passed`; FSIM `24 passed`; application `36 passed`; TSIM `12 passed`; final `VTA BYOC validation passed` |
| `./.envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta` (aggregate step) | exit 0 |
| aggregate retired-reference `rg` scan, nested `git diff --check`, and scoped repository checks | exit 0 |

## Real FSIM matrix

Command:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py \
  --simulator fsim --host-codegen all
```

The command built, exported, reloaded, and executed both host variants. Each
host had 8 routed partitions and 10 exact sample comparisons against its
reloaded reference; the application tests also require equal shape, dtype, all
elements, and top-1 result for every comparison, and exact equality between
the two pure-host reference outputs. The independent mixed FSIM snapshots were:

| host | comparisons | `inp_load_nbytes` | `wgt_load_nbytes` | `acc_load_nbytes` | `uop_load_nbytes` | `out_store_nbytes` | `gemm_counter` | `alu_counter` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LLVM | 10 | 6968640 | 120586240 | 2785280 | 1920 | 696320 | 471040 | 174080 |
| C | 10 | 6968640 | 120586240 | 2785280 | 1920 | 696320 | 471040 | 174080 |

The CLI ended with `MLPerf ResNet LLVM/C FSIM matrix passed`.

## Real TSIM matrix

Command:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py \
  --simulator tsim --host-codegen all
```

The command built and reloaded all host/reference and host/mixed bundles before
lazily initializing the standard TSIM driver and Verilated hardware module.
Each host had 8 routed partitions and 10 exact sample comparisons; the focused
TSIM tests require equal shape, dtype, all elements, and top-1 result for every
comparison and exact pure-host reference agreement. Independent positive TSIM
activity snapshots were:

| host | comparisons | `cycle_count` |
| --- | ---: | ---: |
| LLVM | 10 | 23277470 |
| C | 10 | 23277470 |

The CLI ended with `MLPerf ResNet LLVM/C TSIM matrix passed`. The standalone
TSIM command separately checked the TSIM registries and initialization, and
the focused suite checked exact zero reset, positive integer cycles, simulator
mapping, lazy initialization, and reloaded bundles.

## Bundle and generated-source inspection

The real run produced eight ignored, reloadable bundle directories:
`llvm-fsim/{reference,mixed}`, `c-fsim/{reference,mixed}`,
`llvm-tsim/{reference,mixed}`, and `c-tsim/{reference,mixed}`. Every directory
contained `graph.json`, `params.bin`, `model.dylib`, `manifest.json`, and at
least one generated source file. The manifests recorded the matching
`host_codegen` and simulator labels:

| simulator | reference source | mixed source | mixed routed symbols | reference routed symbols |
| --- | --- | --- | ---: | ---: |
| FSIM | LLVM `.ll` / C `.c` | LLVM `.ll` / C `.c` | exactly 8 (`tvmgen_mlperf_resnet_vta_main_0` through `_7`) | 0 |
| TSIM | LLVM `.ll` / C `.c` | LLVM `.ll` / C `.c` | exactly 8 (`tvmgen_mlperf_resnet_vta_main_0` through `_7`) | 0 |

The C mixed sources contained the generated `VTAPushGEMMOp` and
`VTAPushALUOp` calls, 16 module-local `static const` VTA constants, no
`coproc_uop_scope` capture, and no direct typed store through a VTA constant
handle. The LLVM mixed sources were LLVM IR. These checks demonstrate the
approved C static micro-op and portable constant contract; they do not imply
any deferred deployment-analysis metrics.

## Candidate integrity and final status

For the sole staged path, `docs/initiatives/resnet8-graph-codegen-sim/VERIFICATION.md`,
the required sorted allowlist, staged diff review, `diff --cached --check`,
unstaged-tracked check, and binary/full-index candidate fingerprint were run.
The fingerprint was frozen before verification and matched after all
verification commands. The exact before/after values are reported in the
checkpoint handoff because this document is itself part of the fingerprinted
candidate.

No push, merge, release, or generated-artifact staging was performed.
