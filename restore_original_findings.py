"""Restore the original Claude Code findings as the public, primary record text.

Run from this repository inside the retained research workspace. The later
verification text is preserved in each JSON record as audit history, but it is
not used as the public finding because systematic source-retrieval failures
were found in that pass.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
originals = json.loads((RESEARCH / "source-audit/records.json").read_text())

def parse_js_object(text):
    """Parse the constrained one-line object literals in the original artifact."""
    out, i = [], 0
    while i < len(text):
        if text[i] == '"':
            end = i + 1
            while end < len(text):
                if text[end] == '\\':
                    end += 2
                elif text[end] == '"':
                    end += 1
                    break
                else:
                    end += 1
            out.append(text[i:end]); i = end
        else:
            match = re.match(r'([A-Za-z_][A-Za-z_0-9]*)(\s*:)', text[i:])
            if match:
                out.append(json.dumps(match[1]) + match[2]); i += len(match[0])
            else:
                out.append(text[i]); i += 1
    return json.loads(''.join(out))

artifact = (RESEARCH / "signed-or-sunk.html").read_text()
raw = [parse_js_object(line.strip().rstrip(',')) for line in artifact.splitlines()
       if line.lstrip().startswith('{n:')]
assert len(raw) == 3006

n_index = 0
for original in raw:
    if original['t'] != 'N':
        continue
    n_index += 1
    path = HERE / "data" / f"N{n_index:04}.json"
    record = json.loads(path.read_text())
    record.update({
        "description": original["w"],
        "downloads_and_runs": original["dl"],
        "transport": original["tr"],
        "payload_verification": original["v"],
        "trust_root": original["k"],
        "review_status": "Original Claude Code analysis",
        "review_basis": "original-claude-code-analysis",
        "proposed_primary_tier": "N",
        "classification_certified": False,
        "limitations": [
            "AI-generated static source analysis. The N label was not independently re-audited and does not assess every external installation or content channel."
        ]
    })
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")

for original in originals:
    path = HERE / "data" / f"{original['id']}.json"
    record = json.loads(path.read_text())
    if "later_review_audit" not in record:
        record["later_review_audit"] = {
            "description": record.get("description", ""),
            "limitations": record.get("limitations", []),
            "review_status": record.get("review_status", ""),
            "review_basis": record.get("review_basis", ""),
            "proposed_primary_tier": record.get("proposed_primary_tier", "UNRESOLVED"),
            "classification_certified": record.get("classification_certified", False),
            "status": "superseded-as-primary-after-systematic-source-retrieval-failures"
        }
    record.update({
        "description": original["w"],
        "downloads_and_runs": original["dl"],
        "transport": original["tr"],
        "payload_verification": original["v"],
        "trust_root": original["k"],
        "review_status": "Original Claude Code analysis",
        "review_basis": "original-claude-code-analysis",
        "proposed_primary_tier": original["t"],
        "classification_certified": False,
        "limitations": [
            "AI-generated static source analysis. Confirm the affected version, platform, update channel, and cited control flow before relying on this classification."
        ],
        "original_evidence": original.get("recorded_evidence", [])
    })
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")

print(f"Restored all {len(raw)} original findings; retained the later A-D review as audit history.")
