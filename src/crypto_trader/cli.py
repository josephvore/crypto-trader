from rich.console import Console
from typer import Typer

from crypto_trader.core.app import App

app = Typer(help="Crypto-Trader CLI")
console = Console()


@app.callback(invoke_without_command=True)
def main() -> None:
    console.print("Crypto-Trader CLI")


@app.command()
def init() -> None:
    App().init_project()
    console.print("Initialized project")


@app.command()
def backtest(config: str) -> None:
    App().run_backtest(config_path=config)


@app.command()
def tune(config: str) -> None:
    App().run_tuning(config_path=config)


@app.command()
def paper(config: str) -> None:
    App().run_paper(config_path=config)


@app.command()
def live(config: str) -> None:
    App().run_live(config_path=config)


if __name__ == "__main__":
    app()
