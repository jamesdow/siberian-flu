#!/usr/bin/env python3
"""Apply a daily delta (from the research workflow) to data/outbreak.json.
Usage: python3 scripts/apply_delta.py <delta.json>"""
import json, sys, re
delta = json.load(open(sys.argv[1]))
delta = delta.get('delta', delta)
p = 'data/outbreak.json'; d = json.load(open(p))
def clean(t):
    t = re.sub(r';?\s*also\s+https?://\S+', '', t or ''); t = re.sub(r',?\s*https?://\S+', '', t)
    t = re.sub(r'\(\s*\)', '', t); return re.sub(r'\s{2,}', ' ', t).strip()
e = delta['series_entry']; e['note'] = clean(e['note']); e['note_short'] = clean(e['note_short'])
d['series'] = [s for s in d['series'] if s['date'] != e['date']] + [e]
d['series'].sort(key=lambda s: s['date'])
for k in ['deaths', 'confirmed', 'suspected', 'under_observation', 'hospitalized', 'symptomatic']: d['counts'][k] = e[k]
d['counts']['as_of'] = delta['counts_as_of']
seen = {h['url'] for h in d['headlines']}
new = [h for h in delta['headlines_new'] if h['url'] not in seen and h.get('tone') != 'alarmist']
heads = sorted(new + d['headlines'], key=lambda h: h['date'], reverse=True)
per = {}; out = []
for h in heads:
    k = h['source'].strip().lower()
    if per.get(k, 0) >= 2: continue
    per[k] = per.get(k, 0) + 1; out.append(h)
d['headlines'] = out[:14]
have = {(t['date'], t['text'][:60]) for t in d['timeline']}
for t in delta['timeline_new']:
    t['text'] = clean(t['text'])
    if (t['date'], t['text'][:60]) not in have: d['timeline'].append(t)
d['timeline'].sort(key=lambda t: t['date'])
d['watch'] = delta['watch']; d['unknowns'] = [clean(u) for u in delta['unknowns']]
d['status'] = delta['status']; d['status_note'] = clean(delta['status_note']); d['method_note'] = clean(delta['method_note'])
d['updated'] = e['date']
json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
print(f"applied {e['date']}: counts {d['counts']} · +{len(new)} headlines · +{len(delta['timeline_new'])} timeline · status {d['status']}")
print('SUMMARY:\n' + delta.get('summary', ''))
