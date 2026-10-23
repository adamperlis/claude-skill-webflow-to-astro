#!/usr/bin/env bash
# Lighthouse (desktop) in a clean headless Chrome: no extensions, which in a
# day-to-day browser inflate Total Blocking Time and fail Best Practices with
# their own deprecated APIs. Prints each page's four scores and FCP/LCP/TBT,
# and the audits under 0.9.
#   lighthouse.sh https://example.pages.dev / /about /contact
# Needs Node (npx fetches Lighthouse 12) and Chrome or Chromium. On macOS it
# uses Google Chrome from /Applications; elsewhere Lighthouse finds Chrome on
# its own, or set CHROME_PATH.
set -e
origin=$1; shift
out=${TMPDIR:-/tmp}/lighthouse-$$; mkdir -p "$out"
mac_chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ -z $CHROME_PATH && -x $mac_chrome ]]; then export CHROME_PATH=$mac_chrome; fi
for p in "${@:-/}"; do
  f=$out/$(echo "$p" | tr '/' '_').json
  npx -y lighthouse@12 "$origin$p" --preset=desktop --quiet --output=json --output-path="$f" --chrome-flags="--headless=new" >/dev/null 2>&1
  python3 -I -c "
import json; r=json.load(open('$f')); c=r['categories']; a=r['audits']
print('$p', {k:round(v['score']*100) for k,v in c.items()}, 'FCP',a['first-contentful-paint']['displayValue'],'LCP',a['largest-contentful-paint']['displayValue'],'TBT',a['total-blocking-time']['displayValue'])
print('   under 0.9:', [k for k,v in a.items() if v.get('score') is not None and v['score']<0.9 and v.get('scoreDisplayMode') in ('binary','numeric','metricSavings')][:12])"
done
echo "reports: $out"
