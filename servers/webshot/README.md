# webshot.site MCP server

webshot.site renders a public URL in headless Chrome inside an isolated sandbox and returns a link to the image or PDF. Use it to inspect an unfamiliar or suspicious site without opening it in your own browser.

| | |
| --- | --- |
| Endpoint | `https://webshot.site/mcp` |
| Transport | Streamable HTTP, JSON-RPC 2.0 over POST, protocol `2025-06-18`, stateless |
| Auth | Optional API key |
| Client key | `tuxxin-webshot` |
| Docs | https://webshot.site/llms.txt |
| Server card | https://webshot.site/.well-known/mcp/server-card.json |

`/mcp` accepts POST only. A GET returns 405.

## Client config

[`mcp.json`](mcp.json):

```json
{
  "mcpServers": {
    "tuxxin-webshot": {
      "type": "http",
      "url": "https://webshot.site/mcp"
    }
  }
}
```

The config uses the free tier. To use a paid key, add a header that reads it from `WEBSHOT_API_KEY`:

```json
{
  "mcpServers": {
    "tuxxin-webshot": {
      "type": "http",
      "url": "https://webshot.site/mcp",
      "headers": {
        "Authorization": "Bearer ${WEBSHOT_API_KEY}"
      }
    }
  }
}
```

Claude Code:

```sh
claude mcp add --transport http tuxxin-webshot https://webshot.site/mcp
```

## Authentication

None for the free tier. A paid key (`wsk_` prefix) bills captures to the key's plan instead of the per-IP bucket:

```
Authorization: Bearer <WEBSHOT_API_KEY>
```

Keys are sold at https://webshot.site/pricing (Starter $1.99, Pro $6.99, Business $19.99 a month) and issued immediately. An invalid key returns 401. The server reads the key from the header only and ignores a key in the URL.

## Tools

### capture_sandbox_webshot

Screenshot or PDF of a public URL at desktop, tablet or mobile size; private and metadata addresses are refused. Access: Free.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `url` | string | yes |  | The http(s) URL to render. |
| `viewport` | string: `desktop`, `mobile`, `tablet` |  | `desktop` | Device profile to render with. |
| `full_page` | boolean |  | `false` | Capture the entire scrollable page rather than just the viewport. |
| `format` | string: `jpg`, `png`, `webp`, `pdf` |  | `jpg` |  |

## Rate limits

The free tier allows 5 credits per 15 minutes per client IP. A viewport capture costs 1 credit and a `full_page` capture costs 2, so the bucket covers 5 viewport captures or 2 full-page captures. Output format does not change the cost. A capture can take up to about 90 seconds; set a client timeout above that.

Paid keys use the allowance of their plan.
