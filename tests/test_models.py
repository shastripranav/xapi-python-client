import pytest

from xapi_client import Activity, Actor, Result, Statement, Verb
from xapi_client.models import Score


class TestActor:
    def test_from_email(self):
        actor = Actor.from_email("john@example.com", name="John")
        assert actor.mbox == "mailto:john@example.com"
        assert actor.name == "John"
        assert actor.object_type == "Agent"

    def test_from_email_with_mailto_prefix(self):
        actor = Actor.from_email("mailto:jane@example.com")
        assert actor.mbox == "mailto:jane@example.com"

    def test_from_account(self):
        actor = Actor.from_account("https://lms.example.com", "user42", name="Jane")
        assert actor.account.name == "user42"
        assert actor.account.home_page == "https://lms.example.com"

    def test_requires_one_identifier(self):
        with pytest.raises(ValueError, match="inverse functional identifier"):
            Actor(name="No ID")

    def test_rejects_multiple_identifiers(self):
        with pytest.raises(ValueError, match="inverse functional identifier"):
            Actor(mbox="mailto:a@b.com", openid="https://openid.example.com/user")

    def test_anonymous_group(self):
        member = Actor(mbox="mailto:member@example.com")
        group = Actor(object_type="Group", member=[member])
        assert group.object_type == "Group"
        assert len(group.member) == 1

    def test_account_alias_deserialization(self):
        data = {
            "objectType": "Agent",
            "account": {"homePage": "https://lms.example.com", "name": "jsmith"},
        }
        actor = Actor.model_validate(data)
        assert actor.account.home_page == "https://lms.example.com"


class TestVerb:
    def test_from_registry(self):
        verb = Verb.from_registry("completed")
        assert verb.id == "http://adlnet.gov/expapi/verbs/completed"
        assert verb.display == {"en-US": "completed"}

    def test_from_registry_case_insensitive(self):
        verb = Verb.from_registry("PASSED")
        assert verb.id == "http://adlnet.gov/expapi/verbs/passed"

    def test_unknown_verb_raises(self):
        with pytest.raises(ValueError, match="Unknown verb"):
            Verb.from_registry("nonexistent")

    def test_constants(self):
        assert Verb.COMPLETED.id == "http://adlnet.gov/expapi/verbs/completed"
        assert Verb.PASSED.id == "http://adlnet.gov/expapi/verbs/passed"
        assert Verb.FAILED.id == "http://adlnet.gov/expapi/verbs/failed"
        assert Verb.LAUNCHED.id == "http://adlnet.gov/expapi/verbs/launched"

    def test_custom_verb(self):
        verb = Verb(id="http://custom.org/verbs/reviewed", display={"en-US": "reviewed"})
        assert verb.id == "http://custom.org/verbs/reviewed"


class TestActivity:
    def test_convenience_fields(self):
        act = Activity(
            id="http://example.com/act/1",
            name="Test Activity",
            description="A test",
        )
        assert act.definition is not None
        assert act.definition.name == {"en-US": "Test Activity"}
        assert act.definition.description == {"en-US": "A test"}

    def test_with_full_definition(self):
        act = Activity(
            id="http://example.com/act/1",
            definition={
                "name": {"en-US": "Full Def"},
                "type": "http://adlnet.gov/expapi/activities/course",
            },
        )
        assert act.definition.type == "http://adlnet.gov/expapi/activities/course"


class TestResult:
    def test_score_shorthand(self):
        result = Result(score_scaled=0.9, score_raw=90, score_max=100, completion=True)
        assert result.score.scaled == 0.9
        assert result.score.raw == 90
        assert result.completion is True

    def test_score_validation_scaled_range(self):
        with pytest.raises(ValueError, match="scaled"):
            Score(scaled=1.5)

    def test_score_validation_raw_above_max(self):
        with pytest.raises(ValueError, match="raw score above max"):
            Score(raw=110, max=100)

    def test_score_min_exceeds_max(self):
        with pytest.raises(ValueError, match="min cannot exceed max"):
            Score(min=100, max=50)


class TestStatement:
    def test_serialization(self, sample_statement):
        data = sample_statement.to_xapi()
        assert data["actor"]["objectType"] == "Agent"
        assert data["verb"]["id"] == "http://adlnet.gov/expapi/verbs/completed"
        assert data["object"]["objectType"] == "Activity"
        assert data["result"]["score"]["scaled"] == 0.85
        assert "id" in data

    def test_auto_generates_id(self):
        stmt = Statement(
            actor=Actor(mbox="mailto:test@example.com"),
            verb=Verb.LAUNCHED,
            object=Activity(id="http://example.com/act/1"),
        )
        assert stmt.id is not None
        assert len(stmt.id) == 36

    def test_from_raw_data(self, raw_statement_data):
        stmt = Statement.model_validate(raw_statement_data)
        assert stmt.actor.mbox == "mailto:john@example.com"
        assert stmt.verb.id == "http://adlnet.gov/expapi/verbs/completed"
        assert stmt.object.id == "http://example.com/courses/python-101"

    def test_excludes_none_fields(self):
        stmt = Statement(
            actor=Actor(mbox="mailto:test@example.com"),
            verb=Verb.COMPLETED,
            object=Activity(id="http://example.com/act/1"),
        )
        data = stmt.to_xapi()
        assert "result" not in data
        assert "context" not in data
        assert "stored" not in data
