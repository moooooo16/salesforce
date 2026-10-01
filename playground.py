from salesforce import Salesforce

# Uncomment when using the sandbox/multi-credential examples below:
# from salesforce.config import ClientCredentialsSettings, JWTSettings

# ---------------------------------------------------------------------------
# 1. Connect
# ---------------------------------------------------------------------------

# Client credentials flow (reads .env by default)
sf = Salesforce.from_strategy("client_credentials")

# JWT bearer flow
# sf = Salesforce.from_strategy("jwt")

# Sandbox / second credential set: construct the flow directly
# with a different env file or prefix, then hand it to the client.
#
# from salesforce.client.client import Client
# from salesforce.client.auth import ClientCredentialsFlow, JWTFLow
#
# sandbox = Salesforce(Client(ClientCredentialsFlow(
#     settings=ClientCredentialsSettings(_env_file=".env.sandbox")
# )))
# sandbox = Salesforce(Client(JWTFLow(
#     settings=JWTSettings(_env_prefix="SANDBOX_SF_")
# )))

# ---------------------------------------------------------------------------
# 2. Query (SOQL) - auto-paginates
# ---------------------------------------------------------------------------

accounts = sf.query.query("SELECT Id, Name FROM Account LIMIT 10")
for a in accounts:
  print(a["Id"], a["Name"])

# Include deleted/archived records:
# sf.query.query_all("SELECT Id, Name FROM Account")

# ---------------------------------------------------------------------------
# 3. Record CRUD
# ---------------------------------------------------------------------------

account = sf.sobject("Account")

created = account.insert({"Name": "Playground Co"})
print(created["id"], created["success"])

record = account.get(
  created["id"],
  fields=["Name", "Phone"],
)
print(record)

account.update(created["id"], {"Phone": "416-555-0100"})
account.delete(created["id"])

# Metadata:
# account.metadata()   # basic info + recent items
# account.describe()   # full field/layout metadata

# ---------------------------------------------------------------------------
# 4. Search (SOSL)
# ---------------------------------------------------------------------------

results = sf.search.search("FIND {Playground} IN ALL FIELDS RETURNING Account(Id, Name)")
print(results)

# ---------------------------------------------------------------------------
# 5. Platform events
# ---------------------------------------------------------------------------

# sf.event.publish("Order__e", {"Order_Id__c": "A-1"})

# ---------------------------------------------------------------------------
# 6. Approval processes
# ---------------------------------------------------------------------------

# sf.process.approvals()
# sf.process.submit([{"actionType": "Submit", "contextId": "001xx...", "comments": "ok"}])
