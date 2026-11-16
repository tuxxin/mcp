#!/usr/bin/env python3
"""Validate manifest.json, every servers/*/mcp.json and all-servers.mcp.json.

Checks JSON syntax, the manifest schema, and that the manifest, the per-server configs
and the combined config agree with each other. Exits non-zero on the first run with errors.

Usage: python3 scripts/validate.py   (from the repository root)
"""
import glob
import json
import os
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def load(rel):
    path = os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{rel}: {e}")
        return None


def check_ascii(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        for n, line in enumerate(f, 1):
            if any(b > 0x7F for b in line):
                errors.append(f"{rel}:{n}: non-ASCII character")


def check_client_block(rel, key, blk):
    if not isinstance(blk, dict):
        errors.append(f"{rel}: {key} must be an object")
        return
    if blk.get("type") != "http":
        errors.append(f"{rel}: {key}.type must be \"http\"")
    if not str(blk.get("url", "")).startswith("https://"):
        errors.append(f"{rel}: {key}.url must be an https URL")
    for name, value in (blk.get("headers") or {}).items():
        if re.search(r"(wfk|wsk)_[A-Za-z0-9]{6,}", str(value)):
            errors.append(f"{rel}: {key}.headers.{name} holds what looks like a real key")
        if "${" not in str(value):
            errors.append(f"{rel}: {key}.headers.{name} must use an environment variable placeholder")


# 1. Manifest against its schema.
schema = load("schemas/manifest.schema.json")
manifest = load("manifest.json")
if schema and manifest:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for e in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        errors.append(f"manifest.json: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}")

# 2. Per-server files exist and match the manifest.
combined = load("all-servers.mcp.json")
expected = {}
if manifest:
    ids = [s.get("id") for s in manifest.get("servers", [])]
    if len(ids) != len(set(ids)):
        errors.append("manifest.json: duplicate server id")
    for s in manifest.get("servers", []):
        sid = s.get("id", "?")
        for field in ("config_path", "docs_path"):
            if field in s and not os.path.isfile(os.path.join(ROOT, s[field])):
                errors.append(f"manifest.json: {sid}.{field} points to a missing file: {s[field]}")
        for t in s.get("tools", []):
            missing = set(t.get("required", [])) - set(t.get("parameters", []))
            if missing:
                errors.append(f"manifest.json: {sid}.{t.get('name')}: required names unknown parameters {sorted(missing)}")
        cfg = load(s["config_path"]) if os.path.isfile(os.path.join(ROOT, s.get("config_path", ""))) else None
        if cfg is None:
            continue
        servers = cfg.get("mcpServers", {})
        key = s.get("client_key")
        if list(servers) != [key]:
            errors.append(f"{s['config_path']}: must hold exactly one server named {key}")
            continue
        blk = servers[key]
        check_client_block(s["config_path"], key, blk)
        if blk.get("url") != s.get("transport", {}).get("url"):
            errors.append(f"{s['config_path']}: url differs from manifest transport.url")
        auth = s.get("auth", {})
        if auth.get("required") and auth.get("env_var") and auth["env_var"] not in json.dumps(blk):
            errors.append(f"{s['config_path']}: required auth but no ${{{auth['env_var']}}} placeholder")
        expected[key] = blk

    # 3. Server folders without a manifest entry.
    listed = {os.path.dirname(s.get("config_path", "")) for s in manifest.get("servers", [])}
    for d in sorted(glob.glob(os.path.join(ROOT, "servers", "*"))):
        rel = os.path.relpath(d, ROOT)
        if os.path.isdir(d) and rel not in listed:
            errors.append(f"{rel}: folder has no entry in manifest.json")

# 4. Combined config equals the union of the per-server configs.
if combined is not None and manifest:
    if combined.get("mcpServers") != expected:
        errors.append("all-servers.mcp.json: does not match the union of servers/*/mcp.json")

# 5. ASCII-only text in every tracked JSON and Markdown file.
for rel in sorted(glob.glob("**/*.json", root_dir=ROOT, recursive=True) +
                  glob.glob("**/*.md", root_dir=ROOT, recursive=True)):
    check_ascii(rel)

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok: {len(manifest['servers'])} servers, manifest and client configs agree")
