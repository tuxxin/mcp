# curlhub.sh MCP server

curlhub.sh turns a structured HTTP request into a curl command. The tool returns a shell string and an argv array; spawning the argv array directly avoids shell quoting.

| | |
| --- | --- |
| Endpoint | `https://curlhub.sh/mcp` |
| Transport | Streamable HTTP, JSON-RPC 2.0 over POST, protocol `2025-06-18`, stateless |
| Auth | None |
| Client key | `tuxxin-curlhub` |
| Docs | https://curlhub.sh/llms.txt |
| Server card | https://curlhub.sh/.well-known/mcp/server-card.json |

`/mcp` accepts POST only. A GET returns 405.

## Client config

[`mcp.json`](mcp.json):

```json
{
  "mcpServers": {
    "tuxxin-curlhub": {
      "type": "http",
      "url": "https://curlhub.sh/mcp"
    }
  }
}
```

Claude Code:

```sh
claude mcp add --transport http tuxxin-curlhub https://curlhub.sh/mcp
```

## Authentication

None. The server takes no key and no sign-in.

## Tools

### validate_and_format_curl

Build a curl command from method, URL, headers and body; rejects non-http(s) schemes and control characters. Access: Free.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `url` | string | yes |  | Target http(s) URL. |
| `method` | string: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS` |  | `GET` |  |
| `headers` | object |  |  | Header name -> value. |
| `data` | string |  |  | Raw request body. |

## Rate limits

60 requests a minute per client IP, shared with the curlhub.sh transform tools. A 429 carries `Retry-After`.
