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

# Upsert by external ID field (insert or update in one call):
# account.upsert("External_Id__c", "ERP-1001", {"Name": "Acme"})

# ---------------------------------------------------------------------------
# 3b. Collections: batch up to 200 records per call
# ---------------------------------------------------------------------------

# sf.collections("Account").insert([{"Name": "A"}, {"Name": "B"}])
# sf.collections("Account").update([{"Id": "001xx...", "Phone": "416..."}])
# sf.collections("Account").delete(["001xx...", "001yy..."])

# ---------------------------------------------------------------------------
# 3c. Org info
# ---------------------------------------------------------------------------

# sf.info.describe_global()   # all SObjects in this org
# sf.info.limits()            # API quota usage

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

# ---------------------------------------------------------------------------
# 7. Bulk API 2.0 - for large data loads
# ---------------------------------------------------------------------------

records = [{"Name": f"Bulk Co {i}"} for i in range(5)]
job = sf.bulk("Account").insert(records)
print(job["state"], job["numberRecordsProcessed"])

# Per-record results (CSV text):
# print(sf.bulk("Account").successful_results(job["id"]))
# print(sf.bulk("Account").failed_results(job["id"]))

# update / upsert / delete work the same way:
# sf.bulk("Account").update([{"Id": "001xx...", "Phone": "416..."}])
# sf.bulk("Account").upsert(records, external_id_field="External_Id__c")
# sf.bulk("Account").delete([{"Id": "001xx..."}])
