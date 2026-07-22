from trading_os.policy.capability import ExecutionAuthority, ExecutionContext


def make_context(*, uses_semantic_features: bool) -> ExecutionContext:
    return ExecutionContext(
        capability_release_id="cash-equity-in-us-1",
        account_assignment="assignment-1",
        mandate_active=True,
        compliance_effective=True,
        entitlement_ready=True,
        broker_ready=True,
        portfolio_reconciled=True,
        kill_generation_matches=True,
        uses_semantic_features=uses_semantic_features,
        semantic_activation=None,
    )


def test_missing_account_capability_denies_live_write() -> None:
    context = make_context(uses_semantic_features=False).model_copy(
        update={"account_assignment": None}
    )
    decision = ExecutionAuthority().evaluate(context)
    assert decision.allowed is False
    assert decision.reason == "account_capability_missing"


def test_semantic_activation_is_required_only_when_semantic_features_are_used() -> None:
    baseline = make_context(uses_semantic_features=False)
    semantic = make_context(uses_semantic_features=True)
    assert ExecutionAuthority().evaluate(baseline).allowed is True
    assert ExecutionAuthority().evaluate(semantic).allowed is False


def test_all_authorities_effective_allows() -> None:
    ctx = make_context(uses_semantic_features=True).model_copy(
        update={"semantic_activation": "activation-1"}
    )
    assert ExecutionAuthority().evaluate(ctx).allowed is True


def test_stale_kill_generation_denies() -> None:
    ctx = make_context(uses_semantic_features=False).model_copy(
        update={"kill_generation_matches": False}
    )
    decision = ExecutionAuthority().evaluate(ctx)
    assert decision.allowed is False
    assert decision.reason == "kill_generation_stale"
