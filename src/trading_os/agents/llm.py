"""Provider-neutral structured ``LLMRole`` seam.

Only :mod:`trading_os.agents.providers` adapters know a provider's API. This
module defines the owned types that cross the harness seam (spec §10): a typed
:class:`StructuredInvocation` carrying an immutable role and prompt release,
trusted instruction context, references to untrusted source records, the caller's
Pydantic output schema, an invocation budget, the allowed capability names, and a
``replay_key``; and a typed result that is either a validated
:class:`StructuredResult` or a typed :class:`ExpectedLLMFailure`.

The seam is provider-swappable: unsupported capability combinations fail closed
as ``ExpectedLLMFailure(kind="unsupported")`` and hosted/provider-owned tools are
never requested. Offline tests replace the adapter with :class:`FixtureLLMRole`,
which returns recorded results keyed by ``replay_key`` and never touches a
network or credential.
"""

from typing import Generic, Literal, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)

# Capability names the domain tracer may legitimately request. Anything outside
# this set (hosted web search, code execution, file search, provider memory, ...)
# fails closed rather than reaching a provider.
ALLOWED_CAPABILITY_NAMES: frozenset[str] = frozenset({"source_record_query"})


class StructuredInvocation(BaseModel, Generic[T], frozen=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    invocation_id: str
    role: str
    prompt_release_id: str
    trusted_context: dict[str, str]
    source_record_ids: tuple[str, ...]
    output_type: type[T]
    allowed_capability_names: tuple[str, ...]
    max_tokens: int = Field(ge=1)
    replay_key: str


class StructuredResult(BaseModel, Generic[T], frozen=True):
    output: T
    provider: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    finish_reason: str
    replay_key: str


class ExpectedLLMFailure(BaseModel, frozen=True):
    kind: Literal["timeout", "refusal", "unsupported", "malformed_output", "budget"]
    retryable: bool


def unsupported_capabilities(
    invocation: StructuredInvocation[T],
) -> tuple[str, ...]:
    """Return requested capability names that are not owned/allowed."""

    return tuple(
        name
        for name in invocation.allowed_capability_names
        if name not in ALLOWED_CAPABILITY_NAMES
    )


class LLMRole(Protocol):
    async def invoke(
        self, invocation: StructuredInvocation[T]
    ) -> StructuredResult[T] | ExpectedLLMFailure: ...


class FixtureLLMRole:
    """Deterministic offline adapter keyed by ``replay_key``.

    Recorded results are either a Pydantic model of the invocation's output type
    (yielding a :class:`StructuredResult`) or an :class:`ExpectedLLMFailure`. An
    unknown key, or a recorded model whose type mismatches the requested schema,
    is treated as a malformed-output expected failure rather than raising.
    """

    def __init__(
        self, results: dict[str, BaseModel | ExpectedLLMFailure]
    ) -> None:
        self._results = dict(results)

    async def invoke(
        self, invocation: StructuredInvocation[T]
    ) -> StructuredResult[T] | ExpectedLLMFailure:
        if unsupported_capabilities(invocation):
            return ExpectedLLMFailure(kind="unsupported", retryable=False)
        recorded = self._results.get(invocation.replay_key)
        if recorded is None:
            return ExpectedLLMFailure(kind="malformed_output", retryable=False)
        if isinstance(recorded, ExpectedLLMFailure):
            return recorded
        if not isinstance(recorded, invocation.output_type):
            return ExpectedLLMFailure(kind="malformed_output", retryable=False)
        return StructuredResult[T](
            output=recorded,
            provider="fixture",
            model="fixture",
            input_tokens=0,
            output_tokens=0,
            finish_reason="stop",
            replay_key=invocation.replay_key,
        )
