import pytest
from typer.testing import CliRunner
from bruno.cli.app import app

runner = CliRunner()

def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Bruno" in result.stdout

def test_index_help():
    result = runner.invoke(app, ["index", "--help"])
    assert result.exit_code == 0
    assert "add" in result.stdout
    assert "list" in result.stdout
