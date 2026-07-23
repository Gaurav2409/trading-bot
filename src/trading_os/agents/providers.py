"""Provider adapters behind the one provider-neutral ``LLMRole`` seam.

``OpenAILLMRole`` and ``AnthropicLLMRole`` are the only code in the tracer that
knows a provider's API (spec §10). Each accepts an injected async client so
offline tests inject a fake and no code path reads credentials or opens a
socket. Both:

- request structured output only and never advertise hosted/provider-owned
  tools (web, fetch, code execution, memory, file search);
- fail closed with ``ExpectedLLMFailure(kind="unsupported")`` when the caller
  requests a capability outside the owned allowlist;
- set the strictest supported provider tracing / data-retention controls
  (``store=False``, no server-side prompt logging) so no prompt or output is
  retained by the provider;
- normalize usage to ``input_tokens`` / ``output_tokens``;
- map SDK timeouts, refusals, and malformed structured output to a typed
  :class:`ExpectedLLMFailure` rather than raising across the seam.
"""

from typing import Any, Protocol, TypeVar

import anthropic
import openai
from pydantic import BaseModel, ValidationError

from trading_os.agents.llm import (
    ExpectedLLMFailure,
    StructuredInvocation,
    StructuredResult,
    unsupported_capabilities,
)

T = TypeVar("T", bound=BaseModel)

_STRUCTURED_TOOL_NAME = "emit_structured_output"


class _OpenAIResponsesClient(Protocol):
    responses: Any


class _AnthropicMessagesClient(Protocol):
    messages: Any


def _prompt_text(invocation: StructuredInvocation[T]) -> str:
    """Flatten trusted instruction context into a single deterministic string.

    Untrusted source text is never inlined here; the model reaches sealed source
    records only through node-scoped read-only capability proxies.
    """

    return "\n".join(
        f"{key}: {value}" for key, value in sorted(invocation.trusted_context.items())
    )


class OpenAILLMRole:
    """OpenAI adapter using the Responses structured-parse surface."""

    provider = "openai"

    def __init__(self, *, client: _OpenAIResponsesClient, model: str) -> None:
        self._client = client
        self._model = model

    async def invoke(
        self, invocation: StructuredInvocation[T]
    ) -> StructuredResult[T] | ExpectedLLMFailure:
        if unsupported_capabilities(invocation):
            return ExpectedLLMFailure(kind="unsupported", retryable=False)
        try:
            response = await self._client.responses.parse(
                model=self._model,
                input=_prompt_text(invocation),
                text_format=invocation.output_type,
                max_output_tokens=invocation.max_tokens,
                tools=[],
                store=False,
                metadata={"replay_key": invocation.replay_key},
            )
        except openai.APITimeoutError:
            return ExpectedLLMFailure(kind="timeout", retryable=True)
        except openai.APIError:
            return ExpectedLLMFailure(kind="refusal", retryable=False)

        if getattr(response, "refusal", None):
            return ExpectedLLMFailure(kind="refusal", retryable=False)
        parsed = getattr(response, "output_parsed", None)
        if not isinstance(parsed, invocation.output_type):
            return ExpectedLLMFailure(kind="malformed_output", retryable=False)
        usage = getattr(response, "usage", None)
        return StructuredResult[T](
            output=parsed,
            provider=self.provider,
            model=self._model,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
            finish_reason=str(getattr(response, "status", "completed")),
            replay_key=invocation.replay_key,
        )


class AnthropicLLMRole:
    """Anthropic adapter forcing structured tool-use output only."""

    provider = "anthropic"

    def __init__(self, *, client: _AnthropicMessagesClient, model: str) -> None:
        self._client = client
        self._model = model

    def _tool_spec(self, invocation: StructuredInvocation[T]) -> dict[str, Any]:
        return {
            "name": _STRUCTURED_TOOL_NAME,
            "description": "Emit the required structured evidence output.",
            "input_schema": invocation.output_type.model_json_schema(),
        }

    async def invoke(
        self, invocation: StructuredInvocation[T]
    ) -> StructuredResult[T] | ExpectedLLMFailure:
        if unsupported_capabilities(invocation):
            return ExpectedLLMFailure(kind="unsupported", retryable=False)
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=invocation.max_tokens,
                messages=[{"role": "user", "content": _prompt_text(invocation)}],
                tools=[self._tool_spec(invocation)],
                tool_choice={"type": "tool", "name": _STRUCTURED_TOOL_NAME},
                metadata={"replay_key": invocation.replay_key},
            )
        except anthropic.APITimeoutError:
            return ExpectedLLMFailure(kind="timeout", retryable=True)
        except anthropic.APIError:
            return ExpectedLLMFailure(kind="refusal", retryable=False)

        if getattr(message, "stop_reason", None) == "refusal":
            return ExpectedLLMFailure(kind="refusal", retryable=False)

        payload: dict[str, Any] | None = None
        for block in getattr(message, "content", []) or []:
            if getattr(block, "type", None) == "tool_use" and (
                getattr(block, "name", None) == _STRUCTURED_TOOL_NAME
            ):
                payload = getattr(block, "input", None)
                break
        if payload is None:
            return ExpectedLLMFailure(kind="malformed_output", retryable=False)
        try:
            parsed = invocation.output_type.model_validate(payload)
        except ValidationError:
            return ExpectedLLMFailure(kind="malformed_output", retryable=False)

        usage = getattr(message, "usage", None)
        return StructuredResult[T](
            output=parsed,
            provider=self.provider,
            model=self._model,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
            finish_reason=str(getattr(message, "stop_reason", "end_turn")),
            replay_key=invocation.replay_key,
        )
