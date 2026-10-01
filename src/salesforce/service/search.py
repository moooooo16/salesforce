from dataclasses import dataclass
from typing import ClassVar

from salesforce.service.service import Service


@dataclass
class SearchService(Service):
  """SOSL search. URI: /services/data/vXX.X/search?q=sosl"""

  space: ClassVar[str] = ""

  def search(self, sosl: str) -> list[dict]:
    """Run a SOSL search and return matching records.

    Example:
        search.search("FIND {Acme} IN ALL FIELDS RETURNING Account(Id, Name)") -> [{"Id": ...}, ...]
    """
    res = self.client.get(self.url("/search"), params={"q": sosl})
    return res["searchRecords"]
