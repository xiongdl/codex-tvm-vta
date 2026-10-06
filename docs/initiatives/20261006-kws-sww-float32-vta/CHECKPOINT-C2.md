# Checkpoint 2: Float deployments and workload gate

Status: **ROOT ESCALATION — KWS model import is unsupported by the pinned TVM frontend**

The requested KWS model was copied to
`vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model/kws_ref_model_float32.tflite`.
Its SHA-256 is `e5004c6f1012246e33fa068d8488325538e0444073cd361f5a7edb40c73f12d2`
(43,392 bytes). FlatBuffer inspection confirms float32 input `input_1` with
shape `[1, 49, 10, 1]`, float32 output `Identity` with shape `[1, 12]`, and the
expected 13-operator KWS topology. The graph also contains five int8 Conv2D
weight tensors with quantization metadata, so these are dynamic-range
quantized convolutions despite the float32 model I/O.

The repository TVM environment fails at `relay.frontend.from_tflite` before
Relay import or quantization:

```text
tvm.error.OpNotImplemented: The following operators are likely to have dynamic range quantization: 'CONV_2D'. If you are running an optimized graph, please turn off dynamic range quantization or use full integer quantization
```

SWW's C1 model (`c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267`)
imports with float32 input/output, and its existing WAV feature function
returns float32 `[1, 30, 1, 40]`. C2 has not verified its TVM quantized graph,
deployment, or VTA coverage. KWS CPU and mixed deployment, both workload gates,
and output-equivalence checks therefore remain unrun. This is an importer
failure, not evidence of zero VTA regions. Do not start C3.

Root must decide how to handle KWS dynamic-range Conv2D semantics within the
approved constraints (no model-weight rewrite and no compiler changes) before
Checkpoint 2 can continue. The existing int8 app asset remains until a verified
replacement path exists.
