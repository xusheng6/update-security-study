"""Build a dependency-free GitHub Pages site from reviewed record files."""
import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode, urlparse

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
CONFIG = json.loads((ROOT / 'site.json').read_text())
TITLE = CONFIG['title']
REPO = CONFIG['repository'].rstrip('/')
BRANCH = CONFIG['branch']
if REPO and not re.fullmatch(r'https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', REPO):
    raise ValueError('repository must be an HTTPS GitHub owner/repository URL')
if not re.fullmatch(r'[A-Za-z0-9_.-]+', BRANCH):
    raise ValueError('Invalid branch')
ORDER = {'D': 0, 'C': 1, 'B': 2, 'A': 3, 'N': 4}
LABELS = {'D': 'Broken transport', 'C': 'TLS-only', 'B': 'Publisher identity', 'A': 'Pinned signing key', 'N': 'None / notify'}
MEANINGS = {
    'D': 'Broken transport authentication on an executing update channel, without effective independent payload authentication.',
    'C': 'Validated TLS authenticates distribution, without independently authenticating the update payload.',
    'B': 'The client enforces a valid payload code signature for the expected OS-recognized publisher identity.',
    'A': 'The client enforces a payload signature against a public key already trusted by the application.',
    'N': 'The initial scan recorded no in-app updater or notification-only behavior. This is not a security rating.'
}
e = lambda value: html.escape(str(value), quote=True)
def inline(value):
    """Render the small, safe formatting subset used in evidence cells."""
    value = e(value)
    value = re.sub(r'`([^`]+)`', r'<code class="inline">\1</code>', value)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)

FIELD_LABELS = {
    'repo': 'Repository', 'repo(clone url)': 'Repository',
    'framework': 'Framework', 'commit/date': 'Revision',
    'has_updater': 'Updater present', 'auto': 'Automatic behavior',
    'downloads_and_executes': 'Downloads and executes',
    'transport': 'Transport', 'manifest_signed': 'Manifest authentication',
    'payload_verification': 'Payload verification',
    'verifying_key_source': 'Trust root', 'evidence': 'Source evidence',
    'evidence(file:line)': 'Source evidence'
}
rows = [json.loads(p.read_text()) for p in sorted((ROOT / 'data').glob('*.json'))]
assert rows, 'No records'
ids = set()
for r in rows:
    assert re.fullmatch(r'[RN][0-9]{4}', r['id']) and r['id'] not in ids
    ids.add(r['id'])
    assert r['historical_tier'] in ORDER
    assert r['name'] and r['description'] and r['review_status']
    for url in [r['project_url']] + [s['url'] for s in r['sources']]:
        if url:
            u = urlparse(url)
            assert u.scheme in ('http', 'https') and u.netloc and not u.username
    assert (ROOT / 'data' / (r['id'] + '.json')).is_file()
rows.sort(key=lambda r: (ORDER[r['historical_tier']], r['name'].casefold(), r['id']))
counts = Counter(r['historical_tier'] for r in rows)
OUT.mkdir(exist_ok=True)
(OUT / 'records').mkdir(exist_ok=True)
for asset in ['style.css', 'app.js']:
    shutil.copyfile(ROOT / asset, OUT / asset)
(OUT / '.nojekyll').touch()

def badge(tier):
    return f'<span class="badge tier-{tier}"><span aria-hidden="true">●</span> {tier}</span>'

def shell(content, title=TITLE, prefix='', description='Explore software update authentication, source-review summaries, and classification evidence.'):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#main">Skip to content</a><nav class="top"><a class="wordmark" href="{prefix}index.html">UPDATE SECURITY <span>/ STUDY</span></a><a href="{prefix}about.html">About the tiers</a><a href="{prefix}contribute.html">Contribute ↗</a></nav>{content}<footer>Original AI-assisted source survey · Snapshot {e(CONFIG['snapshot_date'])} · Read each finding and its limitations.</footer></body></html>'''

cards = f'<button class="stat all" data-tier="all"><strong>{len(rows):,}</strong><span>Records surveyed</span></button>'
for t in ORDER:
    cards += f'<button class="stat tier-{t}" data-tier="{t}"><strong>{counts[t]:,}<small>{counts[t]/len(rows):.1%}</small></strong><span>{t} · {LABELS[t]}</span></button>'
