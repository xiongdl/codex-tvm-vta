# Capability Map
| Module | Contract | Dependencies | Order |
| --- | --- | --- | --- |
| Conversion | SPEC-conversion.md | local upstream SWW training source | 1 |
| Model deployment and workload gate | SPEC-models.md | converted SWW model; existing KWS float model; TVM/VTA | 2 |
| Conditional tuning | SPEC-tuning.md | positive gate for both models | 3 |
Applications own their implementations independently; no cross-app runtime imports.
