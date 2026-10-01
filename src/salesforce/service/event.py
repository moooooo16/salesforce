from dataclasses import dataclass
from typing import Any, ClassVar

from salesforce.service.service import Service


@dataclass
class EventService(Service):
  """Platform event publishing. Events are published like record inserts.

  URI: /services/data/vXX.X/sobjects/{EventName}__e/
  """

  space: ClassVar[str] = "/sobjects"

  def publish(self, event_name: str, data: dict[str, Any]) -> dict:
    """Publish one platform event.

    Example:
        event.publish("Order__e", {"Order_Id__c": "A-1"}) -> {"id": ..., "success": True, "errors": []}
    """
    if not event_name.endswith("__e"):
      event_name += "__e"
    return self.client.post(self.url(f"/{event_name}"), json=data)
