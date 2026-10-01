from dataclasses import dataclass
from typing import Any, ClassVar

from salesforce.service.service import Service


@dataclass
class ProcessService(Service):
  """Approval processes. URI: /services/data/vXX.X/process/approvals"""

  space: ClassVar[str] = ""

  def approvals(self) -> dict:
    """List pending approval work items."""
    return self.client.get(self.url("/process/approvals"))

  def submit(self, requests: list[dict[str, Any]]) -> dict:
    """Submit or act on approval requests.

    Example:
        process.submit([{"actionType": "Submit", "contextId": "001xx", "comments": "pls"}])
    """
    res = self.client.post(self.url("/process/approvals"), json={"requests": requests})
    return res
