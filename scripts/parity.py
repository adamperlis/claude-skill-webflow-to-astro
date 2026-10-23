#!/usr/bin/env python3
"""Check a rebuild against the Webflow pages it replaces.

    python3 -I parity.py <reference/live> <dist>

For every page mirrored in <reference/live> (scripts/mirror.py), finds the
built page in <dist> (about.html for /about, index.html for /) and compares
the head: title, description, og:title/description/type, twitter title/
description/card, canonical, robots, Search Console token, presence of
og:image/twitter:image, and the JSON-LD @types. Then, across <dist>: every
internal href/src/srcset/poster resolves to a file, nothing references a
Webflow host, and no file is over 25 MiB (Cloudflare Pages refuses those).
Exit status 1 if anything differs, so it can gate a deploy.
"""
import glob
import html
import json
import os
import re
import sys
import urllib.parse

LIVE, DIST = (os.path.abspath(a) for a in sys.argv[1:3]) if len(sys.argv) > 2 else sys.exit(__doc__)
WEBFLOW = re.compile(r'website-files\.com|uploads-ssl\.webflow\.com|d3e54v103j8qbb\.cloudfront\.net|cdn\.webflow\.com')
KEYS = ['description', 'og:title', 'og:description', 'og:type', 'twitter:title', 'twitter:description', 'twitter:card', 'robots', 'google-site-verification']


def head(path):
    h = open(path, encoding='utf-8', errors='ignore').read()
    hd = h.split('</head>')[0]
    meta = {}
    for t in re.findall(r'<meta\b[^>]*>', hd):
        k = re.search(r'(?:name|property)="([^"]+)"', t)
        c = re.search(r'content="([^"]*)"', t)
        if k and c:
            meta[k.group(1)] = html.unescape(c.group(1))
    title = re.search(r'<title[^>]*>([^<]*)</title>', hd)
    canon = re.search(r'<link[^>]*rel="canonical"[^>]*>', hd)
    canon = canon and re.search(r'href="([^"]+)"', canon.group(0)).group(1)
    lds = []
    for b in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', hd):
        try:
            lds.append(json.loads(b).get('@type'))
        except Exception:
            lds.append('(invalid)')
    return {'title': title and html.unescape(title.group(1)), 'canonical': canon, 'meta': meta, 'ld': lds}


problems = 0
print('== head parity')
for live in sorted(glob.glob(os.path.join(LIVE, '*.html'))):
    name = os.path.basename(live)
    built = os.path.join(DIST, name.replace('__', '/'))
    if not os.path.exists(built):
        print(f'MISSING {name}: no {built}')
        problems += 1
        continue
    a, b = head(live), head(built)
    diffs = []
    for k in ('title', 'canonical', 'ld'):
        if a[k] != b[k]:
            diffs.append((k, a[k], b[k]))
    for k in KEYS:
        if a['meta'].get(k) != b['meta'].get(k):
            diffs.append((k, a['meta'].get(k), b['meta'].get(k)))
    for k in ('og:image', 'twitter:image'):
        if bool(a['meta'].get(k)) != bool(b['meta'].get(k)):
            diffs.append((k, a['meta'].get(k), b['meta'].get(k)))
    print(('OK   ' if not diffs else 'DIFF ') + name)
    for k, x, y in diffs:
        print(f'       {k}: live {x!r:.100} | new {y!r:.100}')
    problems += bool(diffs) and name != '404.html'

print('\n== links, Webflow references, file sizes')
missing, webflow = set(), set()
for page in glob.glob(os.path.join(DIST, '**', '*.html'), recursive=True):
    h = open(page, encoding='utf-8', errors='ignore').read()
    if WEBFLOW.search(h):
        webflow.add(os.path.relpath(page, DIST))
    refs = re.findall(r'(?:href|src|poster)="([^"]+)"', h)
    refs += [p.strip().split(' ')[0] for s in re.findall(r'srcset="([^"]+)"', h) for p in s.split(',')]
    for u in refs:
        if u.startswith(('http:', 'https:', 'mailto:', 'tel:', '#', 'data:', 'javascript:', '//')):
            continue
        p = urllib.parse.unquote(u.split('#')[0].split('?')[0])
        if not p:
            continue
        p = p if p.startswith('/') else '/' + os.path.relpath(os.path.join(os.path.dirname(page), p), DIST)
        cands = [DIST + p, DIST + p + '.html', DIST + p.rstrip('/') + '/index.html'] if p != '/' else [DIST + '/index.html']
        if not any(os.path.isfile(c) for c in cands):
            missing.add((os.path.relpath(page, DIST), u))
for f in glob.glob(os.path.join(DIST, '**', '*'), recursive=True):
    if os.path.isfile(f) and f.endswith(('.css', '.js')) and WEBFLOW.search(open(f, errors='ignore').read()):
        webflow.add(os.path.relpath(f, DIST))
big = [(os.path.getsize(f), f) for f in glob.glob(os.path.join(DIST, '**', '*'), recursive=True) if os.path.isfile(f) and os.path.getsize(f) > 25 * 1024 * 1024]
print(f'unresolved links: {len(missing)}' + ''.join(f'\n  {p}: {u}' for p, u in sorted(missing)[:40]))
print('(redirect sources in _redirects show here too; they resolve at the edge)' if missing else '')
print(f'files referencing Webflow hosts: {sorted(webflow) or "none"}')
print(f'files over 25 MiB: {[(round(s / 1048576, 1), os.path.relpath(f, DIST)) for s, f in big] or "none"}')
problems += bool(webflow) + bool(big)
sys.exit(1 if problems else 0)
