# Intent: Image classification V1 cleanup
User explicitly confirmed the proposed direction on 2026-10-05, including renaming run.py to deploy.py and consolidating modules.

## Outcome
Make image_classification_v1 tidy for its maintainer. Keep deploy.py and tune.py as root CLI entries; move internal Python into python/ and shell scripts into scripts/. Merge cohesive modules and use responsibility-specific names. Remove only demonstrably unnecessary code. Preserve algorithms, tuning policies, CLI options, Makefile deploy/tune-fsim/tune-tsim/tune behavior, model, samples, and tuning data. Add clean for generated build/ and Python caches, preserving tune/. Scope includes affected callers, tests, and documentation; unrelated applications and repository policies are excluded.

## Manual Acceptance
The user inspects the directory and personally runs the original Makefile functionality (deploy, tune-fsim, tune-tsim, tune), confirms it remains functional, runs make clean, and observes build/cache removal and preserved tune/model/samples.
