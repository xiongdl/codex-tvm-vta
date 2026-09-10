# Verification Evidence

## Target extension foundation

The VTA-owned compiler extension was built separately from the simulator with:

```text
./scripts/build_vta_lib.sh --target libtvm-vta-ext --jobs 2
```

Result: `vta/build/libtvm-vta-ext.dylib` was produced successfully on macOS.

With `PYTHONPATH=tvm/python:vta/python` and the default VTA configuration,
`import vta` loaded the extension and `Target("vta")` reported both non-null
`RelayToTIR` and `TIRToRuntime` target attributes. Loading is idempotent within
the process and runtime-only TVM imports do not execute the compiler loader.
The target reports TVM's `kDLExtDev` device identity (12), keeping VTA
distinct from the LLVM host/fallback target.

The pinned `tvm/` checkout was not modified. The native hook is backed by the
private `vta.private.relay_to_tir` IRModule bridge. The bridge validates and
lowers every VTA function deterministically to a scheduled PrimFunc in one
transaction; it is not a `relay.ext.vta` callback and is not part of the
public Python API.

Focused verification:

```text
pytest -q vta/tests/python/unittest/test_byoc_partition.py   # 42 passed
pytest -q vta/tests/python/unittest/test_byoc_lowering.py     # 43 passed
```

The lowering suite and an explicit NHWC/HWIO smoke fixture produced
GEMM-tensorized PrimFuncs with packed tensors internal to the VTA region.
