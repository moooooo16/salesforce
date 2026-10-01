from dataclasses import dataclass
from typing import ClassVar

from salesforce.service.service import Service


@dataclass
class InfoService(Service):
  """Org-level information: object catalog and API limits."""

  space: ClassVar[str] = ""

  def describe_global(self) -> list[dict]:
    """List all SObjects available in this org."""
    res = self.client.get(self.url("/sobjects"))
    return res["sobjects"]

  def limits(self) -> dict:
    """Current API usage limits and remaining quota.

    Example:
        info.limits()["DailyApiRequests"] -> {"Max": 5000000, "Remaining": 4999900}
    """
    return self.client.get(self.url("/limits"))
