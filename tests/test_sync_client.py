import httpx
import respx

from xapi_client import Activity, Actor, Statement, SyncXAPIClient, Verb

LRS_ENDPOINT = "https://lrs.example.com/xapi/"
LRS_BASE = "https://lrs.example.com/xapi"


def test_sync_about():
    with respx.mock:
        respx.get(f"{LRS_BASE}/about").mock(
            return_value=httpx.Response(200, json={"version": ["1.0.3"]})
        )
        with SyncXAPIClient(endpoint=LRS_ENDPOINT, username="k", password="s") as client:
            info = client.about()

    assert info["version"] == ["1.0.3"]


def test_sync_send_statement():
    stmt = Statement(
        actor=Actor(mbox="mailto:test@example.com"),
        verb=Verb.COMPLETED,
        object=Activity(id="http://example.com/act/1"),
    )
    with respx.mock:
        respx.put(f"{LRS_BASE}/statements").mock(
            return_value=httpx.Response(204)
        )
        with SyncXAPIClient(endpoint=LRS_ENDPOINT, username="k", password="s") as client:
            result = client.send_statement(stmt)

    assert result == stmt.id
