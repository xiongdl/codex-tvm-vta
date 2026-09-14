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
| `vta-c-host-codegen` | Extend the VTA `TIRToRuntime` path and mixed-module export so a C host target is accepted, emits valid VTA runtime calls, and produces a runnable Graph Executor library without weakening the LLVM path. | `graph-artifact-bundle` |
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
- FSIM is completed and verified before TSIM model execution is introduced.
- AOT/CRT, model-deployment analysis, per-layer utilization and traffic
  reporting, tuning, accuracy measurement, and MLPerf performance or energy
  claims are outside this initiative.

## Approval Gate

The module boundaries, dependency direction, and build order require explicit
user approval before module specifications are written.
