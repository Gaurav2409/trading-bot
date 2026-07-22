from trading_os.app.settings import Environment, Settings


def test_live_mode_is_disabled_by_default() -> None:
    settings = Settings(_env_file=None)
    assert settings.environment is Environment.DEVELOPMENT
    assert settings.live_mode_requested is False
    assert settings.database_url.startswith("postgresql+asyncpg://")
