# Quickstart Guide

This guide will help you install AgentAudit and run your very first AI agent evaluation in under 5 minutes.

---

## 1. Requirements

Ensure you have the following installed on your machine:
*   Python 3.11 or newer
*   pip (Python Package Installer)

---

## 2. Installation

Install AgentAudit locally by running:

```bash
pip install -e .
```

To verify the installation worked correctly, run:

```bash
agentaudit version
```

This should print:
```text
AgentAudit v0.1.0
```

---

## 3. Workspace Initialization

Run the `init` command to automatically bootstrap a default configuration and sample test suite in your current directory:

```bash
agentaudit init
```

This scaffolds two files:
1.  `agentaudit.yml` - Contains default suite parameters (such as `output_dir` and threshold rules).
2.  `tests/basic.yml` - A basic YAML test suite targeting a simulated (mock) chatbot.

---

## 4. Run Your First Evaluation

Execute the test runner on the created sample suite:

```bash
agentaudit run tests/basic.yml
```

AgentAudit will run the cases, evaluate the outputs against standard assertions, detect safety indicators, and display a report dashboard directly on your terminal.

---

## 5. Review Generated Reports

Evals generate multi-format files saved under your configured output directory (`reports/` by default):
*   **JSON Report (`reports/report_basic_mock_test.json`)**: Contains raw structured test outcomes.
*   **Markdown Report (`reports/report_basic_mock_test.md`)**: Perfect for printing summaries inside GitHub Action logs or pull request logs.
*   **HTML Report (`reports/report_basic_mock_test.html`)**: Open this file in your browser to explore a beautiful, responsive, and interactive dashboard showing individual assertions, latencies, chat history dialogs, and RAG document citations.
