"""Reusable provider-neutral ``LLMRole`` contract suite.

Every ``LLMRole`` adapter (fixture, OpenAI, Anthropic) must satisfy the same
behavior at the harness seam (spec §10, §22): structured output validated
against the caller's Pydantic schema, typed :class:`ExpectedLLMFailure` for
refusal / timeout / malformed output / unsupported capability, no hosted or
provider-owned tools ever requested, normalized usage, and the invocation's
``replay_key`` echoed on the result so replay stays deterministic.

Subclass :class:`LLMRoleContract` and implement :meth:`build_role` to bind the
suite to a concrete adapter. The contract never touches the network and never
requires credentials: OpenAI/Anthropic subclasses inject fake async clients.
"""

from pydantic import BaseModel

from trading_os.agents.llm import (
    ExpectedLLMFailure,
    LLMRole,
    StructuredInvocation,
    StructuredResult,
)


class EventExtraction(BaseModel, frozen=True, extra="forbid"):
    event_type: str
    record_ids: tuple[str, ...]
    issuer_id: str


VALID_KEY = "replay:valid"
MALFORMED_KEY = "replay:malformed"
FABRICATED_FIELD_KEY = "replay:fabricated"
REFUSAL_KEY = "replay:refusal"
TIMEOUT_KEY = "replay:timeout"
UNSUPPORTED_KEY = "replay:unsupported"

VALID_OUTPUT = EventExtraction(
    event_type="material_agreement",
    record_ids=("sec:1",),
    issuer_id="issuer:1",
)


def invocation_for(
    replay_key: str,
    *,
    allowed_capability_names: tuple[str, ...] = ("source_record_query",),
) -> StructuredInvocation[EventExtraction]:
    return StructuredInvocation[EventExtraction](
        invocation_id=f"invocation:{replay_key}",
        role="gather",
        prompt_release_id="prompt:gather:v1",
        trusted_context={"instruction": "Extract the official corporate event."},
        source_record_ids=("sec:1",),
        output_type=EventExtraction,
        allowed_capability_names=allowed_capability_names,
        max_tokens=512,
        replay_key=replay_key,
    )


class LLMRoleContract:
    def build_role(self) -> LLMRole:
        raise NotImplementedError

    async def test_valid_structured_output(self) -> None:
        result = await self.build_role().invoke(invocation_for(VALID_KEY))
        assert isinstance(result, StructuredResult)
        assert isinstance(result.output, EventExtraction)
        assert result.output == VALID_OUTPUT

    async def test_result_echoes_replay_key_and_usage(self) -> None:
        result = await self.build_role().invoke(invocation_for(VALID_KEY))
        assert isinstance(result, StructuredResult)
        assert result.replay_key == VALID_KEY
        assert result.input_tokens >= 0
        assert result.output_tokens >= 0
        assert result.provider
        assert result.model

    async def test_malformed_output_is_expected_failure(self) -> None:
        result = await self.build_role().invoke(invocation_for(MALFORMED_KEY))
        assert result == ExpectedLLMFailure(kind="malformed_output", retryable=False)

    async def test_refusal_is_expected_failure(self) -> None:
        result = await self.build_role().invoke(invocation_for(REFUSAL_KEY))
        assert isinstance(result, ExpectedLLMFailure)
        assert result.kind == "refusal"

    async def test_timeout_is_retryable_expected_failure(self) -> None:
        result = await self.build_role().invoke(invocation_for(TIMEOUT_KEY))
        assert result == ExpectedLLMFailure(kind="timeout", retryable=True)

    async def test_hosted_tools_are_never_requested(self) -> None:
        request = invocation_for(VALID_KEY)
        assert request.allowed_capability_names == ("source_record_query",)
