import json
from hashlib import sha256

from pydantic import BaseModel

# Required boolean readiness items. Any False prevents receipt issuance.
_REQUIRED_BOOLS = (
    "credential_ready",
    "static_ip_ready",
    "tagging_ready",
    "data_entitlement_ready",
    "account_flags_ok",
    "instrument_mapping_ready",
    "compliance_profile_fresh",
    "portfolio_complete",
    "reconciled",
    "kill_switch_exercised",
    "protection_protocol_exercised",
    "endpoint_identity_ok",
    "operator_approved",
)


class ReadinessReport(BaseModel, frozen=True):
    account_hash: str
    broker: str
    environment: str
    capital_release_id: str
    exposure_release_id: str
    promotion_release_id: str
    test_manifest_hash: str
    passed: bool
    failed_items: tuple[str, ...]
    report_hash: str


def build_readiness_report(
    *,
    account_hash: str,
    broker: str,
    environment: str,
    credential_ready: bool,
    static_ip_ready: bool,
    tagging_ready: bool,
    data_entitlement_ready: bool,
    account_flags_ok: bool,
    instrument_mapping_ready: bool,
    compliance_profile_fresh: bool,
    capital_release_id: str,
    exposure_release_id: str,
    promotion_release_id: str,
    portfolio_complete: bool,
    reconciled: bool,
    kill_switch_exercised: bool,
    protection_protocol_exercised: bool,
    endpoint_identity_ok: bool,
    test_manifest_hash: str,
    operator_approved: bool,
) -> ReadinessReport:
    values = {
        "credential_ready": credential_ready,
        "static_ip_ready": static_ip_ready,
        "tagging_ready": tagging_ready,
        "data_entitlement_ready": data_entitlement_ready,
        "account_flags_ok": account_flags_ok,
        "instrument_mapping_ready": instrument_mapping_ready,
        "compliance_profile_fresh": compliance_profile_fresh,
        "portfolio_complete": portfolio_complete,
        "reconciled": reconciled,
        "kill_switch_exercised": kill_switch_exercised,
        "protection_protocol_exercised": protection_protocol_exercised,
        "endpoint_identity_ok": endpoint_identity_ok,
        "operator_approved": operator_approved,
    }
    failed = tuple(name for name in _REQUIRED_BOOLS if not values[name])

    manifest = {
        "account_hash": account_hash,
        "broker": broker,
        "environment": environment,
        "capital_release_id": capital_release_id,
        "exposure_release_id": exposure_release_id,
        "promotion_release_id": promotion_release_id,
        "test_manifest_hash": test_manifest_hash,
        "items": values,
    }
    digest = sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    return ReadinessReport(
        account_hash=account_hash,
        broker=broker,
        environment=environment,
        capital_release_id=capital_release_id,
        exposure_release_id=exposure_release_id,
        promotion_release_id=promotion_release_id,
        test_manifest_hash=test_manifest_hash,
        passed=not failed,
        failed_items=failed,
        report_hash=f"sha256:{digest}",
    )
