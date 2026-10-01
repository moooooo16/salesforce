from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar

from salesforce.client.client import Client
from salesforce.config import Settings


@dataclass
class Service:
  """Base service: owns URL composition, delegates HTTP to the client."""

  space: ClassVar[str]

  client: Client

  @cached_property
  def api_version(self) -> str:
    # Read on first use, not at import time, so a missing env file
    return Settings().api_version

  def url(self, path: str = "") -> str:
    """Build a versioned API path.

    Example:
        service.url("/query") -> "services/data/v61.0/query"
    """
    return f"services/data/{self.api_version}{self.space}{path}"
