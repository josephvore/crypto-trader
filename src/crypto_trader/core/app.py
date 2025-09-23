from crypto_trader.core.config import Settings


class App:
    def __init__(self) -> None:
        self.settings: Settings = Settings()

    def init_project(self) -> None:
        pass

    def run_backtest(self, config_path: str) -> None:
        _ = config_path

    def run_tuning(self, config_path: str) -> None:
        _ = config_path

    def run_paper(self, config_path: str) -> None:
        _ = config_path

    def run_live(self, config_path: str) -> None:
        _ = config_path
