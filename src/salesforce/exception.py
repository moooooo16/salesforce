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


class BulkJobError(SalesforceError):
  """A Bulk API job did not complete successfully."""

  def __init__(self, job_id: str, state: str, message: str = "") -> None:
    self.job_id = job_id
    self.state = state
    super().__init__(f"Bulk job {job_id} ended in state {state}: {message}")
