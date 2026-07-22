from trading_os.decision.models import EligibilityDecision, EligibilityInput


def decide_eligibility(value: EligibilityInput) -> EligibilityDecision:
    """Deterministic eligibility with no agent-provided number. A candidate is
    eligible only if it is on the account-specific tradable allowlist and the
    current portfolio gate allows new exposure."""
    reasons: list[str] = []
    if not value.on_tradable_allowlist:
        reasons.append("not_on_tradable_allowlist")
    if not value.portfolio_gate_allows:
        reasons.append("portfolio_gate_blocks")
    return EligibilityDecision(eligible=not reasons, reason_codes=tuple(reasons))
