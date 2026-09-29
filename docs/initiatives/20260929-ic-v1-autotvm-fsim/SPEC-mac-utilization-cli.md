# Spec: Model-Independent MAC Utilization Calculator

## Objective

Add a maintained command under `scripts/` that calculates useful VTA MAC
utilization from explicit numerical inputs. It must not import, inspect, or
assume any MLPerf Tiny model. A benchmark developer supplies a logical MAC
count, a TSIM cycle count, and a VTA geometry configuration; the script reports
the ratio and percentage.

## Metric

For `M` logical multiply-accumulates, `C` positive TSIM cycles, and `P` peak
MACs per cycle from the configuration:

```text
useful_mac_utilization = M / (C * P)
```

Treat one multiply-accumulate as one MAC. Derive peak throughput from
`2**LOG_BATCH * 2**LOG_BLOCK * 2**LOG_BLOCK`; the standard 64-MAC geometry
therefore gives 64 MAC/cycle. Print both a ratio and percentage. Do not use
FSIM wall-clock duration as `C`.

## Tech Stack

Use a standard-library Python CLI and JSON geometry parsing. Run it with the
repository's required `.envs/tvm-vta-env/bin/python` command even though the
calculator itself has no model or TVM runtime dependency.

## Command

Maintain the entry point at:

```text
scripts/mac_utilization.py
```

The CLI requires positive integer `--macs` and `--cycles` arguments. It accepts
`--config PATH`, defaulting to the shared `vta/config/vta_64mac.json`, and
validates the configuration fields before calculating. Invalid numbers,
malformed JSON, missing fields, or invalid geometry fail clearly before
printing a utilization result.

Example shape (exact option spelling may be aligned with repository
conventions during implementation):

```bash
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py \
  --macs 123456 --cycles 7890
```

## Project Structure

- `scripts/mac_utilization.py`: model-independent CLI and pure calculation.
- `scripts/README.md`: interface, inputs, default config, formula, example,
  outputs, and failure behavior.
- `scripts/tests/` or the repository's existing focused script test location:
  formula and input-validation coverage.

## Code Style

Separate config parsing, geometry derivation, input validation, calculation,
and presentation. Keep the units explicit:

```python
peak_macs_per_cycle = batch * block_in * block_out
utilization = mac_count / (cycle_count * peak_macs_per_cycle)
```

## Testing Strategy

- Unit tests verify the formula, ratio/percentage formatting, standard 64
  MAC/cycle geometry, and rejection of non-positive or non-integral values.
- CLI checks cover missing arguments, malformed geometry JSON, absent or
  invalid geometry fields, and a representative valid invocation.
- Verify the script has no import or runtime dependency on model directories,
  AutoTVM logs, or MLPerf Tiny application modules.

## Boundaries

- **Always:** require explicit MAC and TSIM cycle values; derive peak throughput
  from a validated geometry file; label the result and units; make no model
  assumptions.
- **Ask first:** change the MAC definition, formula, default geometry, or
  introduce a model/log parser.
- **Never:** infer hardware cycles from FSIM wall time, silently accept invalid
  geometry, or label the result as FPGA physical utilization.

## Success Criteria

- A valid invocation prints `MACs`, TSIM cycles, peak MACs/cycle, utilization
  ratio, and percentage.
- The checked-in `vta_64mac.json` produces a peak of 64 MAC/cycle.
- Invalid numerical inputs and malformed geometry return a clear nonzero
  failure without a numeric result.
- The script runs without importing any model-specific module or asset.

## Open Questions

- None. The calculator accepts `--macs` and `--cycles`; automating extraction
  from tuning artifacts is outside this module's confirmed scope.
