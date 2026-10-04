# Irkutsk Plague Watch

A minimal daily tracker of the plague laboratory incident at the Irkutsk Anti-Plague
Research Institute in Siberia: the counts, how they have moved day by day, the
headlines as published, a timeline and the context needed to read it without alarm.

**Live page:** see the artifact link below.

## How it works

| Path | What it is |
|---|---|
| `data/outbreak.json` | The only data file. Counts, daily series, headlines, timeline, context, watch list, sources. |
| `src/page.html` | The page template. It renders everything from the data file. |
| `scripts/build.mjs` | Builds `index.html` (full page) and `artifact.html` (fragment for the claude.ai artifact). |
| `RUNBOOK.md` | The daily update procedure a scheduled Claude routine follows. |

To rebuild after editing the data:

```
node scripts/build.mjs
```

To preview locally, open `index.html` in a browser.

## Daily update

A Claude routine runs every morning, follows `RUNBOOK.md`, commits the new data to
`main` and republishes the artifact. Pause or delete it from the Routines list in
Claude Code if the incident closes or the updates are no longer wanted.

## Artifact

ARTIFACT_URL_PLACEHOLDER
