# Software Update Security Study

A searchable, community-correctable collection of software update authentication records.

**Website:** https://xusheng6.github.io/update-security-study/

The initial scan contains 3,006 records: 49 D, 332 C, 109 B, 134 A, and 2,382 N. These are historical classifications, not a certified census of unique applications or confirmed vulnerabilities. The website presents the original Claude Code analysis as the primary result.

## Browse and contribute

The website links project names to recorded project URLs. Each record has a permanent details page with the original finding, updater facts, retained evidence, source snapshots, and correction links. Original Markdown table rows are presented as labeled fields rather than raw table syntax.

- **Report an error:** use the correction issue template.
- **Propose an edit:** change the corresponding `data/Rxxxx.json` or `data/Nxxxx.json` file and open a pull request.
- Include affected versions, platforms, channels, and supporting evidence.
- Keep `historical_tier` as the original label. Correct the updater facts and description with source evidence when needed.
- A new, unpublished security finding should go through the affected project's private reporting process before public discussion here.

Contributions are reviewed before merge. Pull requests run the build and validation; merging to main publishes an updated site.

## Run locally

Requires Python 3.9+ and Node.js for the interaction test. No package installation or external services are required.

```sh
python3 build.py
python3 validate.py
node test-search.cjs
python3 -m http.server 8765 --directory dist
```

Open http://localhost:8765. `site.json` controls the repository destination and record snapshot date. GitHub Pages uses the workflow in `.github/workflows/pages.yml`.

## Data provenance and limits

The imported snapshot uses the original collection for names, categories, tiers, updater facts, and finding descriptions. These are the original Claude Code results. A later automated verification pass over A–D was removed from the primary presentation after systematic source-retrieval failures were demonstrated, including a GeoGebra review that claimed updater code was absent even though the cited implementation existed in the same checkout. Its former text remains inside the affected JSON records as `later_review_audit` and in repository history for transparency; it is not treated as authoritative.

The site does not reproduce the original blanket exploit claims, update endpoint lists, private disclosure correspondence, contact lists, or downloaded repositories. Source snapshots do not establish the behavior of every release or the latest upstream version. `snapshot_date` is the date of this assembled record snapshot, not the date every application was tested. Missing project links are left unset rather than guessed.

This research was conducted by Xusheng Li in a personal capacity and does not represent the views of his employer.
