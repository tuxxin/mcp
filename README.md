# Tuxxin MCP servers

Model Context Protocol servers run by [Tuxxin LLC](https://tuxxin.com). Every server uses the Streamable HTTP transport (JSON-RPC 2.0 over POST, protocol `2025-06-18`) and is stateless. This repository holds the registry, client configs and docs. The servers run on each product's own domain.

| Service | Domain | Endpoint | Auth | Capabilities |
| --- | --- | --- | --- | --- |
| [issued.live](servers/issued-live/README.md) | issued.live | `https://issued.live/mcp` | None for 3 tools; API key for 12 | Certificate transparency search, domain DNS history, reverse IP, newly registered domains |
| [curlhub.sh](servers/curlhub/README.md) | curlhub.sh | `https://curlhub.sh/mcp` | None | Build escaped curl commands from a structured request |
| [webshot.site](servers/webshot/README.md) | webshot.site | `https://webshot.site/mcp` | None; optional `wsk_` key | Sandboxed screenshots and PDFs of public URLs |
| [webfetch.io](servers/webfetch/README.md) | webfetch.io | `https://webfetch.io/mcp` | `wfk_` key required | Page fetch to markdown, selector extraction to JSON, search engine results |
| [WorldIP.io](servers/worldip/README.md) | worldip.io | `https://worldip.io/mcp` | None | IPv4 and IPv6 owner, ASN, geolocation, reverse DNS |

## Machine-readable registry

[`manifest.json`](manifest.json) lists every server with its endpoint, auth, rate limits and tools. It validates against [`schemas/manifest.schema.json`](schemas/manifest.schema.json).

```
https://raw.githubusercontent.com/tuxxin/mcp/main/manifest.json
```

## Quickstart

Each server has a drop-in config at `servers/<id>/mcp.json`. [`all-servers.mcp.json`](all-servers.mcp.json) combines all five. Server names use a `tuxxin-` prefix to avoid collisions with other servers in the same client.

### Claude Code

Add one server:

```sh
claude mcp add --transport http tuxxin-worldip https://worldip.io/mcp
```

Add a server that needs a key:

```sh
export WEBFETCH_API_KEY=wfk_your_key
claude mcp add --transport http tuxxin-webfetch https://webfetch.io/mcp \
  --header "Authorization: Bearer $WEBFETCH_API_KEY"
```

Add all five to a project by copying `all-servers.mcp.json` to `.mcp.json` in the project root. Claude Code expands `${WEBFETCH_API_KEY}` from the environment when it loads the file, so the key stays out of the file. Remove the `tuxxin-webfetch` block if you have no webfetch.io key.

### Claude Desktop and claude.ai

For servers without a key, open Settings > Connectors > Add custom connector and enter the endpoint URL. WorldIP.io is also listed in the connector directory.

Custom connectors cannot send an `Authorization` header. For webfetch.io, or a paid key on issued.live or webshot.site, add the server to `claude_desktop_config.json` through [`mcp-remote`](https://www.npmjs.com/package/mcp-remote), which needs Node.js:

```json
{
  "mcpServers": {
    "tuxxin-webfetch": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://webfetch.io/mcp", "--header", "Authorization:${AUTH_HEADER}"],
      "env": { "AUTH_HEADER": "Bearer wfk_your_key" }
    }
  }
}
```

### Cursor

Copy the blocks you want from `all-servers.mcp.json` into `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project). Cursor reads environment variables as `${env:NAME}`, so change the webfetch header to:

```json
"headers": { "Authorization": "Bearer ${env:WEBFETCH_API_KEY}" }
```

### VS Code

VS Code uses a `servers` key in `.vscode/mcp.json` and can prompt for the key:

```json
{
  "inputs": [
    { "type": "promptString", "id": "webfetch-key", "description": "webfetch.io API key", "password": true }
  ],
  "servers": {
    "tuxxin-worldip": { "type": "http", "url": "https://worldip.io/mcp" },
    "tuxxin-webfetch": {
      "type": "http",
      "url": "https://webfetch.io/mcp",
      "headers": { "Authorization": "Bearer ${input:webfetch-key}" }
    }
  }
}
```

### Other clients

Any client that supports Streamable HTTP can connect with the endpoint URL. Check a server with curl:

```sh
curl -s https://worldip.io/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

`/mcp` accepts POST only and returns 405 to a GET.

## Authentication

| Server | Header | Environment variable | Get a key |
| --- | --- | --- | --- |
| issued.live | `Authorization: Bearer <key>` (Plus, Pro and subscriber tools) | `ISSUED_LIVE_API_KEY` | https://issued.live/pricing |
| webshot.site | `Authorization: Bearer wsk_...` (optional, paid plans) | `WEBSHOT_API_KEY` | https://webshot.site/pricing |
| webfetch.io | `Authorization: Bearer wfk_...` (required) | `WEBFETCH_API_KEY` | https://webfetch.io/signup |

curlhub.sh and WorldIP.io take no key. Keep keys in environment variables or a secret store. A key written into a shared `.mcp.json` is visible to everyone with access to the repository.

## Adding a server

1. Add an entry to `manifest.json` with a new `id` and a `tuxxin-<id>` `client_key`.
2. Create `servers/<id>/mcp.json` and `servers/<id>/README.md`.
3. Add the same block to `all-servers.mcp.json`.
4. Run `pip install "jsonschema[format]"` and then `python3 scripts/validate.py`.

The [validate](.github/workflows/validate.yml) workflow runs the same check on every push and pull request. It checks the schema, confirms each config matches its manifest entry and the combined file, rejects literal API keys in headers, and rejects non-ASCII characters.
