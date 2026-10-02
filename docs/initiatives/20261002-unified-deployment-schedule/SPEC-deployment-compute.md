# Spec: deployment-compute
Inherits CAPABILITY_MAP.md shared contract.

## Objective
Obtain the computation of each actual prepared VTA deployment layer before schedule choices are fixed. Defaults and every candidate use the same model preparation, legalization, packing, constant treatment, scheduling and lowering implementation.

## Current evidence
vta/python/vta/relay/transform.py exposes real function legalization and lowering.
Existing model fused_tasks.py reconstructs Conv/bias/shift/clip/cast tasks.
Existing tune/deployment.py applies configs to real outlined functions, sometimes through duplicated callback overrides. This is a reusable starting point, not sufficient equivalence evidence.

## Provider interface
A deployment description owns ordered layer occurrences, symbols, canonical computational identity, input/output shapes/dtypes/layouts, bound constants and active geometry identity.
A layer can expose its schedule configuration space and lower/build under either default selection or one explicit configuration.
Capture actual default-path compute and schedule context; do not reverse engineer scheduled TIR/machine code.
Tuning adapters must not manually rebuild a second arithmetic graph.
Include all scheduled VTA occurrences actually routed by the six models; CPU work remains in its existing runtime path.
Repeated shapes do not erase occurrence identity or distinct constants.

## Commands
```bash
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/common/tests/test_deployment_compute.py -q
VTA_BACKEND=tsim ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/common/tests/test_deployment_compute_tsim.py -q
```

## Testing strategy and success criteria
- Default behavior and sample outputs remain unchanged for all six models.
- Default and candidate computation signatures cover actual prepared functions, including bias values, shifts, clipping, casts and packing.
- A candidate is compiled from real deployment compute, with no handwritten shadow fusion template.
- Candidate standalone invocation output matches the corresponding captured deployment-layer output for representative real activations and bound constants.
- Real model application selects the same configuration for the same layer; TE compiler caches cannot leak prior selections.
- Invalid/buffer-infeasible configs remain visible failures rather than default substitution.
- Per-layer isolated cycles and graph-resident/full-model cycles remain separately labeled; surrounding runtime conditions can differ.
- No global callback changes persist beyond their owned scope, including exceptions.

## Boundaries and risks
Follow shared code style/structure/boundaries. Actual TECompiler capture may require changes to VTA lowering; implementation must identify a stable seam and verify constant/ABI handling. A new computational identity invalidates old measurement claims unless validated; historical evidence remains historical.
No open user choices.
