// node tools/test.js：比對網頁版與 Python 版（tools/expected.json）的譯名
const path = require('path');
const T = require(path.join(__dirname, '..', 'translit.js'));
const exp = require(path.join(__dirname, 'expected.json'));
let ok = 0, bad = 0;
for (const [k, v] of Object.entries(exp)) {
  const [lang, mode, w] = k.split('|');
  const r = T[lang](w, mode);
  const got = JSON.stringify([r.zh, r.extra]);
  const want = JSON.stringify([v.zh, v.extra]);
  if (got === want) ok++; else { bad++; console.log(`不同 ${k}\n  JS ${got}\n  PY ${want}`); }
}
console.log(`相同 ${ok}｜不同 ${bad}`);
process.exitCode = bad ? 1 : 0;
