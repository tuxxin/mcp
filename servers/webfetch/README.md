# webfetch.io MCP server

webfetch.io fetches pages for a model to read, extracts structured fields with CSS or XPath selectors, and returns search engine results as JSON. Every result reports the credits it cost.

| | |
| --- | --- |
| Endpoint | `https://webfetch.io/mcp` |
| Transport | Streamable HTTP, JSON-RPC 2.0 over POST, protocol `2025-06-18`, stateless |
| Auth | API key required |
| Client key | `tuxxin-webfetch` |
| Docs | https://webfetch.io/llms.txt |
| Server card | https://webfetch.io/.well-known/mcp/server-card.json |

`/mcp` accepts POST only. A GET returns 405.

## Client config

[`mcp.json`](mcp.json):

```json
{
  "mcpServers": {
    "tuxxin-webfetch": {
      "type": "http",
      "url": "https://webfetch.io/mcp",
      "headers": {
        "Authorization": "Bearer ${WEBFETCH_API_KEY}"
      }
    }
  }
}
```

Set `WEBFETCH_API_KEY` in the environment before starting the client. Claude Code expands `${VAR}` in `.mcp.json`; Cursor uses `${env:VAR}`.

Claude Code:

```sh
claude mcp add --transport http tuxxin-webfetch https://webfetch.io/mcp \
  --header "Authorization: Bearer $WEBFETCH_API_KEY"
```

## Authentication

Required on every call. Keys start with `wfk_`:

```
Authorization: Bearer <WEBFETCH_API_KEY>
```

Create a free account at https://webfetch.io/signup. It starts with 1,000 credits and gets 250 more on the 1st of each month, banking up to 1,000. `search_web` also needs search access on the key: paid plans turn it on in the key portal, and free accounts request it there.

## Tools

### fetch_page

Fetch a URL as markdown, text or HTML; 5 credits rendered, 1 credit with render_js false. Access: API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `url` | string | yes |  | The absolute http or https URL to fetch. |
| `render_js` | boolean |  | `true` | Render in a browser. |
| `return_format` | string: `markdown`, `text`, `html` |  | `markdown` | markdown and text strip the page chrome and are what a model usually wants. |

### extract_data

Fetch a URL and return JSON built from CSS or XPath selector rules. Access: API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `url` | string | yes |  | The absolute http or https URL to fetch. |
| `extract_rules` | object | yes |  | Map a name to a selector. |
| `render_js` | boolean |  | `true` | Render in a browser before extracting. |

A string rule returns the text of the first match, and `"a@href"` returns an attribute. An object rule can set `selector`, `selector_type` (`auto`, `css`, `xpath`), `type` (`item` or `list`) and `output` (`text`, `html`, `@attr`, `table_json`, `table_array`, or nested rules):

```json
{ "title": "h1", "links": { "selector": "a@href", "type": "list" } }
```

### search_web

One page of search results as JSON from Google, Bing, Yahoo or Brave; needs search access enabled on the key. Access: API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | string | yes |  | What to search for, as typed in the search box. |
| `engine` | string: `google`, `bing`, `yahoo`, `brave` |  | `google` | The search engine. |
| `country_code` | string |  | `us` | Two-letter country to search from. |
| `page` | integer |  | `1` | Results page. |
| `search_type` | string: `classic`, `ads` |  | `classic` | classic for the full page, ads for the ads only. |
| `light_request` | boolean |  | `true` | False loads the page in a browser, which on Bing includes the ads, at 15 credits. |

## Rate limits

Calls are metered in credits and only successful calls are charged.

| Call | Credits |
| --- | --- |
| `fetch_page` or `extract_data` with `render_js: false` | 1 |
| `fetch_page` or `extract_data` with JavaScript rendering (default) | 5 |
| `search_web` (default `light_request: true`) | 10 |
| `search_web` with `light_request: false` | 15 |

Concurrency is 5 requests on the Free plan and 25 to 400 on paid plans. Under heavy paid load a free request can receive HTTP 503 `free_tier_busy` with `Retry-After`; it is not charged.
