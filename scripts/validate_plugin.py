#!/usr/bin/env python3
"""Validate the foresdd plugin manifests in .claude-plugin/.

Checks that plugin.json and marketplace.json are valid JSON, carry the fields
Claude Code's loader needs (with the right types), and agree with each other on
name / version / description. Skill and agent content is NOT checked here —
behaviour is covered by the on-demand evals in evals/.

    python3 scripts/validate_plugin.py

Prints one line per check, then a summary. Exits 1 when any check fails.
CI also runs `claude plugin validate .` (the CLI's own schema check).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / ".claude-plugin"
PLUGIN_NAME = "foresdd"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

failures: list[str] = []
passed = 0


def check(ok: bool, ok_msg: str, fail_msg: str) -> bool:
    global passed
    if ok:
        passed += 1
        print(f"  ok    {ok_msg}")
    else:
        failures.append(fail_msg)
        print(f"  FAIL  {fail_msg}")
    return ok


def load(name: str) -> dict | None:
    rel = f".claude-plugin/{name}"
    path = PLUGIN_DIR / name
    if not check(path.is_file(), f"{rel} exists", f"{rel} is missing"):
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        check(False, "", f"{rel} is not valid JSON (line {exc.lineno}, col {exc.colno}: {exc.msg})")
        return None
    if not check(isinstance(data, dict), f"{rel} is a JSON object", f"{rel} must be a JSON object"):
        return None
    return data


def person_name(value) -> str | None:
    if isinstance(value, str):
        return value or None
    if isinstance(value, dict):
        return value.get("name") or None
    return None


def check_plugin(plugin: dict) -> None:
    print("\n== plugin.json ==")
    name = plugin.get("name")
    version = plugin.get("version")
    desc = plugin.get("description") or ""

    check(name == PLUGIN_NAME, f"name is '{PLUGIN_NAME}'",
          f"plugin.json name is {name!r}, expected '{PLUGIN_NAME}' (it sets the /{PLUGIN_NAME}:<skill> namespace)")
    check(isinstance(version, str) and bool(SEMVER.match(version)), f"version {version!r} is semver",
          f"plugin.json version {version!r} is not semver (X.Y.Z)")
    check(isinstance(desc, str) and len(desc) >= 30, f"description present ({len(desc)} chars)",
          f"plugin.json description is missing or shorter than 30 chars ({len(desc)})")
    check(bool(plugin.get("license")), f"license is {plugin.get('license')!r}", "plugin.json has no license")
    check(bool(person_name(plugin.get("author"))), "author has a name",
          "plugin.json author is missing or has no name (string or {\"name\": ...})")

    # Field types — Claude Code's manifest loader rejects the wrong shape.
    for key in ("homepage", "repository"):
        val = plugin.get(key)
        check(val is None or isinstance(val, str), f"{key} is a string (or absent)",
              f"plugin.json `{key}` must be a string URL, got {type(val).__name__}")
    kw = plugin.get("keywords")
    check(kw is None or (isinstance(kw, list) and all(isinstance(k, str) for k in kw)),
          "keywords is a list of strings (or absent)", "plugin.json `keywords` must be a list of strings")

    # Optional component paths, when declared, must exist.
    for key in ("skills", "agents", "commands", "hooks"):
        val = plugin.get(key)
        if val is None:
            continue
        paths = val if isinstance(val, list) else [val]
        for p in paths:
            if isinstance(p, str):
                check((ROOT / p).exists(), f"{key} path {p!r} exists", f"plugin.json `{key}` path {p!r} does not exist")


def check_marketplace(market: dict, plugin: dict | None) -> None:
    print("\n== marketplace.json ==")
    mname = market.get("name")
    check(isinstance(mname, str) and bool(KEBAB.match(mname or "")), f"marketplace name {mname!r} is kebab-case",
          f"marketplace.json name {mname!r} must be a kebab-case string")
    check(bool(person_name(market.get("owner"))), "owner has a name", "marketplace.json owner is missing or has no name")

    plugins = market.get("plugins")
    if not check(isinstance(plugins, list) and bool(plugins), f"lists {len(plugins or [])} plugin(s)",
                 "marketplace.json `plugins` must be a non-empty list"):
        return
    names = [p.get("name") for p in plugins if isinstance(p, dict)]
    dupes = sorted({n for n in names if names.count(n) > 1})
    check(not dupes, "plugin names are unique", f"marketplace.json lists duplicate plugin name(s): {', '.join(map(str, dupes))}")

    entry = next((p for p in plugins if isinstance(p, dict) and p.get("name") == PLUGIN_NAME), None)
    if not check(entry is not None, f"lists the '{PLUGIN_NAME}' plugin", f"marketplace.json has no plugin named '{PLUGIN_NAME}'"):
        return

    source = entry.get("source")
    check(bool(source), f"'{PLUGIN_NAME}' source is {source!r}", f"marketplace '{PLUGIN_NAME}' entry has no source")
    if isinstance(source, str) and source.startswith("./"):
        src = (ROOT / source).resolve()
        check((src / ".claude-plugin" / "plugin.json").is_file(), f"source {source!r} resolves to this plugin",
              f"marketplace source {source!r} has no .claude-plugin/plugin.json")

    if plugin is None:
        return
    print("\n== plugin.json ↔ marketplace.json ==")
    for key in ("version", "description"):
        mval, pval = entry.get(key), plugin.get(key)
        if mval is None:  # optional in the marketplace entry; plugin.json wins
            print(f"  skip  marketplace entry has no {key} (plugin.json's is used)")
            continue
        check(mval == pval, f"{key} matches ({pval!r})",
              f"{key} drift: marketplace.json {mval!r} != plugin.json {pval!r} — bump both together")
    meta_version = (market.get("metadata") or {}).get("version")
    if meta_version is not None:
        check(meta_version == plugin.get("version"), f"metadata.version matches ({meta_version!r})",
              f"marketplace.json metadata.version {meta_version!r} != plugin.json version {plugin.get('version')!r}")


def main() -> int:
    print("== files ==")
    plugin = load("plugin.json")
    market = load("marketplace.json")
    if plugin is not None:
        check_plugin(plugin)
    if market is not None:
        check_marketplace(market, plugin)

    total = passed + len(failures)
    print()
    if failures:
        print(f"FAILED: {len(failures)} of {total} checks")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASSED: {total} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
