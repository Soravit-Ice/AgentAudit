import os
import tempfile

import yaml
from typer.testing import CliRunner

from agentaudit.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "AgentAudit v" in result.stdout


def test_cli_init() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        orig_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            result = runner.invoke(app, ["init"])
            assert result.exit_code == 0
            assert os.path.exists("agentaudit.yml")
            assert os.path.exists("tests/basic.yml")
        finally:
            os.chdir(orig_cwd)


def test_cli_run_mock() -> None:
    suite_data = {
        "name": "cli-smoke-suite",
        "target": {"type": "mock"},
        "cases": [{"id": "c1", "input": "hello"}],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "smoke.yml")
        with open(test_file, "w", encoding="utf-8") as f:
            yaml.dump(suite_data, f, default_flow_style=False)

        # Run smoke test case
        result = runner.invoke(app, ["run", test_file, "-o", os.path.join(temp_dir, "reports")])
        assert result.exit_code == 0
        assert "cli-smoke-suite" in result.stdout
        assert "PASSED" in result.stdout
