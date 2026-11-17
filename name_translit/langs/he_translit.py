"""希伯來語音譯工具：輸入希伯來語人名、地名的拉丁轉寫，依中維「外語譯音表/希伯來語」吐出漢字譯名。

2026-11-17 寫。譯音表存在同目錄 he_translit_table.json（從中維頁面解析，重建用 he_translit_build_table.py）。
  依據：新華社《世界人名翻譯大辭典》（1993）的希伯來語譯音表。頁面註明只適用於大陸簡體環境的「人名」，
  不適用於地名；中國沒有希伯來語地名國標，所以本工具的地名模式也用同一張表，只作參考
  （以色列地名多有慣譯：特拉維夫、海法、耶路撒冷，一律照通行譯名）。
  譯名一律以繁體字形輸出。

輸入：拉丁轉寫（表上的轉寫：' b v w g d h ch kh z t y k q l m n s p f tz ts r sh，元音 a e i o u、ā ī ū、ei ey ou oo）。
  希伯來字母原文不標元音，無法確定讀音，會被拒絕並提示改輸入轉寫。

用法：
  python -X utf8 he_translit.py -p "Shimon Peres" "Ariel Sharon"    （-p 人名表，名與姓間加「·」）
  python -X utf8 he_translit.py Ashdod                              （地名：同一張表，僅供參考）
  python -X utf8 he_translit.py -v -p Netanyahu                      （-v 列出音節與每字來源）
  python -X utf8 he_translit.py -f 名單.txt ／ --test [測試檔.tsv]

處理規則（表上說明＋一般慣例）：
  - ai、ay 按 a 行加「伊」；ia、ie 按 i 行加「亞」「耶」；輔音後的 y＋元音同樣當 i 處理（Netanyahu→內塔尼亞胡），
    輔音後不接元音的 y 當元音 i（Benny→貝尼、Sharansky→沙蘭斯基）。
  - tzh 按 tz（茨）加 h（赫）；h 在詞尾不譯；ch、kh 與 h 同列；q 與 k 同列。
  - 元音後的 n 不接元音時併入 an、on、en、un、in 行；雙寫輔音按一個譯。
  - 弗用於詞首、夫用於詞中與詞尾：頁面寫「(弗)用於詞尾」，與其他所有語言的表相反，判斷為筆誤（Tel Aviv 結尾慣譯「夫」），照其他表處理。
  - (婭)(瑪)(娜)(莎)(蕾) 等女性用字不自動套用，-v 會列出。
限制：新華社對常見人名多有慣譯（伊扎克、摩西、果爾達·梅厄），照表譯不出；寫條目時先查中文維基條目名。轉寫不一致時（Yitzhak／Itzhak）結果不同。
"""
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import opencc  # pip install --user opencc-python-reimplemented
_s2t = opencc.OpenCC("s2t").convert
S = lambda x: "".join(_s2t(c) for c in x).translate(str.maketrans("裏於佔託採佈羣誇", "里于占托采布群夸"))  # 逐字轉繁（整串轉會出「拉剋」）；音譯用字被誤轉的轉回
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "he_translit_table.json"), encoding="utf-8"))

VOW = "aeiouāīū"
CONS_UNITS = ("sh", "tz", "ts", "ch", "kh")
COL = {"ch": "h", "kh": "h", "q": "k", "ts": "tz", "c": "k", "j": "y"}
NORM_V = {"ā": "a", "ī": "i", "ū": "u"}


def pick(cell, notes, label):
    if not cell or not cell["main"]:
        notes.append(f"{label}：表上此格為空")
        return "?"
    if cell["alt"]:
        notes.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['alt'])}")
    return cell["main"][0]


def units(w):
    out, i = [], 0
    while i < len(w):
        d = next((u for u in CONS_UNITS if w.startswith(u, i)), None)
        if d:
            out.append(d); i += len(d)
        else:
            out.append(w[i]); i += 1
    return out


def isv(u):
    return u in VOW


