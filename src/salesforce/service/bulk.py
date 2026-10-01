import csv
import io
import time
from dataclasses import dataclass
from typing import Any, ClassVar

from salesforce.exception import BulkJobError
from salesforce.service.service import Service

_TERMINAL_STATES = {"JobComplete", "Failed", "Aborted"}


def _to_csv(records: list[dict[str, Any]]) -> str:
  """Serialize records to CSV with the first record's keys as header."""
  buf = io.StringIO()
  writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()), lineterminator="\n")
  writer.writeheader()
  writer.writerows(records)
  return buf.getvalue()


@dataclass
class BulkService(Service):
  """Bulk API 2.0 ingest jobs for one SObject type.

  URI: /services/data/vXX.X/jobs/ingest
  """

  space: ClassVar[str] = "/jobs/ingest"

  name: str

  def insert(self, records: list[dict[str, Any]], **kwargs) -> dict:
    """Bulk insert records, returning the final job info.

    Example:
        bulk.insert([{"Name": "A"}, {"Name": "B"}]) -> {"state": "JobComplete", ...}
    """
    return self._run("insert", records, **kwargs)

  def update(self, records: list[dict[str, Any]], **kwargs) -> dict:
    """Bulk update records; each record must include Id."""
    return self._run("update", records, **kwargs)

  def upsert(self, records: list[dict[str, Any]], external_id_field: str, **kwargs) -> dict:
    """Bulk upsert records matched on an external ID field."""
    return self._run("upsert", records, external_id_field=external_id_field, **kwargs)

  def delete(self, records: list[dict[str, Any]], **kwargs) -> dict:
    """Bulk delete records; each record must include Id."""
    return self._run("delete", records, **kwargs)

  def _run(
    self,
    operation: str,
    records: list[dict[str, Any]],
    external_id_field: str | None = None,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
  ) -> dict:
    if not records:
      raise ValueError("records must not be empty")

    payload: dict[str, Any] = {
      "object": self.name,
      "operation": operation,
      "contentType": "CSV",
      "lineEnding": "LF",
    }
    if external_id_field:
      payload["externalIdFieldName"] = external_id_field

    job = self.client.post(self.url(), json=payload)
    job_id = job["id"]

    self.client.put(
      self.url(f"/{job_id}/batches"),
      content=_to_csv(records),
      headers={"Content-Type": "text/csv"},
    )
    self.client.patch(self.url(f"/{job_id}"), json={"state": "UploadComplete"})

    deadline = time.monotonic() + timeout
    while True:
      job = self.client.get(self.url(f"/{job_id}"))
      if job["state"] in _TERMINAL_STATES:
        break
      if time.monotonic() > deadline:
        raise BulkJobError(job_id, "Timeout", f"not done after {timeout}s")
      time.sleep(poll_interval)

    if job["state"] != "JobComplete":
      raise BulkJobError(job_id, job["state"], job.get("errorMessage", ""))
    return job

  def successful_results(self, job_id: str) -> str:
    """CSV of successfully processed records for a completed job."""
    return self.client.get_bytes(self.url(f"/{job_id}/successfulResults")).decode()

  def failed_results(self, job_id: str) -> str:
    """CSV of failed records with error details for a completed job."""
    return self.client.get_bytes(self.url(f"/{job_id}/failedResults")).decode()