filters = '<button class="chip selected" data-tier="all" aria-pressed="true">All records</button>' + ''.join(f'<button class="chip" data-tier="{t}" aria-pressed="false">{t} · {LABELS[t]}</button>' for t in ORDER)
main = f'''<main id="main"><header class="intro"><p class="eyebrow">AN OPEN SURVEY OF UPDATE AUTHENTICATION</p><h1>Software Update<br>Security Study<span class="dot">.</span></h1><p class="lede">What does software trust before it installs an update?<br>Explore the records, read the source reviews, and help improve the findings.</p><div class="stats">{cards}</div><p class="snapshot"><span class="status-dot"></span> Original scan labels · Counts describe records, not unique applications or confirmed vulnerabilities. <a href="about.html">How to read this data →</a></p></header><section class="catalog" aria-label="Software records"><div class="tools"><div class="filters" aria-label="Filter by historical tier">{filters}</div><label class="search"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="Find a project, category, or update mechanism…" aria-label="Search records"></label></div><div class="results-meta"><p id="count" aria-live="polite">Loading records…</p><span>Original tier order: D → C → B → A → N</span></div><div class="table-wrap"><table><thead><tr><th>PROJECT</th><th>ORIGINAL TIER</th><th>UPDATE CHANNEL</th><th>REVIEW</th><th>FINDING</th></tr></thead><tbody id="rows"></tbody></table></div><div id="empty" class="empty" hidden><h2>No matching records</h2><p>Try another project name or clear the filters.</p><button id="reset">Clear filters</button></div><div class="pagination"><button id="prev">← Previous</button><span id="page"></span><button id="next">Next →</button></div><noscript><p>Search requires JavaScript. <a href="directory.html">Browse the complete project directory instead.</a></p></noscript></section></main><script src="app.js" defer></script>'''
(OUT / 'index.html').write_text(shell(main))
(OUT / 'catalog.json').write_text(json.dumps(rows, ensure_ascii=False))

for r in rows:
    rid, tier = r['id'], r['historical_tier']
    project = f'<a class="button" href="{e(r["project_url"])}" target="_blank" rel="noopener noreferrer">Project website / source ↗</a>' if r['project_url'] else '<span class="muted">Project URL not recorded</span>'
    if REPO:
        issue = REPO + '/issues/new?' + urlencode({'template': 'correction.yml', 'title': f'Correction: {r["name"]} ({rid})'})
        edit = f'{REPO}/edit/{BRANCH}/data/{rid}.json'
        actions = f'<a class="button primary" href="{e(issue)}">Report a correction ↗</a><a class="button" href="{e(edit)}">Propose a data edit / PR ↗</a>'
    else:
        actions = '<a class="button primary" href="../contribute.html">Suggest a correction →</a>'
    sources = ''
    for source in r['sources']:
        url, commit = source['url'], source.get('commit', '')
        if re.fullmatch('[0-9a-f]{40}', commit) and url.startswith('https://github.com/'):
            url += '/tree/' + commit
        sources += f'<li><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(source["url"])}</a>' + (f'<code>{e(commit)}</code>' if commit else '') + '</li>'
    if not sources:
        sources = '<li>No source revision is attached to this record.</li>'
    limits = ''.join(f'<li>{e(v)}</li>' for v in r['limitations']) or '<li>This is a historical source observation, not a verification of every released binary or current upstream version.</li>'
    evidence = ''
    items = r.get('structured_evidence', [])
    for number, item in enumerate(items, 1):
        fields = ''
        for field in item['fields']:
            key = re.sub(r'\s+', ' ', field['label'].strip().lower())
            label = FIELD_LABELS.get(key, field['label'].replace('_', ' ').strip().title())
            fields += f'<div class="evidence-field"><dt>{e(label)}</dt><dd>{inline(field["value"])}</dd></div>'
        suffix = f' {number}' if len(items) > 1 else ''
        origin = f'{item["source_file"]}, line {item["source_line"]}'
        evidence += f'<section class="evidence-card"><p class="evidence-origin">Original batch evidence{suffix} · {e(origin)}</p><dl class="evidence-grid">{fields}</dl></section>'
    if not evidence:
        evidence = '<p class="muted">The retained record does not include a separate detailed evidence row. The updater facts and original finding above are the available original analysis.</p>'
    proposed = r['proposed_primary_tier']
    detail_facts = ''
    for label, key in [('Downloads / runs', 'downloads_and_runs'), ('Transport', 'transport'), ('Payload verification', 'payload_verification'), ('Trust root', 'trust_root')]:
        if r.get(key) is not None:
            detail_facts += f'<dt>{label}</dt><dd>{e(r[key])}</dd>'
    content = f'''<main id="main" class="detail"><a class="back" href="../index.html">← All records</a><p class="eyebrow">RECORD {rid} · {e(r['category'])}</p><h1>{e(r['name'])}</h1><div class="record-meta">{badge(tier)}<span>Original classification</span><span class="review-status">{e(r['review_status'])}</span></div><div class="actions">{project}<a class="button" href="../data/{rid}.json">View record data</a></div><div class="detail-grid"><article><section class="panel"><p class="eyebrow">ORIGINAL ANALYSIS</p><h2>What the Claude Code analysis found</h2><p class="description">{e(r['description'])}</p></section><section class="panel"><h2>How the updater works</h2>{evidence}</section><section class="panel"><h2>Scope and limitations</h2><ul>{limits}</ul></section><section class="panel"><h2>Source snapshots</h2><ul class="sources">{sources}</ul><p class="muted">Repository links identify retained study material. This does not certify every released binary or the latest upstream version.</p></section></article><aside><section class="panel facts"><h2>At a glance</h2><dl><dt>Original tier</dt><dd>{tier} · {LABELS[tier]}</dd>{detail_facts}<dt>Original channel label</dt><dd>{e(r['channel'])}</dd><dt>Displayed assessment</dt><dd>{e(proposed)}</dd><dt>Record snapshot</dt><dd>{e(r['snapshot_date'])}</dd><dt>Independently certified?</dt><dd>No — original AI source analysis</dd></dl></section><section class="panel tier-note tier-{tier}"><h2>What tier {tier} means</h2><p>{MEANINGS[tier]}</p><a href="../about.html">Read the definitions →</a></section><section class="panel"><h2>Something missing or incorrect?</h2><p>Help improve this record with the affected version, update channel, and supporting evidence.</p><div class="actions vertical">{actions}</div></section></aside></div></main>'''
    (OUT / 'records' / f'{rid}.html').write_text(shell(content, f'{r["name"]} · {TITLE}', '../', r['category'] + ' — update authentication source review.'))
    (OUT / 'data').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'data' / f'{rid}.json', OUT / 'data' / f'{rid}.json')

