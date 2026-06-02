# Sample GitHub App

This sample app showcases how webhooks can be used with a GitHub App's installation token to create a bot that responds to issues. Code uses [octokit.js](https://github.com/octokit/octokit.js).

## Requirements

- Node.js 20 or higher
- A GitHub App subscribed to **Pull Request** events and with the following permissions:
  - Pull requests: Read & write
  - Metadata: Read-only
- (For local development) A tunnel to expose your local server to the internet (e.g. [smee](https://smee.io/), [ngrok](https://ngrok.com/) or [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/local/))
- Your GitHub App Webhook must be configured to receive events at a URL that is accessible from the internet.

## Setup

1. Clone this repository.
2. Create a `.env` file similar to `.env.example` and set actual values. If you are using GitHub Enterprise Server, also include a `ENTERPRISE_HOSTNAME` variable and set the value to the name of your GitHub Enterprise Server instance.
3. Install dependencies with `npm install`.
4. Start the server with `npm run server`.
5. Ensure your server is reachable from the internet.
    - If you're using `smee`, run `smee -u <smee_url> -t http://localhost:3000/api/webhook`.
6. Ensure your GitHub App includes at least one repository on its installations.

## Usage

With your server running, you can now create a pull request on any repository that
your app can access. GitHub will emit a `pull_request.opened` event and will deliver
the corresponding Webhook [payload](https://docs.github.com/webhooks-and-events/webhooks/webhook-events-and-payloads#pull_request) to your server.

The server in this example listens for `pull_request.opened` events and acts on
them by creating a comment on the pull request, with the message in `message.md`,
using the [octokit.js rest methods](https://github.com/octokit/octokit.js#octokitrest-endpoint-methods).

## Security considerations

To keep things simple, this example reads the `GITHUB_APP_PRIVATE_KEY` from the
environment. A more secure and recommended approach is to use a secrets management system
like [Vault](https://www.vaultproject.io/use-cases/key-management), or one offered
by major cloud providers:
[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-node?tabs=windows),
[AWS Secrets Manager](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-secrets-manager/),
[Google Secret Manager](https://cloud.google.com/nodejs/docs/reference/secret-manager/latest),
etc.

## Gemini Enterprise (GE) Integration & Troubleshooting

This repository is configured to connect directly to Google Cloud's **Gemini Enterprise (GE)** as a custom Data Store connector.

### Connection Parameters
- **App Callback URL:** `https://vertexaisearch.cloud.google.com/oauth-redirect`
- **Owner Login:** Set this to your GitHub organization or account name (e.g., `brendanhills-altostrat`).
- **Required Credentials:** Client ID and Client Secret from your GitHub App's General settings.
- **Repository Selection:** Managed entirely on the GitHub side under your App settings (**Settings > Installed Apps > Configure**).

### ⚠️ Config Mismatch Finding: Invalid `owner_login` format

- **Symptoms:** Programmatic searches (`node query-ge.js`) return zero results, and GCP Logging registers authentication failures during search execution:
  `Connector projects/.../locations/us/collections/.../dataConnector authorization not found.`
- **Cause:** 
  Setting the `owner_login` parameter in the Data Connector setup to the full repository path (e.g., `brendanhills-altostrat/bh-experiments`) is invalid. Slashes are illegal in GitHub usernames, causing Gemini Enterprise's federated query to search for a user/org named `brendanhills-altostrat/bh-experiments`, which fails.
- **Solution:**
  1. The `owner_login` parameter must be strictly set to the owner/org username (e.g., `brendanhills-altostrat`).
  2. Control which repositories are indexed by managing the GitHub App's repository settings on GitHub (**Settings > Installed Apps > Configure** on your GitHub App), not in GCP.
  3. **CRITICAL STEP:** Any manual configuration updates or API PATCH edits to the Data Connector's parameters will invalidate existing OAuth tokens. You **must** go to the GCP Console under **Vertex AI Agent Builder > Data Stores**, click your GitHub store, and click the **"Log In"** or **"Re-authorize"** button to restore active query authorization.

### Crucial Security Finding & Workaround

> [!WARNING]
> **Error Code 7: `USER_AND_DATA_STORE_CUSTOMER_ID_MISMATCH`**
>
> **Symptoms:** The agent only returns irrelevant results or fails completely when querying GitHub data. In `cloudaudit.googleapis.com/data_access` logs, you will find:
> *"User does not belong to the same organization as the Workspace data store."*
>
> **Cause:**
> If your Gemini Enterprise App has Google Workspace data stores (e.g., Google Drive folders) connected that belong to one customer ID (e.g., `C02jmdbhs`), but you query the agent using a Google account belonging to a different customer ID (e.g., `C01foya18`), **Google Cloud strictly blocks the entire search request** to prevent cross-tenant data leaks.
>
> **Workaround:**
> 1. In your Gemini Enterprise App's **Connected data stores** settings page, **uncheck/disconnect** any Google Drive or Workspace data stores belonging to other tenants.
> 2. Leave **only the GitHub data store** connected (since it is an external connector, it is not bound by internal Google Workspace tenant boundaries).
> 3. Save/Connect and retry your query.


## Developer Utilities for Gemini Enterprise (GE)

To help you monitor and query your connector programmatically, this workspace includes two lightweight, robust Node.js tools:

### 1. Connector Ingestion Status Tool (`check-connector-status.js`)

This tool queries the status of the three distinct GitHub schemas in your `us` region data stores and scans GCP Stackdriver Logging for authentication and token errors.

* **To run the script:**
  ```bash
  node check-connector-status.js
  ```
* **Key Features:**
  - Performs native REST API calls using local `gcloud` access tokens.
  - Passes `'X-Goog-User-Project': 'uk-bh-experiments-argolis'` to prevent quota/billing block errors.
  - Dynamically routes requests to the correct **regional API endpoint** (`us-discoveryengine.googleapis.com`).
  - Reports exact error logs if Google Cloud is unable to authenticate with GitHub.

### 2. Search Query Tool (`query-ge.js`)

This tool allows you to perform search queries against your **"GE Demo"** app engine (`ge-demo_1760707227647`) directly from your terminal and displays the results beautifully.

* **To run the script (Default Query - "Large objects"):**
  ```bash
  node query-ge.js
  ```
* **To run with a Custom Query:**
  ```bash
  node query-ge.js "<search term>"
  ```
