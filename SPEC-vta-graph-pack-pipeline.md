# Spec: VTA Relay Graph-Pack Pass Pipeline

> Superseded before implementation by `CAPABILITY_MAP-vta-byoc.md`. The
> clarified objective is a complete VTA BYOC/external-codegen backend with
> pattern-based partitioning, not a compatibility refactor of `graph_pack`.

## Objective

Replace the monolithic orchestration inside `vta.top.graphpack.graph_pack`
with a composable Relay pass pipeline.  The design follows the integration
shape used by TVM's CMSIS-NN and Ethos-U extensions: callers operate on an
`IRModule`, individual transformations are represented as Relay passes, and a
single convenience entry point assembles the default sequence.

The change improves reuse and testability without changing the packed Relay
produced for existing `graph_pack(...)` callers.

## Public Contract

The new API is additive:

```python
from vta.top import graph_pack_passes, transform_for_vta

pipeline = graph_pack_passes(
    bfactor=1,
    cfactor=16,
    weight_bits=8,
    start_name="nn.max_pool2d",
    stop_name="nn.global_avg_pool2d",
)
packed_mod = pipeline(mod)

# Equivalent convenience form.
packed_mod = transform_for_vta(
    mod,
    bfactor=1,
    cfactor=16,
    weight_bits=8,
    start_name="nn.max_pool2d",
    stop_name="nn.global_avg_pool2d",
)
```

`graph_pack_passes(...) -> tvm.transform.Sequential` returns a reusable pass
pipeline. `transform_for_vta(mod, ...) -> tvm.IRModule` constructs and runs
that pipeline. Both accept the existing graph-pack options, including optional
device annotation.

The existing `graph_pack(expr, ...) -> relay.Function` remains available with
its current signature, accepted inputs, return type, defaults, and validation
behavior. It becomes a compatibility adapter over `transform_for_vta`.

No BYOC partitioning or external-codegen function extraction is introduced by
this increment. “Similar to CMSIS-NN and Ethos-U” refers to the composable
`IRModule` pass pipeline and convenience entry point, not to adopting their
`MergeComposite` / `AnnotateTarget` / `PartitionGraph` semantics.

## Pass Decomposition

The default pipeline is assembled in this order:

```text
InferType
  -> AnnotateGraphPackRegion
  -> InferType
  -> PackGraph
  -> InferType
  -> [AnnotateVTADevice]
  -> [InferType]
```

- `AnnotateGraphPackRegion`: converts the selected start/stop operator range
  into the existing `annotation.bitpack_start` and
  `annotation.bitpack_end` markers.
- `PackGraph`: rewrites operators and tensors between those markers into VTA's
  packed batch/channel layouts, including weight bit-packing.
- `AnnotateVTADevice`: optional pass preserving the current `device_annot=True`
  behavior.

Each VTA-specific item is a Relay function pass and therefore independently
composable with TVM passes. The existing expression mutators may remain private
implementation details; their orchestration must move into pass constructors.

## Tech Stack

- Python 3
- TVM Relay `function_pass`, `Sequential`, `IRModule`, and `InferType`
- Existing VTA Relay graph-packing operators and mutators
- pytest and TVM structural equality for regression tests

## Commands

Run from the workspace root with the standalone VTA and pinned TVM Python
trees available:

```bash
PYTHONPATH="$PWD/vta/python:$PWD/tvm/python" \
  python3 -m pytest vta/tests/python/unittest/test_graphpack.py -q

PYTHONPATH="$PWD/vta/python:$PWD/tvm/python" \
  python3 -m compileall -q vta/python/vta/top

git -C tvm status --short
git -C vta status --short
```

If the local TVM runtime library is not available, tests that require importing
TVM must be run in the project's configured TVM build environment; syntax
checks alone do not satisfy the runtime verification criterion.

## Project Structure

```text
vta/python/vta/top/graphpack.py
  Existing graph-pack implementation, new pass constructors, pipeline builder,
  module convenience entry point, and compatibility adapter.

vta/python/vta/top/__init__.py
  Public exports for the new additive API.

vta/tests/python/unittest/test_graphpack.py
  Focused pass composition and backward-compatibility tests.
```

Keeping the implementation in `graphpack.py` avoids an unnecessary module
split in this increment. A later change may separate passes after their public
boundaries have proved stable.

## Code Style

Use TVM's pass-constructor style and keep configuration explicit:

```python
def graph_pack_passes(bfactor, cfactor, weight_bits, **options):
    return tvm.transform.Sequential(
        [
            relay.transform.InferType(),
            AnnotateGraphPackRegion(**region_options),
            relay.transform.InferType(),
            PackGraph(bfactor, cfactor, weight_bits),
            relay.transform.InferType(),
        ]
    )
```

Public functions use snake_case; pass constructors use TVM-style CamelCase.
Docstrings state input and output types and preserve the repository's Apache
license headers. Avoid a configuration class until there are multiple distinct
call sites that benefit from one.

## Testing Strategy

1. Unit-test each VTA-specific pass independently on a small typed Relay
   function.
2. Verify the assembled pipeline returns an `IRModule` and can be embedded in
   another `tvm.transform.Sequential`.
3. For representative convolution graphs, compare the new module entry point
   and the legacy `graph_pack` adapter using `tvm.ir.structural_equal`.
4. Cover indexed start/stop selection, `count_meta`, and optional device
   annotation so existing options do not become nominal-only parameters.
5. Exercise invalid region arguments and missing start/stop markers, preserving
   existing failure behavior unless a separate API change is approved.
6. Run focused VTA tests and confirm the pinned `tvm/` source remains clean.

## Boundaries

- Always:
  - Accept and return `IRModule` at the new pipeline boundary.
  - Keep every stage independently invocable as a TVM pass.
  - Preserve legacy `graph_pack` output and API behavior.
  - Add regression tests before changing orchestration.
  - Keep the pinned `tvm/` submodule read-only.
- Ask first:
  - Rename or remove `graph_pack`.
  - Change graph-region selection from explicit start/stop names to pattern-
    based automatic partitioning.
  - Introduce BYOC external functions or codegen registration.
  - Add dependencies or modify build/CI configuration.
- Never:
  - Mix this refactor with unrelated VTA scheduling, runtime, or hardware
    changes.
  - Silently broaden the set of operators packed for existing callers.
  - Modify CMSIS-NN or Ethos-U implementation code.

## Success Criteria

- A caller can obtain and compose the VTA graph-pack `Sequential` pipeline.
- A caller can transform an `IRModule` through one documented convenience
  function.
- The three VTA-specific stages can be run and tested independently.
- Existing `graph_pack(...)` callers require no source changes and produce
  structurally equivalent Relay for covered configurations.
- Focused unit tests pass in a TVM-enabled environment, Python compilation
  succeeds, and the pinned `tvm/` checkout remains clean.
- Public exports and docstrings describe the current API.

## Open Questions

1. Should the module-level convenience function be named `transform_for_vta`
   (accurate for layout rewriting) or `partition_for_vta` (closer to the ARM
   extension naming, but potentially misleading because no BYOC partition is
   created)? This spec recommends `transform_for_vta`.
2. Is automatic capability/pattern-based region selection part of this first
   increment? This spec keeps the existing explicit start/stop contract and
   leaves automatic selection for a subsequent independently testable feature.
