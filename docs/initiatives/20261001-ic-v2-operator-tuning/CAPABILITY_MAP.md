# Capability map: IC V2 operator tuning

| Module id | Responsibility | Depends on |
| --- | --- | --- |
| two-stage-tuning | Extract complete IC V2 VTA fusions, screen schedules on FSIM, measure candidates on TSIM, resume and export validated best records | — |
| deployment-validation | Apply exported configurations to the actual IC V2 mixed graph, verify outputs, measure each deployed occurrence, enforce strict cycle agreement and publish full-run evidence | two-stage-tuning |

Build order: two-stage-tuning → deployment-validation.
The provider's artifact and replay contract is specified in SPEC-two-stage-tuning.md.
