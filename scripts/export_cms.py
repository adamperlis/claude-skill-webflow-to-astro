#!/usr/bin/env python3
"""Export every Webflow CMS collection, with its schema, items and images.

    WEBFLOW_TOKEN=… python3 -I export_cms.py <site_id> <out-dir> [--images]

Needs a Webflow Data API v2 token with cms:read (Site settings → Apps &
integrations → API access; the owner makes it). Writes, per collection,
<out>/<slug>/schema.json and <out>/<slug>/items.json (every item, drafts and
archived ones too, with isDraft/isArchived so you can choose), and with
--images downloads every image/file field to <out>/<slug>/files/ and adds a
`localFile` beside each URL. Rich text stays HTML: convert it in the import
step for the chosen CMS (Portable Text for Sanity, Markdown for content
collections). Reference fields hold item IDs; resolve them across
collections on import.

With the Webflow MCP connected, the same data comes from data_cms_tool
(get_collection_list, get_collection_details, list_collection_items).
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

if len(sys.argv) < 3 or not os.environ.get('WEBFLOW_TOKEN'):
    sys.exit(__doc__)
SITE, OUT = sys.argv[1], os.path.abspath(sys.argv[2])
IMAGES = '--images' in sys.argv
API = 'https://api.webflow.com/v2'
HDR = {'Authorization': f"Bearer {os.environ['WEBFLOW_TOKEN']}", 'accept': 'application/json'}


def api(path):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, headers=HDR), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited: back off
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError('rate limited too long: ' + path)


def files_in(value):
    """image/file field values: {'url': …} or a list of them"""
    if isinstance(value, dict) and 'url' in value:
        yield value
    elif isinstance(value, list):
        for v in value:
            yield from files_in(v)


for c in api(f'/sites/{SITE}/collections')['collections']:
    slug = c['slug']
    d = os.path.join(OUT, slug)
    os.makedirs(d, exist_ok=True)
    schema = api(f"/collections/{c['id']}")
    json.dump(schema, open(os.path.join(d, 'schema.json'), 'w'), indent=1)
    items, offset = [], 0
    while True:
        page = api(f"/collections/{c['id']}/items?limit=100&offset={offset}")
        items += page['items']
        offset += 100
        if offset >= page['pagination']['total']:
            break
    if IMAGES:
        os.makedirs(os.path.join(d, 'files'), exist_ok=True)
        for it in items:
            for value in it['fieldData'].values():
                for f in files_in(value):
                    name = re.sub(r'[^A-Za-z0-9._-]+', '-', urllib.parse.unquote(f['url'].rsplit('/', 1)[-1]))
                    dest = os.path.join(d, 'files', name)
                    if not os.path.exists(dest):
                        urllib.request.urlretrieve(f['url'], dest)
                    f['localFile'] = f'files/{name}'
    json.dump(items, open(os.path.join(d, 'items.json'), 'w'), indent=1, ensure_ascii=False)
    live = sum(1 for i in items if not i.get('isDraft') and not i.get('isArchived'))
    print(f"{c['displayName']:<36} {len(items):>4} items ({live} published) → {d}")
