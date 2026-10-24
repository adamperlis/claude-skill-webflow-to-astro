#!/usr/bin/env python3
"""Bring every past Webflow form submission into the new site's form store.

    WEBFLOW_TOKEN=… python3 -I forms_to_kv.py export <site_id> <out.json>
    python3 -I forms_to_kv.py csv <out.json> <form name>=<webflow.csv> [...]
    python3 -I forms_to_kv.py map <out.json> <map.json>
    python3 -I forms_to_kv.py kv <out.json> <map.json> <bulk-prefix>
    npx wrangler kv bulk put <bulk-prefix>-1.json --namespace-id <FORMS id> --remote

export  every form and every submission through the Data API v2 (a token with
        forms:read; the owner makes it in Site settings → Apps & integrations).
        With the Webflow MCP connected, list_site_form_submissions gives the
        same data.
csv     the fallback without a token: each form's CSV download from Site
        settings → Forms, named by the form it came from.
map     a starter map: each Webflow form, its count, and a guess at which
        `kind` in functions/api/forms.ts it becomes and which fields hold the
        person's name and email. Edit it: set "kind" to null to skip a form
        (cookie-preference widgets, test forms).
kv      the entries in exactly the shape functions/api/forms.ts stores, as
        `wrangler kv bulk put` files of up to 10,000 each. Keys keep the
        original date and come from Webflow's submission id, so running it
        again overwrites instead of duplicating. Each value says
        "source": "webflow". Loading them bypasses the function, so nothing is
        emailed, posted to Slack or sent to the CRM.

Every file here holds people's details: the script refuses to write inside a
git work tree, and prints counts, never contents. Delete the files once the
import is checked.
"""
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

API = 'https://api.webflow.com/v2'
BULK_MAX = 10_000  # wrangler kv bulk put takes at most this many pairs per call


def outside_repo(path):
    d = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.exists(os.path.join(d, '.git')):
            sys.exit(f"Refusing to write people's details inside a git work tree: {path}")
        parent = os.path.dirname(d)
        if parent == d:
            return path
        d = parent


def api(path):
    hdr = {'Authorization': f"Bearer {os.environ['WEBFLOW_TOKEN']}", 'accept': 'application/json'}
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, headers=hdr), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited: back off
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError('rate limited too long: ' + path)


def pages(path, key):
    offset = 0
    while True:
        page = api(f"{path}{'&' if '?' in path else '?'}limit=100&offset={offset}")
        yield from page[key]
        offset += 100
        if offset >= page['pagination']['total']:
            return


def export(site, out):
    forms = []
    for f in pages(f'/sites/{site}/forms', 'forms'):
        subs = [
            {'id': s['id'], 'at': s['dateSubmitted'], 'fields': s.get('formResponse') or {}}
            for s in pages(f"/forms/{f['id']}/submissions", 'formSubmissions')
        ]
        fields = [v.get('displayName') for v in (f.get('fields') or {}).values() if v.get('displayName')]
        forms.append({'name': f['displayName'], 'page': f.get('pageName'), 'fields': fields, 'submissions': subs})
        print(f"{f['displayName']:<36} {len(subs):>5} submissions  ({f.get('pageName') or 'no page'})")
    return forms


# Webflow's CSV download: one column per field plus the date it came in.
DATE_COLUMNS = ('Date', 'date', 'Submitted at', 'Submitted On', 'Created On', 'Timestamp')
DATE_FORMATS = ('%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S',
                '%b %d, %Y %I:%M %p', '%B %d, %Y %I:%M %p', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M',
                '%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)')


def iso(value):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        except ValueError:
            pass
    return None


def from_csv(pairs):
    forms = []
    for pair in pairs:
        name, _, path = pair.partition('=')
        if not path:
            sys.exit(f'Expected <form name>=<file.csv>, got: {pair}')
        rows = list(csv.DictReader(open(path, newline='', encoding='utf-8-sig')))
        if not rows:
            forms.append({'name': name, 'fields': [], 'submissions': []})
            continue
        date_col = next((c for c in DATE_COLUMNS if c in rows[0]), None)
        if not date_col:
            sys.exit(f'{path}: no date column (looked for {", ".join(DATE_COLUMNS)}); columns are {list(rows[0])}')
        subs = []
        for row in rows:
            at = iso(row[date_col] or '')
            if not at:
                sys.exit(f'{path}: unreadable date in column {date_col!r}; add its format to DATE_FORMATS')
            fields = {k: v for k, v in row.items() if k != date_col and v}
            # no submission id in a CSV: hash the row, so a re-run gives the same key
            rid = hashlib.sha256(json.dumps([name, at, fields], sort_keys=True).encode()).hexdigest()
            subs.append({'id': rid, 'at': at, 'fields': fields})
        forms.append({'name': name, 'fields': [c for c in rows[0] if c != date_col], 'submissions': subs})
        print(f'{name:<36} {len(subs):>5} rows from {os.path.basename(path)}')
    return forms


