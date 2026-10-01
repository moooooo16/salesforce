from dataclasses import dataclass
from typing import Any, ClassVar

from salesforce.service.service import Service


@dataclass
class CollectionService(Service):
  """Batch CRUD for one SObject type, up to 200 records per call.

  URI: /services/data/vXX.X/composite/sobjects
  """

  space: ClassVar[str] = "/composite/sobjects"

  name: str

  def _with_type(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"attributes": {"type": self.name}, **r} for r in records]

  def insert(self, records: list[dict[str, Any]], all_or_none: bool = True) -> list[dict]:
    """Create up to 200 records in one call, returning per-record results.

    Example:
        collections.insert([{"Name": "A"}, {"Name": "B"}])
        -> [{"id": "001xx...", "success": True, "errors": []}, ...]
    """
    res = self.client.request(
      "POST",
      self.url(),
      json={"allOrNone": all_or_none, "records": self._with_type(records)},
    )
    return res.json()

  def update(self, records: list[dict[str, Any]], all_or_none: bool = True) -> list[dict]:
    """Update up to 200 records in one call; each record must include Id."""
    res = self.client.request(
      "PATCH",
      self.url(),
      json={"allOrNone": all_or_none, "records": self._with_type(records)},
    )
    return res.json()

  def delete(self, record_ids: list[str], all_or_none: bool = True) -> list[dict]:
    """Delete up to 200 records in one call."""
    res = self.client.request(
      "DELETE",
      self.url(),
      params={"ids": ",".join(record_ids), "allOrNone": str(all_or_none).lower()},
    )
    return res.json()
