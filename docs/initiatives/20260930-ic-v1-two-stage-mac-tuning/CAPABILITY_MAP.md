# Capability map

| Module id | Responsibility | Depends on |
|---|---|---|
| two-stage-tuning | Deployment-equivalent tasks, adaptive FSIM search, TSIM candidate measurement, best-result artifacts, local RPC lifecycle | — |
| deployment-validation | Apply selected configurations to the real model, correctness and operator cycle comparison, model measurement export | two-stage-tuning |
| deployment-mac-report | Model-independent deployment artifact validation, operator and whole-model MAC statistics | deployment-validation |

Build order: two-stage-tuning → deployment-validation → deployment-mac-report.
Specifications are generated together under the Root lifecycle; this map and all module specs are reviewed at the single Spec approval gate.
