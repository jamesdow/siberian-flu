// Builds index.html (full document, for GitHub) and artifact.html (page fragment, for the claude.ai artifact)
// from src/page.html and data/outbreak.json. Run: node scripts/build.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const template = readFileSync(resolve(root, 'src/page.html'), 'utf8');
const dataText = readFileSync(resolve(root, 'data/outbreak.json'), 'utf8');
const data = JSON.parse(dataText); // fail loudly on a broken data file

const required = ['updated', 'status', 'counts', 'series', 'headlines'];
for (const k of required) if (!(k in data)) throw new Error(`data/outbreak.json is missing "${k}"`);
if (!/^\d{4}-\d{2}-\d{2}$/.test(data.updated)) throw new Error(`"updated" must be YYYY-MM-DD, got ${data.updated}`);
for (const s of data.series) if (!/^\d{4}-\d{2}-\d{2}$/.test(s.date)) throw new Error(`series date must be YYYY-MM-DD, got ${s.date}`);

const section = (name) => {
  const m = template.match(new RegExp(`<!-- ${name} -->([\\s\\S]*?)<!-- /${name} -->`));
  if (!m) throw new Error(`template is missing the ${name} section`);
  return m[1].trim();
};
const json = JSON.stringify(data).replace(/<\/script/gi, '<\\/script').replace(/<!--/g, '<\\!--');
const head = section('HEAD');
const body = section('BODY').replace('__DATA__', () => json);

writeFileSync(resolve(root, 'artifact.html'), `${head}\n${body}\n`);
writeFileSync(resolve(root, 'index.html'),
  `<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="description" content="A calm daily tracker of the Irkutsk plague laboratory incident: counts, headlines, timeline.">\n${head}\n</head>\n<body>\n${body}\n</body>\n</html>\n`);
console.log(`built index.html and artifact.html · updated ${data.updated} · ${data.series.length} days · ${data.headlines.length} headlines`);
