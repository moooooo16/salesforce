class SalesforceError(Exception):
  """All Salesforce Errors"""


# Authentication Erros
class AuthenticationError(SalesforceError):
  """Authentication Errors"""


class UnknownFlowError(AuthenticationError):
  """Wrong Athentication Error selected"""
