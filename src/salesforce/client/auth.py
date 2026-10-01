from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import httpx
import jwt
from pydantic import BaseModel, ConfigDict, ValidationError

from salesforce.config import ClientCredentialsSettings, JWTSettings, Settings
from salesforce.exception import AuthenticationError, UnknownFlowError

logger = logging.getLogger(__name__)


class Session(BaseModel):
  model_config = ConfigDict(frozen=True, extra="allow")

  access_token: str
  instance_url: str
  id: str
  token_type: str
  scope: str


class AuthStrategy(ABC):
  registry: ClassVar[dict[str, type[AuthStrategy]]] = {}
  name: ClassVar[str | None] = None
  auth_endpoint: str = "services/oauth2/token"
  settings: Settings

  def __init_subclass__(cls, **kwargs: object) -> None:

    super().__init_subclass__(**kwargs)

    if cls.name:
      AuthStrategy.registry[cls.name] = cls

  def __repr__(self) -> str:
    return ",".join([k for k in self.registry])

  @abstractmethod
  def authenticate(self) -> Session: ...

  @classmethod
  def create(cls, name: str) -> AuthStrategy:
    try:
      return cls.registry[name]()
    except KeyError:
      raise UnknownFlowError(
        f"Unknow authentication method, available: {list(AuthStrategy.registry.keys())}"
      ) from None

  def get_token(self, base: str, end_point: str, data: dict[str, str]) -> Session:
    logger.info(f"Auth: Obtaining token from {end_point}")
    url = httpx.URL(base).join(end_point)

    res = httpx.post(url, data=data, timeout=30)
    if res.is_error:
      raise AuthenticationError(res.status_code, res.text)
    body = res.json()

    logger.info("Auth: Token Obtained")
    try:
      s = Session(**body)
    except ValidationError as exc:
      raise AuthenticationError(f"Auth: body return incorrect format: {body}") from exc

    return s


@dataclass
class ClientCredentialsFlow(AuthStrategy):
  name = "client_credentials"
  grant_type = "client_credentials"

  settings: ClientCredentialsSettings = field(default_factory=ClientCredentialsSettings)

  def authenticate(self) -> Session:

    return self.get_token(
      self.settings.domain_url,
      "services/oauth2/token",
      {
        "grant_type": self.grant_type,
        "client_id": self.settings.client_id,
        "client_secret": self.settings.client_secret,
      },
    )


@dataclass
class JWTFLow(AuthStrategy):
  name = "jwt"
  grant_type: str = "urn:ietf:params:oauth:grant-type:jwt-bearer"

  settings: JWTSettings = field(default_factory=JWTSettings)

  def authenticate(self) -> Session:
    claim = {
      "iss": self.settings.client_id,
      "sub": self.settings.user_name,
      "aud": self.settings.audiance,
      "exp": int(time.time()) + 100,
    }

    assertion = jwt.encode(
      claim,
      Path(self.settings.privatekey_file).expanduser().read_text(),
      headers={"alg": self.settings.algorithm},
    )

    return self.get_token(
      self.settings.domain_url,
      "services/oauth2/token",
      data={"grant_type": self.grant_type, "assertion": assertion},
    )
