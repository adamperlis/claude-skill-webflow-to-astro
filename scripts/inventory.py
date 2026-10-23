#!/usr/bin/env python3
"""Inventory a live Webflow site before moving it (read-only).

    python3 -I inventory.py https://www.example.com > inventory.md

Prints, as Markdown: hosting and DNS (apex, www, NS, MX, SPF, DMARC), the
sitemap and robots, then for every sitemap page its head (title,
description, OG image, canonical, noindex, JSON-LD types), CMS lists, forms
(Finsweet cookie forms left out), background videos with their sizes, and
across the site the third-party hosts and analytics IDs. It also lists the
CDN files over 25 MiB (Cloudflare Pages' limit) and the biggest videos (the
usual bandwidth culprits). Follow up with the Webflow API (collections and
item counts, forms, webhooks) and the dashboard (301s, HSTS); see
references/inventory.md.
"""
import collections
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ORIGIN = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else sys.exit(__doc__)
HOST = urllib.parse.urlparse(ORIGIN).hostname
APEX = HOST[4:] if HOST.startswith('www.') else HOST
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) webflow-inventory'}
CDN = re.compile(r'https?://(?:cdn\.prod\.website-files\.com|uploads-ssl\.webflow\.com|assets\.website-files\.com|assets-global\.website-files\.com|global-uploads\.webflow\.com|d3e54v103j8qbb\.cloudfront\.net)/(?:[^\s"\'()<>,&\\]|\(\d+\))+')


def get(url, method='GET'):
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, dict(r.headers), (r.read() if method == 'GET' else b'')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), b''


def dig(*args):
    try:
        return subprocess.run(['dig', '+short', *args], capture_output=True, text=True, timeout=20).stdout.split()
    except Exception:
        return ['(dig unavailable)']


def head_of(h):
    hd = h.split('</head>')[0]
    m = lambda p: (lambda x: html.unescape(x.group(1)) if x else None)(re.search(p, hd))
    lds = []
    for block in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', hd):
        try:
            lds.append(json.loads(block).get('@type'))
        except Exception:
            lds.append('(invalid JSON-LD)')
    return {
        'title': m(r'<title>([^<]*)</title>'),
        'description': m(r'<meta content="([^"]*)" name="description"'),
        'og': (m(r'<meta content="([^"]*)" property="og:image"') or '').rsplit('/', 1)[-1][:50],
        'canonical': m(r'<link href="([^"]*)" rel="canonical"'),
        'noindex': bool(re.search(r'name="robots"[^>]*noindex|noindex[^>]*name="robots"', hd)),
        'ld': lds,
    }


print(f'# Inventory: {ORIGIN}\n')
print('## Hosting and DNS\n')
s, hdrs, _ = get(ORIGIN + '/', 'HEAD')
print(f"- {ORIGIN}/ → {s}; server `{hdrs.get('server')}`; Webflow: {'x-wf-region' in {k.lower() for k in hdrs}}")
for name in (APEX, 'www.' + APEX):
    print(f'- `{name}` → {", ".join(dig(name)) or "—"}')
print(f'- NS: {", ".join(dig("NS", APEX))}')
print(f'- MX: {", ".join(dig("MX", APEX)) or "none"}  ← if this is Google/Microsoft, Email Routing must NOT take the apex')
txt = dig('TXT', APEX)
print(f'- SPF: {" ".join(t for t in " ".join(txt).split(chr(34)) if "spf1" in t) or "none"}')
print(f'- DMARC: {" ".join(dig("TXT", "_dmarc." + APEX)) or "none"}')
for alt in (f'https://{APEX}/', f'https://www.{APEX}/'):
    st, h2, _ = get(alt, 'HEAD')
    print(f'- {alt} → {st} {h2.get("location", h2.get("Location", ""))}')

print('\n## Sitemap and robots\n')
_, _, sm = get(ORIGIN + '/sitemap.xml')
urls = re.findall(r'<loc>([^<]+)</loc>', sm.decode('utf-8', 'ignore'))
print(f'{len(urls)} URLs. By first path segment:')
for seg, n in collections.Counter('/' + urllib.parse.urlparse(u).path.strip('/').split('/')[0] for u in urls).most_common():
    print(f'- `{seg}` × {n}{"  ← likely a CMS collection" if n > 2 else ""}')
_, _, rb = get(ORIGIN + '/robots.txt')
print('\n```\n' + rb.decode('utf-8', 'ignore').strip() + '\n```')

print('\n## Pages\n')
hosts, ids, videos, cdn = collections.Counter(), set(), {}, set()
for u in urls:
    st, _, body = get(u)
    h = body.decode('utf-8', 'ignore')
    hd = head_of(h)
    path = urllib.parse.urlparse(u).path or '/'
    forms = [f for f in re.findall(r'<form[^>]*>', h) if 'Cookie' not in f and 'fs-cc' not in f]
    form_names = [(re.search(r'data-name="([^"]*)"', f) or re.search(r'name="([^"]*)"', f)).group(1) if re.search(r'name="', f) else '?' for f in forms]
    hidden = len(re.findall(r'class="section[^"]*\bhidden\b', h))
    print(f"### `{path}` ({st})\n- title: {hd['title']!r}\n- description: {hd['description']!r}\n- canonical: {hd['canonical']} · OG: {hd['og']} · noindex: {hd['noindex']} · JSON-LD: {hd['ld']}")
    print(f"- CMS lists: {h.count('w-dyn-list')} · forms: {form_names or 'none'} · hidden sections: {hidden}")
    for host in re.findall(r'(?:src|href)="https?://([^/"]+)', h):
        hosts[host] += 1
    ids |= set(re.findall(r'\b(G-[A-Z0-9]{8,}|GTM-[A-Z0-9]{5,}|UA-\d+-\d+)\b', h))
    ids |= {f'fbq:{x}' for x in re.findall(r"fbq\('init',\s*'(\d+)'", h)}
    ids |= {f'twq:{x}' for x in re.findall(r"twq\('config',\s*'([a-z0-9]+)'", h)}
    for v in re.findall(r'data-video-urls="([^"]+)"', h):
        for vu in v.split(','):
            videos.setdefault(vu, set()).add(path)
    cdn |= set(CDN.findall(h))

print('## Across the site\n')
print('Third-party hosts (src/href counts):')
for host, n in hosts.most_common(40):
    print(f'- {host} × {n}')
print(f'\nAnalytics and pixel IDs: {", ".join(sorted(ids)) or "none"}  ← check each one actually fires (some Webflow snippets never ran)')

print('\n## Videos and big files\n')
sized = []
for u in sorted(cdn | set(videos)):
    if not re.search(r'\.(mp4|webm|mov|gif|png|jpe?g|webp|pdf|zip|json)$', u.split('?')[0], re.I):
        continue
    _, hh, _ = get(u, 'HEAD')
    size = int(hh.get('content-length') or hh.get('Content-Length') or 0)
    sized.append((size, u))
for size, u in sorted(sized, reverse=True)[:15]:
    flag = '  ← over 25 MiB: Pages refuses it' if size > 25 * 1024 * 1024 else ''
    used = ', '.join(sorted(videos.get(u, [])))
    print(f'- {size / 1048576:6.1f} MiB  {urllib.parse.unquote(u.rsplit("/", 1)[-1])[:80]}{"  on " + used if used else ""}{flag}')
print('\nA small video on a busy page (or one in a hidden section, which still downloads) is the usual bandwidth culprit.')
