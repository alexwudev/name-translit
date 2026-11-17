"""印尼語音譯工具：輸入印尼文地名或人名，依中國標準吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 id_translit_table.json：
  地名表＝MZ/T 127-2019《外语地名汉字译写导则 印度尼西亚语》（中維外語譯音表/印尼語頁只給連結，表從民政部 PDF 抽出）；
  人名表＝中維「外語譯音表/印尼語」（新華社《世界人名翻译大辞典》）。
  兩表都是中國大陸標準，譯名一律以繁體字輸出；雅加達、泗水這類常識性或華人慣用譯名以通行為準，不必跑工具
  （導則 4.3 本身也規定惯用译名、华人常用地名沿用）。伊斯蘭教人名照阿拉伯人名慣譯，本工具不處理。

用法：
  python -X utf8 id_translit.py Panunggalan "Pulau Masalaka Besar" "Sungai Tembesi"   （預設地名表）
  python -X utf8 id_translit.py -p "Sukarno" "Abdul Haris Nasution"                    （-p 人名表）
  python -X utf8 id_translit.py -v Nangasuruk                                          （-v 列出音節與每字來源）
  python -X utf8 id_translit.py -f 名單.txt

處理規則（導則第 5 章與人名表說明）：
  - 舊拼法先換新拼法：tj→c、dj→j、nj→ny、sj→sy、ch→kh、oe→u。
  - e 一律按「厄」行（ǝ）；要按「埃」行（é，如 Bea 贝阿）請在原文寫 é。印尼文拼寫不區分兩者，
    所以原文有開音節的 e 時，另列「e 若讀 é」版本（Tembesi→滕伯西／滕贝西），要查實際讀音再選。
  - 導則 5.1.7 說閉音節尾 p、t、k、h「一般不譯」，但示例 Kapuk 又譯「卡普克」；本工具照 5.1.7 不譯，重名多時自行補上。
  - ng 列的字只用於詞首；詞中 ng 歸前一音節，後面的元音單獨譯（Dodinga→多丁阿）；ngg：ng 歸前、g 歸後（Panggul→庞古尔）。
  - 地名：閉音節尾的 p、t、k、h 一般不譯（Nangasuruk→楠阿苏鲁）；人名：只有詞尾 h 不譯。
  - 相同元音、相同輔音連寫按一個譯；表上沒有的元音組分開譯；ia 照 i 行加「亚」，人名 ie 照 i 行加「耶」。
  - m 在 b、p 前按 n 譯；連字號刪去、前後連譯。
  - 地名通名意譯、修飾詞意譯（附錄 A、B 的常用者）：Pulau X Besar→大X岛、Sungai X→X河、Teluk／Tk. X→X湾。
  - 地名：东／南／西在詞首改栋／楠／锡，海在詞尾改亥；弗用於詞首，夫用於詞中與詞尾。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import opencc  # pip install --user opencc-python-reimplemented
# 譯名一律以繁體字輸出（2026-11-17 使用者指示：簡體看起來怪）；s2t 會把音譯用的里、于、占、托、采轉成裏、於、佔、託、採，要轉回
_s2t = opencc.OpenCC("s2t").convert
S = lambda x: "".join(_s2t(c) for c in x).translate(str.maketrans("裏於佔託採佈羣誇", "里于占托采布群夸"))  # 逐字轉繁（整串轉會出「拉剋」）；音譯用字被誤轉的轉回
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "id_translit_table.json"), encoding="utf-8"))

VOW = "aeéiou"
# 附錄 B 常用通名（意譯）與附錄 A 修飾詞
GENERIC = {"pulau": "岛", "p.": "岛", "pulau-pulau": "群岛", "kepulauan": "群岛", "kep.": "群岛", "sungai": "河", "s.": "河",
           "danau": "湖", "telaga": "湖", "gunung": "山", "g.": "山", "gunung api": "火山", "bukit": "山", "teluk": "湾",
           "tk.": "湾", "selat": "海峡", "tanjung": "角", "tg.": "角", "ujung": "角", "kota": "市", "kabupaten": "县",
           "kecamatan": "乡", "desa": "村", "kampung": "村", "provinsi": "省", "semenanjung": "半岛", "jazirah": "半岛",
           "karang": "礁", "air terjun": "瀑布", "kuala": "河口", "muara": "河口", "tasik": "湖", "rawa": "沼泽",
           "waduk": "水库", "pegunungan": "山脉", "gua": "洞", "candi": "寺", "pura": "寺", "jalan": "路", "kali": "河"}
MODIFIER = {"timur": "东", "barat": "西", "utara": "北", "selatan": "南", "tengah": "中", "besar": "大", "raya": "大",
            "kecil": "小", "tenggara": "东南", "timur laut": "东北", "barat daya": "西南", "barat laut": "西北"}


def prep(w):
    w = w.lower()
    for a, b in (("tj", "c"), ("dj", "j"), ("sj", "sy"), ("ch", "kh"), ("oe", "u")):  # 新拼法的 nj 是 n＋j（Menjalin→门贾林）
        w = w.replace(a, b)
    w = w.replace("-", "")
    w = w.replace("ngg", "ng\x00g")  # ngg：ng 歸前、g 歸後，不可被「相同輔音」規則吃掉
    w = re.sub(r"([bcdfghjklmnpqrstvwxyz])\1", r"\1", w)  # 相同輔音按一個
    w = w.replace("\x00", "")
    w = re.sub(r"([aiou])\1", r"\1", w)  # 相同元音按一個（ee 另有 i 列，先換）
    return w


def units(w):
    out, i = [], 0
    while i < len(w):
        for d in ("ng", "ny", "sy", "kh", "gh", "th", "hw", "kw"):
            if w.startswith(d, i):
                out.append(d); i += 2; break
        else:
            out.append(w[i]); i += 1
    return out


COLMAP = {"v": "f", "x": "s", "q": "k", "gh": "g", "kh": "h", "th": "t", "é": None}


def pick(cell, notes, label):
    if not cell or not cell["main"]:
        notes.append(f"{label}：表上此格為空")
        return "?"
    if len(cell["main"]) > 1 or cell["alt"]:
        notes.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['main'][1:] + cell['alt'])}")
    return cell["main"][0]


def translit_word(word, mode):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    u = units(prep(word))
    res, trace, notes = [], [], []
    isv = lambda x: x in VOW
    vgroups = sorted((k for k in rows if all(c in VOW + "äöǒ" for c in k)), key=len, reverse=True)
    i, n = 0, len(u)
    while i < n:
        c = u[i]
        onset = ""
        if not isv(c):
            nxt = u[i + 1] if i + 1 < n else ""
            # 詞中 ng 不當聲母（歸前一音節）
            if nxt and isv(nxt) and not (c == "ng" and i > 0):
                onset = c; i += 1
            else:
                last = i + 1 >= n
                if mode == "place" and c in ("p", "t", "k", "h") and (last or not isv(nxt)):
                    trace.append(f"{c}→（閉音節尾不譯）"); i += 1; continue
                if mode == "person" and c == "h" and last:
                    trace.append("h→（詞尾不譯）"); i += 1; continue
                if c == "m" and nxt in ("b", "p"):
                    c = "n"
                ch = pick(zero.get(COLMAP.get(c, c) or c), notes, f"{c}（單獨）")
                res.append(ch); trace.append(f"{c}→{ch}"); i += 1; continue
        # 元音組
        s = "".join(u[i:i + 3])
        g = next((k for k in vgroups if s.startswith(k) and len(k) <= 2), u[i])
        if g == "e" and mode == "place":
            g = "e"
        j = i + len(g)
        # 鼻音尾 m／n／ng（後面不是元音才併）
        coda = ""
        # 詞中 ng 一律歸前一音節（後面元音單獨譯）；m、n 後面不是元音才併
        if j < n and (u[j] == "ng" or (u[j] in ("m", "n") and (j + 1 >= n or not isv(u[j + 1])))):
            cand = g.replace("é", "e") + u[j] if g != "é" else None
            if u[j] == "ng" and g in ("u",):
                cand = "ung"
            if cand and cand in rows:
                coda = u[j]
                if u[j] == "m" and j + 1 < n and u[j + 1] in ("b", "p"):
                    cand = cand[:-1] + "n"
                g2 = cand
            else:
                g2 = g
        else:
            g2 = g
        key = g2 if g2 in rows else ("ei" if g2 == "é" else g2)
        col = COLMAP.get(onset, onset) if onset else ""
        prevv = res and trace and trace[-1].split("→")[0][-1:] == "i"
        if onset == "" and g == "a" and prevv:
            ch = "亚"; trace.append("ia→亚")
        elif onset == "" and mode == "person" and g == "e" and prevv:
            ch = "耶"; trace.append("ie→耶")
        else:
            ch = pick(rows.get(key, {}).get(col), notes, f"{onset}{key}")
            trace.append(f"{onset}{key}→{ch}")
        res.append(ch)
        i = j + (1 if coda else 0)
    s = "".join(res)
    if s.startswith("夫"):
        s = "弗" + s[1:]
    s = s[:1] + s[1:].replace("弗", "夫")
    if mode == "place" and s:
        for a, b in (("东", "栋"), ("東", "栋"), ("南", "楠"), ("西", "锡")):
            if s.startswith(a):
                s = b + s[1:]; notes.append(f"詞首{a}改{b}")
        if s.endswith("海"):
            s = s[:-1] + "亥"; notes.append("詞尾海改亥")
    return s, trace, notes


def translit(text, mode):
    words = text.strip().split()
    low = [w.lower() for w in words]
    pre, suf, core, info = [], "", [], []
    k = 0
    while k < len(words):
        two = " ".join(low[k:k + 2])
        if mode == "place" and two in GENERIC and len(words) > 2:
            suf = GENERIC[two]; k += 2; continue
        if mode == "place" and two in MODIFIER:
            pre.append(MODIFIER[two]); k += 2; continue
        if mode == "place" and low[k] in GENERIC and k == 0 and len(words) > 1:
            suf = GENERIC[low[k]]; k += 1; continue
        if mode == "place" and low[k] in MODIFIER and core:
            pre.append(MODIFIER[low[k]]); k += 1; continue
        s, tr, nt = translit_word(words[k], mode)
        core.append(s); info.append((words[k], tr, nt)); k += 1
    sep = "·" if mode == "person" else ""
    return "".join(pre) + sep.join(core) + suf, info


def main(argv):
    mode, verbose, words = "place", False, []
    it = iter(argv)
    for a in it:
        if a == "-p":
            mode = "person"
        elif a == "-v":
            verbose = True
        elif a == "-f":
            words += [l.strip() for l in open(next(it), encoding="utf-8") if l.strip()]
        else:
            words.append(a)
    if not words:
        sys.exit(__doc__)
    print(f"# 依印尼語{'人名' if mode == 'person' else '地名'}表譯寫（中國大陸標準，繁體輸出；常識性與華人慣用譯名以通行為準）")
    for w in words:
        zh, info = translit(w, mode)
        line = f"{w}\t{S(zh)}"
        if re.search(r"e(?!i)", w.lower().replace("ee", "")):
            # 只把開音節的 e 換成 é（Tembesi→滕贝西：Tem 是閉音節照 ǝ）
            alt_src = " ".join(x if x.lower() in GENERIC or x.lower() in MODIFIER else
                               re.sub(r"[eE](?=[^aeiouéAEIOU-][aeiouAEIOU]|$|-)", lambda m: "é" if m.group(0) == "e" else "É", x)
                               for x in w.split())  # 通名、修飾詞不動
            alt, _ = translit(alt_src, mode)
            if alt != zh:
                line += f"\te 若讀 é：{S(alt)}"
        print(line)
        if verbose:
            for part, tr, nt in info:
                print(f"    {part}：{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
