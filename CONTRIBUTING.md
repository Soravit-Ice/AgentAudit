# Contributing to AgentAudit

Thank you for your interest in contributing to **AgentAudit**! We welcome bug reports, feature requests, documentation enhancements, and pull requests.

Following these guidelines helps ensure a smooth contribution process for everyone.

---

## 1. Setting Up Your Development Environment

Ensure you have Python 3.11+ installed. Clone the repository and follow these setup steps:

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies in Editable Mode

Install all required run dependencies along with optional development tools:

```bash
make install
# Or: pip install -e ".[dev]"
```

---

## 2. Developer Workflow commands

We use a simple `Makefile` to automate common development workflows:

*   **Format Code**: Format files using `ruff` before committing.
    ```bash
    make format
    ```
*   **Lint Checks**: Verify syntax constraints.
    ```bash
    make lint
    ```
*   **Type Checking**: Run static type verification with `mypy`.
    ```bash
    make typecheck
    ```
*   **Run Unit Tests**: Execute tests and print coverage metrics.
    ```bash
    make test
    ```
*   **Run Basic Demo**: Run an evaluation suite using the CLI.
    ```bash
    make demo
    ```
*   **Build Package**: Compile source and wheel distributions.
    ```bash
    make build
    ```
*   **Clean Temp Data**: Clear local caches and compilation folders.
    ```bash
    make clean
    ```

---

## 3. Creating a Pull Request (PR)

1.  **Fork the repo** and create your branch from `main`:
    ```bash
    git checkout -b feature/my-awesome-improvement
    ```
2.  **Add test cases** inside the `tests/` directory to cover your implementation.
3.  Ensure all formatting, typing, and unit tests pass:
    ```bash
    make format
    make typecheck
    make test
    ```
4.  **Commit your changes** following clear commit messages.
5.  **Push to your fork** and submit a Pull Request to our main repository.

---

## 4. Good First Issue Ideas

If you're looking for place to start, check out these ideas:
- **Add adapter integrations**: Scaffold an Ollama or OpenAI target adapter.
- **Extend safety packs**: Write new test cases for adversarial roleplay or exfiltration patterns.
- **Improve report details**: Add SVG charts or toggle buttons to the HTML report.