about = '<main id="main" class="reading"><p class="eyebrow">METHODOLOGY & SCOPE</p><h1>Read the trust boundary.</h1><p class="lede">The tiers describe how an update channel authenticates code. They are not overall security ratings.</p>'
for t in ORDER:
    about += f'<section class="panel">{badge(t)}<h2>{LABELS[t]}</h2><p>{MEANINGS[t]}</p></section>'
about += '<section class="panel"><h2>What these counts mean</h2><p>This collection contains 3,006 historical records, including duplicate projects and separate platforms and installation channels. The website displays the original Claude Code findings and tier assignments as the primary study results.</p><p>The sample was assembled for breadth, not randomly selected. Neither these counts nor agreement between AI reviewers establishes a population-wide security rate.</p><h2>How the analysis worked</h2><p>Claude Code agents inspected source in batches and recorded update behavior, transport, payload verification, and trust roots. A later automated verification pass was removed from the primary presentation after systematic failures to find code that was present in its own retained checkouts. That pass remains in repository history for auditability. The study author reports manually reviewing Tier D.</p><h2>Important distinctions</h2><p>A user-initiated update can still install code. A browser link is notification-only. Plugins, firmware, and application updates need separate scopes. HTTPS with proper validation protects transport; a checksum from the same compromised distribution service does not independently authenticate a release. Signature enforcement does not protect against every compromise of the build or authorized release process.</p></section></main>'
(OUT / 'about.html').write_text(shell(about, 'Methodology · ' + TITLE))
destination = f'<p><a class="button primary" href="{e(REPO)}/issues/new/choose">Open an issue ↗</a> <a class="button" href="{e(REPO)}">Browse the repository ↗</a></p>' if REPO else '<p class="notice">This is a local preview. The public repository has not been connected yet, so issue and pull-request submission is not available here.</p>'
contribute = f'<main id="main" class="reading"><p class="eyebrow">COMMUNITY CORRECTIONS</p><h1>Help make the record accurate.</h1><p class="lede">Maintainers and readers are welcome to challenge a classification or improve its scope.</p>{destination}<section class="panel"><h2>What to include</h2><ol><li>The project name and record ID.</li><li>The affected version, platform, and update channel.</li><li>What the current description gets wrong, and your proposed replacement.</li><li>Source or documentation links that support the correction.</li></ol><h2>Proposing a pull request</h2><p>Each record has its own JSON file in the repository’s data directory. Use the record’s edit link, propose a change, and open a pull request. Keep the historical tier separate from a revised assessment. Accepted corrections rebuild the website after review and merge.</p><p>A newly discovered security issue should first go through the affected project’s private security reporting process. This study’s public correction tracker is for discussing published records.</p></section></main>'
(OUT / 'contribute.html').write_text(shell(contribute, 'Contribute · ' + TITLE))
directory = '<main id="main" class="reading"><h1>All records</h1><ul>' + ''.join(f'<li>{badge(r["historical_tier"])} <a href="records/{r["id"]}.html">{e(r["name"])}</a></li>' for r in rows) + '</ul></main>'
(OUT / 'directory.html').write_text(shell(directory, 'Directory · ' + TITLE))
print(f'Built {len(rows):,} detail pages and catalog. Tier counts: {dict(counts)}. GitHub correction links: {bool(REPO)}')
