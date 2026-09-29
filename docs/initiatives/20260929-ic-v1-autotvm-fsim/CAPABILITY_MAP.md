# Capability Map: IC V1 Single-Workload Tuning and MAC Utilization

| Module id | Responsibility | Depends on |
|---|---|---|
| `ic-v1-layer-tune` | Select one extracted IC V1 AutoTVM workload, tune it with random FSIM search, and measure the selected schedule with TSIM. | — |
| `mac-utilization-cli` | Calculate useful MAC utilization from explicit MAC count, TSIM cycles, and VTA geometry, without model-specific imports. | — |

Build order: `ic-v1-layer-tune` and `mac-utilization-cli` are independent and
may be implemented in either order. The tuning output (MAC count and TSIM
cycles) can be passed to the calculator manually.
