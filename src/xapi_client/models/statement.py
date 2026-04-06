from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from .activity import Activity
from .actor import Actor
from .context import Context
from .result import Result
from .verb import Verb


class Statement(BaseModel):
    """An xAPI statement — the core unit of learning data."""

    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    actor: Actor
    verb: Verb
    # TODO: support StatementRef and SubStatement as object types
    object: Activity
    result: Result | None = None
    context: Context | None = None
    timestamp: datetime | None = None
    stored: datetime | None = None
    authority: Actor | None = None
    version: str | None = None

    model_config = {"populate_by_name": True}

    def to_xapi(self) -> dict:
        """Serialize to an xAPI-compliant JSON dict for LRS submission."""
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")


class StatementResult(BaseModel):
    """Response wrapper from GET /statements — includes pagination token."""

    statements: list[Statement]
    more: str | None = None
