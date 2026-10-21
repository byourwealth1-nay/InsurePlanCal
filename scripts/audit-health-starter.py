"""Audit/rebuild Starter from PDF text extracted with pdftotext -layout.

Usage: python scripts/audit-health-starter.py starter-layout.txt [--write]
Checks every printed age/sex/room cell, including renewal-only ages.
"""
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
text = Path(sys.argv[1]).read_text()
products = json.loads((root / 'data/products.json').read_text())
fixtures = {}
changes = []
for mode, count in [('BEGIN', 20), ('BALANCED', 18)]:
    pages = [p for p in text.split('\f') if re.search(r'เบี้ยประกันภัยมาตรฐานราย.{0,8}แบบ\s+' + mode, p)]
    assert len(pages) == 1, (mode, len(pages))
    rows = []
    pending = None
    for line in pages[0].splitlines():
        match = re.match(r'^\s*(?:15\s*วัน|\d+)\s*[-–]\s*(\d+)\*?\s*(.*?)\s*$', line)
        if match:
            pending = int(match[1])
            tail = match[2]
        elif pending is not None:
            tail = line.strip()
        else:
            continue
        if not re.fullmatch(r'[\d,]+(?:\s+[\d,]+){4}', tail):
            continue
        rows.append((pending, [int(v.replace(',', '')) for v in tail.split()]))
        pending = None
    assert len(rows) == count * 2, (mode, len(rows))
    p = next(p for p in products if p['id'] == 'starter' + mode.lower())
    assert rows[:count] and [a for a, _ in rows[:count]] == p['bands']
    assert [a for a, _ in rows[count:]] == p['bands']
    expected = []
    for j, room in enumerate([1500, 2000, 2500, 3500, 4500]):
        rates = {sex: [r[1][j] for r in rows[k*count:(k+1)*count]] for k, sex in enumerate(['M', 'F'])}
        expected.append({'id': str(j), 'room': room, 'rates': rates})
        for sex in ['M', 'F']:
            for index, rate in enumerate(rates[sex]):
                old = p['plans'][j]['rates'][sex][index]
                if old != rate:
                    changes.append({'id': p['id'], 'sex': sex, 'ageBand': p['bands'][index], 'room': room, 'before': old, 'after': rate})
        if '--write' in sys.argv:
            p['plans'][j]['rates'] = rates
    fixtures[p['id']] = {'bands': p['bands'], 'plans': expected}
if '--write' in sys.argv:
    (root / 'data/products.json').write_text(json.dumps(products, ensure_ascii=False, indent=2))
    (root / 'tests/health-starter-source.json').write_text(json.dumps({'source': 'Brochure_AIA_Health_Starter_20260115.pdf', 'pages': [8, 9], 'products': fixtures}, ensure_ascii=False, indent=2))
    (root / 'data/health-starter-audit.json').write_text(json.dumps({'sourcePages': [8, 9], 'comparedCells': 380, 'correctedCells': len(changes), 'changes': changes}, ensure_ascii=False, indent=2))
else:
    assert not changes, changes[:5]
print(f'PASS: 380 Starter source cells; {len(changes)} corrections' if '--write' in sys.argv else 'PASS: all 380 Starter source cells match')
