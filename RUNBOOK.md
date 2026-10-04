# Daily update runbook

This repo is a calm daily tracker of the plague laboratory incident at the Irkutsk
Anti-Plague Research Institute (Irkutsk, Russia, from 25 September 2026). One file
holds all the data: `data/outbreak.json`. The page reads only that file. A scheduled
Claude routine follows these steps once a day; a person can follow them too.

## Steps

1. **Read the current data.** Open `data/outbreak.json`. Note `updated`, the last
   `series` entry, the `watch` items, and the headline URLs already present.

2. **Research today, in English and Russian.** Load the web tools and search with the
   extended mode. Fetch an article before citing it where the environment allows;
   when page fetching is blocked by the network policy (it was on 4 October 2026),
   verify each figure by finding it in at least two independent outlets or in an
   official statement relayed by a wire, and say so in `method_note`. Look at, in
   this order:
   - Official: Rospotrebnadzor (rospotrebnadzor.ru, 38.rospotrebnadzor.ru), the
     Irkutsk regional government (irkobl.ru), Governor Igor Kobzev as quoted,
     the Russian Ministry of Health, WHO Disease Outbreak News, ECDC weekly threats report.
   - Wires: TASS, Interfax, RIA Novosti, Reuters, AP, AFP.
   - Measured outlets: The Moscow Times, Meduza, Kommersant, RBC, BBC, Euronews, CNN,
     The Guardian, IrkutskMedia, IrCity, Baikal-Daily.
   - Useful queries: `Иркутск чума`, `противочумный институт Иркутск`,
     `Роспотребнадзор Иркутск чума наблюдение`, `Irkutsk plague`,
     `Irkutsk Anti-Plague Institute`.
   For every number record the as-of date (the date of the statement, not the publish
   date), the source and a short quote. Prefer official figures; when outlets
   disagree, take the official one and mention the other in the day's note.

3. **Update `data/outbreak.json`.** Keep the schema exactly as it is. Definitions:
   `deaths` are people who have died, whatever the officially stated cause.
   `confirmed` is plague officially confirmed by Rospotrebnadzor or the Ministry of
   Health, and stays 0 until they say so. `suspected` is plague reported or suspected
   but not officially confirmed. `under_observation` is identified contacts under
   medical observation, in hospital or at home. `hospitalized` is contacts placed in
   hospital for preventive observation. `symptomatic` is contacts who have developed
   symptoms or tested positive. `cleared` is contacts released from observation.
   - `series`: add one entry per calendar day since the last entry, through today.
     A day with no new figure carries the previous values forward and its `note`
     says "No new figure; carried forward." Never let `deaths` or `confirmed`
     decrease; if an official source revises a figure down, keep the series honest
     and explain the revision in that day's `note`.
   - `counts`: must equal the last series entry. `counts.as_of` is the date of the
     latest official figure.
   - `headlines`: add new ones with the exact published title, ISO date, outlet,
     URL and `tone`. At most two per outlet, at most 14 in total, newest first,
     and drop the oldest beyond that. Leave out alarmist outlets and headlines
     that lean on words like panic, deadly, horror, Black Death, mystery.
   - `timeline`: add dated events with a source. Keep it to the things that happened.
   - `watch`: when something on the list happens, set `done: true` on that item
     (an item may be a string or `{ "text": ..., "done": true|false }`); add what to
     watch for next. Keep three to five open items.
   - `unknowns`: remove what has become known; add what is newly unclear.
   - `status`: `watching` while contacts are under observation with no secondary
     case; `spreading` if any contact or other person is confirmed infected;
     `contained` once the observation period has ended with no further case;
     `resolved` when authorities close the incident. Update `status_note` (one
     sentence, with its as-of date) to match.
   - `origin_label`: the phrase after "N days" in the masthead; keep it honest about
     whether the start date is official or reported.
   - `method_note`: how today's figures were checked.
   - `updated`: today's date as `YYYY-MM-DD`.

4. **Build.** Run `node scripts/build.mjs`. It fails loudly if the JSON is broken
   or a date is malformed. Fix the data, not the script.

5. **Commit and push.**
   `git add -A && git commit -m "Daily update YYYY-MM-DD" && git push origin main`

6. **Republish the page.** With the Artifact tool, first `read` the artifact URL
   given in `README.md`, then `publish` `artifact.html` to that same `url`.

7. **Report in three lines:** the counts with their as-of date, what changed since
   yesterday, and how many headlines were added. If nothing changed, say so plainly.

## Tone

Plain, specific, short sentences. No exclamation marks. State what is known, what is
not, and the date each figure refers to. The pathogen is the bacterium Yersinia
pestis, not a virus. Do not speculate about causes, cover-ups or bioweapons; if a
named outlet alleges something, it is that outlet's claim, not a fact.
