# Capability Map: VTA Modern Target Pipeline

## Confirmed Intent

Build a VTA-owned compiler extension for the repository's pinned TVM version so
VTA hardware parameters, instructions, lowering passes, schedules, and code
generation can evolve without placing VTA-specific implementation in the TVM
source tree. Replace graph-pack-driven compilation with capability-based Relay
partitioning and the modern `RelayToTIR -> TIRToRuntime` target lifecycle.

Prove the result on the MLPerf Tiny v1.4 floating-point Image Classification
model (`pretrainedResnet.tflite`). Import the model with the pinned TVM, quantize
it into forms supported by the existing VTA hardware, explicitly invoke one
capability-based VTA partition pass, and compile supported regions to VTA while
the remainder uses the host C/LLVM target.
The complete deployment runs directly on the development host with VTA FSIM;
an Arm FVP, CMSIS-NN, CRT, AOT firmware, and VTA ISA changes are out of scope.

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `vta-target-extension` | Build and load the VTA-owned `libtvm-vta-ext` compiler plugin; register the `vta` TargetKind, target options, and modern hook boundary against the pinned TVM libraries | — |
| `vta-relay-to-tir` | Provide the explicitly invoked, capability-based `partition_for_vta()` pass without GraphPack; outline VTA functions, then use the registered RelayToTIR hook to legalize their layouts and quantization and lower all VTA regions in an IRModule to scheduled VTA PrimFuncs | `vta-target-extension` |
| `vta-tir-to-runtime` | Convert VTA TIR IRModules into linkable, importable, and serializable runtime artifacts with a stable host–VTA symbol and driver ABI usable by host FSIM | `vta-relay-to-tir` |
| `mlperf-resnet-host-deployment` | Curate the Image Classification v1 app and ten fixed PNG samples; import the floating-point TFLite model; quantize it with TVM; partition to `VTA -> C/LLVM`; build and execute it on the host with FSIM; verify routing and numerical results | `vta-tir-to-runtime` |
| `vta-modern-cutover` | Migrate repository-owned VTA compiler consumers to the modern path and retire active GraphPack and classic per-function `relay.ext.vta` compilation only after the modern pipeline and benchmark deployment pass | `mlperf-resnet-host-deployment` |

## Build Order

```text
vta-target-extension
  -> vta-relay-to-tir
  -> vta-tir-to-runtime
  -> mlperf-resnet-host-deployment
  -> vta-modern-cutover
```

## Ownership Boundaries

- VTA-specific compiler, runtime integration, tests, and build logic live under
  `vta/` or repository-level VTA automation. The pinned `tvm/` source tree
  remains unmodified.
- `libtvm-vta-ext` is a compiler-side extension for the pinned TVM build. It
  may depend on and be rebuilt with `libtvm`, `libtvm_runtime`, and the existing
  VTA runtime; cross-version source or binary compatibility is not required.
- VTA owns VTA capability checks and compilation. The deployment app owns model
  import, quantization configuration, `VTA -> C/LLVM` partition orchestration,
  host build, and execution.
- The first deployment reproduces the repository's established VTA
  `relay.quantize` flow with `global_scale`; it does not require dataset-driven
  calibration. CIFAR-10 samples are validation inputs, not calibration data.
- Unsupported Relay remains on the host. No CMSIS-NN, Ethos-U, Cortex-M FVP,
  bare-metal CRT/AOT, or chip-specific deployment helper is required.
- The deployment uses the default VTA schedules. It neither runs AutoTVM nor
  consumes pre-existing tuning records.

## Benchmark And Data Boundaries

- Source benchmark tree:
  `vta/apps/mlperf_tiny_benchmark/tiny-v1.4/` (local reference, not committed).
- Source model:
  `benchmark/training/image_classification/trained_models/pretrainedResnet.tflite`.
- Deliverable app:
  `vta/apps/mlperf_tiny_benchmark/image_classification_v1/`.
- Do not train, retrain, or edit the source TFLite model. TVM-side post-training
  quantization is an explicit deployment compilation stage.
- The full CIFAR-10 dataset is supplied locally by the user and is never
  downloaded or committed by this initiative.
- Commit exactly ten deterministic PNG samples, one per CIFAR-10 class, with
  fixed source indices, labels, attribution, and license information. Tests
  must run from these PNGs without requiring the full dataset.
- Copy only the MLPerf files required by the Image Classification deployment,
  preserving license headers and provenance. Do not vendor the complete v1.4
  benchmark tree.

## Stable Contracts

- Relay compiler and target identity remain `vta`.
- VTA target configuration is the single source of truth for compiler lowering,
  generated instruction definitions, and host FSIM execution.
- Runtime device identity and the host–VTA call ABI remain explicit and stable
  across FSIM and future physical drivers.
- VTA partitioning is capability-based, model-independent, idempotent, and does
  not depend on GraphPack annotations or model-specific operator ranges.
- Applications explicitly call `partition_for_vta(mod)` once after TVM
  quantization and before standard `relay.build`. Merely listing `vta` in the
  target collection is not specified to partition an otherwise unannotated
  Relay module.
- Unsupported input must remain compilable for the C/LLVM host rather than fail
  late inside VTA lowering.
- Existing VTA hardware instructions and default parameters are used initially.
  Hardware ISA and SRAM-configuration changes require a separately approved
  scope change.

## Acceptance Evidence

- `libtvm-vta-ext` builds and loads separately, registers the expected target
  and hooks exactly once, and reports missing/incompatible libraries clearly.
- The pinned `tvm/` checkout remains clean.
- Relay tests cover quantized forms emitted by the selected TVM quantization
  flow, supported and rejected regions, multiple VTA partitions, constants,
  symbols, and host fallback.
- Runtime tests cover generated VTA symbols, serialization/linking, and host
  FSIM execution through the stable driver ABI.
- The unmodified floating-point MLPerf model is imported and quantized entirely
  through TVM-side compilation without GraphPack.
- The host deployment contains and executes at least one VTA partition and a
  valid C/LLVM fallback region.
- For all ten committed PNG samples, the `VTA + LLVM` deployment is compared
  only with a pure-LLVM build of the exact same quantized Relay module. Tensor
  outputs must satisfy the approved compiler-correctness comparison, and the
  resulting top-1 classifications must agree.
- Accuracy relative to the source floating-point TFLite model is not evaluated;
  correctness of TVM's quantization and pure-LLVM lowering is trusted as the
  deployment reference.
- The deployment and its tests require neither an FVP nor CMSIS-NN.

## Non-Goals

- Training, retraining, modification of the source TFLite model, or importing
  the separately supplied quantized TFLite model.
- Evaluating quantization accuracy against the source floating-point TFLite
  model or reproducing an official MLPerf accuracy score.
- CMSIS-NN, Ethos-U, Cortex-M FVP, FVPs-on-Mac, Docker FVP wrappers, bare-metal
  deployment, CRT firmware, or TSIM.
- VTA hardware instruction, RTL, or SRAM-parameter changes.
- Supporting the other MLPerf Tiny workloads or making an official MLPerf
  performance/energy submission.
- Collage, runtime cost search, or globally optimal heterogeneous placement.
- AutoTVM tuning, tuning-log generation or consumption, and performance targets.
- A general TVMC plugin-discovery mechanism or standard `tvmc` CLI integration
  in the first release.
- Cross-TVM-version compatibility or operator-coverage expansion beyond what is
  required for the ResNet-8 host deployment.

## Approval Gate

Approved by the user on 2026-09-09. The module boundaries, dependency
direction, and build order are now fixed for specification. Each module receives
its own reviewed spec in this directory; planning and implementation remain
separately gated.
