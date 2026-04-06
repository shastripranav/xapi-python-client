from __future__ import annotations

import asyncio

from .client import XAPIClient
from .models import Statement
from .models.statement import StatementResult


class SyncXAPIClient:
    """Synchronous wrapper around XAPIClient for non-async contexts.

    Every method delegates to the async client via asyncio.run().
    Not suitable for use inside an already-running event loop —
    use the async XAPIClient directly in those environments.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        self._async = XAPIClient(
            endpoint=endpoint, username=username, password=password, **kwargs
        )

    def _run(self, coro):
        return asyncio.run(coro)

    def send_statement(self, statement: Statement) -> str:
        return self._run(self._async.send_statement(statement))

    def send_statements(self, statements: list[Statement]) -> list[str]:
        return self._run(self._async.send_statements(statements))

    def get_statement(self, statement_id: str) -> Statement:
        return self._run(self._async.get_statement(statement_id))

    def get_statements(self, **kwargs) -> StatementResult:
        return self._run(self._async.get_statements(**kwargs))

    def get_all_statements(self, **kwargs) -> list[Statement]:
        return self._run(self._async.get_all_statements(**kwargs))

    def set_state(
        self, activity_id: str, agent_email: str, state_id: str, data: dict, **kwargs
    ) -> None:
        return self._run(
            self._async.set_state(activity_id, agent_email, state_id, data, **kwargs)
        )

    def get_state(
        self, activity_id: str, agent_email: str, state_id: str, **kwargs
    ) -> dict | None:
        return self._run(
            self._async.get_state(activity_id, agent_email, state_id, **kwargs)
        )

    def delete_state(
        self, activity_id: str, agent_email: str, state_id: str, **kwargs
    ) -> None:
        return self._run(
            self._async.delete_state(activity_id, agent_email, state_id, **kwargs)
        )

    def get_activity_profile(
        self, activity_id: str, profile_id: str
    ) -> dict | None:
        return self._run(
            self._async.get_activity_profile(activity_id, profile_id)
        )

    def set_activity_profile(
        self, activity_id: str, profile_id: str, data: dict
    ) -> None:
        return self._run(
            self._async.set_activity_profile(activity_id, profile_id, data)
        )

    def about(self) -> dict:
        return self._run(self._async.about())

    def close(self):
        self._run(self._async.close())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
