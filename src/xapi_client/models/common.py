from typing import Annotated, Any

from pydantic import AfterValidator

LanguageMap = dict[str, str]

Extensions = dict[str, Any]


def _validate_iri(v: str) -> str:
    if not v.startswith(("http://", "https://", "mailto:", "urn:")):
        raise ValueError(f"Invalid IRI: must be a valid URI, got {v!r}")
    return v


IRI = Annotated[str, AfterValidator(_validate_iri)]


def to_language_map(value: str | dict[str, str], lang: str = "en-US") -> LanguageMap:
    """Wrap a plain string into a LanguageMap dict keyed by locale."""
    if isinstance(value, dict):
        return value
    return {lang: value}
