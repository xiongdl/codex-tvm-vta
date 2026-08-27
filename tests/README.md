# Project-Level / End-to-End Tests

Use this directory for tests that validate the project as a whole.

```text
components/<component>/tests/  → Component-local tests
integration/tests/             → Cross-component tests
tests/                         → Project-level / End-to-End tests
```

Run the project lifecycle source-state checks with:

```bash
./tests/project_cli_test.sh
```
