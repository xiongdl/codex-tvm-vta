#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"

env_name="tvm-vta-env"
build_type="Release"
backend="all"
config_file=""
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
    echo "Usage: $0 --config ABS_PATH [OPTIONS]"
    echo
    echo "Build standalone VTA libraries from one geometry configuration."
    echo
    echo "Options:"
    echo "  --config ABS_PATH     Absolute path to the geometry JSON configuration"
    echo "  --backend BACKEND     fsim, tsim, or all (default: all)"
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
        --config)
            [[ $# -ge 2 ]] || { echo "Error: --config requires an absolute path." >&2; exit 1; }
            config_file="$2"
            shift 2
            ;;
        --backend)
            [[ $# -ge 2 ]] || { echo "Error: --backend requires fsim, tsim, or all." >&2; exit 1; }
            backend="$2"
            shift 2
            ;;
        --target)
            echo "Error: --target is no longer supported; use --config ABS_PATH --backend fsim|tsim|all." >&2
            exit 2
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

[[ "${backend}" =~ ^(fsim|tsim|all)$ ]] || {
    echo "Error: --backend must be fsim, tsim, or all." >&2
    exit 1
}
[[ "${jobs}" =~ ^[1-9][0-9]*$ ]] || { echo "Error: --jobs must be a positive integer." >&2; exit 1; }
[[ "${trace}" =~ ^(none|vcd|fst)$ ]] || { echo "Error: --trace must be none, vcd, or fst." >&2; exit 1; }
[[ -n "${config_file}" ]] || {
    echo "Error: --config ABS_PATH is required; use --backend fsim|tsim|all." >&2
    exit 1
}
[[ "${config_file}" = /* ]] || {
    echo "Error: --config must be an absolute path: ${config_file}" >&2
    exit 1
}
[[ -f "${config_file}" ]] || {
    echo "Error: --config does not exist: ${config_file}" >&2
    exit 1
}
config_file="$(cd "$(dirname "${config_file}")" && pwd)/$(basename "${config_file}")"

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

[[ -x "${cmake_bin}" ]] || { echo "Error: required tool was not found: ${cmake_bin}" >&2; exit 1; }
if [[ "${backend}" != "fsim" ]]; then
    [[ -x "${verilator_bin}" ]] || { echo "Error: required tool was not found: ${verilator_bin}" >&2; exit 1; }
fi
[[ -f "${TVM_PATH}/include/tvm/runtime/registry.h" ]] || { echo "Error: invalid TVM_PATH: ${TVM_PATH}" >&2; exit 1; }
[[ -f "${TVM_PATH}/build/libtvm.dylib" || -f "${TVM_PATH}/build/libtvm.so" ]] || {
    echo "Error: libtvm was not found under ${TVM_PATH}/build." >&2
    exit 1
}
[[ -f "${TVM_PATH}/build/libtvm_runtime.dylib" || -f "${TVM_PATH}/build/libtvm_runtime.so" ]] || {
    echo "Error: libtvm_runtime was not found under ${TVM_PATH}/build." >&2
    exit 1
}

export TVM_PATH VTA_PATH JAVA_HOME
vta_build_dir="${VTA_PATH}/build"
cmake_targets=(tvm_vta_ext)
[[ "${backend}" == "fsim" || "${backend}" == "all" ]] && cmake_targets+=(vta_fsim)
[[ "${backend}" == "tsim" || "${backend}" == "all" ]] && cmake_targets+=(vta_tsim)

verilator_root=""
if [[ "${backend}" != "fsim" ]]; then
    verilator_root="$("${verilator_bin}" -getenv VERILATOR_ROOT)"
    [[ -f "${verilator_root}/include/verilated.cpp" ]] || { echo "Error: invalid Verilator root: ${verilator_root}" >&2; exit 1; }
fi

echo "Building VTA libraries..."
echo "  Config:          ${config_file}"
echo "  Backend:         ${backend}"
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
    -DVTA_BACKEND="${backend}" \
    -DVERILATOR_ROOT="${verilator_root}" \
    -DCMAKE_BUILD_TYPE="${build_type}"
"${cmake_bin}" --build "${vta_build_dir}" --target "${cmake_targets[@]}" --parallel "${jobs}"

hardware_built=false
if [[ "${backend}" == "tsim" || "${backend}" == "all" ]]; then
    hardware_ready=true
    [[ -x "${sbt_bin}" ]] || hardware_ready=false
    [[ -x "${JAVA_HOME}/bin/java" ]] || hardware_ready=false
    command -v make >/dev/null 2>&1 || hardware_ready=false
    command -v "${cxx_bin}" >/dev/null 2>&1 || hardware_ready=false
    if [[ "${hardware_ready}" != true ]]; then
        echo "Skipping hardware generation: SBT, Java, make, and C++ are required for libvta_hw." >&2
    else
        export PATH="${env_dir}/bin:${JAVA_HOME}/bin:${PATH}"
        use_trace=0
        use_trace_fst=0
        [[ "${trace}" == "none" ]] || use_trace=1
        [[ "${trace}" == "fst" ]] && use_trace_fst=1
        make_args=(
            -C "${VTA_PATH}/hardware/chisel"
            "TVM_PATH=${TVM_PATH}"
            "VTA_PATH=${VTA_PATH}"
            "VTA_CONFIG_FILE=${config_file}"
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
        hardware_built=true
    fi
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
    library_suffix="dylib"
else
    library_suffix="so"
fi
expected_libraries=("libtvm-vta-ext.${library_suffix}")
[[ "${backend}" == "fsim" || "${backend}" == "all" ]] && expected_libraries+=("libvta_fsim.${library_suffix}")
[[ "${backend}" == "tsim" || "${backend}" == "all" ]] && expected_libraries+=("libvta_tsim.${library_suffix}")
[[ "${hardware_built}" == true ]] && expected_libraries+=("libvta_hw.${library_suffix}")

echo
echo "VTA libraries built successfully:"
for library in "${expected_libraries[@]}"; do
    library_path="${vta_build_dir}/${library}"
    [[ -f "${library_path}" ]] || { echo "Error: expected library was not generated: ${library_path}" >&2; exit 1; }
    echo "  ${library_path}"
done
