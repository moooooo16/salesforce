from salesforce.client.auth import ClientCredentialsFlow

cl = ClientCredentialsFlow.create("client_credentials")

cl.authenticate()
