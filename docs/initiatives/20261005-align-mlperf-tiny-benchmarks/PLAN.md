# Implementation Plan

Initiative: `20261005-align-mlperf-tiny-benchmarks`
Branch: `codex/20261005-align-mlperf-tiny-benchmarks`
Confirmed intent and reviewed Specify: primary repository
`286772e7269814c3f722076d94f61548c67ca305`, all INTENT/CAPABILITY_MAP/SPEC
paths in this initiative. Architecture Review returned Pass on this exact set.
VTA initial evidence/base `26e9c86035b3ef8d6ff68bbbeb8ee7819a297401`;
TVM base `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` (read-only).

## Approach and dependencies
Follow capability-map order: image V2, visual wake words, keyword spotting,
anomaly, streaming wakeword, then integration cleanup. Each migration is one
coherent independently GREEN vertical slice, encompassing model preparation,
selected deployment, snapshot/tuning, tests, its README/manual commands and
its existing maintained caller updates. Single-app copies of the read-only
reference implementation are intentional; never introduce a shared runtime.
Do not split CLI removal from caller migration or publication from validation.
No parallel agents or checkpoints: Root waits for each fresh Default.

`TASKS.md` is the execution contract. Every checkpoint has one attributable
commit unit, final verification, simplification, affected re-verification and
its own commit. The scope exceeds five files because separating an entire
interface replacement across commits would knowingly leave broken old tests
or consumers; size is justified by one app's coherent outcome. Later cleanup
never repairs an intentionally broken app migration. Tests/docs unrelated to
migrated apps remain working until their own replacement checkpoint.

## Risks and mitigation
- Int8 old normalization changes arithmetic: original-QNN/prepared-CPU exact
  checks are separate from CPU/VTA checks; preserve unsupported arithmetic.
- Streaming or KWS may have no supported real regions: follow reviewed
  truthful fallback/export-schedule rejection contract; do not add a probe.
- Template embeds ResNet identities: adapt local input names, model id,
  normalization metadata and report logic; reject foreign snapshots.
- Python packages named python collide: app tests use unique package identities
  and subprocesses for backend selection. Verify all app imports without apps/.
- TSIM is expensive: one selected occurrence, one FSIM success, 60/120-second
  candidate bounds are enough for actual integration evidence; no full search.
- Anomaly preprocessing returns many windows: select the first existing vector
  deterministically, expose exactly one executed window and MSE, no threshold.
- Existing script imports shared cleanup: keep shared modules until no consumers
  need them, then replace maintained cleanup and delete obsolete code together.
- Reference app is excluded: verify zero diff relative to initial VTA OID at
  every checkpoint and at final cleanup.

## Verification and finish
Each Default reports all exact commands, pass/failure counts, runtime outputs,
limitations, original/final and task commit maps. Required libraries/environment
already exist; use pinned Python and documented scripts. Do not recreate env or
install deps. If a genuine external prerequisite is unavailable, report exact
evidence. Ordinary tests/candidate failures are fixed within scope.

Final integration runs updated maintained BYOC runner with appropriate backend
modes, all app-owned tests and script tests, real bounded tuning/replay evidence
where partitions exist, import/dependency scan and reference exclusion checks.
Root then dispatches fresh Implementation Reviewer for complete base-to-tip
range and iterates fixes automatically. On Pass hand off five independent
complete manual acceptance sets, current OIDs, evidence and known risks; stop
for user's acceptance. Root does not merge or supply merge command until user
reports acceptance Pass.
