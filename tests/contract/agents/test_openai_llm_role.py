"""OpenAI ``LLMRole`` adapter satisfies the provider-neutral contract.

Uses a fake injected async client; no network, no credentials. The fake mimics
the OpenAI Responses structured-parse surface the adapter depends on and raises
real SDK exceptions so the adapter's failure classification is exercised.
"""

from typing import Any

import httpx
import openai
import pytest

from tests.contract.agents.llm_role_contract import (
    MALFORMED_KEY,
    REFUSAL_KEY,
    TIMEOUT_KEY,
    UNSUPPORTED_KEY,
    VALID_KEY,
    VALID_OUTPUT,
    EventExtraction,
    LLMRoleContract,
    invocation_for,
)

from trading_os.agents.llm import ExpectedLLMFailure, LLMRole, StructuredResult
from trading_os.agents.providers import OpenAILLMRole

MODEL = "gpt-fixture"


class _Usage:
    def __init__(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _ParsedResponse:
    def __init__(
        self,
        output_parsed: Any,
        *,
        refusal: str | None = None,
        status: str = "completed",
    ) -> None:
        self.output_parsed = output_parsed
        self.refusal = refusal
        self.status = status
        self.usage = _Usage(11, 7)


class _FakeResponses:
    async def parse(self, **kwargs: Any) -> _ParsedResponse:
        replay_key = kwargs["metadata"]["replay_key"]
        # The adapter must never request hosted/provider-owned tools.
        assert "tools" not in kwargs or kwargs["tools"] in (None, [])
        if replay_key == VALID_KEY:
            return _ParsedResponse(VALID_OUTPUT)
        if replay_key == MALFORMED_KEY:
            return _ParsedResponse(None)  # parse produced no structured output
        if replay_key == REFUSAL_KEY:
            return _ParsedResponse(None, refusal="I can't help with that.")
        if replay_key == TIMEOUT_KEY:
            raise openai.APITimeoutError(request=httpx.Request("POST", "http://x"))
        raise AssertionError(f"unexpected replay key {replay_key!r}")


class _FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = _FakeResponses()


class TestOpenAILLMRoleContract(LLMRoleContract):
    def build_role(self) -> LLMRole:
        return OpenAILLMRole(client=_FakeOpenAIClient(), model=MODEL)


async def test_openai_reports_provider_and_model() -> None:
    role = OpenAILLMRole(client=_FakeOpenAIClient(), model=MODEL)
    result = await role.invoke(invocation_for(VALID_KEY))
    assert isinstance(result, StructuredResult)
    assert result.provider == "openai"
    assert result.model == MODEL
    assert result.input_tokens == 11
    assert result.output_tokens == 7


async def test_openai_output_matches_schema() -> None:
    role = OpenAILLMRole(client=_FakeOpenAIClient(), model=MODEL)
    result = await role.invoke(invocation_for(VALID_KEY))
    assert isinstance(result, StructuredResult)
    assert isinstance(result.output, EventExtraction)


async def test_openai_unsupported_capability_fails_closed() -> None:
    role = OpenAILLMRole(client=_FakeOpenAIClient(), model=MODEL)
    result = await role.invoke(
        invocation_for(UNSUPPORTED_KEY, allowed_capability_names=("web_search",))
    )
    assert result == ExpectedLLMFailure(kind="unsupported", retryable=False)


def test_openai_role_needs_no_credentials() -> None:
    # Construction with an injected client must not read env or open a socket.
    assert isinstance(OpenAILLMRole(client=_FakeOpenAIClient(), model=MODEL), OpenAILLMRole)
    with pytest.raises(TypeError):
        OpenAILLMRole()  # type: ignore[call-arg]
