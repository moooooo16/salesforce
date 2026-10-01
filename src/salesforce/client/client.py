from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

from salesforce.client.auth import AuthStrategy, Session
from salesforce.exception import ApiError

logger = logging.getLogger(__name__)


@dataclass
class Client:
  """Salesforce REST API client with pluggable auth."""

  auth: AuthStrategy
  _session: Session | None = field(default=None, init=False, repr=False)
  _http: httpx.Client = field(
    default_factory=lambda: httpx.Client(
      transport=httpx.HTTPTransport(retries=3),
      timeout=httpx.Timeout(60.0, connect=10.0),
    ),
    repr=False,
  )

  @classmethod
  def from_strategy(cls, name: str) -> Client:
    """Create a client using a registered auth flow by name.

    Example:
        Client.from_strategy("jwt")
    """
    return cls(AuthStrategy.create(name))

  @property
  def session(self) -> Session:
    if self._session is None:
      self._session = self.auth.authenticate()
    return self._session

  def request(self, method: str, end_point: str, **kwargs) -> httpx.Response:
    """Send an authenticated request, raising ApiError on failure.

    Example:
        client.request("GET", "services/data/v61.0/query", params={"q": "SELECT Id FROM Account"})
    """
    url = httpx.URL(self.session.instance_url).join(end_point)

    for attempt in (1, 2):
      res = self._http.request(
        method,
        url,
        headers={"Authorization": f"Bearer {self.session.access_token}"},
        **kwargs,
      )
      if res.status_code != 401 or attempt == 2:
        break
      logger.info("Auth: token expired, refreshing session")
      self._session = self.auth.authenticate()

    logger.debug(f"{method} {end_point} -> {res.status_code}")
    if res.is_error:
      logger.warning(f"{method} {end_point} failed: {res.status_code} {res.text[:200]}")
      raise ApiError(res.status_code, res.text)
    return res

  def get(self, end_point: str, **kwargs) -> dict:
    return self.request("GET", end_point, **kwargs).json()

  def get_bytes(self, end_point: str, **kwargs) -> bytes:
    return self.request("GET", end_point, **kwargs).content

  def post(self, end_point: str, **kwargs) -> dict:
    return self.request("POST", end_point, **kwargs).json()

  def patch(self, end_point: str, **kwargs) -> None:
    # PATCH returns 204 No Content on success; nothing to parse.
    self.request("PATCH", end_point, **kwargs)

  def delete(self, end_point: str, **kwargs) -> None:
    # DELETE returns 204 No Content on success; nothing to parse.
    self.request("DELETE", end_point, **kwargs)
