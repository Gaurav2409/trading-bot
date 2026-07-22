from trading_os.app.readiness import build_readiness_report


def _alpaca_kwargs(**overrides: object) -> dict[str, object]:
    base = dict(
        account_hash="hash-alpaca",
        broker="alpaca",
        environment="live",
        credential_ready=True,
        static_ip_ready=True,  # not required for Alpaca but recorded
        tagging_ready=True,
        data_entitlement_ready=True,
        account_flags_ok=True,
        instrument_mapping_ready=True,
        compliance_profile_fresh=True,
        capital_release_id="alpaca-capital-1",
        exposure_release_id="alpaca-exposure-t0",
        promotion_release_id="alpaca-promotion-t0",
        portfolio_complete=True,
        reconciled=True,
        kill_switch_exercised=True,
        protection_protocol_exercised=True,
        endpoint_identity_ok=True,
        test_manifest_hash="sha256:tests",
        operator_approved=True,
    )
    base.update(overrides)
    return base


def test_alpaca_readiness_passes() -> None:
    report = build_readiness_report(**_alpaca_kwargs())  # type: ignore[arg-type]
    assert report.passed is True


def test_missing_data_entitlement_fails_alpaca_readiness() -> None:
    report = build_readiness_report(**_alpaca_kwargs(data_entitlement_ready=False))  # type: ignore[arg-type]
    assert report.passed is False
    assert "data_entitlement_ready" in report.failed_items


def test_one_broker_blocked_does_not_weaken_the_other() -> None:
    kite_ok = build_readiness_report(
        account_hash="hash-kite",
        broker="kite",
        environment="live",
        credential_ready=True,
        static_ip_ready=True,
        tagging_ready=True,
        data_entitlement_ready=True,
        account_flags_ok=True,
        instrument_mapping_ready=True,
        compliance_profile_fresh=True,
        capital_release_id="capital-1",
        exposure_release_id="exposure-t0",
        promotion_release_id="promotion-t0",
        portfolio_complete=True,
        reconciled=True,
        kill_switch_exercised=True,
        protection_protocol_exercised=True,
        endpoint_identity_ok=True,
        test_manifest_hash="sha256:tests",
        operator_approved=True,
    )
    alpaca_blocked = build_readiness_report(**_alpaca_kwargs(credential_ready=False))  # type: ignore[arg-type]
    assert kite_ok.passed is True
    assert alpaca_blocked.passed is False
    assert "credential_ready" in alpaca_blocked.failed_items
