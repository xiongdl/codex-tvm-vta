# Intent: VTA AutoTVM Schedule Tuning for MLPerf Tiny

## Confirmed intent

- **Outcome:** Use AutoTVM to search for and select fast VTA schedules that lower MLPerf Tiny inference cycles.
- **User:** The repository maintainer running VTA simulations and comparing MLPerf Tiny model performance.
- **Why now:** The repository has FSIM/TSIM MLPerf Tiny deployment flows, but does not yet connect them to AutoTVM schedule search and replay.
- **Success:** First complete AutoTVM tuning independently on FSIM and TSIM for `image_classification_v1`; the tuned TSIM schedule has a lower `cycle_count` than the untuned baseline under the same `vta_64mac.json` configuration, while existing output-equivalence checks pass. Then extend tuning to every MLPerf Tiny model in this repository.
- **Constraints:** Use `vta/config/vta_64mac.json`. Keep separate AutoTVM logs for FSIM and TSIM, each paired with a JSON sidecar associating the log with its model, backend, hardware configuration, and tuning parameters. No fixed minimum speedup percentage is required.
- **Out of scope:** Do not change model weights or quantization policy. Do not present simulated cycles as FPGA-measured latency or as an official MLPerf result.

## Confirmed workflow

1. Tune `image_classification_v1` separately with FSIM and TSIM.
2. Preserve each backend's tuning log and its corresponding JSON sidecar.
3. Apply the selected schedule and compare tuned versus untuned TSIM cycle counts and output equivalence.
4. Extend the same workflow to all MLPerf Tiny benchmark models present in the repository.
