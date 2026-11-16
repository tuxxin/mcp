# issued.live MCP server

issued.live indexes certificate transparency logs and the DNS resolution of the names in them. The MCP server answers which certificates exist for a domain, which addresses it has resolved to, which domains share an address or a /24, and which domains were registered recently.

| | |
| --- | --- |
| Endpoint | `https://issued.live/mcp` |
| Transport | Streamable HTTP, JSON-RPC 2.0 over POST, protocol `2025-06-18`, stateless |
| Auth | Optional API key |
| Client key | `tuxxin-issued-live` |
| Docs | https://issued.live/developers |

`/mcp` accepts POST only. A GET returns 405.

## Client config

[`mcp.json`](mcp.json):

```json
{
  "mcpServers": {
    "tuxxin-issued-live": {
      "type": "http",
      "url": "https://issued.live/mcp"
    }
  }
}
```

The config uses the free tier. To use a paid key, add a header that reads it from `ISSUED_LIVE_API_KEY`:

```json
{
  "mcpServers": {
    "tuxxin-issued-live": {
      "type": "http",
      "url": "https://issued.live/mcp",
      "headers": {
        "Authorization": "Bearer ${ISSUED_LIVE_API_KEY}"
      }
    }
  }
}
```

Claude Code:

```sh
claude mcp add --transport http tuxxin-issued-live https://issued.live/mcp
```

## Authentication

`lookup_domain`, `recent_certificates` and `corpus_stats` work without a key. The other tools need an issued.live API key on the plan listed in the Access column. Without a key they return HTTP 200 with a tool error that names the plan.

Send the key in the `Authorization` header of the MCP request:

```
Authorization: Bearer <ISSUED_LIVE_API_KEY>
```

Keys come with a plan from https://issued.live/pricing (Basic $39, Plus $99, Pro $199 a month) or can be requested at https://issued.live/contact.

## Tools

