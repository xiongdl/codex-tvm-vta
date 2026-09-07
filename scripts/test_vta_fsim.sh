#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"

env_name="tvm-vta-env"
run_integration=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-name)
            [[ $# -ge 2 ]] || {
                echo "Error: --env-name requires a value." >&2
                exit 1
            }
            env_name="$2"
            shift 2
            ;;
        --integration)
            run_integration=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Run standalone VTA FSIM unit and BYOC runtime tests."
            echo
            echo "Options:"
            echo "  --env-name NAME       Conda environment under .envs/"
            echo "                        (default: tvm-vta-env)"
            echo "  --integration         Also run the FSIM integration benchmarks"
            echo "  -h, --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Error: unknown option: $1" >&2
            echo "Use --help to see available options." >&2
            exit 1
            ;;
    esac
done

env_dir="${project_dir}/.envs/${env_name}"
python_bin="${env_dir}/bin/python"
TVM_PATH="${TVM_PATH:-${project_dir}/tvm}"
VTA_PATH="${VTA_PATH:-${project_dir}/vta}"
tvm_build_dir="${TVM_PATH}/build"
vta_build_dir="${VTA_PATH}/build"

export TVM_PATH VTA_PATH

if [[ ! -x "${python_bin}" ]]; then
    echo "Error: Python was not found in environment: ${python_bin}" >&2
    echo "Run scripts/setup_tvm_vta_env.sh first." >&2
    exit 1
fi

if [[ ! -f "${vta_build_dir}/libvta_fsim.so" &&
      ! -f "${vta_build_dir}/libvta_fsim.dylib" ]]; then
    echo "Error: libvta_fsim was not found in ${vta_build_dir}" >&2
    echo "Run scripts/build_vta_lib.sh first." >&2
    exit 1
fi

export PYTHONPATH="${TVM_PATH}/python:${VTA_PATH}/python${PYTHONPATH:+:${PYTHONPATH}}"

echo "Running standalone VTA FSIM unit tests..."
echo
echo "  TVM source:       ${TVM_PATH}"
echo "  TVM libraries:    ${tvm_build_dir}"
echo "  VTA source:       ${VTA_PATH}"
echo "  VTA libraries:    ${vta_build_dir}"
echo "  Environment:      ${env_dir}"

test_paths=(
    "${VTA_PATH}/tests/python/unittest/test_environment.py"
    "${VTA_PATH}/tests/python/unittest/test_vta_insn.py"
    "${VTA_PATH}/tests/python/unittest/test_byoc_runtime.py"
)
if [[ "${run_integration}" == true ]]; then
    test_paths+=("${VTA_PATH}/tests/python/integration")
fi

"${python_bin}" -m pytest -v "${test_paths[@]}"
