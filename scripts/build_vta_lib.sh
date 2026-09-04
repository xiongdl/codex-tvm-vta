#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"

env_name="tvm-vta-env"
build_type="Release"

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
    echo "Build the standalone VTA FSIM and TSIM runtime libraries."
    echo
    echo "Options:"
    echo "  --env-name NAME       Conda environment under .envs/"
    echo "                        (default: tvm-vta-env)"
    echo "  --build-type TYPE     CMake build type (default: Release)"
    echo "  --jobs N              Number of parallel build jobs"
    echo "                        (default: detected logical CPU count)"
    echo "  -h, --help            Show this help message"
}

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
        --build-type)
            [[ $# -ge 2 ]] || {
                echo "Error: --build-type requires a value." >&2
                exit 1
            }
            build_type="$2"
            shift 2
            ;;
        --jobs)
            [[ $# -ge 2 ]] || {
                echo "Error: --jobs requires a value." >&2
                exit 1
            }
            jobs="$2"
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

if [[ ! "${jobs}" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: --jobs must be a positive integer." >&2
    exit 1
fi

env_dir="${project_dir}/.envs/${env_name}"
TVM_PATH="${TVM_PATH:-${project_dir}/tvm}"
VTA_PATH="${VTA_PATH:-${project_dir}/vta}"
tvm_build_dir="${TVM_PATH}/build"
vta_build_dir="${VTA_PATH}/build"
cmake_bin="${env_dir}/bin/cmake"
verilator_bin="${env_dir}/bin/verilator"

export TVM_PATH VTA_PATH

if [[ ! -x "${cmake_bin}" ]]; then
    echo "Error: CMake was not found in environment: ${cmake_bin}" >&2
    echo "Run scripts/setup_tvm_vta_env.sh first." >&2
    exit 1
fi

if [[ ! -x "${verilator_bin}" ]]; then
    echo "Error: Verilator was not found in environment: ${verilator_bin}" >&2
    echo "Run scripts/setup_tvm_vta_env.sh first." >&2
    exit 1
fi

verilator_root="$("${verilator_bin}" -getenv VERILATOR_ROOT)"
if [[ ! -f "${verilator_root}/include/verilated.cpp" ]]; then
    echo "Error: Verilator runtime sources were not found in ${verilator_root}" >&2
    exit 1
fi

if [[ ! -f "${TVM_PATH}/include/tvm/runtime/registry.h" ]]; then
    echo "Error: TVM source tree was not found: ${TVM_PATH}" >&2
    exit 1
fi

if [[ ! -f "${tvm_build_dir}/libtvm_runtime.so" &&
      ! -f "${tvm_build_dir}/libtvm_runtime.dylib" ]]; then
    echo "Error: libtvm_runtime was not found in ${tvm_build_dir}" >&2
    echo "Build TVM before building VTA." >&2
    exit 1
fi

if [[ ! -f "${tvm_build_dir}/libtvm.so" &&
      ! -f "${tvm_build_dir}/libtvm.dylib" ]]; then
    echo "Error: libtvm was not found in ${tvm_build_dir}" >&2
    echo "Build TVM before building VTA." >&2
    exit 1
fi

if [[ ! -f "${VTA_PATH}/CMakeLists.txt" ]]; then
    echo "Error: VTA CMake project was not found: ${VTA_PATH}" >&2
    exit 1
fi

echo "Building VTA FSIM and TSIM runtime libraries..."
echo
echo "  TVM source:       ${TVM_PATH}"
echo "  TVM libraries:    ${tvm_build_dir}"
echo "  VTA source:       ${VTA_PATH}"
echo "  VTA build:        ${vta_build_dir}"
echo "  Verilator root:   ${verilator_root}"
echo "  Environment:      ${env_dir}"
echo "  Build type:       ${build_type}"
echo "  Parallel jobs:    ${jobs}"

"${cmake_bin}" \
    -S "${VTA_PATH}" \
    -B "${vta_build_dir}" \
    -DTVM_PATH="${TVM_PATH}" \
    -DVTA_PATH="${VTA_PATH}" \
    -DVERILATOR_ROOT="${verilator_root}" \
    -DCMAKE_BUILD_TYPE="${build_type}"

"${cmake_bin}" \
    --build "${vta_build_dir}" \
    --target vta_fsim vta_tsim \
    --parallel "${jobs}"

if [[ "$(uname -s)" == "Darwin" ]]; then
    fsim_library="${vta_build_dir}/libvta_fsim.dylib"
    tsim_library="${vta_build_dir}/libvta_tsim.dylib"
else
    fsim_library="${vta_build_dir}/libvta_fsim.so"
    tsim_library="${vta_build_dir}/libvta_tsim.so"
fi

for vta_library in "${fsim_library}" "${tsim_library}"; do
    if [[ ! -f "${vta_library}" ]]; then
        echo "Error: VTA library was not generated: ${vta_library}" >&2
        exit 1
    fi
done

echo
echo "VTA libraries built successfully:"
echo "  ${fsim_library}"
echo "  ${tsim_library}"
