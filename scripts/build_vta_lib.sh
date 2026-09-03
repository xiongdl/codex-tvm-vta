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
    echo "Build the standalone VTA fast-simulator library."
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
tvm_dir="${project_dir}/tvm"
tvm_build_dir="${tvm_dir}/build"
vta_dir="${project_dir}/vta"
vta_build_dir="${vta_dir}/build"
cmake_bin="${env_dir}/bin/cmake"

if [[ ! -x "${cmake_bin}" ]]; then
    echo "Error: CMake was not found in environment: ${cmake_bin}" >&2
    echo "Run scripts/setup_tvm_vta_env.sh first." >&2
    exit 1
fi

if [[ ! -f "${tvm_dir}/include/tvm/runtime/registry.h" ]]; then
    echo "Error: TVM source tree was not found: ${tvm_dir}" >&2
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

if [[ ! -f "${vta_dir}/CMakeLists.txt" ]]; then
    echo "Error: VTA CMake project was not found: ${vta_dir}" >&2
    exit 1
fi

echo "Building VTA fast-simulator library..."
echo
echo "  TVM source:       ${tvm_dir}"
echo "  TVM libraries:    ${tvm_build_dir}"
echo "  VTA source:       ${vta_dir}"
echo "  VTA build:        ${vta_build_dir}"
echo "  Environment:      ${env_dir}"
echo "  Build type:       ${build_type}"
echo "  Parallel jobs:    ${jobs}"

"${cmake_bin}" \
    -S "${vta_dir}" \
    -B "${vta_build_dir}" \
    -DTVM_PATH="${tvm_dir}" \
    -DTVM_BUILD_DIR="${tvm_build_dir}" \
    -DCMAKE_BUILD_TYPE="${build_type}"

"${cmake_bin}" \
    --build "${vta_build_dir}" \
    --target vta_fsim \
    --parallel "${jobs}"

if [[ "$(uname -s)" == "Darwin" ]]; then
    vta_library="${vta_build_dir}/libvta_fsim.dylib"
else
    vta_library="${vta_build_dir}/libvta_fsim.so"
fi

if [[ ! -f "${vta_library}" ]]; then
    echo "Error: VTA library was not generated: ${vta_library}" >&2
    exit 1
fi

echo
echo "VTA library built successfully:"
echo "  ${vta_library}"
