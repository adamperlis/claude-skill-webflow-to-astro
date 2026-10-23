#!/usr/bin/env python3
"""Mirror a published Webflow site as the reference for its rebuild.

    python3 -I mirror.py https://www.example.com <repo>/reference [/extra-path ...]

Reads the site's sitemap.xml for its pages (pass any pages it leaves out,
like a form's /success page, as extra paths), and saves each page's HTML,
as served, to <out>/live/<name>.html, plus the 404 page. Every file the pages
load from Webflow's CDNs (images, video, CSS, JS, fonts, Lottie JSON, and
url()s inside the CSS) goes to <out>/assets/<kind>/, with
<out>/assets/manifest.json mapping each CDN URL to its file. Re-running only
fetches what's missing.

Commit <out>/live (the record of what was live) and the manifest; git-ignore
the rest of <out>/assets.
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.error
import urllib.request

ORIGIN = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else sys.exit(__doc__)
REF = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'reference')
EXTRA = sys.argv[3:]
ASSETS = os.path.join(REF, 'assets')
LIVE = os.path.join(REF, 'live')
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) webflow-mirror'}

NOT_FOUND_PROBE = '/__mirror-404-probe'

HOSTS = (
    'cdn.prod.website-files.com',
    'd3e54v103j8qbb.cloudfront.net',  # Webflow's jQuery
    'uploads-ssl.webflow.com',
    'assets.website-files.com',
    'assets-global.website-files.com',
    'global-uploads.webflow.com',
)
# a filename can hold "(1)"; otherwise stop where a URL ends in HTML, CSS or srcset
URL_RE = re.compile(r'https?://(?:%s)/(?:[^\s"\'()<>,&\\]|\(\d+\))+' % '|'.join(map(re.escape, HOSTS)))

KINDS = {
    'css': 'css', 'js': 'js',
    'mp4': 'videos', 'webm': 'videos', 'mov': 'videos',
    'woff': 'fonts', 'woff2': 'fonts', 'ttf': 'fonts', 'otf': 'fonts', 'eot': 'fonts',
    'png': 'images', 'jpg': 'images', 'jpeg': 'images', 'gif': 'images', 'svg': 'images',
    'webp': 'images', 'avif': 'images', 'ico': 'images',
}

manifest_path = os.path.join(ASSETS, 'manifest.json')
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
used = {v: k for k, v in manifest.items()}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.status, r.read()


def key(url):
    # the same file shows up both as …/site/id_name and …/site%2Fid_name
    return urllib.parse.unquote(url.split('?')[0])


def local(url):
    """Download a CDN file once and return its root-relative path."""
    k = key(url)
    if k in manifest:
        return manifest[k]
    name = k.rsplit('/', 1)[-1]
    base, dot, ext = name.rpartition('.')
    ext = ext.lower() if dot else ''
    kind = KINDS.get(ext, 'files')
    safe = re.sub(r'-+', '-', re.sub(r'[^A-Za-z0-9._-]+', '-', name)).strip('-')
    path = f'{kind}/{safe}'
    if path in used and used[path] != k:
        stem, _, e = safe.rpartition('.')
        path = f'{kind}/{stem}-{hashlib.sha1(k.encode()).hexdigest()[:6]}.{e}'
    dest = os.path.join(ASSETS, path)
    if not os.path.exists(dest):
        status, body = fetch(url)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if kind == 'css':
            for m in URL_RE.findall(body.decode('utf-8')):
                local(m)
        with open(dest, 'wb') as f:
            f.write(body)
        print(f'  {len(body):>10,}  {path}')
    manifest[k] = path
    used[path] = k
    return path


def pages():
    """route -> file name, from the sitemap plus any extra paths"""
    _, body = fetch(ORIGIN + '/sitemap.xml')
    routes = [urllib.parse.urlparse(u).path or '/' for u in re.findall(r'<loc>([^<]+)</loc>', body.decode('utf-8'))]
    out = {}
    for r in routes + EXTRA:
        r = '/' + r.strip('/')
        out[r] = 'index.html' if r == '/' else r.strip('/').replace('/', '__') + '.html'
    return out


def main():
    os.makedirs(LIVE, exist_ok=True)
    for route, file in list(pages().items()) + [(NOT_FOUND_PROBE, '404.html')]:
        status, body = fetch_404() if route == NOT_FOUND_PROBE else fetch(ORIGIN + route)
        print(f'{status} {route} -> reference/live/{file}')
        with open(os.path.join(LIVE, file), 'wb') as f:
            f.write(body)
        for m in URL_RE.findall(body.decode('utf-8')):
            try:
                local(m)
            except urllib.error.HTTPError as e:
                print(f'  {e.code} {m}')
    with open(manifest_path, 'w') as f:
        json.dump(dict(sorted(manifest.items())), f, indent=1)
    print(f'{len(manifest)} files in reference/assets/')


def fetch_404():
    try:
        return fetch(ORIGIN + NOT_FOUND_PROBE)
    except urllib.error.HTTPError as e:
        return e.code, e.read()


if __name__ == '__main__':
    sys.exit(main())
