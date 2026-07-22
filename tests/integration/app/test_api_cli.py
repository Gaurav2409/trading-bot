from fastapi.testclient import TestClient

from trading_os.app.api import create_api
from trading_os.app.cli import build_parser
from trading_os.app.scheduler import SchedulerPlan


def test_api_health_and_readonly_portfolio() -> None:
    client = TestClient(create_api())
    assert client.get("/health").json() == {"status": "ok"}
    body = client.get("/accounts/kite-1/portfolio").json()
    assert body["account_id"] == "kite-1"


def test_api_has_no_natural_language_order_endpoint() -> None:
    api = create_api()
    paths = {route.path for route in api.routes}  # type: ignore[attr-defined]
    assert not any("order" in p and "natural" in p for p in paths)
    # Mutating endpoints are limited to controls/policy activation.
    assert "/accounts/{account_id}/entry-disable" in paths
    assert "/accounts/{account_id}/activate-policy" in paths


def test_scheduler_plan_covers_all_clocks() -> None:
    plan = SchedulerPlan()
    assert plan.clocks() == {"discovery", "shortlist", "decision", "protection", "watcher"}


def test_cli_parser_exposes_readiness_and_controls() -> None:
    parser = build_parser()
    args = parser.parse_args(["readiness", "--all-accounts", "--read-only"])
    assert args.command == "readiness"
    assert args.all_accounts is True
