from dataclasses import dataclass
from abc import ABC


@dataclass
class Result:
  pass


@dataclass
class ErrorMsg:
  message: str
  error_code: str


@dataclass
class PostResult(Result):
  id: str
  errors: list[ErrorMsg | None]
  success: bool


class Client(ABC):
  def get(self):

    pass

  def post(self, url: str, **kw) -> Result:

    return PostResult(id="", errors=[], success=True)
