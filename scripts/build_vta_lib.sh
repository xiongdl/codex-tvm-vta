#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"

env_name="tvm-vta-env"
build_type="Release"
target="all"
trace="none"
skip_deps=false
skip_tests=false

if command -v getconf >/dev/null 2>&1; then
    detected_jobs="$(getconf _NPROCESSORS_ONLN 2>/dev/null || true)"
fi
if [[ ! "${detected_jobs:-}" =~ ^[1-9][0-9]*$ ]] && command -v sysctl >/dev/null 2>&1; then
    detected_jobs="$(sysctl -n hw.logicalcpu 2>/dev/null || true)"
fi
jobs="${detected_jobs:-1}"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Build selected standalone VTA libraries."
    echo
    echo "Options:"
    echo "  --target TARGET       libvta_fsim, libvta_tsim, libvta_hw, or all"
    echo "                        (default: all)"
    echo "  --env-name NAME       Conda environment under .envs/"
    echo "                        (default: tvm-vta-env)"
    echo "  --build-type TYPE     CMake build type (default: Release)"
    echo "  --jobs N              Parallel CMake and Verilator build jobs"
    echo "                        (default: detected logical CPU count)"
    echo "  --trace MODE          none, vcd, or fst for libvta_hw (default: none)"
    echo "  --skip-deps           Do not preload Chisel dependencies"
    echo "  --skip-tests          Do not run Chisel lint and unit tests"
    echo "  -h, --help            Show this help message"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            [[ $# -ge 2 ]] || { echo "Error: --target requires a value." >&2; exit 1; }
            target="$2"
            shift 2
            ;;
        --env-name)
            [[ $# -ge 2 ]] || { echo "Error: --env-name requires a value." >&2; exit 1; }
            env_name="$2"
            shift 2
            ;;
        --build-type)
            [[ $# -ge 2 ]] || { echo "Error: --build-type requires a value." >&2; exit 1; }
            build_type="$2"
            shift 2
            ;;
        --jobs)
            [[ $# -ge 2 ]] || { echo "Error: --jobs requires a value." >&2; exit 1; }
            jobs="$2"
            shift 2
            ;;
        --trace)
            [[ $# -ge 2 ]] || { echo "Error: --trace requires a value." >&2; exit 1; }
            trace="$2"
            shift 2
            ;;
        --skip-deps)
            skip_deps=true
            shift
            ;;
        --skip-tests)
            skip_tests=true
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

[[ "${target}" =~ ^(libvta_fsim|libvta_tsim|libvta_hw|all)$ ]] || {
    echo "Error: --target must be libvta_fsim, libvta_tsim, libvta_hw, or all." >&2
    exit 1
}
[[ "${jobs}" =~ ^[1-9][0-9]*$ ]] || { echo "Error: --jobs must be a positive integer." >&2; exit 1; }
[[ "${trace}" =~ ^(none|vcd|fst)$ ]] || { echo "Error: --trace must be none, vcd, or fst." >&2; exit 1; }

env_dir="${project_dir}/.envs/${env_name}"
TVM_PATH="${TVM_PATH:-${project_dir}/tvm}"
VTA_PATH="${VTA_PATH:-${project_dir}/vta}"
TVM_PATH="$(cd "${TVM_PATH}" && pwd)"
VTA_PATH="$(cd "${VTA_PATH}" && pwd)"
expected_vta_path="$(cd "${project_dir}/vta" && pwd)"
[[ "${VTA_PATH}" == "${expected_vta_path}" ]] || {
    echo "Error: VTA_PATH must point to this workspace's VTA checkout: ${expected_vta_path}" >&2
    exit 1
}

cmake_bin="${CMAKE:-${env_dir}/bin/cmake}"
sbt_bin="${SBT:-${env_dir}/bin/sbt}"
verilator_bin="${VERILATOR:-${env_dir}/bin/verilator}"
JAVA_HOME="${JAVA_HOME:-${env_dir}/lib/jvm}"
if [[ "$(uname -s)" == "Darwin" ]]; then
    cxx_bin="${CXX:-$(xcrun --find clang++)}"
else
    cxx_bin="${CXX:-c++}"
fi

for tool in "${cmake_bin}" "${verilator_bin}"; do
    [[ -x "${tool}" ]] || { echo "Error: required tool was not found: ${tool}" >&2; exit 1; }
done
[[ -f "${TVM_PATH}/include/tvm/runtime/registry.h" ]] || { echo "Error: invalid TVM_PATH: ${TVM_PATH}" >&2; exit 1; }
[[ -f "${TVM_PATH}/build/libtvm.dylib" || -f "${TVM_PATH}/build/libtvm.so" ]] || {
    echo "Error: libtvm was not found under ${TVM_PATH}/build." >&2
    exit 1
}
[[ -f "${TVM_PATH}/build/libtvm_runtime.dylib" || -f "${TVM_PATH}/build/libtvm_runtime.so" ]] || {
    echo "Error: libtvm_runtime was not found under ${TVM_PATH}/build." >&2
    exit 1
}

verilator_root="$("${verilator_bin}" -getenv VERILATOR_ROOT)"
[[ -f "${verilator_root}/include/verilated.cpp" ]] || { echo "Error: invalid Verilator root: ${verilator_root}" >&2; exit 1; }

export TVM_PATH VTA_PATH JAVA_HOME
vta_build_dir="${VTA_PATH}/build"
case "${target}" in
    libvta_fsim) cmake_targets=(vta_fsim) ;;
    libvta_tsim|libvta_hw) cmake_targets=(vta_tsim) ;;
    all) cmake_targets=(vta_fsim vta_tsim) ;;
esac

config_file="${VTA_PATH}/config/vta_config.json"
if [[ "${target}" != "libvta_fsim" ]]; then
    config_file="${VTA_PATH}/config/tsim_sample.json"
fi

echo "Building VTA libraries..."
echo "  Target:          ${target}"
echo "  TVM_PATH:        ${TVM_PATH}"
echo "  VTA_PATH:        ${VTA_PATH}"
echo "  Build path:      ${vta_build_dir}"
echo "  Parallel jobs:   ${jobs}"

"${cmake_bin}" \
    -S "${VTA_PATH}" \
    -B "${vta_build_dir}" \
    -DTVM_PATH="${TVM_PATH}" \
    -DVTA_PATH="${VTA_PATH}" \
    -DVTA_CONFIG_FILE="${config_file}" \
    -DVERILATOR_ROOT="${verilator_root}" \
    -DCMAKE_BUILD_TYPE="${build_type}"
"${cmake_bin}" --build "${vta_build_dir}" --target "${cmake_targets[@]}" --parallel "${jobs}"

if [[ "${target}" == "libvta_hw" || "${target}" == "all" ]]; then
    [[ -x "${sbt_bin}" ]] || { echo "Error: SBT was not found: ${sbt_bin}" >&2; exit 1; }
    [[ -x "${JAVA_HOME}/bin/java" ]] || { echo "Error: JAVA_HOME does not contain bin/java: ${JAVA_HOME}" >&2; exit 1; }
    command -v make >/dev/null 2>&1 || { echo "Error: make was not found." >&2; exit 1; }
    command -v "${cxx_bin}" >/dev/null 2>&1 || { echo "Error: C++ compiler was not found: ${cxx_bin}" >&2; exit 1; }

    export PATH="${env_dir}/bin:${JAVA_HOME}/bin:${PATH}"
    use_trace=0
    use_trace_fst=0
    [[ "${trace}" == "none" ]] || use_trace=1
    [[ "${trace}" == "fst" ]] && use_trace_fst=1
    make_args=(
        -C "${VTA_PATH}/hardware/chisel"
        "TVM_PATH=${TVM_PATH}"
        "VTA_PATH=${VTA_PATH}"
        "SBT=${sbt_bin}"
        "VERILATOR=${verilator_bin}"
        "VERILATOR_ROOT=${verilator_root}"
        "CXX=${cxx_bin}"
        "USE_TRACE=${use_trace}"
        "USE_TRACE_FST=${use_trace_fst}"
    )
    if [[ "$(uname -s)" == "Darwin" ]]; then
        make_args+=("MACOS_SDK_PATH=$(xcrun --show-sdk-path)")
    fi
    [[ "${skip_deps}" == true ]] || make "${make_args[@]}" deps
    if [[ "${skip_tests}" == false ]]; then
        make "${make_args[@]}" lint
        make "${make_args[@]}" unittest
    fi
    make --jobs "${jobs}" "${make_args[@]}" lib
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
    library_suffix="dylib"
else
    library_suffix="so"
fi
case "${target}" in
    libvta_fsim) expected_libraries=("libvta_fsim.${library_suffix}") ;;
    libvta_tsim) expected_libraries=("libvta_tsim.${library_suffix}") ;;
    libvta_hw) expected_libraries=("libvta_tsim.${library_suffix}" "libvta_hw.${library_suffix}") ;;
    all) expected_libraries=("libvta_fsim.${library_suffix}" "libvta_tsim.${library_suffix}" "libvta_hw.${library_suffix}") ;;
esac

echo
echo "VTA libraries built successfully:"
for library in "${expected_libraries[@]}"; do
    library_path="${vta_build_dir}/${library}"
    [[ -f "${library_path}" ]] || { echo "Error: expected library was not generated: ${library_path}" >&2; exit 1; }
    echo "  ${library_path}"
done
