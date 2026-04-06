import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class LRSConfig:
    """Connection config for an xAPI Learning Record Store."""

    endpoint: str
    username: str | None = None
    password: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    version: str = "1.0.3"
    timeout: float = 30.0

    def __post_init__(self):
        # trailing slash matters for httpx base_url resolution
        if not self.endpoint.endswith("/"):
            self.endpoint += "/"

    @classmethod
    def from_env(cls, dotenv_path: str | None = None) -> "LRSConfig":
        """Build config from environment variables. Loads .env if present."""
        load_dotenv(dotenv_path)

        endpoint = os.environ.get("XAPI_LRS_ENDPOINT")
        if not endpoint:
            raise ValueError("XAPI_LRS_ENDPOINT environment variable is required")

        return cls(
            endpoint=endpoint,
            username=os.environ.get("XAPI_LRS_USERNAME"),
            password=os.environ.get("XAPI_LRS_PASSWORD"),
            version=os.environ.get("XAPI_LRS_VERSION", "1.0.3"),
            timeout=float(os.environ.get("XAPI_REQUEST_TIMEOUT", "30")),
        )

    @property
    def auth(self) -> tuple[str, str] | None:
        if self.username and self.password:
            return (self.username, self.password)
        return None
