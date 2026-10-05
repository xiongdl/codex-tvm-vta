# Plan
Reviewed Specify: primary repository 59e060b8aacdf8e683572c74903dd4ed49b29835, docs/initiatives/20261005-image-classification-cleanup/SPEC.md; Architecture Review Pass.
VTA base: 9e2035f1866d125a24608d646cd5e4e005355c74. TVM base: 9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca.

One execution checkpoint, two atomic tasks: migrate source, callers, tests and docs together so no intermediate broken imports; then add clean as an independently stable feature. The first task necessarily spans more than five files because the import graph and its consumers must migrate together. No architecture changes. Biggest risks are duplicate names in merges, lazy imports, multiprocessing spawn, test monkeypatch ownership and asset/script roots. Validate existing functional contracts after migration, then validate destructive clean with temporary sentinels and preservation hashes. Prebuilt library unavailability is reported, never compensated by rebuilding or weakening tests.

Use TASKS.md for execution. Final implementation review covers complete committed range and verification evidence. User manually validates all Make targets and clean before merge.
