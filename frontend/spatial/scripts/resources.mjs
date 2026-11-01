import { cp, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const output = process.argv.includes('--dev') ? resolve('public') : resolve('../../src/beamerpkg/static/spatial');
const target = `${output}/pdfjs`;
await mkdir(target, { recursive: true });
for (const name of ['cmaps', 'standard_fonts', 'iccs', 'wasm']) {
  await cp(`node_modules/pdfjs-dist/${name}`, `${target}/${name}`, { recursive: true });
}
await cp('node_modules/pdfjs-dist/LICENSE', `${target}/LICENSE`);
const notices = [];
for (const name of ['pdfjs-dist', 'react', 'react-dom', 'scheduler', 'zod']) {
  const base = `node_modules/${name}`;
  const pkg = JSON.parse(await readFile(`${base}/package.json`, 'utf8'));
  const license = (await readdir(base)).find(x => /^license/i.test(x));
  notices.push(`${name} ${pkg.version} (${pkg.license})\n${license ? await readFile(`${base}/${license}`, 'utf8') : 'See dependency package license.'}`);
}
await writeFile(`${output}/THIRD_PARTY_NOTICES.txt`, notices.join('\n\n-----\n\n'));
