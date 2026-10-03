# Verification evidence

Initiative: `20261003-workflow-consistency-validation`
Checkpoint: C1/T1 — reproduce existing validation
Branch: `codex/20261003-workflow-consistency-validation`

## Inputs

The audit range is root `470b501dcc7e2b1a51baad5968f75e68efeb6848` through
`e1d9589cd4b5a9b3bac58d50c04823e640c98aac`. At execution start, the managed
repository map was:

| Repository | Branch | OID |
| --- | --- | --- |
| root | `codex/20261003-workflow-consistency-validation` | `65007c6209e0415e1823faf1d64c3d2f7e6f9533` |
| `tvm` | `codex/20261003-workflow-consistency-validation` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| `vta` | `codex/20261003-workflow-consistency-validation` | `2708a80c19246ec99efe359125f02ae9b121e164` |

The required project interpreter exists at
`.envs/tvm-vta-env/bin/python`. Both managed child checkouts are initialized.

## Commands and results

Commands ran from the repository root on 2026-10-03 (Asia/Shanghai):

| Command | Exit | Result |
| --- | ---: | --- |
| `git diff --check 470b501dcc7e2b1a51baad5968f75e68efeb6848 e1d9589cd4b5a9b3bac58d50c04823e640c98aac` | 0 | No whitespace errors; no output. |
| `bash -n .agents/custom/scripts/git-workflow .agents/custom/scripts/test-git-workflow .agents/custom/scripts/test-role-workflow` | 0 | Initial invocation checked only the first script; subsequent arguments are positional parameters, not additional input scripts. See individual checks below. |
| `bash .agents/custom/scripts/test-role-workflow` | 0 | `OK role workflow contract`. |
| `bash .agents/custom/scripts/test-git-workflow` | 0 | `OK git-workflow tests`. Happy path, unmerged-task deletion, and submodule parent-commit retry cases completed. |
| `./.envs/tvm-vta-env/bin/python` TOML/path validation (command below) | 0 | Four TOML files parsed; all ten listed role and skill paths existed. |
| `./.agents/custom/scripts/git-workflow status` | 0 | All managed repositories and gitlinks were clean on the expected task branch and OIDs. |

TOML/path validation command:

```bash
./.envs/tvm-vta-env/bin/python - <<'PY'
import pathlib
import tomllib
paths = [
    pathlib.Path('.codex/config.toml'),
    pathlib.Path('.codex/agents/default.toml'),
    pathlib.Path('.codex/agents/architecture-reviewer.toml'),
    pathlib.Path('.codex/agents/implementation-reviewer.toml'),
]
for path in paths:
    with path.open('rb') as stream:
        data = tomllib.load(stream)
    print(f'OK {path}: {", ".join(data)}')
for path in [
    pathlib.Path('AGENTS.md'),
    pathlib.Path('.agents/custom/root.md'),
    pathlib.Path('.agents/custom/default.md'),
    pathlib.Path('.agents/custom/architecture-reviewer.md'),
    pathlib.Path('.agents/custom/implementation-reviewer.md'),
    pathlib.Path('.agents/custom/architecture.md'),
    pathlib.Path('.agents/custom/version-control.md'),
    pathlib.Path('.agents/custom/automation.md'),
    pathlib.Path('.agents/vendor/agent-skills/skills/incremental-implementation/SKILL.md'),
    pathlib.Path('.agents/vendor/agent-skills/skills/test-driven-development/SKILL.md'),
]:
    print(f'{"OK" if path.is_file() else "MISSING"} {path}')
PY
```

The parser reported the expected top-level keys in `.codex/config.toml` and
each of the three agent TOMLs. Every path checked by the script printed `OK`.

## Test side effects and limits

`test-role-workflow` only searches for required text and prints a result.
`test-git-workflow` creates three fixture repositories beneath
`${TMPDIR:-/tmp}/git-workflow-tests.XXXXXX`. Its tests make commits, branches,
and a local submodule inside those fixtures. An `EXIT` trap removes only the
fixture directory after confirming its expected name prefix. The test does not
run mutating workflow operations in the managed project repositories.

These checks establish shell syntax, textual role-contract assertions, Git
workflow behavior for the tested fixture scenarios, TOML syntax, and existence
of the checked paths. They do not establish runtime role selection or agent
behavior. The suites passed, so no test failure is recorded as a finding here.

## Root verification correction

After independent review, Root identified the overly broad initial shell-syntax
claim and ran each script separately on 2026-10-03 (Asia/Shanghai), at root OID
`1bc5c1df94f32e7066e3499f18aa17af82ed1545`:

```bash
for script_path in .agents/custom/scripts/git-workflow .agents/custom/scripts/test-git-workflow .agents/custom/scripts/test-role-workflow; do
    bash -n "$script_path" || exit
    printf 'OK syntax %s\n' "$script_path"
done
```

Exit status: 0. Output:

```text
OK syntax .agents/custom/scripts/git-workflow
OK syntax .agents/custom/scripts/test-git-workflow
OK syntax .agents/custom/scripts/test-role-workflow
```

All three scripts therefore have individual syntax-check evidence. This corrects
the audit record only; no workflow, configuration, or test-source file changed.
