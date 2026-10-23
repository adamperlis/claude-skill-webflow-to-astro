#!/usr/bin/env python3
"""Unzip a Webflow Code Export safely.

    python3 -I unzip_webflow.py ~/Downloads/<site>.webflow.zip <out-dir>

Webflow's ZIPs store some file names in cp437 without the UTF-8 flag (names
with curly quotes, accents, odd spaces), and macOS `unzip` stops on them
with a misleading "write error (disk full?)". This decodes each name,
refuses paths that escape <out-dir>, and prints MISSING.txt (the files
Webflow failed to export; scripts/mirror.py fetches them from the CDN).
"""
import os
import sys
import zipfile

if len(sys.argv) < 3:
    sys.exit(__doc__)
src, out = sys.argv[1], os.path.abspath(sys.argv[2])
z = zipfile.ZipFile(src)
n = 0
for info in z.infolist():
    name = info.filename
    if not info.flag_bits & 0x800:
        try:
            name = name.encode('cp437').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    if name.endswith('/'):
        continue
    dest = os.path.normpath(os.path.join(out, name))
    if not dest.startswith(out + os.sep):
        sys.exit(f'refusing {name!r}: outside {out}')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with z.open(info) as r, open(dest, 'wb') as w:
        w.write(r.read())
    n += 1
print(f'{n} files → {out}')
missing = os.path.join(out, 'MISSING.txt')
if os.path.exists(missing):
    print('\nMISSING.txt:\n' + open(missing).read())
