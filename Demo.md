# Demo docs

This demo shows how triggering an error results in a message being posted to Slack via our sre-agent bot.

To do this, the bot needs some Kubernetes secret to work.

## Step 1: Check if the secret already exists
There are 3 secret you will need to create if you have not already done so.

### Secret 1: 

Run the following command:
```bash
kubectl describe secret slack-bot-secret
```

If the secret is present, you should see something like this:

```bash
Name:         slack-bot-secret
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
SLACK_BOT_TOKEN:  56 bytes
```


### Secret 2: 

Run the following command:
```bash
kubectl describe secret slack-channel-id
```

If the secret is present, you should see something like this:

```bash
Name:         slack-channel-id
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
SLACK_CHANNEL_ID:  11 bytes
```

### Secret 3:

Run the following command:
```bash
kubectl describe secret mcp-client-endpoint
```

If the secret is present, you should see something like this:

```bash
Name:         mcp-client-endpoint
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
MCP_CLIENT_ENDPOINT:  87 bytes
```

### Secret 4:

Run the following command:
```bash
kubectl describe secret client-endpoint-bearer-token
```

If the secret is present, you should see something like this:

```bash
Name:         client-endpoint-bearer-token
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
CLIENT-ENDPOINT-BEARER-TOKEN:  11 bytes
```

## Step 2: Create the secret (if they don't exists)

### Secret 1: 

If the secret doesn’t exist, create it by running:
```bash
kubectl create secret generic slack-bot-secret \
  --from-literal=SLACK_BOT_TOKEN=<slack-bot-token>
```

Replace `<slack-bot-token>` with your actual Slack bot token.

### Secret 2: 
The secret contains the ID of the channel which you want to post message to.

If the secret doesn’t exist, create it by running:
```bash
kubectl create secret generic slack-channel-id \
  --from-literal=SLACK_CHANNEL_ID=<slack-channel-id>
```

Replace `<slack-channel-id>` with the ID of the channel that you want the agent to post error messages to.

### Secret 3:
This secret contains the endpoint of the MCP client.

If the secret doesn’t exist, create it by running:
```bash
kubectl create secret generic mcp-client-endpoint \
  --from-literal=MCP_CLIENT_ENDPOINT=<mcp-client-endpoint>
```

Replace `<mcp-client-endpoint>` with the publicly expose endpoint.

### Secret 4:
This secret contains the bearer token for the MCP client endpoint.

If the secret doesn’t exist, create it by running:
```bash
kubectl create secret generic client-endpoint-bearer-token \
  --from-literal=CLIENT_ENDPOINT_BEARER_TOKEN=<client-endpoint-bearer-token>
```

Replace `<client-endpoint-bearer-token>` with the bearer token.