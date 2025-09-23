from crypto_trader.core.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.env == "development"
    assert s.api_port == 8080
