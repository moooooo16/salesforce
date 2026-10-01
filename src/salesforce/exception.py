class SalesforceError(Exception):
  """All Salesforce Errors"""


# Authentication Erros
class AuthenticationError(SalesforceError):
  """Authentication Errors"""


class UnknownFlowError(AuthenticationError):
  """Wrong Athentication Error selected"""


class ApiError(SalesforceError):
  """Salesforce REST API returned an error response."""

  def __init__(self, status_code: int, body: str) -> None:
    self.status_code = status_code
    self.body = body
    super().__init__(f"Salesforce API error {status_code}: {body[:200]}")
