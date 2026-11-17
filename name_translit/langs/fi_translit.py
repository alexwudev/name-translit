"""芬蘭語音譯工具：輸入芬蘭文地名或人名，依中維「外語譯音表/芬蘭語」吐出漢字譯名。

2026-11-17 為芬蘭裝甲師條目而寫。譯音表存在同目錄 fi_translit_table.json（取自中維 oldid=90440181）：
  地名表＝GB/T 17693.20-2025《外語地名漢字譯寫導則 芬蘭語》；人名表＝新華社《世界人名翻譯大辭典》。
  兩表都是中國大陸標準，頁面明說不適用於台灣譯名：台灣已有通行譯名時以通行譯名為準，本工具只給參考。
  譯名一律以繁體字輸出（2026-11-17 使用者指示，原先的簡體輸出看起來怪）。

用法：
  python -X utf8 fi_translit.py Kuuterselkä Vuosalmi "Ala-Sommee"     （預設地名表）
  python -X utf8 fi_translit.py -p "Ruben Lagus" "Erkki Käkelä"        （-p 用人名表）
  python -X utf8 fi_translit.py -v Mantsinsaari                         （-v 列出音節切分與每個字的來源）
  python -X utf8 fi_translit.py -f 名單.txt                             （每行一個原文）

處理規則（表上的說明＋芬蘭語拼寫慣例）：
  - 音節切分：兩個元音之間的輔音群，最後一個歸下一音節，其餘留在前一音節尾（Kavant-saa-ri、Man-tsin 拆成 t+s）。
  - 雙寫輔音（kk、pp、ll…）只譯一次（Lappeenranta→拉彭蘭塔、Kokkari→科卡里）；
    nn 例外，前一個 n 併入元音（Kivennapa→基文納帕、Hämeenlinna→海門林納）。ck、th、dt 照表當 k、t。
  - 音節尾的 n／ng 併入元音列（an、en、in、on、un、än、aan、een、ang、ing…）；表上沒有的組合，元音與「恩」分開譯。
  - 只合譯表上列出的元音組（地名：ai ei äi äe au ou iu uo ie io…；人名：ae ie io iu ao au ou），其餘兩個元音分開譯。
  - ia：i 照該列譯，a 譯「亞」；m 在 b、p 前照 n 譯。
  - 地名：東／南／西在詞首改棟／楠／錫，海在詞尾改亥；弗用於詞首、夫用於詞中與詞尾；š→s、ž→z。
  - 同一格有兩個字（奧/歐、海/黑、萊/雷）時取第一個，-v 會列出另一個。
  - 通名：järvi、joki、saari、lahti 另列「通名意譯」版本（萊蒂莫湖、圖萊馬河），由使用者自選；
    niemi、salmi、linna 等習慣音譯（羅瓦涅米、武薩爾米），不另列。
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
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fi_translit_table.json"), encoding="utf-8"))

VOW = "aeiouyäöåü"
COL = {"b": "b", "c": "c", "d": "d", "f": "f", "g": "g", "h": "h", "j": "j", "k": "k", "q": "k", "l": "l", "m": "m",
       "n": "n", "p": "p", "r": "r", "s": "s", "t": "t", "v": "v", "w": "v", "x": "x", "z": "ts", "ts": "ts", "tz": "ts"}
GENERIC = [("järvi", "湖"), ("joki", "河"), ("saari", "島"), ("lahti", "灣")]


def syllables(w):
    """切成 (onset, nucleus, coda) 串列。"""
    out, i, n = [], 0, len(w)
    while i < n:
        j = i
        while j < n and w[j] not in VOW:
            j += 1
        onset = w[i:j]
        if j >= n:  # 詞尾只剩輔音
            if out:
                out[-1][2] += onset
            else:
                out.append(["", "", onset])
            break
        k = j
        while k < n and w[k] in VOW:
            k += 1
        vow = w[j:k]
        m = k
        while m < n and w[m] not in VOW:
            m += 1
        cons = w[k:m]
        if m >= n:
            coda, nxt = cons, m
        else:
            coda, nxt = cons[:-1], k + len(cons) - 1
        out.append([onset, vow, coda])
        i = nxt
    return out


def split_vowels(vow, rows):
    """把元音串切成表上有的組；長的先比。"""
    keys = sorted((k for k in rows if all(c in VOW for c in k)), key=len, reverse=True)
    parts, i = [], 0
    while i < len(vow):
        for k in keys:
            if vow.startswith(k, i):
                parts.append(k); i += len(k); break
        else:
            parts.append(vow[i]); i += 1
    return parts


def pick(cell, note, label):
    if not cell or not cell["main"] or cell["main"][0] in ("—", ""):
        note.append(f"{label}：表上此格為空或「—」")
        return "?"
    if len(cell["main"]) > 1 or cell["alt"]:
        note.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['main'][1:] + cell['alt'])}")
    return cell["main"][0]


def translit_word(word, mode):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    w = word.lower().replace("š", "s").replace("ž", "z").replace("w", "v")
    w = w.translate(str.maketrans("áàâéèêíìîóòôúùû", "aaaeeeiiiooouuu"))  # 外來名字的重音符號（Aladár）
    w = w.replace("ck", "k").replace("th", "t").replace("dt", "t").replace("ph", "f")  # 表上同列的拼法
    sy = syllables(w)
    res, notes, trace = [], [], []
    for idx, (on, vow, coda) in enumerate(sy):
        # 雙寫輔音：前一音節尾與本音節首相同就丟掉前一個
        nxt_on = sy[idx + 1][0] if idx + 1 < len(sy) else ""
        # nn 例外：前一個 n 併入元音（Kivennapa→基文納帕、Hämeenlinna→海門林納）
        if coda and nxt_on and coda[-1] == nxt_on[0] and coda[-1] != "n":
            coda = coda[:-1]
        # 詞首 ts／tz 才當一個輔音
        if on in ("ts", "tz") and idx == 0:
            ons = ["ts"]
        else:
            ons = list(on)
        # 多個起首輔音（外來字）：前面的單獨譯
        for c in ons[:-1]:
            res.append(pick(zero.get(COL.get(c, c)), notes, f"{c}（單獨）"))
        c0 = ons[-1] if ons else ""
        col = COL.get(c0, c0) if c0 else ""
        # 鼻音尾併入元音組
        parts = split_vowels(vow, rows)
        last = parts[-1]
        rest_coda = coda
        if coda.startswith("ng") and last + "ng" in rows:
            parts[-1] = last + "ng"; rest_coda = coda[2:]
        elif coda.startswith("n") and last + "n" in rows:
            parts[-1] = last + "n"; rest_coda = coda[1:]
        elif coda.startswith("n") and len(last) == 2 and last[0] == last[1] and last[0] + "n" in rows:
            parts[-1] = last[0] + "n"; rest_coda = coda[1:]  # oon→on 列
        for pi, v in enumerate(parts):
            cc = col if pi == 0 else ""
            if pi > 0 and v[0] == "a" and parts[pi - 1][-1:] == "i":
                res.append("亞"); trace.append(f"{v}→亞（ia 規則）"); continue
            ch = pick(rows.get(v, {}).get(cc), notes, f"{c0 if pi == 0 else ''}{v}")
            res.append(ch); trace.append(f"{(c0 if pi == 0 else '')}{v}→{ch}")
        for k, c in enumerate(rest_coda):
            if c == "m" and k + 1 == len(rest_coda) and nxt_on[:1] in ("b", "p"):
                c = "n"
            if c == "n" and k + 1 == len(rest_coda) and nxt_on[:1] in ("b", "p") and parts:
                # m→n 規則：把 n 併回前面的元音
                v = parts[-1] + "n"
                if v in rows:
                    res[-1] = pick(rows[v].get(col if len(parts) == 1 else ""), notes, v)
                    trace[-1] = f"{c0}{v}→{res[-1]}（m 在 p/b 前作 n）"
                    continue
            ch = pick(zero.get(COL.get(c, c)), notes, f"{c}（音節尾）")
            res.append(ch); trace.append(f"{c}→{ch}")
    s = "".join(res)
    if mode == "place":
        for a, b in (("東", "棟"), ("南", "楠"), ("西", "錫")):
            if s.startswith(a):
                s = b + s[1:]; notes.append(f"詞首{a}改{b}")
        if s.endswith("海"):
            s = s[:-1] + "亥"; notes.append("詞尾海改亥")
    if s.startswith("夫"):
        s = "弗" + s[1:]
    s = s[0] + s[1:].replace("弗", "夫") if s else s
    sy_txt = "-".join(a + b + c for a, b, c in sy)
    return s, sy_txt, trace, notes


def translit(text, mode):
    out, info = [], []
    for part in re.split(r"(\s+|-)", text.strip()):
        if not part or part.isspace() or part == "-":
            continue
        s, sy, tr, nt = translit_word(part, mode)
        out.append(s); info.append((part, sy, tr, nt))
    sep = "·" if mode == "person" else ""
    return sep.join(out), info


def generic_variant(text):
    low = text.lower()
    for g, zh in GENERIC:
        if low.endswith(g) and len(low) > len(g) + 1:
            stem = text[: -len(g)]
            # 專名在複合地名裡是屬格（Kärstilän-järvi＝Kärstilä 的湖），意譯通名時專名要還原主格，去掉屬格 -n
            # （Kärstilänjärvi→凱爾斯蒂萊湖、Rokkalanjoki→羅卡拉河；Hämeen→Häme 海梅）
            if stem.lower().endswith("n") and len(stem) > 2 and stem[-2].lower() in VOW:
                stem = stem[:-1]
            return stem, zh
    return None


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
    print(f"# 依{'人名' if mode == 'person' else '地名'}表譯寫（中國大陸標準，譯名一律以繁體字輸出；台灣有通行譯名時以通行為準）")
    for w in words:
        zh, info = translit(w, mode)
        line = f"{w}\t{S(zh)}"
        if mode == "place":
            g = generic_variant(w)
            if g:
                stem_zh, _ = translit(g[0], mode)
                line += f"\t通名意譯：{S(stem_zh + g[1])}"
        print(line)
        if verbose:
            for part, sy, tr, nt in info:
                print(f"    {part}：{sy}｜{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
