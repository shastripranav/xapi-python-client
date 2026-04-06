import pytest

from xapi_client.utils import format_duration, parse_duration


class TestParseDuration:
    def test_hours_and_minutes(self):
        assert parse_duration("PT1H30M") == 5400.0

    def test_seconds_only(self):
        assert parse_duration("PT45S") == 45.0

    def test_fractional_seconds(self):
        assert parse_duration("PT45.5S") == 45.5

    def test_days_and_hours(self):
        assert parse_duration("P1DT2H") == 93600.0

    def test_hours_only(self):
        assert parse_duration("PT2H") == 7200.0

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid ISO 8601"):
            parse_duration("not-a-duration")

    def test_empty_period(self):
        with pytest.raises(ValueError):
            parse_duration("")


class TestFormatDuration:
    def test_standard(self):
        assert format_duration(5400) == "PT1H30M"

    def test_zero(self):
        assert format_duration(0) == "PT0S"

    def test_seconds_only(self):
        assert format_duration(45) == "PT45S"

    def test_minutes_only(self):
        assert format_duration(120) == "PT2M"

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="negative"):
            format_duration(-10)
