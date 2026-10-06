# SWW Conversion
## Objective
Produce actual float32 TFLite from the supplied SWW H5, without retraining or requiring calibration samples for float conversion.
## Ownership and Contracts
`scripts/setup_sww_env.sh` owns dedicated `.envs/sww-env` Conda creation and installation from upstream streaming_wakeword/requirements.txt. Options: --env-name NAME, --help. Validate environment names; reuse a valid existing prefix without deleting it. Never mutate tvm-vta-env. Document prerequisites, outputs and side effects in scripts/README.md, including the explicit SWW Python environment exception for conversion only.
A maintained repository conversion entry point owns a reproducible minimal adaptation of upstream quantize.py for float conversion. Upstream source under ignored `.envs/tiny-v1.4` must not be irreproducibly edited: create a temporary adapted source beside its imports or stage its source tree into ignored conversion output. Preserve upstream int8 behavior; remove optimization, representative dataset, int8 I/O and calibration loading in the float branch. Execute actual upstream conversion logic with float branch and user-selected H5/output. No new generic framework. Dependency installs may need network permission; report concrete failures.
Output: `str_ww_ref_model_floag32.tflite` (retain requested spelling). Verify input/output tensor types and no quantized weight operators with a FlatBuffer inspection; record H5/source/output hashes and commands. Copy final model into the SWW app's model directory for standalone deployment, retaining license provenance.
## Commands and Tests
`bash scripts/setup_sww_env.sh --help`; `bash scripts/setup_sww_env.sh`; conversion under `.envs/sww-env/bin/python` or conda run with that prefix only. TVM inspection uses `.envs/tvm-vta-env/bin/python`.
Test invalid options/name boundaries and float conversion without calibration dependency; run pip check and imports in created environment. Shell style follows setup_tvm_vta_env.sh, set -euo pipefail, quoted paths.
## Boundaries
Never delete an existing unrelated environment, train models, or commit environment/package caches. Dependency changes are confined to conversion environment. Conversion owns external file I/O; app modules do not import TensorFlow.
Application directories contain only float32 `.tflite` model assets, never H5 or int8 model assets. H5 conversion source stays in upstream training directory. Generated conversion intermediates stay outside application tree.
