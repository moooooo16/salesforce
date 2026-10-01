from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from salesforce.client.client import Client
from salesforce.service import (
  BulkService,
  CollectionService,
  EventService,
  InfoService,
  ProcessService,
  QueryService,
  SearchService,
  SObjectService,
)


@dataclass
class Salesforce:
  """Entry point: one client, all services."""

  client: Client

  @classmethod
  def from_strategy(cls, name: str) -> Salesforce:
    """Create from a registered auth flow name.

    Example:
        sf = Salesforce.from_strategy("jwt")
    """
    return cls(Client.from_strategy(name))

  @cached_property
  def query(self) -> QueryService:
    return QueryService(self.client)

  def bulk(self, name: str) -> BulkService:
    """Get a bulk-load service for one SObject type.

    Example:
        sf.bulk("Account").insert([{"Name": "Acme"}])
    """
    return BulkService(self.client, name)

  def collections(self, name: str) -> CollectionService:
    """Get a batch CRUD service for one SObject type (up to 200 records per call).

    Example:
        sf.collections("Account").insert([{"Name": "Acme"}])
    """
    return CollectionService(self.client, name)

  @cached_property
  def info(self) -> InfoService:
    return InfoService(self.client)

  @cached_property
  def search(self) -> SearchService:
    return SearchService(self.client)

  @cached_property
  def process(self) -> ProcessService:
    return ProcessService(self.client)

  @cached_property
  def event(self) -> EventService:
    return EventService(self.client)

  def sobject(self, name: str) -> SObjectService:
    """Get a CRUD service for one SObject type.

    Example:
        sf.sobject("Account").get("001xx000003DHP0")
    """
    return SObjectService(self.client, name)
