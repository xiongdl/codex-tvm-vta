# Capability Map

Each application is independently deployable and testable; there are no runtime
edges between applications. Their repeated code is deliberate local ownership,
not a new shared module. The template is read-only design/source evidence.

| Module | Specification | Depends on | Build order |
| --- | --- | --- | --- |
| image_classification_v2 | SPEC-image_classification_v2.md | TVM/VTA external libraries only | 1 |
| visual_wake_words_v1 | SPEC-visual_wake_words_v1.md | TVM/VTA external libraries only | 2 |
| keyword_spotting_v1 | SPEC-keyword_spotting_v1.md | TVM/VTA external libraries only | 3 |
| anomaly_detection_v1 | SPEC-anomaly_detection_v1.md | TVM/VTA external libraries only | 4 |
| streaming_wakeword_v1 | SPEC-streaming_wakeword_v1.md | TVM/VTA external libraries only | 5 |
| integration | SPEC-integration.md | all five migrated apps | 6 |

Integration owns repository runners, cleanup entrypoint transition and removal
of obsolete shared code after all consumers move. It owns no application logic.
