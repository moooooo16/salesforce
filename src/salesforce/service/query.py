from dataclasses import dataclass
from typing import ClassVar

from salesforce.service.service import Service


@dataclass
class QueryService(Service):
  """SOQL queries. URI: /services/data/vXX.X/query"""

  space: ClassVar[str] = ""

  def _fetch_all(self, end_point: str, soql: str) -> list[dict]:
    res = self.client.get(end_point, params={"q": soql})
    records = res["records"]

    while not res["done"]:
      res = self.client.get(res["nextRecordsUrl"])
      records.extend(res["records"])

    return records

  def query(self, soql: str) -> list[dict]:
    """Run a SOQL query, following pagination until done.

    Example:
        query.query("SELECT Id, Name FROM Account") -> [{"Id": "001xx", "Name": "Acme"}, ...]
    """
    return self._fetch_all(self.url("/query"), soql)

  def query_all(self, soql: str) -> list[dict]:
    """Like query(), but also includes deleted and archived records."""
    return self._fetch_all(self.url("/queryAll"), soql)
