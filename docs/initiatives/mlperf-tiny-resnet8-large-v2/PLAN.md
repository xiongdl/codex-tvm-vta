# Implementation Plan: MLPerf Tiny ResNet8 Large V2 Deployment

Status: Proposed

## Approved Source Of Truth

- `SPEC.md`

This plan implements one capability: a functionally V1-equivalent, isolated
ResNet8 Large deployment plus aggregate-gate integration. It does not require a
capability map because the assets, pipeline, runtime, CLI, and gate are ordered
slices of one independently shippable deployment.

## Architecture Decisions

1. **Isolated fixed-purpose V2 application.** Copy V1's tracked content shape
   into `image_classification_v2` and make only Large-specific substitutions.
   V1 is not refactored or changed, keeping its verified deployment stable.
2. **Original upstream model name and bytes.** Commit
   `pretrainedResnet_large_float.tflite` unchanged and authenticate its exact
   size, SHA-256, tensor names, operator order, and `40/80/160` channels.
3. **Model-specific routing is explicit.** Preserve V1 quantization but accept
   only the observed four single-convolution VTA regions and five HOST
   convolutions. Do not pad channels or weaken the routing test to force V1's
   eight-region count.
4. **Distinct runtime identity.** Use module name `mlperf_resnet_large` and
   artifact identity `resnet8_large`, while preserving the V1 CLI and bundle
   schema.
5. **Same sample semantics.** Duplicate the ten authenticated PNGs, manifest,
   and license byte-for-byte so V2 remains independently runnable after the
   local source checkout is absent.
6. **Test-first behavioral copies.** Adapt each V1 test group first, observe a
   V2-specific failure, then add the smallest matching implementation copy.
   Static byte copies are authenticated immediately after creation.
7. **Nested repository commits remain ordered.** Complete and commit VTA
   application changes first. The parent gate/documentation commit then records
   the reviewed VTA gitlink.

## Dependency Graph

```text
authenticated Large model + provenance
               |
               +--> authenticated CIFAR-10 sample bundle
               |
               v
exact TFLite import + quantization + 4-region routing
               |
               v
Graph artifact bundle copy
               |
               v
HOST/FSIM deployment --> CLI/TSIM deployment
               |                 |
               +--------+--------+
                        v
             parent aggregate gate
                        |
                        v
               full verification
```

## Implementation Phases

### Phase 0: Approved lifecycle baseline

Create matching `codex/mlperf-tiny-resnet8-large-v2` branches from parent
`dev@ecac767b47bcf9a57435d848a350b3626108726c` and VTA
`vta_v0.0.2@7add5bf069cde2172e0b70592a549e854c293f66`. Commit exactly this
specification, plan, and task list in the parent before Build dispatch.

#### Gate 0

- The user approves the exact lifecycle commit.
- Both task branches remain attached to the recorded clean baselines.
- The approved lifecycle path allowlist and commit OID are passed to every
  Default and Reviewer.

### Phase 1: Assets and deterministic model pipeline

Authenticate and copy the Large model, license, and two halves of the ten PNG
sample set. Add the manifest and complete asset tests. Then adapt pipeline tests
to the exact Large tensor/topology contract and observed 4-VTA/5-HOST routing,
confirm their initial V2 failure, and implement the V2 pipeline.

#### Checkpoint A

- Exact model, license, and sample bytes are committed in VTA.
- Asset tests prove provenance and reject model drift.
- The Large model imports and quantizes once.
- Partitioning produces four exact `mlperf_resnet_large` symbols, one
  convolution each, with five HOST convolutions.
- Focused asset/pipeline tests pass and receive an independent Review Pass.

### Phase 2: Artifact and simulator deployment parity

Copy the already-verified Graph bundle implementation under V2 and adapt its
tests for the `resnet8_large` identity. Add HOST/FSIM runtime tests before the
runtime copy, then add TSIM/CLI tests before the CLI and documentation. Preserve
disk-only reload, exact output comparison, independent simulator windows, and
lazy TSIM initialization.

#### Checkpoint B

- V2 Graph bundles preserve schema, atomicity, hashes, sources, and symbols.
- LLVM/C FSIM artifacts reload and execute all ten samples exactly.
- LLVM/C TSIM artifacts reload and execute all ten samples exactly.
- Each mixed run provides independent positive simulator evidence.
- V2 README commands and reported four-region behavior are accurate.
- Focused and real V2 matrices pass and receive an independent Review Pass.

### Phase 3: Parent gate integration and complete verification

Extend the maintained aggregate gate without changing its CLI. Run V1's
existing gates and V2's asset, pipeline, HOST/FSIM, and fresh-process real TSIM
matrix in deterministic order. Update `scripts/README.md`, run the complete
gate, verify candidate fingerprints, commit the parent script changes plus the
reviewed VTA gitlink, and request a final independent review.

#### Checkpoint C

- `scripts/test_vta_byoc.sh` covers both applications and exits zero.
- `scripts/README.md` documents that coverage and prerequisites.
- V1 checks remain green and its source tree is unchanged.
- VTA and parent verified commits contain only approved paths.
- The final change receives an independent Review Pass.

## Verification Strategy

- Use `.envs/tvm-vta-env/bin/python` for every Python invocation.
- Use focused pytest commands during RED/GREEN cycles.
- Run real FSIM and TSIM matrices after their runtime slices.
- Run `bash scripts/test_vta_byoc.sh` once after the final staged candidate is
  frozen; do not repeat it without an intervening change.
- At each commit, compare the exact staged-path allowlist, run `diff --check`,
  require no unstaged tracked changes, and verify the candidate fingerprint is
  stable across tests.
- Never stage ignored build output, `.envs/`, caches, or traces.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Large channels route differently from V1 | Incorrect eight-region assumptions or build failure | Pin the observed 4-VTA/5-HOST contract in tests and docs before runtime work |
| 1.93 MB model increases build/runtime cost | Longer FSIM/TSIM gate or resource pressure | Reuse one prepared model per matrix and existing artifact pipeline; measure actual gate completion |
| Duplicated module names collide in Python tests | Tests may import the wrong application | Load modules by V2-local paths and use unique `mlperf_resnet_large` symbols |
| Binary/sample copy drift | Non-reproducible or misattributed assets | Authenticate exact SHA-256/manifest bytes immediately and in permanent tests |
| Full TSIM matrix is environment-sensitive | Late integration failure | Keep TSIM initialization lazy, run focused fake tests first, then a fresh-process real matrix before parent integration |
| Aggregate gate silently drops V1 coverage | Regression escapes | Append explicit V2 stages; do not replace or weaken any V1 stage |

## Rollback

The feature is additive. Reverting the parent gate/gitlink commit and the VTA
V2 commits removes the deployment without changing V1, TVM, or shared VTA
compiler/runtime behavior. Generated application output is ignored and may be
discarded separately by the user if desired.

## Open Questions

None.
