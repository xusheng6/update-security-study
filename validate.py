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
print(f'Validated local links and data for {len(rows):,} records.')
