#!/usr/bin/env node
// 命令列版：與網頁共用 translit.js、data.js，結果相同。
//   npx -y github:alexwudev/name-translit fi place Kuuterselkä Vuosalmi
//   npx -y github:alexwudev/name-translit ru person "Константин Рокоссовский"
//   echo Kuuterselkä | npx -y github:alexwudev/name-translit fi place
// 選項：-v 顯示音節與來源；--json 輸出 JSON（給程式或 AI 解析）。
'use strict';
const T = require('./translit.js');

const USAGE = `用法：name-translit <fi|ru|id> <place|person> [原文…] [-v] [--json]
  fi 芬蘭語／ru 俄語（西里爾字母）／id 印尼語；place 地名／person 人名
  沒給原文時從標準輸入讀，每行一個。
  依中文維基外語譯音表與中國國標音譯，輸出繁體字形；台灣已有通行譯名時以通行譯名為準。`;

function main(argv) {
  const flags = new Set(argv.filter((a) => a.startsWith('-')));
  const args = argv.filter((a) => !a.startsWith('-'));
  if (flags.has('-h') || flags.has('--help') || args.length < 2) { console.log(USAGE); return args.length < 2 && !flags.has('-h') && !flags.has('--help') ? 1 : 0; }
  const [lang, mode, ...words] = args;
  if (!T[lang]) { console.error(`不支援的語言：${lang}（只有 fi、ru、id）`); return 1; }
  if (mode !== 'place' && mode !== 'person') { console.error(`類別要是 place 或 person：${mode}`); return 1; }
  const run = (list) => {
    const results = list.map((w) => ({ src: w, ...T[lang](w, mode) }));
    if (flags.has('--json')) {
      console.log(JSON.stringify(results.map((r) => ({ src: r.src, zh: r.zh, extra: Object.fromEntries(r.extra || []), error: r.error,
        ...(flags.has('-v') ? { detail: r.info } : {}) })), null, 1));
      return;
    }
    for (const r of results) {
      const extra = (r.extra || []).map(([k, v]) => `\t${k}：${v}`).join('');
      console.log(`${r.src}\t${r.error ? '（' + r.error + '）' : r.zh}${extra}`);
      if (flags.has('-v')) for (const x of r.info || []) {
        console.log(`    ${x.src}${x.syl ? '：' + x.syl : ''}｜${(x.trace || []).join('，')}`);
        for (const n of x.notes || []) console.log(`      註：${n}`);
      }
    }
  };
  if (words.length) { run(words); return 0; }
  let buf = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (d) => { buf += d; });
  process.stdin.on('end', () => run(buf.split(/\r?\n/).map((l) => l.trim()).filter((l) => l)));
  return 0;
}
process.exitCode = main(process.argv.slice(2));
