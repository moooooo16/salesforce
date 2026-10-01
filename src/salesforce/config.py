from typing import Annotated

from pydantic import AfterValidator, FilePath, HttpUrl, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict

_http_url = TypeAdapter(HttpUrl)


def to_url_str(v: str) -> str:
  if not (v.startswith("https://") or v.startswith("http://")):
    v = f"https:{v}"

  return str(_http_url.validate_python(v)).rstrip("/")


UrlStr = Annotated[str, AfterValidator(to_url_str)]


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_prefix="SF_",
    extra="ignore",
  )
  client_id: str
  domain_url: UrlStr


class ClientCredentialsSettings(Settings):
  client_secret: str


class JWTSettings(Settings):
  user_name: str
  privatekey_file: FilePath
  audiance: str = "https://login.salesforce.com"
  algorithm: str = "RS256"
