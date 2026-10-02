# Confirmed intent
Initiative: 20261002-unified-deployment-schedule
Branch: codex/20261002-unified-deployment-schedule
Human confirmation: 2026-10-02, “确认”, following the unified interface and partial-coverage proposal.

- Outcome: Remove generic isolated-operator tuning; tune the actual deployed VTA layer computation for all six MLPerf Tiny applications.
- User: Developers running, tuning, and comparing these models.
- Why: Separate tuning/deployment implementations and artifact interfaces make schedule selection confusing and allow measurement/deployment divergence.
- Success: Each model has one deployment implementation and one run.py schedule interface accepting no input/none, any candidate snapshot, or a selected best snapshot.
- Constraint: Partial snapshots apply supplied layer configurations and use defaults for absent layers, with explicit coverage reporting. Invalid records and identity mismatches fail.
- Organization: Model-independent application code belongs under vta/apps; model code remains local; generated temporary files have a scoped cleanup interface.
- Preservation: Retain model assets, committed reproducibility evidence, correctness checks, simulator isolation, and existing measurement/validation standards.
- Out of scope: FPGA deployment, official MLPerf submission, model/quantization changes, guaranteed speedups, and destructive deletion of saved results.

No implementation is authorized until the repository's Specify and Plan/Tasks gates complete.
