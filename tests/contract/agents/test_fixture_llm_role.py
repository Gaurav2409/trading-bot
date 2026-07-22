"""Fixture ``LLMRole`` adapter satisfies the provider-neutral contract."""

from tests.contract.agents.llm_role_contract import (
    MALFORMED_KEY,
    REFUSAL_KEY,
    TIMEOUT_KEY,
    VALID_KEY,
    VALID_OUTPUT,
    LLMRoleContract,
)

from trading_os.agents.llm import ExpectedLLMFailure, FixtureLLMRole, LLMRole


def _fixture_role() -> FixtureLLMRole:
    return FixtureLLMRole(
        results={
            VALID_KEY: VALID_OUTPUT,
            MALFORMED_KEY: ExpectedLLMFailure(kind="malformed_output", retryable=False),
            REFUSAL_KEY: ExpectedLLMFailure(kind="refusal", retryable=False),
            TIMEOUT_KEY: ExpectedLLMFailure(kind="timeout", retryable=True),
        }
    )


class TestFixtureLLMRoleContract(LLMRoleContract):
    def build_role(self) -> LLMRole:
        return _fixture_role()


async def test_missing_replay_key_is_malformed_failure() -> None:
    role = FixtureLLMRole(results={})
    from tests.contract.agents.llm_role_contract import invocation_for

    result = await role.invoke(invocation_for(VALID_KEY))
    assert result == ExpectedLLMFailure(kind="malformed_output", retryable=False)


async def test_fixture_reports_fixture_provider() -> None:
    from tests.contract.agents.llm_role_contract import invocation_for

    from trading_os.agents.llm import StructuredResult

    result = await _fixture_role().invoke(invocation_for(VALID_KEY))
    assert isinstance(result, StructuredResult)
    assert result.provider == "fixture"
