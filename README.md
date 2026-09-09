# Software Update Security Study

A searchable, community-correctable collection of software update authentication records.

**Website:** https://xusheng6.github.io/update-security-study/

The initial scan contains 3,006 records: 49 D, 332 C, 109 B, 134 A, and 2,382 N. These are historical classifications, not a certified census of unique applications or confirmed vulnerabilities. The collection includes mixed platforms and update channels. Read each record's later source-review description and limitations before interpreting its original tier.

## Browse and contribute

The website links project names to recorded project URLs. Each record has a permanent details page with its source-review description, scope, limitations, source snapshots, and correction links.

- **Report an error:** use the correction issue template.
- **Propose an edit:** change the corresponding `data/Rxxxx.json` or `data/Nxxxx.json` file and open a pull request.
- Include affected versions, platforms, channels, and supporting evidence.
- Keep `historical_tier` as the original label. Use `proposed_primary_tier`, the description, and review fields for later assessments.
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

The imported snapshot uses the original collection for names, categories, and historical tiers. For the 624 A–D records, longer descriptions come from the retained source-review ledger, with 372 later publication decisions and seven deeper reviews taking precedence where available. Those descriptions may narrow, withdraw, or contradict the original finding. The N records have a short scope statement; they have not received the same recheck as the positive findings.

The site does not reproduce the original blanket exploit claims, update endpoint lists, private disclosure correspondence, contact lists, or downloaded repositories. Source snapshots do not establish the behavior of every release or the latest upstream version. `snapshot_date` is the date of this assembled record snapshot, not the date every application was tested. Missing project links are left unset rather than guessed.

This research was conducted by Xusheng Li in a personal capacity and does not represent the views of his employer.