def guess(fields, *patterns):
    for p in patterns:
        for f in fields:
            if re.fullmatch(p, f, re.I):
                return f
    return None


def starter_map(forms):
    seen = {}
    for f in forms:
        keys = sorted({k for s in f['submissions'] for k in s['fields']} | set(f['fields']))
        m = seen.setdefault(f['name'], {
            'kind': re.sub(r'[^a-z0-9]+', '-', f['name'].lower()).strip('-')[:20] or None,
            'title': f['name'],
            'nameField': guess(keys, r'name(-\d+)?', r'full[- ]?name', r'first[- ]?name'),
            'emailField': guess(keys, r'e-?mail(-\d+)?', r'.*e-?mail.*'),
            'submissions': 0,
            'fields': keys,
        })
        m['submissions'] += len(f['submissions'])
        if re.search(r'cookie|consent|preference', f['name'], re.I):
            m['kind'] = None  # Webflow counts cookie banners as forms
    return seen


def to_kv(forms, mapping):
    pairs, counts, skipped = [], {}, {}
    for f in forms:
        m = mapping.get(f['name'])
        if not m or not m.get('kind'):
            skipped[f['name']] = skipped.get(f['name'], 0) + len(f['submissions'])
            continue
        for s in f['submissions']:
            fields = {k: str(v).strip() for k, v in s['fields'].items() if str(v).strip()}
            at = s['at'] if s['at'].endswith('Z') else iso(s['at']) or s['at']
            name, email = fields.get(m.get('nameField') or ''), fields.get(m.get('emailField') or '')
            entry = {
                'form': m['kind'],
                'title': m.get('title') or f['name'],
                'at': at,
                'fields': fields,
                'contact': {'name': name, 'email': email},
                'labels': {k: k for k in fields},
                'source': 'webflow',
                'webflowId': s['id'],
            }
            short = hashlib.sha256(s['id'].encode()).hexdigest()[:6]
            pairs.append({
                'key': f"{m['kind']}:{at}:wf{short}",
                'value': json.dumps(entry, ensure_ascii=False),
                'metadata': {'at': at, 'name': (name or '')[:200]},
            })
            counts[m['kind']] = counts.get(m['kind'], 0) + 1
    return pairs, counts, skipped


def main(argv):
    if len(argv) < 2 or argv[1] not in ('export', 'csv', 'map', 'kv'):
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == 'export':
        if len(argv) != 4 or not os.environ.get('WEBFLOW_TOKEN'):
            sys.exit(__doc__)
        out = outside_repo(argv[3])
        json.dump(export(argv[2], out), open(out, 'w'), indent=1, ensure_ascii=False)
    elif cmd == 'csv':
        if len(argv) < 4:
            sys.exit(__doc__)
        out = outside_repo(argv[2])
        json.dump(from_csv(argv[3:]), open(out, 'w'), indent=1, ensure_ascii=False)
    elif cmd == 'map':
        if len(argv) != 4:
            sys.exit(__doc__)
        mapping = starter_map(json.load(open(argv[2])))
        json.dump(mapping, open(outside_repo(argv[3]), 'w'), indent=1, ensure_ascii=False)
        for name, m in mapping.items():
            print(f"{name:<36} {m['submissions']:>5}  → {m['kind'] or 'skip'}  name={m['nameField']} email={m['emailField']}")
        print('Check each kind against FORMS in functions/api/forms.ts, then run kv.')
    else:
        if len(argv) != 5:
            sys.exit(__doc__)
        pairs, counts, skipped = to_kv(json.load(open(argv[2])), json.load(open(argv[3])))
        prefix = outside_repo(argv[4] + '-1.json')[:-len('-1.json')]
        for i in range(0, len(pairs), BULK_MAX):
            path = f'{prefix}-{i // BULK_MAX + 1}.json'
            json.dump(pairs[i:i + BULK_MAX], open(path, 'w'), ensure_ascii=False)
            print(f'wrote {path}')
        for kind, n in sorted(counts.items()):
            print(f'{kind:<20} {n:>5} entries')
        for name, n in skipped.items():
            print(f'skipped {name!r}: {n} submissions (no kind in the map)')


if __name__ == '__main__':
    main(sys.argv)
