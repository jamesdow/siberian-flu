#!/usr/bin/env python3
"""Normalise a research result into data/outbreak.json.
Usage: python3 scripts/postprocess.py <result.json>
Accepts either the data object itself or a wrapper with a "data" key."""
import json, sys, datetime as dt

src = sys.argv[1]
r = json.load(open(src))
d = r.get('data', r) if isinstance(r, dict) else r
if not d: sys.exit('no data in result')

d.setdefault('title', 'Irkutsk Plague Watch')
d.setdefault('eyebrow', 'Siberia · Yersinia pestis · laboratory incident')

def day(s): return dt.date.fromisoformat(s)
NUM = ['deaths', 'confirmed', 'suspected', 'under_observation', 'hospitalized', 'symptomatic', 'cleared']

# series: sort, de-duplicate by date, fill gaps by carrying forward
series = sorted(d.get('series', []), key=lambda s: s['date'])
by_date = {}
for s in series: by_date[s['date']] = s
if not by_date: sys.exit('empty series')
first, last = day(min(by_date)), day(d['updated'])
out, prev = [], None
cur = first
while cur <= last:
    k = cur.isoformat()
    s = by_date.get(k)
    if s is None:
        s = {'date': k, 'note': 'No new figure; carried forward.'}
        for n in NUM:
            if prev is not None and n in prev: s[n] = prev[n]
    else:
        for n in NUM:
            if n not in s and prev is not None and n in prev: s[n] = prev[n]
    for n in ['deaths', 'confirmed', 'suspected', 'under_observation', 'symptomatic']: s.setdefault(n, 0)
    out.append(s); prev = s; cur += dt.timedelta(days=1)
d['series'] = out

# counts mirror the last series entry
counts = d.setdefault('counts', {})
for n in NUM:
    if n in out[-1]: counts[n] = out[-1][n]
counts.setdefault('as_of', out[-1]['date'])

# watch items as to-do objects
d['watch'] = [({'text': w, 'done': False} if isinstance(w, str) else w) for w in d.get('watch', [])]

# headlines: newest first, no alarmist, max two per outlet, max 14
seen = {}
heads = []
for h in sorted(d.get('headlines', []), key=lambda h: h.get('date', ''), reverse=True):
    if h.get('tone') == 'alarmist': continue
    if not h.get('date') or h['date'] == 'unknown': continue
    k = h.get('source', '').strip().lower()
    if seen.get(k, 0) >= 2: continue
    seen[k] = seen.get(k, 0) + 1
    heads.append({'date': h['date'], 'source': h['source'], 'title': h['title'].strip(), 'url': h['url'], 'tone': h.get('tone', 'neutral')})
d['headlines'] = heads[:14]

d['timeline'] = sorted(d.get('timeline', []), key=lambda t: t['date'])

json.dump(d, open('data/outbreak.json', 'w'), indent=2, ensure_ascii=False)
print(f"wrote data/outbreak.json · {len(out)} days ({out[0]['date']} to {out[-1]['date']}) · counts {json.dumps({k: counts.get(k) for k in NUM if k in counts})} as of {counts['as_of']} · {len(heads[:14])} headlines · {len(d['timeline'])} timeline · status {d.get('status')}")
