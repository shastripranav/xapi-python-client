import re
from datetime import datetime, timezone

_DURATION_RE = re.compile(
    r"^P"
    r"(?:(\d+)Y)?"
    r"(?:(\d+)M)?"
    r"(?:(\d+)D)?"
    r"(?:T"
    r"(?:(\d+)H)?"
    r"(?:(\d+)M)?"
    r"(?:(\d+(?:\.\d+)?)S)?"
    r")?$"
)


def parse_duration(iso_duration: str) -> float:
    """Parse an ISO 8601 duration string into total seconds.

    Handles PT1H30M, P1DT2H, PT45.5S, etc.
    """
    match = _DURATION_RE.match(iso_duration)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration: {iso_duration!r}")

    years, months, days, hours, minutes, seconds = match.groups()

    # FIXME: year/month approximations lose precision — consider dateutil for calendar-aware math
    total = 0.0
    if years:
        total += int(years) * 365 * 86400
    if months:
        total += int(months) * 30 * 86400
    if days:
        total += int(days) * 86400
    if hours:
        total += int(hours) * 3600
    if minutes:
        total += int(minutes) * 60
    if seconds:
        total += float(seconds)

    return total


def format_duration(total_seconds: int | float) -> str:
    """Convert a number of seconds to an ISO 8601 duration string."""
    total_seconds = int(total_seconds)
    if total_seconds < 0:
        raise ValueError("Duration cannot be negative")

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = ["PT"]
    if hours:
        parts.append(f"{hours}H")
    if minutes:
        parts.append(f"{minutes}M")
    if seconds or not (hours or minutes):
        parts.append(f"{seconds}S")

    return "".join(parts)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso_timestamp(dt: datetime | str | None) -> str | None:
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()