| Tool | Access | Description |
| --- | --- | --- |
| [`lookup_domain`](#lookup_domain) | Free | Certificate record and every address the domain apex has resolved to. |
| [`recent_certificates`](#recent_certificates) | Free | Certificates logged in the last 30 minutes, newest first. |
| [`corpus_stats`](#corpus_stats) | Free | Corpus size, freshness, DNS coverage, CT log health and top issuers. |
| [`domain_detail`](#domain_detail) | Plus plan | Full record for one domain: registration timing, addresses with network data, and certificates with SANs. |
| [`domains_on_ip`](#domains_on_ip) | Plus plan | Hostnames observed resolving to one IP address. |
| [`domains_in_range`](#domains_in_range) | Plus plan | Hostnames observed on any address in a CIDR range of up to 256 addresses. |
| [`get_certificate`](#get_certificate) | Plus plan | One certificate by cert_id or SHA-256, with its full SAN list. |
| [`certificates_by_key`](#certificates_by_key) | Plus plan | Certificates issued for one public key (SPKI SHA-256), first seen in the last 32 hours. |
| [`domain_timeline`](#domain_timeline) | Plus plan | Dated sequence of zone, certificate and DNS observations for one domain. |
| [`new_domains`](#new_domains) | Pro plan | Newly registered domains from ICANN zone files, cursor-paged oldest first. |
| [`search_domains`](#search_domains) | Pro plan | Registrable domains matching a name pattern, optionally by nameserver. |
| [`lookup_domains`](#lookup_domains) | Pro plan | Up to 500 domains in one call. |
| [`provisioning`](#provisioning) | Pro plan | Domains whose registration, first certificate and first DNS answer fall inside a short window. |
| [`certificates_on_ip`](#certificates_on_ip) | Pro plan | Certificates for the hostnames observed on one IP address, in issuance order. |
| [`list_dataset_files`](#list_dataset_files) | Any subscription | Bulk dataset files the subscription can download today. |

### lookup_domain

Certificate record and every address the domain apex has resolved to. Access: Free.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `domain` | string | yes |  | A domain name or a URL containing one, e.g. |

### recent_certificates

Certificates logged in the last 30 minutes, newest first. Access: Free.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `limit` | integer |  |  | How many certificates to return. |

### corpus_stats

Corpus size, freshness, DNS coverage, CT log health and top issuers. Access: Free.

No parameters.

### domain_detail

Full record for one domain: registration timing, addresses with network data, and certificates with SANs. Access: Plus plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `domain` | string | yes |  | A domain name or a URL containing one, e.g. |

### domains_on_ip

Hostnames observed resolving to one IP address. Access: Plus plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `ip` | string | yes |  | A single IPv4 or IPv6 address, e.g. |
| `limit` | integer |  |  | Maximum hostnames to return. |
| `after` | string |  |  | Paging. |
| `first_seen_from` | string |  |  | Only hostnames FIRST observed at this address at or after this time. |
| `first_seen_to` | string |  |  | Only hostnames first observed at or before this time. |

### domains_in_range

Hostnames observed on any address in a CIDR range of up to 256 addresses. Access: Plus plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `cidr` | string | yes |  | A CIDR range covering at most 256 addresses, e.g. |
| `limit` | integer |  |  | Maximum hostnames to return. |
| `after` | string |  |  | Paging. |
| `first_seen_from` | string |  |  | Only hostnames FIRST observed at this address at or after this time. |
| `first_seen_to` | string |  |  | Only hostnames first observed at or before this time. |

### get_certificate

One certificate by cert_id or SHA-256, with its full SAN list. Access: Plus plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `id` | string | yes |  | A 32-hex cert_id (ssl_cert on a domain record) or a 64-hex certificate SHA-256. |

### certificates_by_key

Certificates issued for one public key (SPKI SHA-256), first seen in the last 32 hours. Access: Plus plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `spki_sha256` | string | yes |  | The 64-hex SHA-256 of the SubjectPublicKeyInfo, as get_certificate reports it. |

### domain_timeline

Dated sequence of zone, certificate and DNS observations for one domain. Access: Plus plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `domain` | string | yes |  | A domain name or a URL containing one. |

### new_domains

Newly registered domains from ICANN zone files, cursor-paged oldest first. Access: Pro plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `limit` | integer |  |  | Domains per page. |
| `after` | string |  |  | The next_cursor from the previous call. |
| `certified` | boolean |  |  | Only newly registered domains that have since appeared in a certificate. |
| `max_hours_to_cert` | number |  |  | With certified: only domains certified within this many hours of registration. |
| `since` | string |  |  | Window start, RFC3339 or YYYY-MM-DD, UTC. |
| `until` | string |  |  | Window end, RFC3339 or YYYY-MM-DD, UTC. |
| `tld` | string |  |  | Only this TLD, e.g. |

### search_domains

Registrable domains matching a name pattern, optionally by nameserver. Access: Pro plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | string | yes |  | The pattern, e.g. |
| `ns` | string |  |  | Only domains delegated to this nameserver. |
| `limit` | integer |  |  | Rows per page. |
| `after` | string |  |  | The next_cursor from the previous call. |

### lookup_domains

Up to 500 domains in one call. Access: Pro plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `domains` | string[] | yes |  | Domain names, up to 500. |
| `include` | string[] |  |  | Optional sub-lists for each found domain. |

### provisioning

Domains whose registration, first certificate and first DNS answer fall inside a short window. Access: Pro plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `tld` | string |  |  | Only this TLD. |
| `ns` | string |  |  | Only domains delegated to this nameserver. |
| `since` | string |  |  | Window start, RFC3339 or YYYY-MM-DD, UTC. |
| `until` | string |  |  | Window end, RFC3339 or YYYY-MM-DD, UTC. |
| `max_hours_to_cert` | number |  |  | Registration to first certificate, at most this many hours. |
| `cert_to_dns_max` | number |  |  | First certificate to first DNS answer, at most this many hours. |
| `include_cert_before_zone` | boolean |  |  | Also include domains certified BEFORE a zone file listed them. |
| `limit` | integer |  |  | Rows per page. |
| `after` | string |  |  | The next_cursor from the previous call. |

### certificates_on_ip

Certificates for the hostnames observed on one IP address, in issuance order. Access: Pro plan.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `ip` | string | yes |  | A single IPv4 or IPv6 address. |
| `from` | string |  |  | First observation day, YYYY-MM-DD (UTC). |
| `to` | string |  |  | Last observation day, YYYY-MM-DD (UTC). |
| `issuer` | string |  |  | Only this issuer organization, e.g. |
| `wildcard` | boolean |  |  | true: only certificates reaching a hostname through a wildcard SAN; false: only through an exact SAN. |
| `order` | string: `asc`, `desc` |  |  | By valid_from; asc (default) is oldest first. |
| `limit` | integer |  |  | Certificates per page. |
| `after` | string |  |  | The next_cursor from the previous call. |

### list_dataset_files

Bulk dataset files the subscription can download today. Access: Any subscription.

No parameters.

## Rate limits

| Plan | Requests | Notes |
| --- | --- | --- |
| Free (no key) | 1,000 a day per client IP, reset 00:00 UTC | Free tools only |
| Basic | 60 a minute, no daily cap | |
| Plus | 300 a minute, no daily cap | 1 advanced query in flight |
| Pro | 1,200 a minute, no daily cap | 2 advanced queries in flight |

Over the limit the server returns 429 with `Retry-After`.
