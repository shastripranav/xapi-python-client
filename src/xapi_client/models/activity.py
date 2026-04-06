from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .common import IRI, Extensions, LanguageMap, to_language_map


class ActivityDefinition(BaseModel):
    name: LanguageMap | None = None
    description: LanguageMap | None = None
    type: IRI | None = None
    more_info: str | None = Field(default=None, alias="moreInfo")
    interaction_type: str | None = Field(default=None, alias="interactionType")
    extensions: Extensions | None = None

    model_config = {"populate_by_name": True}


class Activity(BaseModel):
    object_type: str = Field(default="Activity", alias="objectType")
    id: IRI
    definition: ActivityDefinition | None = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _wrap_convenience_fields(cls, data):
        """Allow name/description/activity_type as top-level shorthand."""
        if not isinstance(data, dict):
            return data

        name = data.pop("name", None)
        description = data.pop("description", None)
        activity_type = data.pop("activity_type", None)

        if name or description or activity_type:
            defn = data.get("definition") or {}
            if hasattr(defn, "model_dump"):
                defn = defn.model_dump(exclude_none=True)
            if name:
                defn["name"] = to_language_map(name)
            if description:
                defn["description"] = to_language_map(description)
            if activity_type:
                defn["type"] = activity_type
            data["definition"] = defn

        return data
