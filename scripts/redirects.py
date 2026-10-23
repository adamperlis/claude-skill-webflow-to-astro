#!/usr/bin/env python3
"""Webflow 301s → Cloudflare Pages `_redirects`, and a checker for them.

    python3 -I redirects.py from-csv <webflow-301s.csv>       # prints _redirects lines
    python3 -I redirects.py check <public/_redirects> <base-url>

from-csv reads Webflow's export (Site settings → Publishing → 301 redirects →
Export; columns old path, new path), converts Webflow's regex captures
`(.*)` + `%1` into Pages' `*` + `:splat` (or `:p1`, `:p2` placeholders for
captures mid-path), lowercases sources (Webflow matched case-insensitively),
and adds a trailing-slash variant for each static source.

check requests each rule's source on <base-url> without following
redirects and reports anything that isn't the rule's status with the
expected Location. Wildcards are tried with a sample segment, and it flags
chains (a target that redirects again). Exit 1 if any rule fails.
"""
import csv
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def convert(old, new):
    old, new = old.strip(), new.strip()
    if not old or old.lower() in ('old path', 'source', 'from'):
        return []
    caps = re.findall(r'\([^)]*\)', old)
    if caps:
        src = old
        tgt = new
        if len(caps) == 1 and old.endswith(caps[0]):
            src = old[: -len(caps[0])] + '*'
            tgt = new.replace('%1', ':splat')
        else:
            for i, c in enumerate(caps, 1):
                src = src.replace(c, f':p{i}', 1)
                tgt = tgt.replace(f'%{i}', f':p{i}')
        return [f'{src.lower()}  {tgt}  301']
    src = old.lower().rstrip('/') or '/'
    lines = [f'{src}  {new}  301']
    if src != '/':
        lines.append(f'{src}/  {new}  301')
    return lines


def from_csv(path):
    print("# Webflow's 301s (Site settings → Publishing), converted by redirects.py")
    for row in csv.reader(open(path, newline='', encoding='utf-8-sig')):
        if len(row) >= 2:
            for line in convert(row[0], row[1]):
                print(line)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def head(url):
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, method='GET', headers={'User-Agent': 'redirects-check'})
    try:
        r = opener.open(req, timeout=30)
        return r.status, r.headers.get('Location')
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get('Location')


def check(path, base):
    base = base.rstrip('/')
    failed = 0
    for line in open(path, encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        parts = line.split()
        src, tgt, status = parts[0], parts[1], int(parts[2]) if len(parts) > 2 else 301
        sample = src.replace('*', 'sample-path')
        sample = re.sub(r':(\w+)', 'sample', sample)
        expect = tgt.replace(':splat', 'sample-path')
        expect = re.sub(r':(\w+)', 'sample', expect)
        got, loc = head(base + sample)
        loc_path = urllib.parse.urlparse(loc).path if loc and loc.startswith(base) else loc
        ok = got == status and loc_path in (expect, base + expect)
        hops = ''
        if ok and loc:
            nxt = loc if loc.startswith('http') else base + loc
            s2, _ = head(nxt)
            if 300 <= s2 < 400:
                ok, hops = False, f' → then {s2} (a chain)'
        print(('OK   ' if ok else 'FAIL ') + f'{sample} → {got} {loc}{hops}' + ('' if ok else f'   expected {status} {expect}'))
        failed += not ok
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'from-csv':
        from_csv(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == 'check':
        check(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
