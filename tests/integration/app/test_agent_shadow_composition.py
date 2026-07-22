"""Shadow-only rollout: disabled by default and never wired without opt-in.

P0 remains shadow-only (spec §18). The application must not construct a domain
agent harness or any provider client unless shadow mode is *explicitly* enabled
in settings, and shadow mode must default to off. These tests bind at the
``Settings`` and container public surface only.
"""

from trading_os.app.container import TradingApp, build_shadow_agent_port
from trading_os.app.settings import Settings


def test_agent_shadow_mode_is_disabled_by_default() -> None:
    assert Settings().agent_shadow_enabled is False


def test_container_does_not_build_agent_when_shadow_disabled() -> None:
    settings = Settings(agent_shadow_enabled=False)
    assert build_shadow_agent_port(settings) is None


def test_container_declines_when_shadow_enabled_without_provider_credentials() -> None:
    # Even with shadow mode on, the container must not fabricate a live provider
    # client from absent credentials; it declines rather than reaching for the
    # network. Offline replay wiring is a separate, explicit composition path.
    settings = Settings(agent_shadow_enabled=True)
    assert settings.agent_provider_api_key is None
    assert build_shadow_agent_port(settings) is None


def test_trading_app_still_constructs_without_agent() -> None:
    # The relational champion (the existing app) must remain fully operable
    # regardless of shadow-agent configuration.
    app = TradingApp(event_store=object(), live_writes_enabled=False)  # type: ignore[arg-type]
    assert app is not None
