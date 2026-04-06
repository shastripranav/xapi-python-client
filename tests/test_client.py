import httpx
import pytest
import respx

from xapi_client import XAPIClient
from xapi_client.exceptions import LRSAuthError, LRSConnectionError, LRSResponseError

LRS_ENDPOINT = "https://lrs.example.com/xapi/"
LRS_BASE = "https://lrs.example.com/xapi"


def _make_client():
    return XAPIClient(endpoint=LRS_ENDPOINT, username="key", password="secret")


def _stmt_json(actor_email="john@example.com"):
    return {
        "actor": {"objectType": "Agent", "mbox": f"mailto:{actor_email}"},
        "verb": {
            "id": "http://adlnet.gov/expapi/verbs/completed",
            "display": {"en-US": "completed"},
        },
        "object": {
            "objectType": "Activity",
            "id": "http://example.com/courses/py101",
        },
    }


async def test_send_statement_with_id(sample_statement):
    with respx.mock:
        route = respx.put(f"{LRS_BASE}/statements").mock(
            return_value=httpx.Response(204)
        )
        client = _make_client()
        stmt_id = await client.send_statement(sample_statement)
        await client.close()

    assert stmt_id == sample_statement.id
    assert route.called


async def test_send_statements_batch(sample_statement):
    with respx.mock:
        respx.post(f"{LRS_BASE}/statements").mock(
            return_value=httpx.Response(200, json=["id-aaa", "id-bbb"])
        )
        client = _make_client()
        ids = await client.send_statements([sample_statement, sample_statement])
        await client.close()

    assert ids == ["id-aaa", "id-bbb"]


async def test_send_empty_batch():
    client = _make_client()
    result = await client.send_statements([])
    assert result == []


async def test_get_statement_by_id():
    with respx.mock:
        respx.get(f"{LRS_BASE}/statements").mock(
            return_value=httpx.Response(200, json=_stmt_json())
        )
        client = _make_client()
        stmt = await client.get_statement("some-uuid")
        await client.close()

    assert stmt.actor.mbox == "mailto:john@example.com"
    assert stmt.verb.id == "http://adlnet.gov/expapi/verbs/completed"


async def test_get_statements_with_filters():
    with respx.mock:
        route = respx.get(f"{LRS_BASE}/statements").mock(
            return_value=httpx.Response(
                200,
                json={"statements": [_stmt_json()], "more": ""},
            ),
        )
        client = _make_client()
        result = await client.get_statements(
            agent_email="john@example.com", verb="completed", limit=10
        )
        await client.close()

    assert len(result.statements) == 1
    assert route.called


async def test_auto_pagination():
    call_count = 0

    def handler(request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(
                200,
                json={
                    "statements": [_stmt_json()],
                    "more": f"{LRS_BASE}/statements?token=pg2",
                },
            )
        return httpx.Response(
            200,
            json={
                "statements": [_stmt_json("jane@example.com")],
                "more": "",
            },
        )

    with respx.mock:
        respx.get(url__regex=r".*/statements.*").mock(side_effect=handler)
        client = _make_client()
        all_stmts = await client.get_all_statements(agent_email="john@example.com")
        await client.close()

    assert len(all_stmts) == 2
    assert call_count == 2


async def test_set_state():
    with respx.mock:
        route = respx.put(f"{LRS_BASE}/activities/state").mock(
            return_value=httpx.Response(204)
        )
        client = _make_client()
        await client.set_state(
            activity_id="http://example.com/act/1",
            agent_email="john@example.com",
            state_id="progress",
            data={"page": 5},
        )
        await client.close()

    assert route.called


async def test_get_state():
    with respx.mock:
        respx.get(f"{LRS_BASE}/activities/state").mock(
            return_value=httpx.Response(
                200, json={"page": 5, "bookmarks": [1, 3]}
            )
        )
        client = _make_client()
        state = await client.get_state(
            activity_id="http://example.com/act/1",
            agent_email="john@example.com",
            state_id="progress",
        )
        await client.close()

    assert state == {"page": 5, "bookmarks": [1, 3]}


async def test_get_state_not_found_returns_none():
    with respx.mock:
        respx.get(f"{LRS_BASE}/activities/state").mock(
            return_value=httpx.Response(404)
        )
        client = _make_client()
        state = await client.get_state(
            activity_id="http://example.com/act/1",
            agent_email="john@example.com",
            state_id="missing",
        )
        await client.close()

    assert state is None


async def test_about():
    with respx.mock:
        respx.get(f"{LRS_BASE}/about").mock(
            return_value=httpx.Response(200, json={"version": ["1.0.3"]})
        )
        client = _make_client()
        info = await client.about()
        await client.close()

    assert info["version"] == ["1.0.3"]


async def test_auth_error_raises():
    with respx.mock:
        respx.get(f"{LRS_BASE}/about").mock(
            return_value=httpx.Response(401, text="Unauthorized")
        )
        client = _make_client()
        with pytest.raises(LRSAuthError):
            await client.about()
        await client.close()


async def test_server_error_raises():
    with respx.mock:
        respx.get(f"{LRS_BASE}/about").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        client = _make_client()
        with pytest.raises(LRSResponseError) as exc_info:
            await client.about()
        await client.close()

    assert exc_info.value.status_code == 500


async def test_connection_error_raises():
    with respx.mock:
        respx.get(f"{LRS_BASE}/about").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        client = _make_client()
        with pytest.raises(LRSConnectionError):
            await client.about()
        await client.close()


# TODO: add edge case tests for concurrent batch submissions
