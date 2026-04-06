from __future__ import annotations

from pydantic import BaseModel, Field

from .activity import Activity
from .actor import Actor
from .common import Extensions


class ContextActivities(BaseModel):
    parent: list[Activity] | None = None
    grouping: list[Activity] | None = None
    category: list[Activity] | None = None
    other: list[Activity] | None = None


class Context(BaseModel):
    registration: str | None = None
    instructor: Actor | None = None
    team: Actor | None = None
    context_activities: ContextActivities | None = Field(
        default=None, alias="contextActivities"
    )
    revision: str | None = None
    platform: str | None = None
    language: str | None = None
    extensions: Extensions | None = None

    model_config = {"populate_by_name": True}