def translit_word(word, mode):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    w = word.lower().replace("ʼ", "'").replace("ʻ", "'").replace("’", "'").replace("‘", "'").replace("ʿ", "'").replace("ʾ", "'")
    w = w.replace("x", "ks").replace("ph", "f")  # Ephraim 的 ph＝f
    w = re.sub(r"([bcdfghjklmnpqrstvwxz])\1", r"\1", w)  # 雙寫輔音按一個
    # 輔音後、不接元音的 y 當元音 i（Benny→貝尼）
    w = re.sub(r"(?<=[bcdfghjklmnpqrstvwxz])y(?![aeiouāīū])", "i", w)
    u = units(w)
    res, trace, notes = [], [], []
    i, n = 0, len(u)
    while i < n:
        c = u[i]
        if c == "-":
            i += 1; continue
        onset = ""
        if not isv(c):
            nxt = u[i + 1] if i + 1 < n else ""
            nxt2 = u[i + 2] if i + 2 < n else ""
            # 輔音＋y＋元音：y 當 i（ia→亞、ie→耶）
            if c != "y" and nxt == "y" and nxt2 and isv(nxt2):
                col = COL.get(c, c)
                ch = pick(rows["i"].get(col), notes, f"{c}i")
                res.append(ch); trace.append(f"{c}y→{ch}")
                i += 2
                v = NORM_V.get(u[i], u[i])
                if v in ("a", "e"):
                    extra = "亞" if v == "a" else "耶"
                    res.append(extra); trace.append(f"y{v}→{extra}（i{v} 規則）"); i += 1
                continue
            if nxt and isv(nxt):
                onset = c; i += 1
            else:
                if c == "'":
                    i += 1; continue
                if c == "h" and (i + 1 >= n) and res:
                    trace.append("h→（詞尾不譯）"); i += 1; continue
                col = COL.get(c, c)
                ch = pick(zero.get(col), notes, f"{c}（單獨）")
                res.append(ch); trace.append(f"{c}→{ch}"); i += 1; continue
        # 元音組
        v = NORM_V.get(u[i], u[i])
        j = i + 1
        nx = NORM_V.get(u[j], u[j]) if j < n else ""
        key, extra = v, ""
        if v == "e" and nx in ("i", "y") and not (j + 1 < n and isv(u[j + 1])):
            key, j = "ei", j + 1
        elif v == "o" and nx in ("u", "o"):
            key, j = "u", j + 1
        elif v == "a" and nx in ("i", "y") and not (j + 1 < n and isv(u[j + 1])):
            extra, j = "伊", j + 1
        # 鼻音尾
        if j < n and u[j] == "n" and not (j + 1 < n and (isv(u[j + 1]) or u[j + 1] == "y")) and key + "n" in rows:
            key, j = key + "n", j + 1
        col = COL.get(onset, onset) if onset else ""
        if col == "'":
            col = "'"
        prev_v = trace[-1].split("→")[0][-1:] if trace else ""
        if not onset and prev_v == "i" and v in ("a", "e") and key in ("a", "e"):
            ch = "亞" if v == "a" else "耶"
            res.append(ch); trace.append(f"i{v}→{ch}（i{v} 規則）"); i = j; continue
        ch = pick(rows.get(key, {}).get(col), notes, f"{onset}{key}")
        res.append(ch + extra); trace.append(f"{onset}{key}→{ch}{extra}" + ("（ai 規則）" if extra else ""))
        i = j
    s = "".join(res)
    if s.startswith("夫"):
        s = "弗" + s[1:]
    s = s[:1] + s[1:].replace("弗", "夫")
    return s, trace, notes


def translit(text, mode="person"):
    if re.search(r"[֐-׿]", text):
        return "（希伯來字母不標元音，無法確定讀音；請改輸入拉丁轉寫）", []
    out, info = [], []
    for part in re.split(r"\s+", text.strip()):
        if not part:
            continue
        s, tr, nt = translit_word(part, mode)
        out.append(s); info.append((part, tr, nt))
    return ("·" if mode == "person" else "").join(out), info


def run_tests(path):
    ok = bad = 0
    for row in csv.reader(open(path, encoding="utf-8"), delimiter="\t"):
        if len(row) < 3 or row[0] not in ("place", "person"):
            continue
        got = S(translit(row[1], row[0])[0])
        if got == row[2]:
            ok += 1
        else:
            bad += 1; print(f"不通過\t{row[0]}\t{row[1]}\t預期 {row[2]}\t得到 {got}\t{row[3] if len(row) > 3 else ''}")
    print(f"通過 {ok}／{ok + bad}")


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
        elif a in ("--test", "-t"):
            return run_tests(next(it, os.path.join(os.path.dirname(os.path.abspath(__file__)), "he_translit_test.tsv")))
        elif a in ("-h", "--help"):
            print(__doc__); return
        else:
            words.append(a)
    if not words:
        print(__doc__); return
    print(f"# 依希伯來語{'人名' if mode == 'person' else '人名（地名無國標，僅供參考）'}表譯寫（中國大陸標準，繁體輸出；常識性與慣用譯名以通行為準）")
    for w in words:
        zh, info = translit(w, mode)
        print(f"{w}\t{S(zh)}")
        if verbose:
            for part, tr, nt in info:
                print(f"    {part}：{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
