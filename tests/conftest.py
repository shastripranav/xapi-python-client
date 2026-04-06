import pytest

from xapi_client import Activity, Actor, Result, Statement, Verb


@pytest.fixture
def sample_actor():
    return Actor(mbox="mailto:john@example.com", name="John Doe")


@pytest.fixture
def sample_verb():
    return Verb.COMPLETED


@pytest.fixture
def sample_activity():
    return Activity(
        id="http://example.com/courses/python-101",
        name="Python 101",
        description="Introduction to Python programming",
    )


@pytest.fixture
def sample_statement(sample_actor, sample_verb, sample_activity):
    return Statement(
        actor=sample_actor,
        verb=sample_verb,
        object=sample_activity,
        result=Result(score_scaled=0.85, completion=True, duration="PT1H30M"),
    )


@pytest.fixture
def raw_statement_data():
    return {
        "actor": {
            "objectType": "Agent",
            "name": "John Doe",
            "mbox": "mailto:john@example.com",
        },
        "verb": {
            "id": "http://adlnet.gov/expapi/verbs/completed",
            "display": {"en-US": "completed"},
        },
        "object": {
            "objectType": "Activity",
            "id": "http://example.com/courses/python-101",
            "definition": {
                "name": {"en-US": "Python 101"},
                "type": "http://adlnet.gov/expapi/activities/course",
            },
        },
    }
