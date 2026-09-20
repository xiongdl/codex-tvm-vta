# Confirmed Intent: Keyword Spotting v1 Deployment

## Outcome

Add a `keyword_spotting_v1` deployment application under
`vta/apps/mlperf_tiny_benchmark`, following the existing MLPerf Tiny deployment
examples.

## Inputs

- Use the KWS model already available under `.envs/tiny-v1.4`.
- Use speech samples already available under `.envs/speech_commands_v0.02`.
- Select one deterministic test sample for each of the model's 12 output
  classes: `yes`, `no`, `up`, `down`, `left`, `right`, `on`, `off`, `stop`,
  `go`, `unknown`, and `silence`.
- Record the selected samples and labels in a committed manifest so the test
  set is reproducible. The ten target-word classes use one deterministic WAV;
  `unknown` uses one deterministic non-target word; `silence` uses one fixed
  one-second segment derived from background noise.

## Verification

The deployment must expose the same practical flow as the reference examples:

- build and execute a HOST reference and a VTA-partitioned deployment;
- run the deployment on VTA FSIM;
- run the deployment on VTA TSIM;
- verify output comparisons and positive simulator activity;
- provide focused tests for assets, model/pipeline contracts, graph artifacts,
  and deployment behavior.

## Scope boundaries

In scope: model import/quantization, deterministic sample packaging, VTA graph
partitioning/code generation, HOST/FSIM/TSIM execution, focused tests, and
usage documentation.

Out of scope: model retraining, changing the upstream model, benchmark
accuracy claims, performance/energy measurements, and MLPerf submission
packaging.
