#!/usr/bin/env bash

set -euo pipefail

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_path="$(cd "${script_path}/.." && pwd)"

env_name="tvm-vta-env"
python_version="3.11"

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
        --python-version)
            [[ $# -ge 2 ]] || {
                echo "Error: --python-version requires a value." >&2
                exit 1
            }
            python_version="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --env-name NAME           Environment name (default: tvm-vta-env)"
            echo "  --python-version VERSION  Python version (default: 3.11)"
            echo "  -h, --help                Show this help message"
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

echo "Creating TVM/VTA build environment..."
echo "  Project path:     ${project_path}"
echo "  Environment:      ${env_name}"
echo "  Environment path: ${env_path}"
echo "  Python:           ${python_version}"

mkdir -p "${project_path}/.envs"

# Remove the existing environment if it exists.
if [[ -d "${env_path}" ]]; then
    echo
    echo "Removing existing environment..."
    conda env remove -p "${env_path}" -y
fi

# Install TVM/VTA native build dependencies.
echo
echo "Installing Conda packages..."

conda create \
    -p "${env_path}" \
    -y \
    -c conda-forge \
    "llvmdev=17" \
    "cmake>=3.24" \
    git \
    verilator \
    "python=${python_version}" \
    pip

# Install TVM/VTA Python dependencies.
echo
echo "Installing Python packages..."

conda run -p "${env_path}" \
    python -m pip install \
    numpy \
    cython \
    tornado \
    psutil \
    xgboost \
    cloudpickle

echo
echo "TVM/VTA build environment created successfully."
echo
echo "Activate it with:"
echo "  conda activate ${env_path}"
