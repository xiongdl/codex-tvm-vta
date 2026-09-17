#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"

env_name="tvm-vta-env"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Run the complete VTA BYOC validation gate."
    echo
    echo "The gate requires an existing Python environment plus built FSIM, TSIM,"
    echo "hardware, and TVM libraries. It runs structural tests, FSIM, TSIM, Python"
    echo "compilation, retired-graphpack checks, and scoped repository checks."
    echo
    echo "Options:"
    echo "  --env-name NAME       Environment under .envs/ (default: tvm-vta-env)"
    echo "  -h, --help            Show this help message"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-name)
            [[ $# -ge 2 ]] || { echo "Error: --env-name requires a value." >&2; exit 1; }
            env_name="$2"
            shift 2
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

env_dir="${project_dir}/.envs/${env_name}"
python_bin="${env_dir}/bin/python"
TVM_PATH="${TVM_PATH:-${project_dir}/tvm}"
VTA_PATH="${VTA_PATH:-${project_dir}/vta}"
TVM_PATH="$(cd "${TVM_PATH}" && pwd)"
VTA_PATH="$(cd "${VTA_PATH}" && pwd)"
fsim_config="${VTA_PATH}/config/vta_config.json"
tsim_config="${VTA_PATH}/config/tsim_sample.json"

if [[ "$(uname -s)" == "Darwin" ]]; then
    library_suffix="dylib"
else
    library_suffix="so"
fi

[[ -x "${python_bin}" ]] || {
    echo "Error: Python was not found in environment: ${python_bin}" >&2
    echo "Run scripts/setup_tvm_vta_env.sh first." >&2
    exit 1
}
[[ -f "${fsim_config}" ]] || {
    echo "Error: FSIM config was not found: ${fsim_config}" >&2
    exit 1
}
[[ -f "${tsim_config}" ]] || {
    echo "Error: TSIM config was not found: ${tsim_config}" >&2
    exit 1
}
for library in \
    "${TVM_PATH}/build/libtvm.${library_suffix}" \
    "${VTA_PATH}/build/libvta_fsim.${library_suffix}" \
    "${VTA_PATH}/build/libvta_tsim.${library_suffix}" \
    "${VTA_PATH}/build/libvta_hw.${library_suffix}"; do
    [[ -f "${library}" ]] || {
        echo "Error: required library was not found: ${library}" >&2
        case "${library}" in
            *libvta_fsim*) echo "Run scripts/build_vta_lib.sh --target libvta_fsim first." >&2 ;;
            *libvta_tsim*|*libvta_hw*) echo "Run scripts/build_vta_lib.sh --target libvta_hw first." >&2 ;;
            *) echo "Build TVM before running this validation gate." >&2 ;;
        esac
        exit 1
    }
done

export TVM_PATH VTA_PATH
export PYTHONPATH="${TVM_PATH}/python:${VTA_PATH}/python${PYTHONPATH:+:${PYTHONPATH}}"

echo "==> BYOC structural tests"
VTA_CONFIG_FILE="${fsim_config}" "${python_bin}" -m pytest -q \
    "${VTA_PATH}/tests/python/unittest/test_target_extension.py" \
    "${VTA_PATH}/tests/python/unittest/test_target_hooks.py" \
    "${VTA_PATH}/tests/python/unittest/test_abi_fingerprint.py" \
    "${VTA_PATH}/tests/python/unittest/test_byoc_contract.py" \
    "${VTA_PATH}/tests/python/unittest/test_byoc_partition.py" \
    "${VTA_PATH}/tests/python/unittest/test_byoc_lowering.py" \
    "${VTA_PATH}/tests/python/unittest/test_byoc_codegen.py" \
    "${VTA_PATH}/tests/python/unittest/test_byoc_graphpack_retirement.py"

echo "==> FSIM gate"
VTA_CONFIG_FILE="${fsim_config}" "${script_dir}/test_vta_fsim.sh" --env-name "${env_name}"

echo "==> MLPerf ResNet V1 HOST/FSIM gate"
VTA_CONFIG_FILE="${fsim_config}" "${python_bin}" -m pytest -q \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_assets.py" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_model_pipeline.py" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py"

echo "==> MLPerf ResNet V2 HOST/FSIM gate"
VTA_CONFIG_FILE="${fsim_config}" "${python_bin}" -m pytest -q \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_assets.py" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_graph_artifacts.py" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_host_deployment.py"

echo "==> TSIM gate"
VTA_CONFIG_FILE="${tsim_config}" "${script_dir}/test_vta_tsim.sh" --env-name "${env_name}"

echo "==> MLPerf ResNet V1 HOST/TSIM gate"
VTA_CONFIG_FILE="${tsim_config}" "${python_bin}" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v1/run.py" \
    --simulator tsim --host-codegen all

echo "==> MLPerf ResNet V2 HOST/TSIM gate"
VTA_CONFIG_FILE="${tsim_config}" "${python_bin}" \
    "${VTA_PATH}/apps/mlperf_tiny_benchmark/image_classification_v2/run.py" \
    --simulator tsim --host-codegen all

echo "==> Python compilation"
"${python_bin}" -m compileall -q "${VTA_PATH}/python/vta"

legacy_reference_pattern="$(
    printf '%s' \
        'graph_' 'pack|' \
        'get_' 'subgraph|' \
        'start_' 'name|' \
        'stop_' 'name|' \
        'bitpack_' 'start|' \
        'bitpack_' 'end|' \
        'register_' 'byoc|' \
        'relay[.]' 'ext[.]' 'vta|' \
        'EXTERNAL_' 'COMPILER'
)"
legacy_reference_paths=(
    "${VTA_PATH}/README.md"
    "${VTA_PATH}/python"
    "${VTA_PATH}/apps"
    "${VTA_PATH}/tutorials"
    "${VTA_PATH}/tests"
    "${VTA_PATH}/docs"
    "${VTA_PATH}/scripts"
    "${VTA_PATH}/Jenkinsfile"
    "${project_dir}/scripts"
)

echo "==> Retired Relay compiler and graph-range reference check"
if rg -n "${legacy_reference_pattern}" "${legacy_reference_paths[@]}" \
    --glob '!**/build/**' \
    --glob '!**/3rdparty/**' \
    --glob '!**/tiny-v1.4/**' \
    --glob '!**/cifar-10-batches-py/**' \
    --glob '!test_byoc_graphpack_retirement.py'; then
    echo "Error: retired Relay compiler or graph-range references remain." >&2
    exit 1
fi

echo "==> Scoped repository checks"
[[ -z "$(git -C "${TVM_PATH}" status --short)" ]] || {
    echo "Error: pinned TVM submodule has local changes." >&2
    exit 1
}
git -C "${VTA_PATH}" diff --check
git diff --check

echo "VTA BYOC validation passed"
