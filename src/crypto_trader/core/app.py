from crypto_trader.core.config import Settings


class App:
    def __init__(self) -> None:
        self.settings: Settings = Settings()

    def init_project(self) -> None:
        return

    def run_backtest(self, config_path: str) -> None:
        _ = config_path
        return

    def run_tuning(self, config_path: str) -> None:
        _ = config_path
        return

    def run_paper(self, config_path: str) -> None:
        _ = config_path
        return

    def run_live(self, config_path: str) -> None:
        _ = config_path
        return
