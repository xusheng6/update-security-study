"""Convert original Markdown table rows into labeled evidence fields.

This is a presentation transform only. It does not change the original text,
tier, or security conclusion stored in each record.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent

def split_row(line):
    """Split a Markdown table row, preserving pipes inside code spans."""
    cells, current, in_code = [], [], False
    for char in line.strip():
        if char == '`':
            in_code = not in_code
            current.append(char)
        elif char == '|' and not in_code:
            cells.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append(''.join(current).strip())
    if cells and not cells[0]:
        cells.pop(0)
    if cells and not cells[-1]:
        cells.pop()
    return cells

def table_header(lines, row_index):
    for index in range(min(row_index - 1, len(lines) - 2), -1, -1):
        if not lines[index].lstrip().startswith('|'):
            continue
        separator = lines[index + 1]
        remaining = separator.replace('|', '').replace('-', '').replace(':', '').strip()
        if separator.lstrip().startswith('|') and not remaining:
            return split_row(lines[index])
    return None

changed = 0
structured_count = 0
for path in sorted((HERE / 'data').glob('R*.json')):
    record = json.loads(path.read_text())
    structured = []
    for evidence in record.get('original_evidence', []):
        source = RESEARCH / evidence['file']
        lines = source.read_text(errors='replace').splitlines()
        row_index = evidence['line'] - 1
        headers = table_header(lines, row_index)
        values = split_row(evidence['text'])
        if headers is None:
            raise ValueError(f"No table header for {record['id']} at {source}:{evidence['line']}")
        if len(headers) == len(values) + 1:
            values.insert(-1, 'not separately recorded')
        elif len(values) == len(headers) + 1:
            values[-2:] = [values[-2] + ' | ' + values[-1]]
        if len(headers) != len(values):
            raise ValueError(f"Column mismatch for {record['id']}: {len(headers)} headers, {len(values)} values")
        fields = []
        for header, value in zip(headers, values):
            normalized = re.sub(r'\s+', ' ', header.strip().lower())
            if normalized in {'name', 'application', 'app'}:
                continue
            fields.append({'label': header.strip(), 'value': value.strip()})
        structured.append({
            'source_file': evidence['file'],
            'source_line': evidence['line'],
            'fields': fields
        })
        structured_count += 1
    if structured:
        record['structured_evidence'] = structured
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
        changed += 1

print(f"Structured {structured_count} evidence rows across {changed} records.")
