from __future__ import annotations

import json
import logging
from datetime import datetime

import httpx

from .exceptions import LRSAuthError, LRSConnectionError, LRSResponseError
from .lrs import LRSConfig
from .models import Actor, Statement
from .models.statement import StatementResult
from .models.verb import _VERB_REGISTRY
from .utils import to_iso_timestamp

logger = logging.getLogger(__name__)

XAPI_CONTENT_TYPE = "application/json"
XAPI_VERSION_HEADER = "X-Experience-API-Version"


class XAPIClient:
    """Async client for communicating with an xAPI Learning Record Store.

    Can be used as a context manager for automatic resource cleanup::

        async with XAPIClient(endpoint=..., username=..., password=...) as client:
            await client.send_statement(stmt)
    """

    def __init__(
        self,
        endpoint: str | None = None,
        username: str | None = None,
        password: str | None = None,
        *,
        config: LRSConfig | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ):
        if config:
            self._config = config
        elif endpoint:
            self._config = LRSConfig(
                endpoint=endpoint,
                username=username,
                password=password,
                headers=headers or {},
                timeout=timeout,
            )
        else:
            raise ValueError("Provide either 'endpoint' or a 'config' object")

        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            default_headers = {
                XAPI_VERSION_HEADER: self._config.version,
                "Content-Type": XAPI_CONTENT_TYPE,
            }
            default_headers.update(self._config.headers)

            self._client = httpx.AsyncClient(
                base_url=self._config.endpoint,
                auth=self._config.auth,
                headers=default_headers,
                timeout=self._config.timeout,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> XAPIClient:
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _handle_response(self, resp: httpx.Response) -> httpx.Response:
        """Check response status and raise typed exceptions."""
        if resp.status_code in (401, 403):
            raise LRSAuthError(f"Authentication failed: {resp.status_code} {resp.text}")
        if resp.status_code >= 400:
            raise LRSResponseError(
                f"LRS returned {resp.status_code}: {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp

    # --- Statement API ---

    async def send_statement(self, statement: Statement) -> str:
        """Send a single statement to the LRS. Returns the statement ID."""
        client = self._get_client()
        payload = statement.to_xapi()
        stmt_id = payload.get("id")

        # TODO: add retry logic for transient network failures
        try:
            if stmt_id:
                resp = await client.put(
                    "statements", params={"statementId": stmt_id}, json=payload
                )
            else:
                resp = await client.post("statements", json=[payload])
        except httpx.ConnectError as exc:
            raise LRSConnectionError(
                f"Cannot connect to LRS at {self._config.endpoint}"
            ) from exc

        self._handle_response(resp)
        if stmt_id:
            return stmt_id
        return resp.json()[0]

    async def send_statements(self, statements: list[Statement]) -> list[str]:
        """Send a batch of statements. Returns list of assigned IDs."""
        if not statements:
            return []

        client = self._get_client()
        payload = [s.to_xapi() for s in statements]

        try:
            resp = await client.post("statements", json=payload)
        except httpx.ConnectError as exc:
            raise LRSConnectionError(
                f"Cannot connect to LRS at {self._config.endpoint}"
            ) from exc

        self._handle_response(resp)
        return resp.json()

    async def get_statement(self, statement_id: str) -> Statement:
        """Retrieve a single statement by ID."""
        client = self._get_client()

        try:
            resp = await client.get(
                "statements", params={"statementId": statement_id}
            )
        except httpx.ConnectError as exc:
            raise LRSConnectionError(
                f"Cannot connect to LRS at {self._config.endpoint}"
            ) from exc

        self._handle_response(resp)
        return Statement.model_validate(resp.json())

    async def get_statements(
        self,
        *,
        agent_email: str | None = None,
        agent: Actor | None = None,
        verb: str | None = None,
        activity: str | None = None,
        since: str | datetime | None = None,
        until: str | datetime | None = None,
        limit: int | None = None,
        ascending: bool | None = None,
        related_activities: bool | None = None,
    ) -> StatementResult:
        """Query statements from the LRS with optional filters.

        Args:
            agent_email: Filter by agent email (convenience — wraps into agent JSON).
            agent: Filter by Actor object directly.
            verb: Verb short name (from registry) or full IRI.
            activity: Activity IRI to filter by.
            since: Only statements stored after this time.
            until: Only statements stored before this time.
            limit: Max number of statements to return.
            ascending: Sort order by stored timestamp.
            related_activities: Include related activity context matches.
        """
        params = self._build_query_params(
            agent_email=agent_email,
            agent=agent,
            verb=verb,
            activity=activity,
            since=since,
            until=until,
            limit=limit,
            ascending=ascending,
            related_activities=related_activities,
        )

        client = self._get_client()
        try:
            resp = await client.get("statements", params=params)
        except httpx.ConnectError as exc:
            raise LRSConnectionError(
                f"Cannot connect to LRS at {self._config.endpoint}"
            ) from exc

        self._handle_response(resp)
        data = resp.json()
        return StatementResult(
            statements=[Statement.model_validate(s) for s in data.get("statements", [])],
            more=data.get("more"),
        )

    async def get_all_statements(self, **kwargs) -> list[Statement]:
        """Auto-paginate through all matching statements.

        Accepts the same keyword args as get_statements().
        Warning: may return a large result set for broad queries.
        """
        all_stmts: list[Statement] = []
        result = await self.get_statements(**kwargs)
        all_stmts.extend(result.statements)

        # xAPI pagination uses opaque 'more' tokens, not offset
        while result.more:
            result = await self._follow_more(result.more)
            all_stmts.extend(result.statements)

        return all_stmts

    async def _follow_more(self, more_url: str) -> StatementResult:
        """Follow a pagination 'more' URL from the LRS."""
        client = self._get_client()
        resp = await client.get(more_url)
        self._handle_response(resp)
        data = resp.json()
        return StatementResult(
            statements=[Statement.model_validate(s) for s in data.get("statements", [])],
            more=data.get("more"),
        )

    # --- State API ---

    async def set_state(
        self,
        activity_id: str,
        agent_email: str,
        state_id: str,
        data: dict,
        *,
        registration: str | None = None,
    ) -> None:
        """Store state data for an activity/agent pair."""
        params = self._state_params(activity_id, agent_email, state_id, registration)
        client = self._get_client()

        try:
            resp = await client.put("activities/state", params=params, json=data)
        except httpx.ConnectError as exc:
            raise LRSConnectionError("Cannot connect to LRS") from exc

        self._handle_response(resp)

    async def get_state(
        self,
        activity_id: str,
        agent_email: str,
        state_id: str,
        *,
        registration: str | None = None,
    ) -> dict | None:
        """Retrieve state data. Returns None if not found."""
        params = self._state_params(activity_id, agent_email, state_id, registration)
        client = self._get_client()

        try:
            resp = await client.get("activities/state", params=params)
        except httpx.ConnectError as exc:
            raise LRSConnectionError("Cannot connect to LRS") from exc

        if resp.status_code == 404:
            return None
        self._handle_response(resp)
        return resp.json()

    async def delete_state(
        self,
        activity_id: str,
        agent_email: str,
        state_id: str,
        *,
        registration: str | None = None,
    ) -> None:
        params = self._state_params(activity_id, agent_email, state_id, registration)
        client = self._get_client()

        try:
            resp = await client.delete("activities/state", params=params)
        except httpx.ConnectError as exc:
            raise LRSConnectionError("Cannot connect to LRS") from exc

        self._handle_response(resp)

    # --- Activity Profile API ---

    async def get_activity_profile(
        self, activity_id: str, profile_id: str
    ) -> dict | None:
        params = {"activityId": activity_id, "profileId": profile_id}
        client = self._get_client()

        try:
            resp = await client.get("activities/profile", params=params)
        except httpx.ConnectError as exc:
            raise LRSConnectionError("Cannot connect to LRS") from exc

        if resp.status_code == 404:
            return None
        self._handle_response(resp)
        return resp.json()

    async def set_activity_profile(
        self, activity_id: str, profile_id: str, data: dict
    ) -> None:
        params = {"activityId": activity_id, "profileId": profile_id}
        client = self._get_client()

        try:
            resp = await client.put("activities/profile", params=params, json=data)
        except httpx.ConnectError as exc:
            raise LRSConnectionError("Cannot connect to LRS") from exc

        self._handle_response(resp)

    # --- About ---

    async def about(self) -> dict:
        """Get LRS metadata and supported xAPI version info."""
        client = self._get_client()

        try:
            resp = await client.get("about")
        except httpx.ConnectError as exc:
            raise LRSConnectionError(
                f"Cannot connect to LRS at {self._config.endpoint}"
            ) from exc

        self._handle_response(resp)
        return resp.json()

    # --- Internal helpers ---

    def _state_params(
        self,
        activity_id: str,
        agent_email: str,
        state_id: str,
        registration: str | None,
    ) -> dict:
        params: dict = {
            "activityId": activity_id,
            "agent": json.dumps(
                {"mbox": f"mailto:{agent_email}", "objectType": "Agent"}
            ),
            "stateId": state_id,
        }
        if registration:
            params["registration"] = registration
        return params

    def _build_query_params(
        self,
        agent_email: str | None = None,
        agent: Actor | None = None,
        verb: str | None = None,
        activity: str | None = None,
        since: str | datetime | None = None,
        until: str | datetime | None = None,
        limit: int | None = None,
        ascending: bool | None = None,
        related_activities: bool | None = None,
    ) -> dict:
        params: dict = {}

        if agent_email:
            params["agent"] = json.dumps(
                {"mbox": f"mailto:{agent_email}", "objectType": "Agent"}
            )
        elif agent:
            params["agent"] = json.dumps(
                agent.model_dump(by_alias=True, exclude_none=True)
            )

        if verb:
            # resolve short names like "completed" from registry, pass IRIs through
            params["verb"] = (
                verb if verb.startswith("http") else _VERB_REGISTRY.get(verb.lower(), verb)
            )

        if activity:
            params["activity"] = activity
        if since:
            params["since"] = to_iso_timestamp(since)
        if until:
            params["until"] = to_iso_timestamp(until)
        if limit is not None:
            params["limit"] = str(limit)
        if ascending is not None:
            params["ascending"] = str(ascending).lower()
        if related_activities is not None:
            params["related_activities"] = str(related_activities).lower()

        return params
