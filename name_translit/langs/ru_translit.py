"""俄語音譯工具：輸入西里爾字母的地名或人名，依中維「外語譯音表/俄語」吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 ru_translit_table.json（取自中維 Wikipedia:外語譯音表/俄語）：
  地名表＝GB/T 17693.4-2009《外语地名汉字译写导则 俄语》（中維已修正 гу→古、пун→蓬 兩處印刷錯誤）；
  人名表＝新華社《世界人名翻译大辞典》《俄语姓名译名手册》。另含「н 雙拼詞幹表」40 個。
  兩表都是中國大陸標準，譯名一律以繁體字輸出；莫斯科、彼得堡這類常識性譯名以通行譯名為準，不必跑工具。
  白俄羅斯語、烏克蘭語、哈薩克語等以西里爾字母拼寫的人名，中維註明也參照人名表。

用法：
  python -X utf8 ru_translit.py Ржев Вязьма Ивановка        （預設地名表）
  python -X utf8 ru_translit.py -p "Константин Рокоссовский"   （-p 人名表，名與姓間加「·」）
  python -X utf8 ru_translit.py -v Зеленокумск                 （-v 列出音節與每字來源）
  python -X utf8 ru_translit.py -f 名單.txt                     （每行一個原文）
  只收西里爾字母；拉丁轉寫（Rzhev）請先換回俄文原文。

處理規則（照表上說明）：
  - 兩個相同輔音按單輔音譯，нн 例外按兩個輔音譯（前一個併入元音列）。
  - д、т 在 ч、ц 前不發音；зш、сш→ш；дс、тс、цс、дц、тц→ц；жч、зч、сч→щ；гк 的 г 譯「赫」；чт 的 ч 譯「什」；
    -стн、-стл、-здн、-рдц 的中間輔音、лнц 的 л 不發音；形容詞詞尾 -ого、-его 的 г 譯 в。
  - м 在 б、п 前按 н 譯；詞首 р、л 後接輔音譯「勒」；ъ 只起隔音作用。
  - ей、ой 按 е、о 列加「伊」；я、е、ё、ю 在詞首、元音後、ъ／ь 後用元音零行（亞、耶、約、尤）。
  - 叶、弗用於詞首，耶、夫用於詞中與詞尾。
  - 地名：東／南／西在詞首改栋／楠／锡，江、海在詞尾改姜、亥；-бург 堡、-град 格勒、-город 哥罗德、-цов 佐夫。
  - 詞幹在雙拼表內（Иван、Антон、Пушкин…）時，詞幹照表譯，詞尾的 н 再與後綴連譯（Ивановка→伊万诺夫卡）。
  - 同一格有兩個字時取第一個，女性用字（娅、玛、娜…）不自動套用；-v 會列出另一個。
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
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ru_translit_table.json"), encoding="utf-8"))

VOW = "аяэеыиоёуюь"
IOT = "яеёю"
SUFFIX = [("бург", "堡"), ("град", "格勒"), ("город", "哥罗德"), ("цов", "佐夫")]


def prep(w):
    w = w.lower().replace("ъ", "|")
    w = re.sub(r"(ого|его)$", lambda m: m.group(1).replace("г", "в"), w)
    for a, b in (("стн", "сн"), ("стл", "сл"), ("здн", "зн"), ("рдц", "рц"), ("лнц", "нц"),
                 ("зш", "ш"), ("сш", "ш"), ("жч", "щ"), ("зч", "щ"), ("сч", "щ"),
                 ("дс", "ц"), ("тс", "ц"), ("цс", "ц"), ("дц", "ц"), ("тц", "ц"), ("тч", "ч"), ("дч", "ч")):
        w = w.replace(a, b)
    w = w.replace("гк", "хк").replace("чт", "шт")
    w = re.sub(r"(?<=[бвгджзклмнпрстфхцчшщ])ьи", "и", w)  # 表上 ьи 與 и 同列（Ильинка→伊林卡）
    # 雙寫輔音（нн 除外）
    w = re.sub(r"([бвгджзклмпрстфхцчшщ])\1", lambda m: m.group(0) if m.group(1) == "н" else m.group(1), w)
    return w


def units(w):
    out, i = [], 0
    while i < len(w):
        if w.startswith("дж", i):
            out.append("дж"); i += 2
        else:
            out.append(w[i]); i += 1
    return out


def pick(cell, notes, label):
    if not cell or not cell["main"]:
        notes.append(f"{label}：表上此格為空")
        return "?"
    if len(cell["main"]) > 1 or cell["alt"]:
        notes.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['main'][1:] + cell['alt'])}")
    return cell["main"][0]


def translit_core(word, mode):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    u = units(prep(word))
    res, notes, trace = [], [], []
    i, n = 0, len(u)
    isv = lambda x: x in VOW
    while i < n:
        c = u[i]
        if c == "|":
            i += 1; continue
        if c == "й" and i + 1 < n and u[i + 1] in "аоуэ":  # йа→я 等
            u[i + 1] = {"а": "я", "о": "ё", "у": "ю", "э": "е"}[u[i + 1]]; i += 1; continue
        onset = ""
        if not isv(c) and c != "й":
            nxt = u[i + 1] if i + 1 < n else ""
            if nxt and isv(nxt) and not (nxt == "ь" and (i + 2 >= n or not isv(u[i + 2]) and u[i + 2] != "")):
                onset = c; i += 1
            elif nxt == "ь":
                onset = c; i += 1
            else:
                # 單獨輔音
                if c == "м" and nxt in ("б", "п"):
                    c = "н"
                if c in ("р", "л") and not res and nxt and not isv(nxt):
                    res.append("勒"); trace.append(f"{c}→勒（詞首後接輔音）"); i += 1; continue
                if c == "н" and res and trace and trace[-1].endswith("+н?"):
                    pass
                ch = pick(zero.get(c), notes, f"{c}（單獨）")
                res.append(ch); trace.append(f"{c}→{ch}"); i += 1; continue
        elif c == "й":
            ch = "伊"; res.append(ch); trace.append("й→伊"); i += 1; continue
        # 元音組
        prev = u[i - 1] if i > 0 else ""
        iot_zero = (onset == "" and u[i] in IOT)
        best = None
        for L in (3, 2, 1):
            g = "".join(u[i:i + L])
            if len(g) != L:
                continue
            if g in rows and all(isv(x) or x == "й" for x in g):
                best = g; break
            if L == 2 and g in ("ей", "ой"):
                best = g; break
        if best is None:
            best = u[i]
        j = i + len(best)
        # 鼻音尾 н／нь（後面不是元音才併）
        nasal = ""
        if j < n and u[j] == "н" and best[-1] not in "йь":
            after = u[j + 1] if j + 1 < n else ""
            if after == "ь" and (j + 2 >= n or not isv(u[j + 2])) and best + "нь" in rows:
                nasal = "нь"
            elif (not after or (not isv(after)) or after == "н") and best + "н" in rows:
                nasal = "н"
        if j < n and u[j] == "м" and j + 1 < n and u[j + 1] in "бп" and best + "н" in rows:
            nasal = "м"
        key = best + ("н" if nasal else "")
        if nasal == "нь":
            key = best + "нь"
        extra = ""
        if best in ("ей", "ой"):
            key = best[0]; extra = "伊"
        col = onset
        if onset == "" and best[0] in IOT and prev and not isv(prev) and prev != "|":
            col = ""
        row = rows.get(key)
        ch = pick(row.get(col) if row else None, notes, f"{onset}{key}")
        if onset == "" and key[:1] in ("е",) and not res:
            ch = "叶"
        if onset == "ь":
            ch = pick(rows["ь"].get(""), notes, "ь")
        res.append(ch + extra); trace.append(f"{onset}{key}→{ch}{extra}" + ("（м 在 б／п 前作 н）" if nasal == "м" else ""))
        i = j + (len(nasal) if nasal in ("н", "м") else 2 if nasal == "нь" else 0)
    s = "".join(res)
    if s.startswith("夫"):
        s = "弗" + s[1:]
    s = s[:1] + s[1:].replace("弗", "夫").replace("叶", "耶")
    if mode == "place" and s:
        for a, b in (("东", "栋"), ("東", "栋"), ("南", "楠"), ("西", "锡")):
            if s.startswith(a):
                s = b + s[1:]; notes.append(f"詞首{a}改{b}")
        for a, b in (("江", "姜"), ("海", "亥")):
            if s.endswith(a):
                s = s[:-1] + b; notes.append(f"詞尾{a}改{b}")
    return s, trace, notes


def translit_word(word, mode):
    low = word.lower()
    stems = TABLE["stems"]
    if low in stems:
        return stems[low], [f"{word}→雙拼詞幹表"], []
    for st, zh in sorted(stems.items(), key=lambda x: -len(x[0])):
        if low == st + "ь":
            return zh, [f"{word}→雙拼詞幹表"], []
        if low.startswith(st) and len(low) > len(st) and low[len(st)] in VOW and low[len(st)] != "ь":
            rest, tr, nt = translit_core("н" + low[len(st):], mode)
            # rest 以 н 開頭的音節已含 н，去掉詞幹最後的「恩」重複：詞幹譯名本身不含單獨 н
            return zh + rest, [f"{st}→{zh}（雙拼詞幹）"] + tr, nt
    if mode == "place":
        for suf, zh in SUFFIX:
            if low.endswith(suf) and len(low) > len(suf):
                s, tr, nt = translit_core(low[: -len(suf)], mode)
                return s + zh, tr + [f"-{suf}→{zh}"], nt
    return translit_core(word, mode)


def translit(text, mode):
    out, info = [], []
    for part in re.split(r"[\s\-]+", text.strip()):
        if part:
            s, tr, nt = translit_word(part, mode)
            out.append(s); info.append((part, tr, nt))
    return ("·" if mode == "person" else "").join(out), info


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
    print(f"# 依俄語{'人名' if mode == 'person' else '地名'}表譯寫（中國大陸標準，繁體輸出；常識性譯名以通行為準）")
    for w in words:
        if re.search(r"[a-zA-Z]", w):
            print(f"{w}\t（請輸入西里爾字母原文）"); continue
        zh, info = translit(w, mode)
        print(f"{w}\t{S(zh)}")
        if verbose:
            for part, tr, nt in info:
                print(f"    {part}：{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
