from pydantic import BaseModel, model_validator

from .common import Extensions


class Score(BaseModel):
    scaled: float | None = None
    raw: float | None = None
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def _validate_ranges(self):
        if self.scaled is not None and not (-1.0 <= self.scaled <= 1.0):
            raise ValueError("scaled score must be between -1.0 and 1.0")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min cannot exceed max")
        if self.raw is not None:
            if self.min is not None and self.raw < self.min:
                raise ValueError("raw score below min")
            if self.max is not None and self.raw > self.max:
                raise ValueError("raw score above max")
        return self


class Result(BaseModel):
    score: Score | None = None
    success: bool | None = None
    completion: bool | None = None
    response: str | None = None
    duration: str | None = None
    extensions: Extensions | None = None

    @model_validator(mode="before")
    @classmethod
    def _wrap_score_shorthand(cls, data):
        """Allow score_scaled, score_raw, etc. as top-level convenience fields."""
        if not isinstance(data, dict):
            return data

        mapping = {
            "score_scaled": "scaled",
            "score_raw": "raw",
            "score_min": "min",
            "score_max": "max",
        }
        found = {v: data.pop(k) for k, v in mapping.items() if k in data}
        if found:
            existing = data.get("score") or {}
            if hasattr(existing, "model_dump"):
                existing = existing.model_dump(exclude_none=True)
            existing.update(found)
            data["score"] = existing

        return data
