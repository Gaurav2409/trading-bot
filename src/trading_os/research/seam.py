"""Categorical evidence-seam vocabulary and executable-number rejection (spec §4, §16).

The primary constitutional invariant of the domain-agent architecture is that
**no executable number crosses the evidence seam**: no price, quantity, target,
expected return, position weight, conviction multiplier, or order intent may
reach an :class:`EvidencePacket`. Numeric intermediates stay internal.

Enforcement is a *closed-vocabulary allowlist* on the packet ``assessment`` plus
an executable-number rejection over the assessment string. An allowlist is the
correct shape (not a blocklist of field-name words): a model-authored assessment
such as ``"agent_2500"`` or ``"ret_18pct"`` carries a bare number yet contains
none of the forbidden English words, so a substring blocklist fails open. The
allowlist admits only the finite set of categorical assessments the reasoning
layer is permitted to emit and rejects everything else — including any string
bearing a standalone numeric run.

This lives in the research layer because the evidence seam is a research-layer
concept: ``admit_packet`` (the idempotent defence at the port boundary that no
node path can bypass) calls it, and the agents layer imports it for early typed
rejection at the categorical-seam node.
"""

import re

from trading_os.research.models import EvidenceDomain

# --- closed categorical assessment vocabulary --------------------------------

# corporate_event domain outcomes (spec §16, §15).
_CORPORATE_EVENT_ASSESSMENTS: frozenset[str] = frozenset(
    {
        "material_event_supported",
        "material_event_supported_degraded",
        "missing_applicable_official_sources",
        "contradictory_official_sources",
    }
)

# Expected-failure assessments shared across every domain: an expected model,
# tool, or budget failure becomes an admitted explicit-missing packet so the
# relational champion is never disabled (spec §16, constraint 4). These are
# authored by the harness, never by a model.
_FAILURE_ASSESSMENTS: frozenset[str] = frozenset(
    {
        "agent_provider_timeout",
        "agent_provider_refusal",
        "agent_capability_unsupported",
        "agent_malformed_output",
        "agent_budget_exhausted",
        "agent_profile_unavailable",
        "categorical_seam_violation",
    }
)

# Registered per-domain categorical vocabularies. A domain absent here has no
# admitted categorical assessment yet, so any assessment for it fails closed.
_DOMAIN_ASSESSMENTS: dict[EvidenceDomain, frozenset[str]] = {
    EvidenceDomain.CORPORATE_EVENT: _CORPORATE_EVENT_ASSESSMENTS,
}

# Executable-number field names that must never appear as a token anywhere in a
# categorical artifact (spec §4).
_FORBIDDEN_SEAM_TOKENS: frozenset[str] = frozenset(
    {
        "price",
        "quantity",
        "target",
        "target_price",
        "expected_return",
        "position_weight",
        "conviction",
        "conviction_multiplier",
        "order_intent",
        "notional",
    }
)

# Any digit. Applied ONLY to the closed-vocabulary ``assessment`` field (record
# IDs legitimately contain digits, e.g. ``sec:1``, so this is never applied to
# citations). A categorical assessment never carries a digit.
_NUMERIC_RUN = re.compile(r"\d")


class CategoricalSeamViolation(RuntimeError):
    """An executable number, an unknown assessment, or a forbidden token reached
    the evidence seam."""


def allowed_assessments(domain: EvidenceDomain) -> frozenset[str]:
    """The closed set of categorical assessments admissible for ``domain``."""

    return _DOMAIN_ASSESSMENTS.get(domain, frozenset()) | _FAILURE_ASSESSMENTS


def reject_forbidden_token(value: str) -> None:
    """Raise if ``value`` contains an executable-number field-name token."""

    lowered = value.lower()
    for forbidden in _FORBIDDEN_SEAM_TOKENS:
        if forbidden in lowered:
            raise CategoricalSeamViolation(
                f"executable-number token {forbidden!r} reached the seam"
            )


def assert_categorical_assessment(domain: EvidenceDomain, assessment: str) -> None:
    """Enforce the closed-vocabulary allowlist and numeric-run rejection on a
    packet assessment.

    Raises :class:`CategoricalSeamViolation` if the assessment carries any digit
    (a smuggled executable number the allowlist would not name) or is not a
    registered categorical value for the domain.
    """

    if _NUMERIC_RUN.search(assessment) is not None:
        raise CategoricalSeamViolation(
            f"assessment {assessment!r} carries a numeric run — not categorical"
        )
    reject_forbidden_token(assessment)
    if assessment not in allowed_assessments(domain):
        raise CategoricalSeamViolation(
            f"assessment {assessment!r} is not in the closed categorical "
            f"vocabulary for domain {domain}"
        )
