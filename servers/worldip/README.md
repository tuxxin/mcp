# WorldIP.io MCP server

WorldIP.io profiles public IPv4 and IPv6 addresses: owner, ASN, location, CIDR, reverse DNS and forward-confirmed DNS. IPv4 profiles include a daily count of the domains hosted on the address.

| | |
| --- | --- |
| Endpoint | `https://worldip.io/mcp` |
| Transport | Streamable HTTP, JSON-RPC 2.0 over POST, protocol `2025-06-18`, stateless |
| Auth | None |
| Client key | `tuxxin-worldip` |
| Docs | https://worldip.io/llms.txt |
| Server card | https://worldip.io/.well-known/mcp/server-card.json |

`/mcp` accepts POST only. A GET returns 405.

## Client config

[`mcp.json`](mcp.json):

```json
{
  "mcpServers": {
    "tuxxin-worldip": {
      "type": "http",
      "url": "https://worldip.io/mcp"
    }
  }
}
```

Claude Code:

```sh
claude mcp add --transport http tuxxin-worldip https://worldip.io/mcp
```

## Authentication

None. The server takes no key, no sign-in and no OAuth.

## Tools

### lookup_ip

Profile of a public IPv4 or IPv6 address: owner, ASN, location, CIDR, PTR and forward-confirmed DNS. Access: Free.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `ip` | string | yes |  | Public IPv4 or IPv6 address, e.g. |

### whats_my_ip

The caller's own public IP address and its profile. Access: Free.

No parameters.

## Rate limits

1,000 requests a day and 60 a minute per client IP. The limit is shared with the keyless worldip.io JSON API.
