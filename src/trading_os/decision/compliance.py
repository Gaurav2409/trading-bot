from pydantic import BaseModel


class ComplianceDecision(BaseModel, frozen=True):
    outcome: str  # allow | shrink | veto | reduce_only
    reason: str


class IndiaComplianceInput(BaseModel, frozen=True):
    static_ip_ready: bool
    algorithm_tag_ready: bool
    settled_cash_sufficient: bool
    order_rate_last_second: int
    max_orders_per_second: int
    instrument_allowed: bool


def evaluate_india(value: IndiaComplianceInput) -> ComplianceDecision:
    """Deterministic India cash-equity compliance. Fails closed; never assumes
    algo market orders are permitted (the order-type enum has no MARKET)."""
    if not value.instrument_allowed:
        return ComplianceDecision(outcome="veto", reason="instrument_not_allowed")
    if not value.static_ip_ready:
        return ComplianceDecision(outcome="veto", reason="static_ip_not_ready")
    if not value.algorithm_tag_ready:
        return ComplianceDecision(outcome="veto", reason="algorithm_tag_not_ready")
    if not value.settled_cash_sufficient:
        return ComplianceDecision(outcome="veto", reason="settled_cash_insufficient")
    if value.order_rate_last_second >= value.max_orders_per_second:
        return ComplianceDecision(outcome="veto", reason="order_rate_exceeded")
    return ComplianceDecision(outcome="allow", reason="all_clear")


class UsComplianceInput(BaseModel, frozen=True):
    trading_blocked: bool
    account_blocked: bool
    trade_suspended_by_user: bool
    buying_power_minor: int
    required_minor: int
    asset_tradable: bool
    data_entitlement_ready: bool
    pdt_round_trips_used: int
    pdt_round_trip_budget: int


def evaluate_us(value: UsComplianceInput) -> ComplianceDecision:
    """Deterministic Alpaca cash-equity compliance. Reads account flags and the
    same-day round-trip budget dynamically; never assumes unrestricted intraday
    exits."""
    if value.trading_blocked:
        return ComplianceDecision(outcome="veto", reason="trading_blocked")
    if value.account_blocked:
        return ComplianceDecision(outcome="veto", reason="account_blocked")
    if value.trade_suspended_by_user:
        return ComplianceDecision(outcome="veto", reason="trade_suspended_by_user")
    if not value.asset_tradable:
        return ComplianceDecision(outcome="veto", reason="asset_not_tradable")
    if not value.data_entitlement_ready:
        return ComplianceDecision(outcome="veto", reason="data_entitlement_not_ready")
    if value.buying_power_minor < value.required_minor:
        return ComplianceDecision(outcome="veto", reason="insufficient_buying_power")
    if value.pdt_round_trips_used >= value.pdt_round_trip_budget:
        return ComplianceDecision(outcome="veto", reason="pdt_budget_exhausted")
    return ComplianceDecision(outcome="allow", reason="all_clear")
