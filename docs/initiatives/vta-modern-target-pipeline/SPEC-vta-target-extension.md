# Spec: VTA Target Extension

Module id: `vta-target-extension`

Status: Approved by the user on 2026-09-09

## Objective

Provide a separately built compiler-side shared library named
`libtvm-vta-ext` for the repository's pinned TVM checkout. Loading the Python
`vta` package in a full TVM environment automatically loads this library and
registers a native `vta` TargetKind with the modern `RelayToTIR` and
`TIRToRuntime` hook boundary.

The extension keeps VTA-specific compiler registration outside the TVM source
tree and makes the complete target spelling simply `Target("vta")`. It is the
stable entry boundary for the later `vta-relay-to-tir` and
`vta-tir-to-runtime` modules; this module does not define their lowering or
code-generation algorithms.

## Public Contract

### Python import

In a full TVM installation, this is the only initialization required:

```python
import tvm
import vta

target = tvm.target.Target("vta")
```

`import vta` must:

1. Locate the platform-specific `libtvm-vta-ext` built in this workspace.
2. Load it with symbols visible to its TVM dependencies.
3. Verify that `Target("vta")` exists and exposes both modern target hooks.
4. Perform these actions at most once per Python process.
5. Raise an actionable import error if location, dynamic linking, or
   registration validation fails.

There is no required public `load_compiler_extension()` call and no exported
VTA-specific C initialization ABI.

When `tvm._ffi.base._RUNTIME_ONLY` is true, `import vta` must skip the compiler
extension entirely and preserve the existing runtime/RPC import behavior.

### Target

The complete accelerator target is:

```python
tvm.target.Target("vta")
```

VTA hardware ABI properties such as tensor blocking, integer widths, and SRAM
sizes are not repeated as target-string options. They are bound when
`libtvm-vta-ext` and the selected VTA runtime/FSIM library are built from the
same `VTA_CONFIG_FILE`.

Only one VTA hardware configuration may be active in a process. Changing the
hardware configuration requires rebuilding the compiler extension and VTA
runtime library. Cross-checking their configuration identity at runtime belongs
to the `vta-tir-to-runtime` contract.

The TargetKind uses VTA's external-device identity and registers:

- TVM's standard TargetKind options inherited from the pinned TVM API;
- the `RelayToTIR` attribute supplied by `vta-relay-to-tir`;
- the `TIRToRuntime` attribute supplied by `vta-tir-to-runtime`.

No VTA hardware option is accepted merely to duplicate `VTA_CONFIG_FILE`.

### Native library

- CMake target: `tvm_vta_ext`.
- Output basename: `libtvm-vta-ext` with the host platform suffix.
- Build location: `vta/build/` alongside standalone VTA libraries.
- Compile language level: C++17, matching the existing standalone VTA build.
- TVM compatibility: only the repository's pinned TVM source and built
  libraries; no source or binary compatibility promise across TVM versions.
- Registration is performed through the pinned TVM's native static
  TargetKind-registration mechanism when the library is loaded.

## Tech Stack

- Repository-pinned Apache TVM C++ and Python APIs.
- CMake 3.18 or newer, consistent with `vta/CMakeLists.txt`.
- C++17.
- Python 3.11 environment managed by existing repository automation.
- `ctypes` and existing VTA library-location conventions for dynamic loading;
  no new Python package dependency.

## Commands

Implementation must extend the existing automation rather than introduce a
parallel build workflow. The intended user-facing commands are:

```bash
./scripts/build_vta_lib.sh --target libtvm-vta-ext
```

and the focused validation command defined by the implementation plan, using
the existing `.envs/tvm-vta-env/bin/python -m pytest` convention. The complete
initiative gate remains `scripts/test_vta_byoc.sh` after that script is updated
through later modules.

The build command must use the same `TVM_PATH`, `VTA_PATH`, `VTA_CONFIG_FILE`,
environment selection, build type, and parallel-job conventions already
implemented by `scripts/build_vta_lib.sh`.

## Project Structure

```text
vta/CMakeLists.txt
    Builds the compiler extension separately from FSIM and TSIM runtimes.

vta/src/compiler/
    VTA-owned native compiler extension and TargetKind registration.

vta/python/vta/__init__.py
    Triggers compiler-extension loading only in full TVM mode.

vta/python/vta/libinfo.py
    Locates the compiler extension using VTA's library-location conventions.

vta/tests/python/unittest/
    Import, registration, target-contract, and failure-path tests.

scripts/build_vta_lib.sh
    Existing standalone VTA build entry extended with the compiler target.
```

