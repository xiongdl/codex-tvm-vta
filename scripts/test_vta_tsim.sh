#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"

env_name="tvm-vta-env"
smoke_only=false
run_integration=false

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Run standalone VTA TSIM tests."
    echo
    echo "Options:"
    echo "  --env-name NAME       Conda environment under .envs/"
    echo "                        (default: tvm-vta-env)"
    echo "  --smoke-only          Only verify TSIM library loading and initialization"
    echo "  --integration         Also run the TSIM integration benchmarks"
    echo "  -h, --help            Show this help message"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-name)
            [[ $# -ge 2 ]] || { echo "Error: --env-name requires a value." >&2; exit 1; }
            env_name="$2"
            shift 2
            ;;
        --smoke-only)
            smoke_only=true
            shift
            ;;
        --integration)
            run_integration=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [[ "${smoke_only}" == true && "${run_integration}" == true ]]; then
    echo "Error: --smoke-only and --integration cannot be used together." >&2
    exit 1
fi

env_dir="${project_dir}/.envs/${env_name}"
python_bin="${env_dir}/bin/python"
TVM_PATH="${TVM_PATH:-${project_dir}/tvm}"
VTA_PATH="${VTA_PATH:-${project_dir}/vta}"
TVM_PATH="$(cd "${TVM_PATH}" && pwd)"
VTA_PATH="$(cd "${VTA_PATH}" && pwd)"
VTA_CONFIG_FILE="${VTA_CONFIG_FILE:-${VTA_PATH}/config/vta_64mac.json}"

[[ "${VTA_CONFIG_FILE}" = /* ]] || {
    echo "Error: VTA_CONFIG_FILE must be an absolute path." >&2
    exit 1
}

export TVM_PATH VTA_PATH VTA_CONFIG_FILE
export VTA_BACKEND="${VTA_BACKEND:-tsim}"
export PYTHONPATH="${TVM_PATH}/python:${VTA_PATH}/python${PYTHONPATH:+:${PYTHONPATH}}"

[[ -x "${python_bin}" ]] || {
    echo "Error: Python was not found in environment: ${python_bin}" >&2
    exit 1
}
[[ -f "${VTA_CONFIG_FILE}" ]] || {
    echo "Error: VTA_CONFIG_FILE does not exist: ${VTA_CONFIG_FILE}" >&2
    exit 1
}

if [[ "$(uname -s)" == "Darwin" ]]; then
    library_suffix="dylib"
else
    library_suffix="so"
fi

for library in \
    "${TVM_PATH}/build/libtvm.${library_suffix}" \
    "${VTA_PATH}/build/libvta_tsim.${library_suffix}" \
    "${VTA_PATH}/build/libvta_hw.${library_suffix}"; do
    [[ -f "${library}" ]] || {
        echo "Error: required library was not found: ${library}" >&2
        exit 1
    }
done

echo "Running standalone VTA TSIM tests..."
echo
echo "  TVM_PATH:         ${TVM_PATH}"
echo "  VTA_PATH:         ${VTA_PATH}"
echo "  VTA_CONFIG_FILE:  ${VTA_CONFIG_FILE}"
echo "  Environment:      ${env_dir}"

"${python_bin}" - <<'PY'
import json

import tvm
import vta
from vta.testing import simulator

for name in (
    "vta.tsim.init",
    "vta.tsim.profiler_clear",
    "vta.tsim.profiler_status",
    "runtime.module.loadfile_vta-tsim",
):
    if tvm.get_global_func(name, allow_missing=True) is None:
        raise RuntimeError("Missing TSIM registry function: %s" % name)

simulator.clear_stats()
json.loads(tvm.get_global_func("vta.tsim.profiler_status")())
print("TSIM library loading and initialization passed")
PY

if [[ "${smoke_only}" == true ]]; then
    exit 0
fi

test_paths=(
    "${VTA_PATH}/tests/python/unittest/test_runtime_backend.py"
    "${VTA_PATH}/tests/python/unittest/test_environment.py"
    "${VTA_PATH}/tests/python/unittest/test_vta_insn.py"
)
if [[ "${run_integration}" == true ]]; then
    test_paths+=("${VTA_PATH}/tests/python/integration")
fi

"${python_bin}" -m pytest -v "${test_paths[@]}"
