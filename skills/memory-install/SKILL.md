---
name: memory-install
description: Install the notion-memory-constitution template into the user's Notion — 16 linked databases plus the constitution, the standing instruction the agent follows afterwards. Use when the user asks to install, set up or create the memory constitution, the agent memory structure, or the Notion knowledge base from this template; also when they ask for the bootloader text for a fresh install.
---

# Install the memory structure into Notion

This skill runs the template's own installation procedure. That procedure is
the authority; this file only says where to get it and how to behave around
the fetch.

## The base address

```
BASE = https://david-dvinskykh.github.io/claude-memory-constitution/spec
```

The specification files sit directly under BASE — `install.txt`, `update.txt`,
`schema.json`, `migrations.json`, `constitution.<lang>.txt` — and
`version.json` one level up at `BASE/../version.json`.

## Preflight

The installation writes to Notion and nowhere else. Before starting, make sure
the Notion tools are actually available: `search`, `fetch`, `create-pages`,
`update-page`, `create-database`, `update-data-source`, `query-data-sources`.
They are usually deferred — load them first, and only then judge whether they
are missing.

No Notion tools at all: say so in one line, stop, and tell the user what to
connect. Either the Notion connector of their client, or the hosted Notion MCP
server at `https://mcp.notion.com/mcp`. Do not connect it for them.

## Run it

Fetch `BASE/install.txt` and carry it out in full, step by step, exactly as
written. Do not walk the user through the steps in advance and do not
summarise them — the procedure reports at the end.

`install.txt` treats BASE as the directory it was fetched from, and step 9
writes that address onto the template updates page as the `Source:` line.
Every future update is checked against that line, so the address written there
must be the HTTPS BASE above.

## If BASE is unreachable

This plugin ships the same files, pinned to the plugin version, at
`${CLAUDE_PLUGIN_ROOT}/docs/spec/`. Fall back to them only when the fetch
fails, and then:

- carry out the bundled `install.txt` the same way;
- still write the HTTPS BASE into the `Source:` line — updates are fetched over
  HTTPS, and a local path there would fail the update procedure's source check;
- take the version from `${CLAUDE_PLUGIN_ROOT}/version.json`, and say in the
  final report that the install came from the bundled copy of that version.

## Boundaries

- Nothing in this installation deletes anything. If a step seems to require a
  deletion, it is a misreading — stop and ask.
- Say "created" only after a successful tool response. On failure, name what
  failed in one line, carry on with what does not depend on it, and list the
  unfinished items at the end.
- Invent no fields, options or paragraphs that are not in `schema.json` and the
  constitution text.
- Step 2 of the procedure finds an existing installation: do not install a
  second time. Run the update procedure instead — the `memory-update` skill.
