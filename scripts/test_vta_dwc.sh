#!/usr/bin/env bash
# Run the same real KWS layer on fresh matching FSIM then TSIM libraries.
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
artifacts="${1:-${project_dir}/vta/build/dwc-acceptance}"
mkdir -p "${artifacts}"
artifacts="$(cd "${artifacts}" && pwd)"
export TVM_PATH="${project_dir}/tvm" VTA_PATH="${project_dir}/vta"
export PYTHONPATH="${VTA_PATH}/python:${TVM_PATH}/python"
python_bin="${project_dir}/.envs/tvm-vta-env/bin/python"
cd "${project_dir}"
"${python_bin}" - "${VTA_PATH}/config/vta_64mac.json" "${artifacts}" <<'PY'
import json, pathlib, sys
base = json.loads(pathlib.Path(sys.argv[1]).read_text())
for bi, bo in [(3, 3), (3, 4), (4, 3)]:
    cfg = dict(base, LOG_BLOCK_IN=bi, LOG_BLOCK_OUT=bo)
    pathlib.Path(sys.argv[2], f'{1<<bi}x{1<<bo}.json').write_text(json.dumps(cfg, indent=2)+'\n')
PY
fresh_hardware() {
    rm -rf "${VTA_PATH}/build/verilator"
    rm -f "${VTA_PATH}/build/chisel/Test.DefaultTsimConfig.sv" "${VTA_PATH}/build/chisel/vta_geometry.properties"
}
restore_default() {
    fresh_hardware
    "${project_dir}/scripts/build_vta_lib.sh" --config "${VTA_PATH}/config/vta_64mac.json" --backend all --jobs "${DWC_JOBS:-4}" --skip-deps --skip-tests > "${artifacts}/restore-default.log" 2>&1
}
trap restore_default EXIT
for backend in fsim tsim; do
    export VTA_BACKEND="${backend}"
    for geometry in 8x8 8x16 16x8; do
        export VTA_CONFIG_FILE="${artifacts}/${geometry}.json"
        run_dir="${artifacts}/${backend}-${geometry}"
        mkdir -p "${run_dir}/libraries"
        export DWC_ARTIFACTS="${run_dir}"
        echo "Building ${backend} ${geometry}; logs: ${run_dir}"
        if [[ "${backend}" == tsim ]]; then fresh_hardware; fi
        "${project_dir}/scripts/build_vta_lib.sh" --config "${VTA_CONFIG_FILE}" --backend "${backend}" --jobs "${DWC_JOBS:-4}" --skip-deps --skip-tests > "${run_dir}/build.log" 2>&1
        cp "${VTA_CONFIG_FILE}" "${run_dir}/config.json"
        cp "${VTA_PATH}/build/libtvm-vta-ext."* "${run_dir}/libraries/"
        cp "${VTA_PATH}/build/libvta_${backend}."* "${run_dir}/libraries/"
        if [[ "${backend}" == tsim ]]; then
            cp "${VTA_PATH}/build/libvta_hw."* "${run_dir}/libraries/"
            cp "${VTA_PATH}/build/chisel/vta_geometry.properties" "${run_dir}/"
        fi
        "${python_bin}" - "${run_dir}" <<'PY'
import hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
files = [root/'config.json', *sorted((root/'libraries').iterdir())]
(root/'fingerprints.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, indent=2)+'\n')
(root/'source-head.txt').write_text(subprocess.check_output(['git','-C','vta','rev-parse','HEAD'], text=True))
PY
        "${python_bin}" -m pytest -q -s vta/tests/python/integration/test_depthwise_conv2d.py::test_real_kws_layer_signed_int32 > "${run_dir}/kws.log" 2>&1
        "${python_bin}" -m pytest -q -s vta/tests/python/integration/test_benchmark_gemm.py > "${run_dir}/gemm.log" 2>&1
        "${python_bin}" -m pytest -q vta/tests/python/unittest/test_backend_contract.py vta/tests/python/unittest/test_runtime_backend.py vta/tests/python/unittest/test_vta_insn.py > "${run_dir}/backend-isa.log" 2>&1
        "${python_bin}" - "${run_dir}" <<'PY'
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1])
log = (root/'kws.log').read_text()
match = re.search(r'KWS_ACCEPTANCE (\{[^\n]+\})', log)
assert match, 'numerical acceptance summary missing'
summary = json.loads(match.group(1))
if summary['backend'] == 'tsim':
    properties = dict(line.split('=', 1) for line in (root/'vta_geometry.properties').read_text().splitlines() if '=' in line and not line.startswith('#'))
    assert [int(properties['BLOCK_IN']), int(properties['BLOCK_OUT'])] == summary['geometry'], 'stale Chisel geometry'
assert 'DWC' in log, 'opcode-five runtime instruction trace missing'
assert log.count(': FINISH') == 4, 'not all byte-store commands completed'
assert 'NOP-STORE-STAGE' in log and 'NOP-COMPUTE-STAGE' in log, 'bridged queue trace missing'
summary['opcode5_trace'] = True
summary['completed_with_interleaved_queues'] = True
(root/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, sort_keys=True))
PY
    done
done
echo "All three FSIM geometries followed by all three TSIM geometries passed."
