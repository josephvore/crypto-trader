from typer.testing import CliRunner

from crypto_trader import cli

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0
    assert "Crypto-Trader CLI" in result.stdout
