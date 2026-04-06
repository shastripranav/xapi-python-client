from __future__ import annotations

from pydantic import BaseModel

from .common import IRI, LanguageMap

_VERB_REGISTRY: dict[str, str] = {
    "completed": "http://adlnet.gov/expapi/verbs/completed",
    "passed": "http://adlnet.gov/expapi/verbs/passed",
    "failed": "http://adlnet.gov/expapi/verbs/failed",
    "attempted": "http://adlnet.gov/expapi/verbs/attempted",
    "experienced": "http://adlnet.gov/expapi/verbs/experienced",
    "launched": "http://adlnet.gov/expapi/verbs/launched",
    "answered": "http://adlnet.gov/expapi/verbs/answered",
    "scored": "http://adlnet.gov/expapi/verbs/scored",
    # mastered lives under w3id.org, not adlnet.gov
    "mastered": "https://w3id.org/xapi/adl/verbs/mastered",
    "progressed": "http://adlnet.gov/expapi/verbs/progressed",
    "registered": "http://adlnet.gov/expapi/verbs/registered",
    "initialized": "http://adlnet.gov/expapi/verbs/initialized",
    "terminated": "http://adlnet.gov/expapi/verbs/terminated",
}


class Verb(BaseModel):
    id: IRI
    display: LanguageMap | None = None

    @classmethod
    def from_registry(cls, name: str) -> Verb:
        """Look up a common verb by short name (e.g., 'completed') from the ADL registry."""
        key = name.lower()
        if key not in _VERB_REGISTRY:
            available = ", ".join(sorted(_VERB_REGISTRY.keys()))
            raise ValueError(f"Unknown verb {name!r}. Available: {available}")
        return cls(id=_VERB_REGISTRY[key], display={"en-US": key})


Verb.COMPLETED = Verb(id=_VERB_REGISTRY["completed"], display={"en-US": "completed"})
Verb.PASSED = Verb(id=_VERB_REGISTRY["passed"], display={"en-US": "passed"})
Verb.FAILED = Verb(id=_VERB_REGISTRY["failed"], display={"en-US": "failed"})
Verb.ATTEMPTED = Verb(id=_VERB_REGISTRY["attempted"], display={"en-US": "attempted"})
Verb.EXPERIENCED = Verb(id=_VERB_REGISTRY["experienced"], display={"en-US": "experienced"})
Verb.LAUNCHED = Verb(id=_VERB_REGISTRY["launched"], display={"en-US": "launched"})
Verb.ANSWERED = Verb(id=_VERB_REGISTRY["answered"], display={"en-US": "answered"})
Verb.INITIALIZED = Verb(id=_VERB_REGISTRY["initialized"], display={"en-US": "initialized"})
Verb.TERMINATED = Verb(id=_VERB_REGISTRY["terminated"], display={"en-US": "terminated"})
