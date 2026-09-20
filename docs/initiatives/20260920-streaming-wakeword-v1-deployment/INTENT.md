# Confirmed Intent: streaming_wakeword_v1 Deployment

## Outcome

Add a deployment example for `streaming_wakeword_v1`, following the existing
`vta/apps/mlperf_tiny_benchmarks` deployment pattern.

## Inputs

- Reuse the model and test data already available under `.envs`.
- Select one test sample for each category.

## Acceptance Direction

- Prefer a local HOST/FSIM execution path.
- Load the model, run one sample per category, and report classification
  results.
- Preserve compatible TSIM/hardware entry points when the existing deployment
  structure provides them, without requiring real FPGA validation.

## Out of Scope

- Retraining the model.
- Downloading or replacing the dataset.
- Unrelated refactoring.

## Confirmation

The user explicitly confirmed this intent on 2026-09-20.
