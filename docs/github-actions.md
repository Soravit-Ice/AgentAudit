# CI/CD & GitHub Actions Integration

Running evaluations automatically on every pull request is the best way to catch regressions before they hit production. 

This guide describes how to configure AgentAudit inside GitHub Actions.

---

## Example Workflow File

Create a file named `.github/workflows/agentaudit.yml` in your repository:

```yaml
name: AI Evals

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  run-evals:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Package
        run: |
          pip install -upgrade pip
          pip install -e ".[dev]"

      - name: Run Safety and Quality Evals
        run: |
          agentaudit run tests/ --fail-under-score 0.85 --fail-on-risk medium
```

---

## Controlling CI Exit Gates

The `agentaudit run` command supports parameters to control CLI exit codes:

### 1. Fail Under Score (`--fail-under-score`)
Sets an accuracy threshold (percentage of passed assertions as a fraction). If the suite accuracy falls below this decimal limit, the command exits with code `1`, failing the CI pipeline.

```bash
agentaudit run tests/ --fail-under-score 0.90
```

### 2. Fail on Risk (`--fail-on-risk`)
Sets a defensive safety policy. Available levels:
*   `none` (default): Exit code is not affected by safety warnings.
*   `low`: Fails if *any* hallucination risk is flagged or safety scans trigger warnings.
*   `medium`: Fails if *any* safety-focused test case fails.
*   `high`: Fails if more than 50% of the safety cases fail.

```bash
agentaudit run tests/ --fail-on-risk medium
```
