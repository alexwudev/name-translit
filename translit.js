// 芬蘭語、俄語、印尼語地名人名音譯（依中文維基「外語譯音表」與中國國標）。
// 由 Python 版 fi_translit.py、ru_translit.py、id_translit.py 逐行移植，規則說明見 README。
(function (root) {
  const T = typeof TABLES !== 'undefined' ? TABLES : require('./data.js');

  function pickFactory(emptyMark) {
    return function pick(cell, notes, label) {
      if (!cell || !cell.main || !cell.main.length || (emptyMark && (cell.main[0] === '—' || cell.main[0] === ''))) {
        notes.push(`${label}：表上此格為空${emptyMark ? '或「—」' : ''}`);
        return '?';
      }
      if (cell.main.length > 1 || cell.alt.length) {
        notes.push(`${label}：取「${cell.main[0]}」，另有 ${cell.main.slice(1).concat(cell.alt).join('、')}`);
      }
      return cell.main[0];
    };
  }
  const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const byLenDesc = (arr) => arr.slice().sort((a, b) => b.length - a.length);

  // ================= 芬蘭語 =================
  const FI = (() => {
    const VOW = 'aeiouyäöåü';
    const COL = { b: 'b', c: 'c', d: 'd', f: 'f', g: 'g', h: 'h', j: 'j', k: 'k', q: 'k', l: 'l', m: 'm', n: 'n', p: 'p', r: 'r', s: 's', t: 't', v: 'v', w: 'v', x: 'x', z: 'ts', ts: 'ts', tz: 'ts' };
    const GENERIC = [['järvi', '湖'], ['joki', '河'], ['saari', '島'], ['lahti', '灣']];
    const pick = pickFactory(true);
    const isV = (c) => c !== '' && VOW.includes(c);

    function syllables(w) {
      const out = []; let i = 0; const n = w.length;
      while (i < n) {
        let j = i; while (j < n && !isV(w[j])) j++;
        const onset = w.slice(i, j);
        if (j >= n) { if (out.length) out[out.length - 1][2] += onset; else out.push(['', '', onset]); break; }
        let k = j; while (k < n && isV(w[k])) k++;
        const vow = w.slice(j, k);
        let m = k; while (m < n && !isV(w[m])) m++;
        const cons = w.slice(k, m);
        let coda, nxt;
        if (m >= n) { coda = cons; nxt = m; } else { coda = cons.slice(0, -1); nxt = k + cons.length - 1; }
        out.push([onset, vow, coda]);
        i = nxt;
      }
      return out;
    }
    function splitVowels(vow, rows) {
      const keys = byLenDesc(Object.keys(rows).filter((k) => [...k].every((c) => VOW.includes(c))));
      const parts = []; let i = 0;
      while (i < vow.length) {
        const k = keys.find((k) => vow.startsWith(k, i));
        if (k) { parts.push(k); i += k.length; } else { parts.push(vow[i]); i += 1; }
      }
      return parts;
    }
    function word(wordIn, mode) {
      const t = T.fi[mode]; const rows = t.rows; const zero = t.zero;
      let w = wordIn.toLowerCase().replace(/š/g, 's').replace(/ž/g, 'z').replace(/w/g, 'v');
      w = w.replace(/[áàâ]/g, 'a').replace(/[éèê]/g, 'e').replace(/[íìî]/g, 'i').replace(/[óòô]/g, 'o').replace(/[úùû]/g, 'u');
      w = w.replace(/ck/g, 'k').replace(/th/g, 't').replace(/dt/g, 't').replace(/ph/g, 'f');
      const sy = syllables(w);
      const res = [], notes = [], trace = [];
      sy.forEach(([on, vow, codaIn], idx) => {
        let coda = codaIn;
        const nxtOn = idx + 1 < sy.length ? sy[idx + 1][0] : '';
        if (coda && nxtOn && coda.slice(-1) === nxtOn[0] && coda.slice(-1) !== 'n') coda = coda.slice(0, -1);
        const ons = (on === 'ts' || on === 'tz') && idx === 0 ? ['ts'] : [...on];
        for (const c of ons.slice(0, -1)) res.push(pick(zero[COL[c] || c], notes, `${c}（單獨）`));
        const c0 = ons.length ? ons[ons.length - 1] : '';
        const col = c0 ? (COL[c0] || c0) : '';
        const parts = splitVowels(vow, rows);
        const last = parts[parts.length - 1];
        let rest = coda;
        if (coda.startsWith('ng') && has(rows, last + 'ng')) { parts[parts.length - 1] = last + 'ng'; rest = coda.slice(2); }
        else if (coda.startsWith('n') && has(rows, last + 'n')) { parts[parts.length - 1] = last + 'n'; rest = coda.slice(1); }
        else if (coda.startsWith('n') && last.length === 2 && last[0] === last[1] && has(rows, last[0] + 'n')) { parts[parts.length - 1] = last[0] + 'n'; rest = coda.slice(1); }
        parts.forEach((v, pi) => {
          const cc = pi === 0 ? col : '';
          if (pi > 0 && v[0] === 'a' && parts[pi - 1].slice(-1) === 'i') { res.push('亞'); trace.push(`${v}→亞（ia 規則）`); return; }
          const ch = pick((rows[v] || {})[cc], notes, `${pi === 0 ? c0 : ''}${v}`);
          res.push(ch); trace.push(`${pi === 0 ? c0 : ''}${v}→${ch}`);
        });
        [...rest].forEach((cIn, k) => {
          let c = cIn;
          const lastC = k + 1 === rest.length;
          if (c === 'm' && lastC && (nxtOn[0] === 'b' || nxtOn[0] === 'p')) c = 'n';
          if (c === 'n' && lastC && (nxtOn[0] === 'b' || nxtOn[0] === 'p') && parts.length) {
            const v = parts[parts.length - 1] + 'n';
            if (has(rows, v)) {
              res[res.length - 1] = pick(rows[v][parts.length === 1 ? col : ''], notes, v);
              trace[trace.length - 1] = `${c0}${v}→${res[res.length - 1]}（m 在 p/b 前作 n）`;
              return;
            }
          }
          const ch = pick(zero[COL[c] || c], notes, `${c}（音節尾）`);
          res.push(ch); trace.push(`${c}→${ch}`);
        });
      });
      let s = res.join('');
      if (mode === 'place') {
        for (const [a, b] of [['東', '棟'], ['南', '楠'], ['西', '錫']]) if (s.startsWith(a)) { s = b + s.slice(1); notes.push(`詞首${a}改${b}`); }
        if (s.endsWith('海')) { s = s.slice(0, -1) + '亥'; notes.push('詞尾海改亥'); }
      }
      if (s.startsWith('夫')) s = '弗' + s.slice(1);
      if (s) s = s[0] + s.slice(1).replace(/弗/g, '夫');
      return { zh: s, syl: sy.map((x) => x.join('')).join('-'), trace, notes };
    }
    function translit(text, mode) {
      const parts = text.trim().split(/\s+|-/).filter((p) => p);
      const info = parts.map((p) => ({ src: p, ...word(p, mode) }));
      return { zh: info.map((x) => x.zh).join(mode === 'person' ? '·' : ''), info };
    }
    function run(text, mode) {
      const r = translit(text, mode);
      const extra = [];
      if (mode === 'place') {
        const low = text.toLowerCase();
        for (const [g, zh] of GENERIC) {
          if (low.endsWith(g) && low.length > g.length + 1) {
            let stem = text.slice(0, -g.length);
            // 專名在複合地名裡是屬格，意譯通名時還原主格（Kärstilänjärvi→凱爾斯蒂萊湖）
            if (/n$/i.test(stem) && stem.length > 2 && VOW.includes(stem[stem.length - 2].toLowerCase())) stem = stem.slice(0, -1);
            extra.push(['通名意譯', translit(stem, mode).zh + zh]); break;
          }
        }
      }
      return { zh: r.zh, extra, info: r.info };
    }
    return { run };
  })();

  // ================= 俄語 =================
  const RU = (() => {
    const VOW = 'аяэеыиоёуюь';
    const IOT = 'яеёю';
    const SUFFIX = [['бург', '堡'], ['град', '格勒'], ['город', '哥羅德'], ['цов', '佐夫']];
    const pick = pickFactory(false);
    const isV = (x) => VOW.includes(x);   // 照 Python：空字串也算 True，呼叫處已先排除

    function prep(wIn) {
      let w = wIn.toLowerCase().replace(/ъ/g, '|');
      w = w.replace(/(ого|его)$/, (m) => m.replace('г', 'в'));
      for (const [a, b] of [['стн', 'сн'], ['стл', 'сл'], ['здн', 'зн'], ['рдц', 'рц'], ['лнц', 'нц'], ['зш', 'ш'], ['сш', 'ш'], ['жч', 'щ'], ['зч', 'щ'], ['сч', 'щ'],
        ['дс', 'ц'], ['тс', 'ц'], ['цс', 'ц'], ['дц', 'ц'], ['тц', 'ц'], ['тч', 'ч'], ['дч', 'ч']]) w = w.split(a).join(b);
      w = w.split('гк').join('хк').split('чт').join('шт');
      w = w.replace(/(?<=[бвгджзклмнпрстфхцчшщ])ьи/g, 'и');
      w = w.replace(/([бвгджзклмпрстфхцчшщ])\1/g, (m, c) => (c === 'н' ? m : c));
      return w;
    }
    function units(w) {
      const out = []; let i = 0;
      while (i < w.length) { if (w.startsWith('дж', i)) { out.push('дж'); i += 2; } else { out.push(w[i]); i += 1; } }
      return out;
    }
    function core(wordIn, mode) {
      const t = T.ru[mode]; const rows = t.rows; const zero = t.zero;
      const u = units(prep(wordIn));
      const res = [], notes = [], trace = [];
      let i = 0; const n = u.length;
      while (i < n) {
        let c = u[i];
        if (c === '|') { i++; continue; }
        if (c === 'й' && i + 1 < n && 'аоуэ'.includes(u[i + 1])) { u[i + 1] = { а: 'я', о: 'ё', у: 'ю', э: 'е' }[u[i + 1]]; i++; continue; }
        let onset = '';
        if (!isV(c) && c !== 'й') {
          const nxt = i + 1 < n ? u[i + 1] : '';
          if (nxt && isV(nxt) && !(nxt === 'ь' && (i + 2 >= n || (!isV(u[i + 2]) && u[i + 2] !== '')))) { onset = c; i++; }
          else if (nxt === 'ь') { onset = c; i++; }
          else {
            if (c === 'м' && (nxt === 'б' || nxt === 'п')) c = 'н';
            if ((c === 'р' || c === 'л') && !res.length && nxt && !isV(nxt)) { res.push('勒'); trace.push(`${c}→勒（詞首後接輔音）`); i++; continue; }
            const ch = pick(zero[c], notes, `${c}（單獨）`);
            res.push(ch); trace.push(`${c}→${ch}`); i++; continue;
          }
        } else if (c === 'й') { res.push('伊'); trace.push('й→伊'); i++; continue; }
        const prev = i > 0 ? u[i - 1] : '';
        let best = null;
        for (const L of [3, 2, 1]) {
          const seg = u.slice(i, i + L);
          if (seg.length !== L) continue;
          const g = seg.join('');
          if (has(rows, g) && seg.every((x) => isV(x) || x === 'й')) { best = g; break; }
          if (L === 2 && (g === 'ей' || g === 'ой')) { best = g; break; }
        }
        if (best === null) best = u[i];
        const bestUnits = units(best).length; // best 只含單字元單位
        const j = i + bestUnits;
        let nasal = '';
        if (j < n && u[j] === 'н' && !'йь'.includes(best.slice(-1))) {
          const after = j + 1 < n ? u[j + 1] : '';
          if (after === 'ь' && (j + 2 >= n || !isV(u[j + 2])) && has(rows, best + 'нь')) nasal = 'нь';
          else if ((!after || !isV(after) || after === 'н') && has(rows, best + 'н')) nasal = 'н';
        }
        if (j < n && u[j] === 'м' && j + 1 < n && 'бп'.includes(u[j + 1]) && has(rows, best + 'н')) nasal = 'м';
        let key = best + (nasal ? 'н' : '');
        if (nasal === 'нь') key = best + 'нь';
        let extra = '';
        if (best === 'ей' || best === 'ой') { key = best[0]; extra = '伊'; }
        let col = onset;
        if (onset === '' && IOT.includes(best[0]) && prev && !isV(prev) && prev !== '|') col = '';
        const row = rows[key];
        let ch = pick(row ? row[col] : null, notes, `${onset}${key}`);
        if (onset === '' && key[0] === 'е' && !res.length) ch = '葉';
        if (onset === 'ь') ch = pick(rows['ь'][''], notes, 'ь');
        res.push(ch + extra); trace.push(`${onset}${key}→${ch}${extra}` + (nasal === 'м' ? '（м 在 б／п 前作 н）' : ''));
        i = j + (nasal === 'н' || nasal === 'м' ? 1 : nasal === 'нь' ? 2 : 0);
      }
      let s = res.join('');
      if (s.startsWith('夫')) s = '弗' + s.slice(1);
      s = s.slice(0, 1) + s.slice(1).replace(/弗/g, '夫').replace(/葉/g, '耶');
      if (mode === 'place' && s) {
        for (const [a, b] of [['東', '棟'], ['南', '楠'], ['西', '錫']]) if (s.startsWith(a)) { s = b + s.slice(1); notes.push(`詞首${a}改${b}`); }
        for (const [a, b] of [['江', '姜'], ['海', '亥']]) if (s.endsWith(a)) { s = s.slice(0, -1) + b; notes.push(`詞尾${a}改${b}`); }
      }
      return { zh: s, trace, notes };
    }
    function word(w, mode) {
      const low = w.toLowerCase();
      const stems = T.ru.stems;
      if (has(stems, low)) return { zh: stems[low], trace: [`${w}→雙拼詞幹表`], notes: [] };
      const sorted = Object.entries(stems).sort((a, b) => b[0].length - a[0].length);
      for (const [st, zh] of sorted) {
        if (low === st + 'ь') return { zh, trace: [`${w}→雙拼詞幹表`], notes: [] };
        if (low.startsWith(st) && low.length > st.length && VOW.includes(low[st.length]) && low[st.length] !== 'ь') {
          const r = core('н' + low.slice(st.length), mode);
          return { zh: zh + r.zh, trace: [`${st}→${zh}（雙拼詞幹）`].concat(r.trace), notes: r.notes };
        }
      }
      if (mode === 'place') {
        for (const [suf, zh] of SUFFIX) {
          if (low.endsWith(suf) && low.length > suf.length) {
            const r = core(low.slice(0, -suf.length), mode);
            return { zh: r.zh + zh, trace: r.trace.concat([`-${suf}→${zh}`]), notes: r.notes };
          }
        }
      }
      return core(w, mode);
    }
    function run(text, mode) {
      if (/[a-zA-Z]/.test(text)) return { zh: '', extra: [], info: [], error: '請輸入西里爾字母原文' };
      const parts = text.trim().split(/[\s-]+/).filter((p) => p);
      const info = parts.map((p) => ({ src: p, ...word(p, mode) }));
      return { zh: info.map((x) => x.zh).join(mode === 'person' ? '·' : ''), extra: [], info };
    }
    return { run };
  })();

  // ================= 印尼語 =================
  const ID = (() => {
    const VOW = 'aeéiou';
    const GENERIC = { pulau: '島', 'p.': '島', 'pulau-pulau': '群島', kepulauan: '群島', 'kep.': '群島', sungai: '河', 's.': '河', danau: '湖', telaga: '湖', gunung: '山', 'g.': '山', 'gunung api': '火山', bukit: '山', teluk: '灣', 'tk.': '灣', selat: '海峽', tanjung: '角', 'tg.': '角', ujung: '角', kota: '市', kabupaten: '縣', kecamatan: '鄉', desa: '村', kampung: '村', provinsi: '省', semenanjung: '半島', jazirah: '半島', karang: '礁', 'air terjun': '瀑布', kuala: '河口', muara: '河口', tasik: '湖', rawa: '沼澤', waduk: '水庫', pegunungan: '山脈', gua: '洞', candi: '寺', pura: '寺', jalan: '路', kali: '河' };
    const MODIFIER = { timur: '東', barat: '西', utara: '北', selatan: '南', tengah: '中', besar: '大', raya: '大', kecil: '小', tenggara: '東南', 'timur laut': '東北', 'barat daya': '西南', 'barat laut': '西北' };
    const COLMAP = { v: 'f', x: 's', q: 'k', gh: 'g', kh: 'h', th: 't' };
    const pick = pickFactory(false);
    const isV = (x) => VOW.includes(x);

    function prep(wIn) {
      let w = wIn.toLowerCase();
      for (const [a, b] of [['tj', 'c'], ['dj', 'j'], ['sj', 'sy'], ['ch', 'kh'], ['oe', 'u']]) w = w.split(a).join(b);
      w = w.replace(/-/g, '');
      w = w.split('ngg').join('ng\u0000g');
      w = w.replace(/([bcdfghjklmnpqrstvwxyz])\1/g, '$1');
      w = w.replace(/\u0000/g, '');
      w = w.replace(/([aiou])\1/g, '$1');
      return w;
    }
    function units(w) {
      const out = []; let i = 0;
      while (i < w.length) {
        const d = ['ng', 'ny', 'sy', 'kh', 'gh', 'th', 'hw', 'kw'].find((d) => w.startsWith(d, i));
        if (d) { out.push(d); i += 2; } else { out.push(w[i]); i += 1; }
      }
      return out;
    }
    function word(wIn, mode) {
      const t = T.id[mode]; const rows = t.rows; const zero = t.zero;
      const u = units(prep(wIn));
      const res = [], trace = [], notes = [];
      const vgroups = byLenDesc(Object.keys(rows).filter((k) => [...k].every((c) => (VOW + 'äöǒ').includes(c))));
      let i = 0; const n = u.length;
      while (i < n) {
        let c = u[i];
        let onset = '';
        if (!isV(c)) {
          const nxt = i + 1 < n ? u[i + 1] : '';
          if (nxt && isV(nxt) && !(c === 'ng' && i > 0)) { onset = c; i++; }
          else {
            const last = i + 1 >= n;
            if (mode === 'place' && 'ptkh'.includes(c) && c.length === 1 && (last || !isV(nxt))) { trace.push(`${c}→（閉音節尾不譯）`); i++; continue; }
            if (mode === 'person' && c === 'h' && last) { trace.push('h→（詞尾不譯）'); i++; continue; }
            if (c === 'm' && (nxt === 'b' || nxt === 'p')) c = 'n';
            const ch = pick(zero[COLMAP[c] || c], notes, `${c}（單獨）`);
            res.push(ch); trace.push(`${c}→${ch}`); i++; continue;
          }
        }
        const s3 = u.slice(i, i + 3).join('');
        const g = vgroups.find((k) => s3.startsWith(k) && k.length <= 2) || u[i];
        const j = i + g.length;
        let coda = '';
        let g2 = g;
        if (j < n && (u[j] === 'ng' || ((u[j] === 'm' || u[j] === 'n') && (j + 1 >= n || !isV(u[j + 1]))))) {
          let cand = g !== 'é' ? g.replace('é', 'e') + u[j] : null;
          if (u[j] === 'ng' && g === 'u') cand = 'ung';
          if (cand && has(rows, cand)) {
            coda = u[j];
            if (u[j] === 'm' && j + 1 < n && (u[j + 1] === 'b' || u[j + 1] === 'p')) cand = cand.slice(0, -1) + 'n';
            g2 = cand;
          }
        }
        const key = has(rows, g2) ? g2 : (g2 === 'é' ? 'ei' : g2);
        const col = onset ? (COLMAP[onset] || onset) : '';
        const prevv = res.length && trace.length && trace[trace.length - 1].split('→')[0].slice(-1) === 'i';
        let ch;
        if (onset === '' && g === 'a' && prevv) { ch = '亞'; trace.push('ia→亞'); }
        else if (onset === '' && mode === 'person' && g === 'e' && prevv) { ch = '耶'; trace.push('ie→耶'); }
        else { ch = pick((rows[key] || {})[col], notes, `${onset}${key}`); trace.push(`${onset}${key}→${ch}`); }
        res.push(ch);
        i = j + (coda ? 1 : 0);
      }
      let s = res.join('');
      if (s.startsWith('夫')) s = '弗' + s.slice(1);
      s = s.slice(0, 1) + s.slice(1).replace(/弗/g, '夫');
      if (mode === 'place' && s) {
        for (const [a, b] of [['東', '棟'], ['南', '楠'], ['西', '錫']]) if (s.startsWith(a)) { s = b + s.slice(1); notes.push(`詞首${a}改${b}`); }
        if (s.endsWith('海')) { s = s.slice(0, -1) + '亥'; notes.push('詞尾海改亥'); }
      }
      return { zh: s, trace, notes };
    }
    function translit(text, mode) {
      const words = text.trim().split(/\s+/).filter((w) => w);
      const low = words.map((w) => w.toLowerCase());
      const pre = []; let suf = ''; const core = []; const info = [];
      let k = 0;
      while (k < words.length) {
        const two = low.slice(k, k + 2).join(' ');
        if (mode === 'place' && has(GENERIC, two) && words.length > 2) { suf = GENERIC[two]; k += 2; continue; }
        if (mode === 'place' && has(MODIFIER, two)) { pre.push(MODIFIER[two]); k += 2; continue; }
        if (mode === 'place' && has(GENERIC, low[k]) && k === 0 && words.length > 1) { suf = GENERIC[low[k]]; k++; continue; }
        if (mode === 'place' && has(MODIFIER, low[k]) && core.length) { pre.push(MODIFIER[low[k]]); k++; continue; }
        const r = word(words[k], mode);
        core.push(r.zh); info.push({ src: words[k], ...r }); k++;
      }
      return { zh: pre.join('') + core.join(mode === 'person' ? '·' : '') + suf, info };
    }
    function run(text, mode) {
      const r = translit(text, mode);
      const extra = [];
      if (/e(?!i)/.test(text.toLowerCase().split('ee').join(''))) {
        const altSrc = text.split(/\s+/).filter((x) => x).map((x) => (has(GENERIC, x.toLowerCase()) || has(MODIFIER, x.toLowerCase())) ? x
          : x.replace(/[eE](?=[^aeiouéAEIOU-][aeiouAEIOU]|$|-)/g, (m) => (m === 'e' ? 'é' : 'É'))).join(' ');
        const alt = translit(altSrc, mode).zh;
        if (alt !== r.zh) extra.push(['e 若讀 é', alt]);
      }
      return { zh: r.zh, extra, info: r.info };
    }
    return { run };
  })();

  const API = { fi: FI.run, ru: RU.run, id: ID.run };
  if (typeof module !== 'undefined') module.exports = API; else root.Translit = API;
})(this);
