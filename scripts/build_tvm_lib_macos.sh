#!/usr/bin/env bash

set -euo pipefail

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_path="$(cd "${script_path}/.." && pwd)"

env_name="tvm-vta-env"
build_type="Release"

cpu_count="$(sysctl -n hw.logicalcpu)"
jobs="$((cpu_count > 2 ? cpu_count - 2 : 1))"

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
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --env-name NAME       Environment name (default: tvm-vta-env)"
            echo "  --build-type TYPE     CMake build type (default: Release)"
            echo "  --jobs N              Number of parallel build jobs"
            echo "                        (default: logical CPU count minus 2)"
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

env_path="${project_path}/.envs/${env_name}"
tvm_path="${project_path}/tvm"
build_path="${tvm_path}/build"
llvm_config="${env_path}/bin/llvm-config"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Error: this script is intended for macOS." >&2
    exit 1
fi

if [[ "$(uname -m)" != "arm64" ]]; then
    echo "Error: this script is intended for Apple Silicon (arm64)." >&2
    exit 1
fi

if [[ ! "${jobs}" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: --jobs must be a positive integer." >&2
    exit 1
fi

if [[ ! -d "${env_path}" ]]; then
    echo "Error: Conda environment not found: ${env_path}" >&2
    echo "Run scripts/setup_tvm_vta_env.sh first." >&2
    exit 1
fi

if [[ ! -f "${tvm_path}/CMakeLists.txt" ]]; then
    echo "Error: TVM source directory not found: ${tvm_path}" >&2
    echo "Make sure the TVM submodule has been initialized." >&2
    exit 1
fi

if [[ ! -x "${llvm_config}" ]]; then
    echo "Error: llvm-config not found: ${llvm_config}" >&2
    exit 1
fi

if ! xcrun --find clang++ >/dev/null 2>&1; then
    echo "Error: Apple Clang was not found." >&2
    echo "Install the Xcode Command Line Tools first." >&2
    exit 1
fi

echo "Building TVM..."
echo
echo "  Project path:     ${project_path}"
echo "  TVM source:       ${tvm_path}"
echo "  Build path:       ${build_path}"
echo "  Environment:      ${env_path}"
echo "  Build type:       ${build_type}"
echo "  Architecture:     $(uname -m)"
echo "  Logical CPUs:     ${cpu_count}"
echo "  Parallel jobs:    ${jobs}"
echo "  LLVM:             $("${llvm_config}" --version)"

mkdir -p "${build_path}"

echo
echo "Configuring TVM..."

conda run --no-capture-output -p "${env_path}" \
    cmake \
    -S "${tvm_path}" \
    -B "${build_path}" \
    -DCMAKE_BUILD_TYPE="${build_type}" \
    "-DUSE_LLVM=${llvm_config} --ignore-libllvm --link-static" \
    -DHIDE_PRIVATE_SYMBOLS=ON \
    -DUSE_CUDA=OFF \
    -DUSE_METAL=OFF \
    -DUSE_VULKAN=OFF \
    -DUSE_OPENCL=OFF

echo
echo "Building TVM..."

conda run --no-capture-output -p "${env_path}" \
    cmake \
    --build "${build_path}" \
    --parallel "${jobs}"

libtvm="${build_path}/libtvm.dylib"
libtvm_runtime="${build_path}/libtvm_runtime.dylib"

echo

if [[ ! -f "${libtvm}" ]]; then
    echo "Error: libtvm.dylib was not generated." >&2
    exit 1
fi

if [[ ! -f "${libtvm_runtime}" ]]; then
    echo "Error: libtvm_runtime.dylib was not generated." >&2
    exit 1
fi

echo "TVM build completed successfully."
echo
echo "Generated libraries:"
echo "  ${libtvm}"
echo "  ${libtvm_runtime}"
