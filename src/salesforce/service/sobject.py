from dataclasses import dataclass
from datetime import datetime
from typing import Any

from salesforce.client import Client

from .service import Service


@dataclass()
class SObjectService(Service):
  name: str
  client: Client

  def __post_init__(self) -> None:

    self.url = self.base_url + "name"

  def metadata(self) -> None:

    self.client.post(self.url)

  def create_record(self, json_data: Any):
    self.client.post(self.url, json=json_data)

  def describe(self):

    self.client.get()

  def deleted(self, start: datetime, end: datetime):

    pass
