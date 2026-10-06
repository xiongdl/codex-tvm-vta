# Confirmed Intent
User explicitly confirmed on 2026-10-06.
Use `.envs/tiny-v1.4/benchmark/training/keyword_spotting/trained_models/kws_ref_model_float32.tflite` for KWS; no KWS conversion environment.
Create `scripts/setup_sww_env.sh`, using setup_tvm_vta_env.sh as a reference, and a dedicated Conda environment satisfying `.envs/tiny-v1.4/benchmark/training/streaming_wakeword/requirements.txt`. This environment exists only to convert `trained_models/str_ww_ref_model.h5` through quantize.py to float32 TFLite (corrected filename `str_ww_ref_model_float32.tflite`).
Deploy both models and determine real VTA workloads. If either has none, stop and report evidence to the user. Only if both have real workloads, complete standalone deployment and tuning using image_classification_v1 as the template.
No retraining or artificial activity probes.
## Manual Acceptance
User runs documented deployment/Make commands and inspects output, actual VTA coverage and, on the positive branch, tuning results.
## Additional confirmed constraint
User explicitly requires application tree to store only float32 TFLite models, no float32 H5. Both deploy.py and tune.py must take float32 TFLite as model input. H5 remains solely in upstream training source.

## Confirmed source correction
User authorized re-exporting KWS to an all-float32 TFLite using the existing SWW environment, then corrected the source: no KWS H5 exists; read trained_models/README and use TensorFlow SavedModel at `.envs/tiny-v1.4/benchmark/training/keyword_spotting/trained_models/kws_ref_model/`. The previously specified `_float32.tflite` has dynamic-range int8 convolution weights and is not the final deployment model. Do not retrain or create another environment. User corrected SWW filename to `str_ww_ref_model_float32.tflite`. Both app trees only store float32 TFLite assets; deploy/tune inputs remain float32 TFLite.
