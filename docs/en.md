---
title: English quick start
---

# Long-term memory for an agent, in Notion

[Русская документация](index.md) · [Українською](uk.md)

---

A template for an AI agent's long-term memory: 16 linked Notion databases plus
a written instruction the agent follows to keep that memory itself — with no
reminders, no "please write this down", and no losing what you said six months
ago.

One command to install. Scheduled updates.

## What makes it different from ordinary agent memory

Ordinary memory features store loose notes. This one is built around four
things notes cannot do:

- **Atomicity.** One fact, one row, one checkable statement. Prose cannot be
  filtered, refuted or aged; a row can.
- **Two timestamps.** Every record carries when it happened and when it was
  recorded, plus a validity interval. "Worked at X, now at Y" is two records,
  not one.
- **Trust.** Every statement is marked with where it came from and how solid
  it is. An agent's guess never looks as reliable as a line from a document.
- **Invalidation instead of deletion.** A contradiction closes the old fact
  with a date and points the new one at it; the past stays queryable.

Plus two loops that keep it alive: the agent records the rules of working with
you that it derives from your corrections, and it maintains a register of what
it may do without asking — a level only you can raise, and one it lowers on
itself the moment you roll something back.

## Install

Tell an agent that has Notion connected:

```
Read https://david-dvinskykh.github.io/claude-memory-constitution/spec/install.txt and carry it out in full.
```

It asks two things — the language of the structure (`ru`, `uk` or `en`) and
where in Notion to create the base — then does the rest: creates the databases,
links them, assembles the constitution with real ids substituted, adds the
service pages, and hands you a ready bootloader to paste into your agent's
settings.

Answer `en` and everything is created in English: base names, field names,
option values, the constitution, the bootloader. The language is chosen once
at install time — it is baked into the field names the constitution and the
migrations refer to.

## Keep it updated

Set up a weekly recurring task with one line:

```
Read https://david-dvinskykh.github.io/claude-memory-constitution/spec/update.txt and carry it out in full.
```

The procedure compares versions and applies the difference. It deletes nothing,
never touches your data, never narrows a list of options, never changes the
protected sections of the constitution, and never raises its own permissions.
If nothing changed, it says nothing.

## What you get

| | |
| --- | --- |
| 🧩 Facts | Atomic statements — the core of the whole memory |
| 🎛️ Preferences | Rules of conduct the agent derives from your corrections |
| 👥 People · 🏢 Organizations · 📍 Places · 📦 Things · 📅 Projects · 💡 Ideas | Entities |
| 🗓️ Journal | What happened, day by day |
| 🗃️ Documents · 📁 Cases · 🧬 Biography | The card file: papers, storylines, milestones |
| ⚙️ Processes | Standing procedures, versioned |
| ⚖️ Permissions · 📮 Decision queue | What the agent may do alone, and where it asks |
| 📥 Inbox | Quarantine for whatever has no obvious home |

## Read the sources directly

The specification is language-neutral and machine-readable:

- [spec/schema.json](spec/schema.json) — 16 databases, 30 relations, formulas
  and rollups, with `ru` / `uk` / `en` branches
- [spec/constitution.en.txt](spec/constitution.en.txt) — the constitution,
  17 sections
- [spec/install.txt](spec/install.txt) — the installation procedure
- [spec/update.txt](spec/update.txt) — the update procedure
- [version.json](version.json) — the current version

## Privacy

The template carries nobody's personal data — no names, numbers, addresses or
countries. Nothing is sent anywhere: the installer reads files over HTTPS and
writes only to your Notion.

Version 1.1 works with **Notion only**. No file storage, mail, messengers or
calendars.

The full documentation is currently in Russian: [index.md](index.md).
