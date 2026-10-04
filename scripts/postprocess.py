#!/usr/bin/env python3
"""Normalise a research result into data/outbreak.json.
Usage: python3 scripts/postprocess.py <result.json>
Accepts either the data object itself or a wrapper with a "data" key."""
import json, sys, re, datetime as dt

def clean(text):
    """Strip inline URLs from prose; sources live in source_url fields."""
    t = re.sub(r';?\s*also\s+https?://\S+', '', text or '')
    t = re.sub(r',?\s*https?://\S+', '', t)
    t = re.sub(r'\(\s*\)', '', t)
    t = re.sub(r'\(\s*[,;]\s*', '(', t)
    t = re.sub(r'\s+([.,;)])', r'\1', t)
    return re.sub(r'\s{2,}', ' ', t).strip()

def short(text):
    """One sentence for the table: skip carry-forward boilerplate when there is more to say."""
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    body = [x for x in sents if not re.search(r'carried forward|no new (contact )?(figure|count)', x, re.I)] or sents
    out = body[0]
    if len(out) > 210: out = out[:207].rsplit(' ', 1)[0] + '…'
    return out

src = sys.argv[1]
r = json.load(open(src))
d = r.get('data', r) if isinstance(r, dict) else r
if not d: sys.exit('no data in result')

d['title'] = 'Irkutsk Plague Watch'  # the page's name; the research title is kept in research_title
if r is not d and d.get('title') != 'Irkutsk Plague Watch': pass
d['eyebrow'] = d.get('eyebrow') or ('Irkutsk · suspected plague · laboratory incident' if not d.get('counts', {}).get('confirmed') else 'Irkutsk · plague · laboratory incident')

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
    s['note'] = clean(s.get('note', ''))
    s['note_short'] = short(s['note'])
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

for t in d.get('timeline', []): t['text'] = clean(t['text'])
for c in d.get('context', []): c['text'] = clean(c['text'])
d['unknowns'] = [clean(u) for u in d.get('unknowns', [])]
d['status_note'] = clean(d.get('status_note', ''))
d['timeline'] = sorted(d.get('timeline', []), key=lambda t: t['date'])

json.dump(d, open('data/outbreak.json', 'w'), indent=2, ensure_ascii=False)
print(f"wrote data/outbreak.json · {len(out)} days ({out[0]['date']} to {out[-1]['date']}) · counts {json.dumps({k: counts.get(k) for k in NUM if k in counts})} as of {counts['as_of']} · {len(heads[:14])} headlines · {len(d['timeline'])} timeline · status {d.get('status')}")
