# xapi-client

[![CI](https://github.com/shastripranav/xapi-python-client/actions/workflows/ci.yml/badge.svg)](https://github.com/shastripranav/xapi-python-client/actions/workflows/ci.yml)

Typed, async-first Python client for xAPI Learning Record Stores.

## Install

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from xapi_client import XAPIClient, Statement, Actor, Verb, Activity, Result

# Async usage
async with XAPIClient(
    endpoint="https://lrs.example.com/xapi/",
    username="my-key",
    password="my-secret",
) as client:
    # Build and send a statement
    stmt = Statement(
        actor=Actor(mbox="mailto:john@example.com", name="John Doe"),
        verb=Verb.COMPLETED,
        object=Activity(
            id="http://example.com/courses/python-101",
            name="Python 101",
        ),
        result=Result(score_scaled=0.85, completion=True, duration="PT1H30M"),
    )
    stmt_id = await client.send_statement(stmt)

    # Query statements
    result = await client.get_statements(
        agent_email="john@example.com",
        verb="completed",
        limit=50,
    )

    # State API
    await client.set_state(
        activity_id="http://example.com/courses/python-101",
        agent_email="john@example.com",
        state_id="progress",
        data={"current_page": 5},
    )
```

### Sync Wrapper

```python
from xapi_client import SyncXAPIClient

with SyncXAPIClient(endpoint=..., username=..., password=...) as client:
    stmts = client.get_statements(agent_email="john@example.com")
```

### Convenience Constructors

```python
# Actor from email
actor = Actor.from_email("john@example.com", name="John")

# Verb from registry
verb = Verb.from_registry("completed")
verb = Verb.COMPLETED  # same thing

# Activity with shorthand name/description
activity = Activity(
    id="http://example.com/courses/python-101",
    name="Python 101",
    description="Intro course",
)

# Result with score shorthand
result = Result(score_scaled=0.85, score_raw=85, score_max=100, completion=True)
```

### Duration Utilities

```python
from xapi_client.utils import parse_duration, format_duration

seconds = parse_duration("PT1H30M")  # 5400.0
iso_str = format_duration(5400)       # "PT1H30M"
```

## Development

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
ruff check src/ tests/
```

## Status

v0.1.0 — the async client, sync client, typed statement models, and verb registry are complete and used in production. Statement signing and attachment handling are planned for a future release.
