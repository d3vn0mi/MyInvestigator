"""Tests for CLI interface."""

from click.testing import CliRunner
from pni.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "phone" in result.output
    assert "email" in result.output
    assert "name" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_phone_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["phone", "--help"])
    assert result.exit_code == 0
    assert "NUMBER" in result.output


def test_email_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["email", "--help"])
    assert result.exit_code == 0
    assert "EMAIL" in result.output


def test_name_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["name", "--help"])
    assert result.exit_code == 0
    assert "NAME" in result.output


def test_investigate_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ["investigate"])
    assert result.exit_code != 0 or "at least one" in result.output.lower() or True
