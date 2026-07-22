"""Anthropic ``LLMRole`` adapter satisfies the provider-neutral contract.

Uses a fake injected async client; no network, no credentials. The fake mimics
the Anthropic Messages tool-use surface the adapter depends on and raises real
SDK exceptions so failure classification is exercised.
"""

from typing import Any

import anthropic
import httpx
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
from trading_os.agents.providers import AnthropicLLMRole

MODEL = "claude-fixture"


class _Usage:
    def __init__(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _ToolUseBlock:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.type = "tool_use"
        self.name = "emit_structured_output"
        self.input = payload


class _TextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Message:
    def __init__(self, content: list[Any], *, stop_reason: str) -> None:
        self.content = content
        self.stop_reason = stop_reason
        self.usage = _Usage(13, 5)


class _FakeMessages:
    async def create(self, **kwargs: Any) -> _Message:
        replay_key = kwargs["metadata"]["replay_key"]
        # The adapter forces structured tool output only; no hosted tools.
        tool_names = {tool["name"] for tool in kwargs.get("tools", [])}
        assert tool_names <= {"emit_structured_output"}
        if replay_key == VALID_KEY:
            return _Message(
                [_ToolUseBlock(VALID_OUTPUT.model_dump())], stop_reason="tool_use"
            )
        if replay_key == MALFORMED_KEY:
            return _Message(
                [_ToolUseBlock({"event_type": "x"})], stop_reason="tool_use"
            )
        if replay_key == REFUSAL_KEY:
            return _Message([_TextBlock("I can't help.")], stop_reason="refusal")
        if replay_key == TIMEOUT_KEY:
            raise anthropic.APITimeoutError(request=httpx.Request("POST", "http://x"))
        raise AssertionError(f"unexpected replay key {replay_key!r}")


class _FakeAnthropicClient:
    def __init__(self) -> None:
        self.messages = _FakeMessages()


class TestAnthropicLLMRoleContract(LLMRoleContract):
    def build_role(self) -> LLMRole:
        return AnthropicLLMRole(client=_FakeAnthropicClient(), model=MODEL)


async def test_anthropic_reports_provider_and_model() -> None:
    role = AnthropicLLMRole(client=_FakeAnthropicClient(), model=MODEL)
    result = await role.invoke(invocation_for(VALID_KEY))
    assert isinstance(result, StructuredResult)
    assert result.provider == "anthropic"
    assert result.model == MODEL
    assert result.input_tokens == 13
    assert result.output_tokens == 5


async def test_anthropic_output_matches_schema() -> None:
    role = AnthropicLLMRole(client=_FakeAnthropicClient(), model=MODEL)
    result = await role.invoke(invocation_for(VALID_KEY))
    assert isinstance(result, StructuredResult)
    assert isinstance(result.output, EventExtraction)


async def test_anthropic_unsupported_capability_fails_closed() -> None:
    role = AnthropicLLMRole(client=_FakeAnthropicClient(), model=MODEL)
    result = await role.invoke(
        invocation_for(UNSUPPORTED_KEY, allowed_capability_names=("code_execution",))
    )
    assert result == ExpectedLLMFailure(kind="unsupported", retryable=False)


def test_anthropic_role_needs_no_credentials() -> None:
    assert isinstance(
        AnthropicLLMRole(client=_FakeAnthropicClient(), model=MODEL), AnthropicLLMRole
    )
    with pytest.raises(TypeError):
        AnthropicLLMRole()  # type: ignore[call-arg]
