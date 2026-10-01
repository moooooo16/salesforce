from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from salesforce.service.service import Service


@dataclass
class SObjectService(Service):
  """CRUD and metadata for one SObject type.

  URI: /services/data/vXX.X/sobjects/{name}/
  """

  space: ClassVar[str] = "/sobjects"

  name: str

  def metadata(self) -> dict:
    """Get basic metadata and recently viewed records for this object."""
    return self.client.get(self.url(f"/{self.name}"))

  def describe(self) -> dict:
    """Get full field/layout metadata for this object."""
    return self.client.get(self.url(f"/{self.name}/describe"))

  def get(self, record_id: str, fields: list[str] | None = None) -> dict:
    """Retrieve one record, optionally restricted to the given fields.

    Example:
        sobject.get("001xx000003DHP0", ["Name", "Phone"])
    """
    params = {"fields": ",".join(fields)} if fields else None
    return self.client.get(self.url(f"/{self.name}/{record_id}"), params=params)

  def insert(self, data: dict[str, Any]) -> dict:
    """Create a record.

    Example:
        sobject.insert({"Name": "Acme"}) -> {"id": "001xx...", "success": True, "errors": []}
    """
    return self.client.post(self.url(f"/{self.name}"), json=data)

  def update(self, record_id: str, data: dict[str, Any]) -> None:
    """Update a record."""
    self.client.patch(self.url(f"/{self.name}/{record_id}"), json=data)

  def delete(self, record_id: str) -> None:
    """Delete a record."""
    self.client.delete(self.url(f"/{self.name}/{record_id}"))

  def blob(self, record_id: str, field: str) -> bytes:
    """Fetch a binary field (e.g. Attachment Body) as raw bytes.

    Example:
        sobject.blob("00Pxx...", "Body")
    """
    return self.client.get_bytes(self.url(f"/{self.name}/{record_id}/{field}"))

  def updated(self, start: datetime, end: datetime) -> list[str]:
    """IDs of records updated within [start, end] (max 30-day span)."""
    res = self.client.get(
      self.url(f"/{self.name}/updated"),
      params={"start": start.isoformat(), "end": end.isoformat()},
    )
    return res["ids"]

  def deleted(self, start: datetime, end: datetime) -> list[str]:
    """IDs of records deleted within [start, end] (max 30-day span)."""
    res = self.client.get(
      self.url(f"/{self.name}/deleted"),
      params={"start": start.isoformat(), "end": end.isoformat()},
    )
    return [r["id"] for r in res["deletedRecords"]]
