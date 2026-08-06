---
name: mcp-cli
description: >-
  CLI for MCP (Model Context Protocol) servers — connect via HTTP or stdio
  transport. Use when querying MCP tools, listing resources, calling prompts,
  or debugging MCP server connectivity. Similar to curl for MCP endpoints.
  Don't use for non-MCP RPC calls (use stubby-call instead).
---

# MCP CLI Skill

Query and interact with MCP servers from the command line.

> [!IMPORTANT]
>
> **Always prefer remote MCP servers.** Local servers take significant time (13s
> to 30+ seconds, sometimes several minutes) to start. Remote servers connect in
> under 2 seconds. For MCP servers not available as remote servers, prefer a
> simple CLI tool if one exists rather than starting a local MCP server.

<!-- disableFinding(HEADING_REPEAT_H1) -->

## Quick Start

Prefer using the pre-built binary (available on all gLinux machines):

```bash
MCP_CLI=/google/bin/releases/gemini-agents-mcp/mcp_cli
```

Alternatively, install via apt (the `mcp_cli` binary will be available directly
on PATH):

```bash
sudo glinux-add-repo -b gemini-agents-mcp stable
sudo apt update && sudo apt install -y gemini-agents-mcp
```

If you modify the CLI source code, build from source:

```bash
blaze build //learning/gemini/agents/clis/mcp_cli:mcp_cli
MCP_CLI=blaze-bin/learning/gemini/agents/clis/mcp_cli/mcp_cli
```

**Option 1: Start Codemind HTTP server (fast, recommended):**

```bash
/google/bin/releases/codemind-mcp-server-v2/codemind-mcp-server.par \
--transport=sse --port=8080 --alsologtostderr &

# Then use --url for all commands

$MCP_CLI tools --url http://localhost:8080/sse
$MCP_CLI call --url http://localhost:8080/sse --tool get_current_workspace
```

**Option 2: Use binary directly (slower, ~13s startup each time):**

```bash
$MCP_CLI tools --binary /google/bin/releases/codemind-mcp-server-v2/codemind-mcp-server.par
```

**Option 3: Use CLI to start/manage servers:**

```bash
$MCP_CLI start --binary /google/bin/releases/codemind-mcp-server-v2/codemind-mcp-server.par
$MCP_CLI status
$MCP_CLI stop --name codemind-mcp-server.par
```

## MCP Transport Types

There are two ways to connect to an MCP server:

**1. Remote MCP (preferred)** — Uses `remote_mcp` as a stdio proxy to a blade
server. The MCP server runs as a managed production service. This is faster,
more reliable, and requires no local resources.

```bash
$MCP_CLI tools \
  --binary=/google/bin/releases/gemini-cli/tools/remote_mcp \
  --server_args='--use_gaia_mint=True,--mcp_server=blade:devtools.buganizer.mcpservice-prod'
```

**2. Local binary MCP** — Runs the MCP server as a local process. Slower
startup, uses local resources, and may require building first. Use only when no
remote server exists.

```bash
$MCP_CLI tools \
  --binary=/google/bin/releases/codemind-mcp-server-v2/codemind-mcp-server.par
```

Always prefer remote MCP servers when available — they are production-grade,
faster to connect, and don't consume local compute. See
[references/mcps.md](references/mcps.md) for a catalog of 70+ known MCP servers
with their transport types.

## Registered Servers

Register MCP servers here for easy reference:

> **Codemind** - 69 tools (Buganizer, Critique, Piper, Drive, XManager) `Binary:
> /google/bin/releases/codemind-mcp-server-v2/codemind-mcp-server.par HTTP args:
> --transport=sse --port=8080 --alsologtostderr`

> **Buganizer** - 32 tools (create/edit/search bugs, hotlists, components)
> `Binary: /google/bin/releases/gemini-cli/tools/remote_mcp Args:
> --use_gaia_mint=True,--mcp_server=blade:devtools.buganizer.mcpservice-prod,--credential_exchanger_call_gaia_client_with_compass_stub_task_percentage=0`

> **Plx MCP** - 35 tools (SQL queries, data warehouse, analytics) `Build: blaze
> build //datawarehouse/plx/ai/mcp_bridge:plx_mcp Binary:
> blaze-bin/datawarehouse/plx/ai/mcp_bridge/plx_mcp Note: Slow startup (~30s)
> due to RPC connections`

## Commands

Command     | Description
----------- | -----------------------------------------------
`tools`     | List available tools (use `--search` to filter)
`call`      | Call a specific tool
`schema`    | Get input and output schema for a specific tool
`ping`      | Ping server to check connectivity
`resources` | List available resources
`start`     | Start HTTP server from a binary
`stop`      | Stop a running HTTP server
`status`    | Show status of running servers

## Options

Option          | Description
--------------- | -----------------------------------------------
`--url`         | HTTP URL (e.g., http://localhost:8080/sse)
`--binary`      | Path to MCP server binary
`--server_args` | Comma-separated args for server
`--name`        | Name for tracking (defaults to binary basename)
`--tool`        | Tool name (required for `call` and `schema`)
`--args`        | JSON arguments for tool call
`--search`      | Filter tools by name/description

## Performance

Mode               | Latency | Notes
------------------ | ------- | ------------------------
HTTP (`--url`)     | ~1.8s   | Fast, recommended
stdio (`--binary`) | ~13s+   | Server startup each time

## References

-   [references/mcps.md](references/mcps.md) — Catalog of all known MCP servers
-   [go/official-1p-mcp-servers-and-tools](http://go/official-1p-mcp-servers-and-tools)
-   [go/mcp](http://go/mcp) - MCP overview

## Reporting Issues

Report bugs or improvements for this skill at
[Agent Skill: mcp_cli](http://b/hotlists/8077537). See the `skill_issue` skill
for instructions on filing and triaging skill bugs.