Exact source filenames under `vta/src/compiler/` are a planning decision; the
directory boundary is part of this spec.

## Code Style

Native registration follows the pinned TVM idiom and keeps target identity in
one translation unit:

```cpp
TVM_REGISTER_TARGET_KIND("vta", kDLExtDev)
    .set_attr<relay::transform::FTVMRelayToTIR>(
        tvm::attr::kRelayToTIR, VtaRelayToTIR())
    .set_attr<FTVMTIRToRuntime>("TIRToRuntime", VtaTIRToRuntime);
```

The exact hook function names may change during planning, but registration must
use typed TVM interfaces, live outside `tvm/`, and avoid stringly typed global
callbacks such as `relay.ext.vta`.

Python loading code must be private, deterministic, and free of broad exception
suppression. Public imports retain the repository's existing Apache license
headers and formatting conventions.

## Testing Strategy

### Python contract tests

Run import behavior in isolated subprocesses so TVM global registration state
cannot leak between cases:

- Full TVM mode automatically loads the expected platform library.
- `Target("vta")` fails before the extension is loaded in a controlled probe,
  then succeeds after ordinary `import vta`.
- The target exposes non-null, correctly typed `RelayToTIR` and `TIRToRuntime`
  attributes.
- Re-import and `importlib.reload(vta)` do not duplicate registration or change
  registered hook identity.
- A missing library reports its searched names/locations and the required build
  command.
- A library with unresolved TVM symbols reports the underlying loader error
  without silently continuing.
- Runtime-only mode proves the compiler library is neither searched nor loaded.

### Native/build tests

- CMake produces exactly one platform-appropriate `libtvm-vta-ext` artifact.
- The artifact resolves against the pinned TVM libraries without copying VTA
  compiler objects into `libtvm` or modifying the TVM checkout.
- macOS and Linux library naming and runtime search paths follow the existing
  standalone VTA conventions.

### Regression checks

- Existing FSIM imports and runtime-only/RPC imports continue to work.
- `git -C tvm status --short` remains empty.
- Python compile checks and `git diff --check` pass.

## Boundaries

### Always

- Fail immediately in full TVM mode if the compiler extension cannot be loaded
  or its target contract is incomplete.
- Skip compiler loading in TVM runtime-only mode.
- Derive the extension from the same VTA configuration source used by the VTA
  runtime libraries.
- Keep VTA compiler sources and tests outside the pinned `tvm/` tree.
- Preserve deterministic, idempotent import behavior.

### Ask first

- Add any public explicit-loading API or exported VTA-specific C ABI.
- Add VTA hardware parameters to the target string.
- Permit more than one VTA hardware configuration in a process.
- Add a third-party dependency or change the established build-script CLI in an
  incompatible way.

### Never

- Modify the pinned TVM source to register VTA.
- Restore `relay.ext.vta` as the modern compiler entry point.
- Silently fall back to an unregistered or legacy VTA compiler when extension
  loading fails.
- Load compiler-only code in runtime-only deployments.
- Promise compatibility with a different TVM checkout or binary ABI.

## Success Criteria

1. The existing standalone VTA build workflow can explicitly build
   `libtvm-vta-ext` for macOS and Linux naming conventions.
2. In a full TVM process, ordinary `import vta` makes `Target("vta")` available
   with both modern hooks and no further initialization call.
3. Repeated Python imports are safe and preserve a single registration.
4. Missing or incompatible compiler libraries fail at import with actionable
   diagnostics.
5. Runtime-only VTA imports do not depend on or attempt to load the compiler
   extension.
6. Hardware configuration is build-bound, and `Target("vta")` requires no VTA
   hardware options.
7. Focused tests pass without modifying the pinned `tvm/` checkout or regressing
   existing FSIM/runtime-only behavior.

## Dependencies And Deferred Work

- This module depends only on the pinned TVM build and existing VTA build
  configuration machinery.
- The implementations and detailed behavior of the registered `RelayToTIR` and
  `TIRToRuntime` hooks are specified by their respective downstream modules.
- Automatic Relay partitioning, MLPerf model import/quantization, host FSIM
  deployment, GraphPack retirement, AutoTVM, FVP, and CMSIS-NN are outside this
  module.

## Open Questions

None.

## Approval Gate

The user must approve this spec before technical planning begins for
`vta-target-extension`. Approval does not authorize implementation.
