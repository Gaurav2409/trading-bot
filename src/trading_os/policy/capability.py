from pydantic import BaseModel


class ExecutionContext(BaseModel, frozen=True):
    capability_release_id: str | None
    account_assignment: str | None
    mandate_active: bool
    compliance_effective: bool
    entitlement_ready: bool
    broker_ready: bool
    portfolio_reconciled: bool
    kill_generation_matches: bool
    uses_semantic_features: bool
    semantic_activation: str | None


class AuthorityDecision(BaseModel, frozen=True):
    allowed: bool
    reason: str


class ExecutionAuthority:
    """Deny-by-default intersection of independent AND-gates. Semantic activation
    is required only when semantic features influence the decision; product
    execution capability never implies semantic activation, and vice versa."""

    def evaluate(self, context: ExecutionContext) -> AuthorityDecision:
        checks = (
            (context.capability_release_id is not None, "capability_release_missing"),
            (context.account_assignment is not None, "account_capability_missing"),
            (context.mandate_active, "mandate_inactive"),
            (context.compliance_effective, "compliance_inactive"),
            (context.entitlement_ready, "data_entitlement_not_ready"),
            (context.broker_ready, "broker_not_ready"),
            (context.portfolio_reconciled, "portfolio_not_reconciled"),
            (context.kill_generation_matches, "kill_generation_stale"),
            (
                not context.uses_semantic_features or context.semantic_activation is not None,
                "semantic_activation_missing",
            ),
        )
        for passed, reason in checks:
            if not passed:
                return AuthorityDecision(allowed=False, reason=reason)
        return AuthorityDecision(allowed=True, reason="all_authorities_effective")
