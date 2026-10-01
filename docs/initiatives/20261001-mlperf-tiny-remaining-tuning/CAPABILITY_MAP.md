# Capability map

| Module id | Responsibility | Depends on |
| --- | --- | --- |
| operator-tuning | Complete deployed fusion extraction, seed schedules, batched FSIM search, TSIM selection and replay artifacts for four models | — |
| deployment-evidence | Seed alignment gate, selected deployment, correctness and measured MAC reports | operator-tuning |

Build order: implement operator-tuning seed/export support → implement deployment-evidence gate → execute seed gates → execute full operator-tuning search → execute selected deployment-evidence.
There is no module dependency cycle: the tuning provider emits seed artifacts before search; orchestration requires validated seed evidence before enabling full search.
