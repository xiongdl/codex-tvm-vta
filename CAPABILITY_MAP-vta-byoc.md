# Capability Map: VTA BYOC Compiler Extension

## Goal

Replace VTA's model-specific `graph_pack.py` entry flow with a complete Relay
BYOC compiler extension. A caller invokes `partition_for_vta`, supported Relay
regions are selected by capability-aware dataflow patterns, TVM outlines them
as `Compiler="vta"` functions, and the VTA external compiler lowers and builds
those functions through the existing VTA TE/TIR and runtime stack. Unsupported
Relay remains on the host target.

The pinned `tvm/` checkout is an upstream dependency and remains unmodified.
All VTA-specific registration, lowering, tests, and integration live in the
standalone `vta/` project.

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `vta-byoc-contract` | Define the external compiler name, target/options contract, supported tensor/layout constraints, module boundaries, and end-to-end test fixture | — |
| `vta-pattern-partition` | Register capability-checked Relay patterns and implement `partition_for_vta` using the standard BYOC partition Pass sequence | `vta-byoc-contract` |
| `vta-relay-lowering` | Legalize each supported composite, replace graph-pack marker/range logic with local packed-layout transformations, and lower outlined VTA Relay functions into VTA-compatible TIR | `vta-pattern-partition` |
| `vta-external-codegen` | Register the `relay.ext.vta` compilation hooks and turn lowered VTA partitions into runtime modules/artifacts that Relay build can import | `vta-relay-lowering` |
| `vta-runtime-integration` | Connect external-codegen artifacts to existing VTA device/runtime execution, including constants, workspace, symbol, serialization, and host/VTA boundary behavior | `vta-external-codegen` |
| `vta-graphpack-retirement` | Migrate repository-owned apps/tutorials/tests to `partition_for_vta`, then remove the public start/stop selection API and obsolete graphpack-only machinery | `vta-runtime-integration` |
| `vta-byoc-validation` | Prove partition correctness, host fallback, compiled artifact creation, serialization/loading, and FSIM/TSIM execution for representative supported graphs | `vta-graphpack-retirement` |

## Build Order

```text
vta-byoc-contract
  -> vta-pattern-partition
  -> vta-relay-lowering
  -> vta-external-codegen
  -> vta-runtime-integration
  -> vta-graphpack-retirement
  -> vta-byoc-validation
```

## Boundary Contracts

```text
Relay IRModule
  -> partition_for_vta
  -> mixed host module + Compiler="vta" Relay functions
  -> relay.ext.vta
  -> VTA-lowered TIR/runtime artifacts
  -> Relay build output containing host and VTA runtime modules
```

- `vta-byoc-contract` owns the stable compiler name (`vta`), PassContext
  options, target requirements, and supported-subgraph rules.
- `vta-pattern-partition` only decides what is eligible and outlines regions;
  it does not generate runtime artifacts.
- `vta-relay-lowering` owns Relay-to-packed-Relay/TIR conversion and must not
  depend on model-specific operator indices or graph-wide start/stop markers.
- `vta-external-codegen` owns TVM registry hooks and artifact production; it
  consumes only outlined functions satisfying the contract.
- `vta-runtime-integration` owns execution ABI and lifecycle, not graph
  matching or Relay legality.

## Initial Supported Capability Slice

The first end-to-end slice should be intentionally narrow but real:

1. Quantized `nn.conv2d` with constant weights and VTA-compatible dtypes,
   layouts, channel factors, and attributes.
2. Optional bias/add and requantization/cast/clip operations already supported
   by the existing VTA TOPI path.
3. Host fallback before and after the VTA region.
4. FSIM execution as the mandatory runtime proof; TSIM follows after the ABI
   and artifact lifecycle are stable.

Additional convolution variants, pooling, elementwise operations, dense, and
multi-region graphs expand the pattern table in later vertical slices. Pattern
checks must reject unsupported shapes/attributes rather than allowing failures
during lowering.

## Migration Policy

This is a compulsory repository migration because the requested architecture
removes the explicit start/stop mechanism:

1. Build and verify the BYOC replacement first.
2. Migrate all repository-owned `graph_pack` consumers.
3. Verify no repository references to start/stop graph packing remain.
4. Remove `graph_pack`, `get_subgraph`, marker-specific orchestration, and their
   public export in a separate reviewable task.

External downstream users cannot be measured from this repository. The final
spec must explicitly state whether removal is immediate or goes through one
deprecated compatibility release; repository-owned consumers will not retain
the old API.

## Non-Goals

- Modifying the pinned TVM source tree to embed VTA-specific code.
- Reimplementing the VTA hardware runtime or instruction set.
- Automatically accepting every operator currently found between historical
  graph-pack start/stop points.
- Preserving graph-pack operator-index semantics.
- Mixing MetaSchedule/AutoTVM redesign into the initial BYOC backend.

## Primary Evidence

- `tvm/docs/dev/how_to/relay_bring_your_own_codegen.rst`: upstream BYOC
  compiler/runtime contract.
- `tvm/python/tvm/relay/op/contrib/cmsisnn.py`: pattern table and standard
  partition Pass assembly.
- `tvm/python/tvm/relay/op/contrib/ethosu.py`: capability checks and Ethos-U
  partition flow.
- `tvm/src/relay/backend/te_compiler.cc`: lookup and invocation of
  `relay.ext.<compiler>`.
- `tvm/python/tvm/relay/backend/contrib/uma/` and
  `tvm/src/relay/backend/contrib/uma/`: Relay-to-TIR external backend hooks
  suitable for reusing an accelerator's existing TIR lowering path.

## Approval Gate

After this map is approved, write and review one spec per module in dependency
order. No implementation begins until the relevant module spec, plan, and task
list have been approved.
