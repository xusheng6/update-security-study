"""Check static links, record routing, and public-output hygiene."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        for key, val in attrs:
            if key in ('href', 'src') and val:
                self.links.append(val)

rows = json.loads((OUT / 'catalog.json').read_text())
assert len({r['id'] for r in rows}) == len(rows)
expected = sorted(rows, key=lambda r: ('DCBAN'.index(r['historical_tier']),r['name'].casefold(),r['id']))
assert rows == expected
for file in OUT.rglob('*.html'):
    text = file.read_text()
    assert '/Users/' not in text and 'verify-clones/' not in text, file
    parser = Links(); parser.feed(text)
    for link in parser.links:
        u = urlsplit(link)
        if u.scheme:
            assert u.scheme in ('http', 'https'), (file, link)
        elif u.path:
            target = (file.parent / unquote(u.path)).resolve()
            assert target.is_relative_to(OUT.resolve()) and target.is_file(), (file, link)
for r in rows:
    assert (OUT / 'records' / (r['id'] + '.html')).is_file()
    assert json.loads((OUT / 'data' / (r['id'] + '.json')).read_text()) == r
    assert r['description'] and r['name']
by_id = {r['id']: r for r in rows}
geogebra = by_id['R0207']
assert geogebra['historical_tier'] == 'C'
assert geogebra['description'] == 'Windows auto-updater silently downloads+loads new application jars, zero verification.'
assert geogebra['transport'] == 'https (validated)'
assert geogebra['payload_verification'] == 'none'
assert geogebra['review_basis'] == 'original-claude-code-analysis'
assert len(geogebra['structured_evidence']) == 1
geogebra_fields = {f['label']: f['value'] for f in geogebra['structured_evidence'][0]['fields']}
assert geogebra_fields['transport'].startswith('https')
assert 'GeoGebraFrame.java:529-577' in geogebra_fields['evidence']
assert '| GeoGebra (desktop) |' not in (OUT / 'records' / 'R0207.html').read_text()
print(f'Validated local links and data for {len(rows):,} records.')
