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
            echo "Run standalone VTA FSIM unit tests."
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
tvm_dir="${project_dir}/tvm"
vta_dir="${project_dir}/vta"
tvm_build_dir="${tvm_dir}/build"
vta_build_dir="${vta_dir}/build"

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

export PYTHONPATH="${tvm_dir}/python:${vta_dir}/python${PYTHONPATH:+:${PYTHONPATH}}"
export TVM_LIBRARY_PATH="${tvm_build_dir}"
export VTA_LIBRARY_PATH="${vta_build_dir}"
export VTA_HW_PATH="${vta_dir}"

echo "Running standalone VTA FSIM unit tests..."
echo
echo "  TVM Python:       ${tvm_dir}/python"
echo "  TVM libraries:    ${TVM_LIBRARY_PATH}"
echo "  VTA Python:       ${vta_dir}/python"
echo "  VTA libraries:    ${VTA_LIBRARY_PATH}"
echo "  VTA hardware:     ${VTA_HW_PATH}"
echo "  Environment:      ${env_dir}"

test_paths=(
    "${vta_dir}/tests/python/unittest/test_environment.py"
    "${vta_dir}/tests/python/unittest/test_vta_insn.py"
)
if [[ "${run_integration}" == true ]]; then
    test_paths+=("${vta_dir}/tests/python/integration")
fi

"${python_bin}" -m pytest -v "${test_paths[@]}"
