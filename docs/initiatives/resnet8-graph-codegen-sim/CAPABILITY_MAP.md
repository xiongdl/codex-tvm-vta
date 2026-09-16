# Capability Map: ResNet8 Graph Codegen And Simulation

## Confirmed Intent

Extend the existing MLPerf Tiny ResNet-8 deployment while preserving its model,
quantization, partitioning, Graph Executor, and numerical-equivalence contracts.
The deployment must support complete LLVM-host and C-host execution. Both host
codegen paths must run first with FSIM and then with TSIM. Generated Graph JSON,
parameters, and inspectable LLVM or C source artifacts must be persisted under
the application build directory. AOT/CRT and deployment-result analysis are
deferred.

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `graph-artifact-bundle` | Define and persist a self-contained Graph Executor artifact bundle containing the runnable library, Graph JSON, parameters, and inspectable host source for LLVM and C variants. | — |
| `vta-c-host-codegen` | Extend VTA host lowering and the repository-pinned TVM C host backend so a C host target is accepted, emits ABI-correct VTA runtime calls, preserves `coproc_uop_scope` as static micro-op initialization, and produces a runnable Graph Executor library through standard TVM export without weakening the LLVM path. | `graph-artifact-bundle` |
| `resnet8-fsim-matrix` | Build, reload, and execute the fixed ResNet-8 model through LLVM and C host variants on FSIM, requiring the existing eight VTA regions and exact reference-output equality. | `graph-artifact-bundle`, `vta-c-host-codegen` |
| `resnet8-tsim-matrix` | Build, reload, initialize, and execute the same LLVM and C Graph Executor variants on TSIM with the Verilated hardware module, preserving routing and exact reference-output equality. | `resnet8-fsim-matrix` |

## Build Order

```text
graph-artifact-bundle
  -> vta-c-host-codegen
    -> resnet8-fsim-matrix
      -> resnet8-tsim-matrix
```

## Stable Boundaries

- The committed `pretrainedResnet.tflite` bytes, quantization policy, eight VTA
  partitions, LLVM fallback semantics, and exact output-comparison rule remain
  unchanged.
- Graph Executor is the only executor in this initiative.
- LLVM and C identify host code generators, not alternative VTA hardware
  implementations; generated VTA regions continue to use the existing VTA C
  runtime ABI.
- Pinned TVM changes are restricted to the C host source backend and its focused
  tests: Graph-runtime module-context emission, external-symbol declarations,
  behavior required for standard multi-module C export, and C emission of the
  existing `coproc_uop_scope` static-initialization contract. For each supported
  capture-free micro-op scope, generated C owns a unique static handle and
  callback and invokes the attribute-selected initializer such as
  `VTAPushGEMMOp` or `VTAPushALUOp` before normal execution. Unsupported captured
  scopes fail during code generation rather than emitting a direct
  `VTAUopPush`. LLVM codegen, TVM executors, runtimes, VTA runtime ABI, and
  unrelated target backends remain unchanged.
- C-host lowering may use TVM's standard `tir.disable_vectorize` pass option to
  scalarize code that the pinned C backend explicitly does not support. Source
  rewriting, custom export or compiler wrappers, custom compiler/linker flags,
  and fallback from C to LLVM remain forbidden.
- FSIM is completed and verified before TSIM model execution is introduced.
- The C mixed FSIM path must prove this boundary with generated-source tests and
  real ResNet-8 execution. Successful C compilation or DSO reload alone is not
  sufficient: both GEMM and ALU micro-op initializers must be present, and the
  first mixed sample must execute without an uninitialized VTA recording
  kernel.
- AOT/CRT, model-deployment analysis, per-layer utilization and traffic
  reporting, tuning, accuracy measurement, and MLPerf performance or energy
  claims are outside this initiative.

## Approval Gate

The module boundaries, dependency direction, and build order require explicit
user approval before module specifications are written.
