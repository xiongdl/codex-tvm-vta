#!/usr/bin/env bash

set -euo pipefail

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_path="$(cd "${script_path}/.." && pwd)"
env_name="sww-env"

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
        -h|--help)
            echo "Usage: $0 [--env-name NAME] [--help]"
            echo "Creates or reuses the dedicated SWW conversion environment under .envs/."
            exit 0
            ;;
        *)
            echo "Error: unknown option: $1" >&2
            echo "Use --help to see available options." >&2
            exit 1
            ;;
    esac
done

if [[ ! "${env_name}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ || "${env_name}" == "." || "${env_name}" == ".." ]]; then
    echo "Error: invalid environment name: ${env_name}" >&2
    exit 1
fi

command -v conda >/dev/null 2>&1 || {
    echo "Error: conda is required to create the SWW conversion environment." >&2
    exit 1
}

env_path="${project_path}/.envs/${env_name}"
requirements="${project_path}/.envs/tiny-v1.4/benchmark/training/streaming_wakeword/requirements.txt"
[[ -f "${requirements}" ]] || {
    echo "Error: upstream requirements not found: ${requirements}" >&2
    exit 1
}

if [[ -e "${env_path}" ]]; then
    [[ -x "${env_path}/bin/python" ]] || {
        echo "Error: existing prefix is not a valid Python environment; it was left untouched: ${env_path}" >&2
        exit 1
    }
    echo "Reusing existing environment: ${env_path}"
else
    mkdir -p "${project_path}/.envs"
    conda create -y -p "${env_path}" -c conda-forge python=3.11 pip
fi

"${env_path}/bin/python" -m pip install -r "${requirements}"

echo "SWW conversion environment is ready: ${env_path}"
