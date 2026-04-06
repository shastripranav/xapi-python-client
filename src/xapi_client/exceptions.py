class XAPIError(Exception):
    """Base exception for all xAPI client errors."""


class LRSConnectionError(XAPIError):
    """Failed to reach the Learning Record Store."""


class LRSAuthError(XAPIError):
    """Authentication or authorization failure (401/403)."""


class StatementValidationError(XAPIError):
    """Statement data failed validation before sending."""


class LRSResponseError(XAPIError):
    """Unexpected or error response from the LRS (4xx/5xx)."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)
