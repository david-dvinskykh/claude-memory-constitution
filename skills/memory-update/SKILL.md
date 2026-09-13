---
name: memory-update
description: Check whether a newer version of the notion-memory-constitution template has been released and apply it safely to an already installed Notion memory structure. Use when the user asks to update, upgrade or check the version of their memory constitution or memory structure, and when a scheduled update check fires.
---

# Update an installed memory structure

This skill runs the template's own update procedure. That procedure is the
authority; this file only says where to get it.

## The base address

```
BASE = https://david-dvinskykh.github.io/claude-memory-constitution/spec
```

`schema.json`, `migrations.json` and `constitution.<lang>.txt` sit next to
`update.txt`; `version.json` is one level up at `BASE/../version.json`.

## Preflight

Load the Notion tools first: `search`, `fetch`, `update-page`,
`update-data-source`, `create-pages`, `query-data-sources`. They are deferred;
without them nothing will be written.

## Run it

Fetch `BASE/update.txt` and carry it out in full, exactly as written.

A quiet run is the normal outcome. When the installed version is current, the
procedure updates one line on the updates page and says nothing to the owner —
do not turn that into a report.

## No local fallback here

`update.txt` compares the address it was actually fetched from with the
`Source:` line recorded in Notion and applies nothing when the two differ. The
bundled copy under `${CLAUDE_PLUGIN_ROOT}` is a different address, so it is not
a fallback for an update: if BASE is unreachable, say so in one line and stop.
Updating the structure from a copy whose address does not match the recorded
source is exactly what that check exists to prevent.

## Boundaries

The procedure deletes nothing, touches no data of the owner's — facts, people,
documents, cases, preferences, journal — and changes only structure and service
text. It never restores a paragraph the owner rewrote, never raises a level in
the permissions register, and never edits the protected sections of the
constitution. A migration that would do any of that is not applied: it becomes
a question in the decision queue.

## Running it on a schedule

The template expects a weekly check. Whatever recurring-task mechanism the
user's client offers, the scheduled instruction is this skill, or the plain
line it wraps:

```
Read https://david-dvinskykh.github.io/claude-memory-constitution/spec/update.txt and carry it out in full.
```

The schedule must live in the agent's settings, not in a Notion page — the
source address is only trustworthy while whoever can edit Notion cannot change
what the agent fetches next.
