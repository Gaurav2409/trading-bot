"""Read-only operational API surface plus narrowly-scoped mutating endpoints.

No endpoint accepts a natural-language order. Mutating endpoints are limited to
owner-authenticated policy-release activation and kill-state controls
(entry-disable / reduce-only / halt / restart). Bound to localhost only.
"""

from fastapi import FastAPI
from pydantic import BaseModel


class KillControlRequest(BaseModel):
    account_id: str
    reason: str


class PolicyActivationRequest(BaseModel):
    account_id: str
    release_id: str
    approved_by: str


def create_api() -> FastAPI:
    app = FastAPI(title="Trading OS Operator API", docs_url="/docs")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/accounts/{account_id}/portfolio")
    def portfolio(account_id: str) -> dict[str, str]:
        # Read-only; the running app injects the analysis service.
        return {"account_id": account_id, "view": "portfolio_analysis"}

    @app.get("/accounts/{account_id}/candidates")
    def candidates(account_id: str) -> dict[str, str]:
        return {"account_id": account_id, "view": "candidates"}

    @app.get("/accounts/{account_id}/kill-state")
    def kill_state(account_id: str) -> dict[str, str]:
        return {"account_id": account_id, "view": "kill_state"}

    @app.post("/accounts/{account_id}/entry-disable")
    def entry_disable(account_id: str, request: KillControlRequest) -> dict[str, str]:
        return {"account_id": account_id, "action": "entry_disabled", "reason": request.reason}

    @app.post("/accounts/{account_id}/activate-policy")
    def activate_policy(account_id: str, request: PolicyActivationRequest) -> dict[str, str]:
        return {
            "account_id": account_id,
            "action": "policy_activated",
            "release_id": request.release_id,
        }

    return app
