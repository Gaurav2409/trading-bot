from trading_os.app.readiness import ReadinessReport, build_readiness_report


def _ready_kwargs(**overrides: object) -> dict[str, object]:
    base = dict(
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
    base.update(overrides)
    return base


def test_kite_readiness_passes_when_all_required_items_hold() -> None:
    report = build_readiness_report(**_ready_kwargs())  # type: ignore[arg-type]
    assert isinstance(report, ReadinessReport)
    assert report.passed is True
    assert report.report_hash.startswith("sha256:")


def test_missing_static_ip_fails_kite_readiness() -> None:
    report = build_readiness_report(**_ready_kwargs(static_ip_ready=False))  # type: ignore[arg-type]
    assert report.passed is False
    assert "static_ip_ready" in report.failed_items


def test_operator_approval_is_required() -> None:
    report = build_readiness_report(**_ready_kwargs(operator_approved=False))  # type: ignore[arg-type]
    assert report.passed is False
    assert "operator_approved" in report.failed_items
