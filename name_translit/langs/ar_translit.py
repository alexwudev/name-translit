"""阿拉伯語音譯工具：輸入阿拉伯語地名或人名（拉丁轉寫或帶短元音符號的阿拉伯字母），
依中維「外語譯音表/阿拉伯語」吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 ar_translit_table.json（由 ar_translit_build_table.py 從中維頁面原始碼重建）：
  地名表＝GB/T 17693.6-2008《外语地名汉字译写导则 阿拉伯语》（表1，含中維對 f 欄「弗→费」的勘誤）；
  人名表＝新華社《世界人名翻译大辞典》第2版。兩表都是中國大陸標準，譯名一律以繁體字輸出；
  台灣已有通行譯名、或屬慣用譯名（開羅、巴格達、穆罕默德、侯賽因、納賽爾…）時以通行為準，本工具只給參考
  （GB/T 4.3 本身也規定惯用译名沿用）。

用法：
  python -X utf8 ar_translit.py "Wādī Ḥalfā" "Ash-Shiḥr" Qarn             （預設地名表）
  python -X utf8 ar_translit.py -p "Nūrī al-Mālikī" "Hishām Qandīl"         （-p 人名表，各部分間加「·」）
  python -X utf8 ar_translit.py -v "Maʿrūf"                                  （-v 列出音節切分與每字來源）
  python -X utf8 ar_translit.py -f 名單.txt                                  （每行一個原文）
  python -X utf8 ar_translit.py "مَعْرُوف"                                    （阿拉伯字母，必須標短元音）
  python -X utf8 ar_translit.py --test                                       （跑同目錄 ar_translit_test.tsv）

輸入格式（表是依讀音排的，拉丁字母欄就是表上收的轉寫）：
  - 拉丁轉寫：UNGEGN 1972、ALA-LC 為主，也收表上括號內的法語／埃及轉寫與 DIN 31635 的字母：
      ʾ（ʼ ’）＝ء；ʿ（ʻ ‘ `）＝ع；半形撇號 ' 一律當 ʿ（ع 比 ء 常見；要 ء 請寫 ʾ 或 ’）。
      th ṯ、kh ḫ ẖ、sh š ch、dh ḏ、gh ġ、j dj ǧ g（g 依表當 ج，埃及讀法）；ṭ ţ、ṣ ş、ḍ ḑ、ẓ z̧、ḥ ḩ（點下或下加符都可）；
      長元音 ā á â、ī î、ū û；短 a 可寫 e è é ê；o ô ou＝u；ai ei ey＝ay；au aou av＝aw；aa＝ā、ee＝ī、oo＝ū（英語式拼法）。
      ou 後接元音當 w（法語 Khaloua＝khalwa）；詞尾 -ne／-nne（法語 Hassane、Ramdane）當 n。
      兩個字母要分開讀時用 ʹ 或 | 隔開（ALA-LC 的 Adʹham）。
  - 阿拉伯字母：必須標出短元音（َ ِ ُ ْ ّ）；沒有標短元音的原文無法確定讀音，程式會拒絕並請你改輸入拉丁轉寫。
    標了一部分的，沒標的字母當無元音（ـْ）處理並在 -v 註明。

處理規則（照表與表下說明、GB/T 17693.6 第5章）：
  - 音節：兩元音間的輔音群，最後一個歸下一音節，其餘留在前一音節尾；詞首輔音群前面的字母單獨譯（零行）。
  - 雙寫輔音（含 shadda）只譯一次（Burullus→布鲁卢斯）；a 後的 yy／ww 例外，前一個併入 ay／aw（Sayyid→賽伊德）。
  - a 後接 y、w 而 y、w 後面沒有元音時用 ay、aw 行；音節尾的 n 併入 an／in／un 行（ān、īn、ūn 同行）；
    ayn→ay 行＋「因」、awn→aw 行＋「温」（GB/T 5.3.4 的 yn、wn）。
  - 地名表 n 行（GB/T 5.3.4）：bn 本、tn 坦、sn 森、rn 伦、shn 申（n 後無元音時；Qarn→盖伦、Ibn→伊本）。人名表沒有這一行。
  - ء／ع（表注 厄、阿；GB/T 5.3.1）：詞中不帶元音時省譯，前面短元音按長元音譯（Maʿrūf→马鲁夫、Raʾs→拉斯）；
    詞尾前面是長元音時省譯（Ḥamrāʾ→哈姆拉、Niṭāʿ→尼塔）；詞尾前面是短元音或輔音時譯出（Isbaʿ→伊斯拜阿）。
  - 詞尾 ة（h，前面是短元音 a）不譯（Daulah→道莱）；ḥ 必譯（Rīḥ→里赫）；寫成 -at 的（後接他詞發音）照譯「特」。
  - m 在 b、p 前按 n 譯。弗用於詞首，夫用於詞中與詞尾。
  - 地名：h·kh 與 ḥ 分讀（ha 海／ḥa 哈、hu 胡／ḥu 侯），s·th 與 ṣ 分讀（si 西／ṣi 绥、sun 松／ṣun 孙）；
    南、西在地名開頭改楠、锡，海在地名結尾改亥；aw 行「萨乌/索」類取單字，單音節詞（GB/T 5.1.9 用兩字）才用兩字，
    ay、aw 單音節詞拆成 ā 行＋伊／乌（Al Lay→拉伊、Al Sau→萨乌）。
  - 定冠詞（al-、el-、l-，及同化的 ash-、an-、ar-、at-…）省譯；Āl（家族，要寫長音符）譯「阿勒」並與後一詞連寫。
  - 人名常用成分照 GB/T 附錄B／新華社慣例（表上推不出）：Abū 阿布（含 Abu'X 連寫）、ʿAbd al- 阿卜杜勒（人名接「-」、
    地名接「·」）、Abdul-／Abdel- 連寫、ʿAbd Allāh／Abdullah 阿卜杜拉、ibn 伊本、bin／ben 本、bint 宾特；-v 會註明。
  - 名稱最後一詞以短 a＋t 結尾（-at、-et，拉丁轉寫的 ة）時不譯 t（Baḥrat→拜赫拉）；後面還有詞時照譯（Birkat al Sabʿ→比尔凯特塞卜阿）。
  - 地名多詞連寫，譯名 8 字以上時第一個詞後加「-」（GB/T 5.1.7）；人名各部分間加「·」。
  - 通名：Jabal、Wādī、Bi'r、Ra's、Baḥr、Jazīrah、Qaṣr、Sūq 等在地名開頭時，另列「通名意譯」版本（纳伊夫山），由使用者自選
    （GB/T 5.1.1：專名化的通名一般音譯）。
  - 人名另列「地名表版本」（-p 時與人名表結果不同才列）：中維表注說常見人名的實際譯法反而常合地名表
    （Ḥusayn 侯赛因、ʿArafāt 阿拉法特、Ḥakīm 哈基姆），由使用者對照新華社譯名自選。
  - 同一格有兩個字（坦/唐、龙/伦、旺/万、扬/延）時取第一個；女性用字（莎、玛、娜、娅、丽、莉、妮、娃、蒂）不自動套用；-v 會列出。

限制（做不到或沒做）：
  - 英文報刊式拼法（Mohamed、Hussein、Sheikh）不一定照標準轉寫，譯出來可能與讀音有出入；譯音表頁面也明說此表不一定適用於英文寫法。
  - ASCII 撇號無法分辨 ء 與 ع，一律當 ع；只在詞首與詞尾短元音後才有差別（例：詞首 ʾa 艾、ʿa 阿）。
  - 法語轉寫的 qu（＝k）、rh（＝gh）不處理（與英語 Qu、r+h 衝突），請改寫成 k、gh。
  - ة 寫成 h 一律當詞尾不譯；寫成 t／et 一律譯出。真正的詞尾 h（ه）前面是短元音時會被誤刪，請寫成 hʹ 或用阿拉伯字母。
  - 不處理語法上的格尾（i'rab）與連讀（Shajāʿa 的詞尾 a）；長名、意譯（GB/T 5.1.2–5.1.6，方位、大小、顏色、數詞）要自己處理。
  - 新華社、中維的實際人名譯法常不照人名表：短 a 常用 ā 行（Mubārak 穆巴拉克 而非 穆巴雷克、Anwar 安瓦尔、Asad 阿萨德）、
    詞尾 q 常作「克」（Ṭāriq 塔里克，表上是「格」）、慣用名（Muḥammad 穆罕默德、ʿAlī 阿里、ʿAbd Rabbuh 阿卜杜拉布）。
    人名請先查中維條目或新華社譯名，本工具只在查不到時參考。
  - 詞尾 -at 的省譯規則會誤刪真正的詞尾 t（極少見），遇到時改用阿拉伯字母輸入。
  - GB/T 表2、表4 的例子本身與表1不一致之處（Jabal→杰贝勒 的「贝」、Ḥufrat→侯夫赖特 的「赖」、Quraiyāt→古莱亚特 的「莱」），
    本工具照表1，不照例子。
"""
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
import opencc  # pip install --user opencc-python-reimplemented
# 譯名一律以繁體字輸出（2026-11-17 使用者指示：簡體看起來怪）；s2t 會把音譯用的里、于、占、托、采轉成裏、於、佔、託、採，要轉回
_s2t = opencc.OpenCC("s2t").convert
S = lambda x: "".join(_s2t(c) for c in x).translate(str.maketrans("裏於佔託採佈羣誇", "里于占托采布群夸"))  # 逐字轉繁（整串轉會出「拉剋」）；音譯用字被誤轉的轉回
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ar_translit_table.json"), encoding="utf-8"))

VOWELS = set("aāiīuū")
ROW = {"a": "a", "ā": "ā", "i": "i", "ī": "i", "u": "u", "ū": "u"}
LONG = {"a": "ā", "i": "ī", "u": "ū"}
# 音素 → 表上欄位
COLMAP = {"ṭ": "t", "th": "s", "kh": "h", "ḍ": "d", "dh": "z", "ẓ": "z", "gh": "q", "g": "j", "v": "w", "č": "ch"}
SHOW = {"`": "ʿ", "'": "ʾ", "č": "ch"}
GENERIC = {
    "jabal": "山", "jebel": "山", "djebel": "山", "jbel": "山",
    "wadi": "干河", "oued": "干河", "wad": "干河",
    "bir": "井", "bi`r": "井", "bi'r": "井",
    "ras": "角", "ra's": "角", "ra`s": "角",
    "bahr": "湖", "buhayrah": "湖", "buhayrat": "湖", "buheirat": "湖",
    "jazirah": "岛", "jazirat": "岛", "jazira": "岛", "djezira": "岛",
    "qasr": "堡", "ksar": "堡", "kasar": "堡", "suq": "集市", "souk": "集市", "suk": "集市", "bur": "港",
    "madinah": "城", "madinat": "城", "khalij": "湾", "nahr": "河", "ayn": "泉", "ain": "泉", "`ayn": "泉",
    "sahra": "沙漠", "sahra'": "沙漠", "wahat": "绿洲", "wahah": "绿洲", "tall": "丘", "tell": "丘",
    "sabkhah": "盐沼", "sebkha": "盐沼", "sabkhat": "盐沼", "hamadah": "石漠", "hamada": "石漠",
    "shallal": "瀑布", "qararah": "洼地", "qararat": "洼地", "muhafazah": "省", "muhafazat": "省",
}
# 附錄B／新華社慣用的人名成分（表上推不出）
PARTICLE = {"abu": "阿布", "abou": "阿布", "abū": "阿布", "ibn": "伊本", "bin": "本", "ben": "本", "bint": "宾特",
            "abdullah": "阿卜杜拉", "abdallah": "阿卜杜拉", "abdellah": "阿卜杜拉"}
ARTICLES = {"al", "el", "il", "ul", "l"}

# ---------- 拉丁轉寫 → 音素 ----------
APOS_HAMZA = "ʾʼ’"
APOS_AYN = "ʿʻ‘`'"
SEP = "ʹ|"
DOT = {"̣", "̧", "̦"}           # 點下、下加符、逗號下
LONGMARK = {"̄", "́", "̂"}       # 長音符、尖音符、揚抑符
EMPH = {"t": "ṭ", "s": "ṣ", "d": "ḍ", "z": "ẓ", "h": "ḥ"}
DIGRAPH = {"th": "th", "kh": "kh", "sh": "sh", "dh": "dh", "gh": "gh", "dj": "j", "ch": "sh", "zh": "j"}


def _chars(word):
    """拆成 (基本字母小寫, 附加符號集合)。"""
    out = []
    for ch in unicodedata.normalize("NFD", word):
        if unicodedata.combining(ch) and out:
            out[-1][1].add(ch)
        else:
            out.append([ch.lower(), set()])
    return out


def latin_phones(word, notes):
    cs = _chars(word)
    ph, i, n = [], 0, len(cs)

    def base(k):
        return cs[k][0] if k < n else ""

    def isvow(k):
        return base(k) in "aeiouy" and k < n

    def truevow(k):
        return base(k) in "aeiou" and k < n

    while i < n:
        b, m = cs[i]
        b2 = base(i + 1)
        if b in SEP:
            ph.append("|"); i += 1; continue
        if b in APOS_HAMZA:
            ph.append("'"); i += 1; continue
        if b in APOS_AYN:
            if b == "'":
                notes.append("半形撇號 ' 當 ʿ（ع）；若是 ء 請寫 ʾ")
            ph.append("`"); i += 1; continue
        # 帶附加符號的輔音
        if b in EMPH and m & DOT:
            ph.append(EMPH[b]); i += 1; continue
        if b == "h" and "̮" in m or b == "h" and "̱" in m or b == "k" and "̱" in m:
            ph.append("kh"); i += 1; continue
        if b == "t" and "̱" in m:
            ph.append("th"); i += 1; continue
        if b == "d" and "̱" in m:
            ph.append("dh"); i += 1; continue
        if b == "s" and "̌" in m:
            ph.append("sh"); i += 1; continue
        if b == "g" and "̌" in m:
            ph.append("j"); i += 1; continue
        if b == "g" and "̇" in m:
            ph.append("gh"); i += 1; continue
        # 二合字母（兩個字母都不帶符號才算）
        if not m and b + b2 in DIGRAPH and i + 1 < n and not cs[i + 1][1]:
            ph.append(DIGRAPH[b + b2]); i += 2; continue
        # 元音
        if b == "a":
            if m & LONGMARK:
                ph.append("ā"); i += 1; continue
            if b2 == "a" and not cs[i + 1][1]:
                ph.append("ā"); i += 2; continue
            if b2 == "o" and base(i + 2) == "u":       # aou → aw
                ph += ["a", "w"]; i += 3; continue
            if b2 == "u" and not cs[i + 1][1] and not isvow(i + 2):   # au → aw
                ph += ["a", "w"]; i += 2; continue
            if b2 == "v" and not isvow(i + 2):          # av → aw
                ph += ["a", "w"]; i += 2; continue
            if b2 == "i" and not cs[i + 1][1] and not truevow(i + 2):   # ai → ay（aiy＝ayy）
                ph += ["a", "y"]; i += 2; continue
            ph.append("a"); i += 1; continue
        if b == "e":
            if b2 in "iy" and i + 1 < n and not cs[i + 1][1] and not truevow(i + 2):   # ei ey → ay
                ph += ["a", "y"]; i += 2; continue
            if b2 == "e" and not cs[i + 1][1]:
                ph.append("ī"); i += 2; continue
            if i == n - 1 and len(ph) >= 2 and ph[-1] == "n" and ph[-2] in VOWELS | {"n"}:
                notes.append("詞尾 -ne 照法語拼法當 n"); i += 1; continue
            ph.append("a"); i += 1; continue
        if b == "i":
            if m & LONGMARK:
                ph.append("ī"); i += 1; continue
            if b2 == "y" and not isvow(i + 2):          # iy → ī
                ph.append("ī"); i += 2; continue
            ph.append("i"); i += 1; continue
        if b == "o":
            if b2 == "u" and not cs[i + 1][1]:
                if isvow(i + 2):                          # ou + 元音 → w
                    ph.append("w"); i += 2; continue
                ph.append("ū"); i += 2; continue
            if b2 == "o":
                ph.append("ū"); i += 2; continue
            ph.append("ū" if m & LONGMARK else "u"); i += 1; continue
        if b == "u":
            if m & (LONGMARK | {"̀"}):
                ph.append("ū"); i += 1; continue
            if b2 == "w" and not isvow(i + 2):
                ph.append("ū"); i += 2; continue
            ph.append("u"); i += 1; continue
        if b == "y":
            if isvow(i + 1) and base(i + 1) != "y":
                ph.append("y")
            elif ph and ph[-1] == "a" or ph and ph[-1] == "y" and len(ph) > 1 and ph[-2] == "a":
                ph.append("y")
            else:
                ph.append("ī")                            # 輔音後的 y 當 i（表上 i 行收 y）
            i += 1; continue
        if b == "v":
            ph.append("w"); i += 1; continue
        if b == "c":
            notes.append("單獨的 c 當 k")
            ph.append("k"); i += 1; continue
        if b == "x":
            ph += ["k", "s"]; i += 1; continue
        if b.isalpha() and b in "bdfghjklmnpqrstwz":
            ph.append(b); i += 1; continue
        if b.isalpha():
            notes.append(f"不認得的字母 {b}，略過")
        i += 1
    return ph


# ---------- 阿拉伯字母 → 音素 ----------
AR = {"ب": "b", "ت": "t", "ث": "th", "ج": "j", "ح": "ḥ", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r", "ز": "z",
      "س": "s", "ش": "sh", "ص": "ṣ", "ض": "ḍ", "ط": "ṭ", "ظ": "ẓ", "ع": "`", "غ": "gh", "ف": "f", "ق": "q",
      "ك": "k", "ک": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "پ": "p", "چ": "č", "گ": "g", "ڤ": "v",
      "ء": "'", "أ": "'", "إ": "'", "ؤ": "'", "ئ": "'", "و": "w", "ي": "y", "ی": "y", "ة": "h"}
HARAKA = {"َ": "a", "ِ": "i", "ُ": "u", "ٰ": "ā"}
SUKUN, SHADDA = "ْ", "ّ"
MARKS = set("ًٌٍَُِّْٰ")


def is_arabic(s):
    return any("؀" <= c <= "ۿ" for c in s)


def arabic_phones(word, notes):
    word = word.replace("ـ", "")
    if not any(c in MARKS for c in word):
        raise ValueError("原文沒有標短元音，無法確定讀音；請改輸入拉丁轉寫（ALA-LC 或 UNGEGN，例如 Maʿrūf）")
    # 拆成 (字母, 附加符號)
    units = []
    for c in word:
        if c in MARKS and units:
            units[-1][1] += c
        elif c not in MARKS:
            units.append([c, ""])
    # 定冠詞 ال
    if len(units) > 2 and units[0][0] == "ا" and units[1][0] == "ل":
        notes.append("定冠詞 ال 省譯")
        units = units[2:]
    ph, missing = [], 0
    for k, (c, d) in enumerate(units):
        vowel = next((HARAKA[x] for x in d if x in HARAKA), None)
        last = k == len(units) - 1
        if c in ("ا", "ى"):
            if ph and ph[-1] == "a":
                ph[-1] = "ā"
            elif k == 0:
                ph += ["'", vowel or "a"]
                if not vowel:
                    notes.append("詞首 ا 沒標元音，當 a")
            else:
                ph.append("ā")
            continue
        if c == "آ":
            ph += ["'", "ā"]; continue
        if c == "و" and not vowel and SHADDA not in d and ph and ph[-1] == "u":
            ph[-1] = "ū"; continue
        if c == "ي" and not vowel and SHADDA not in d and ph and ph[-1] == "i":
            ph[-1] = "ī"; continue
        if c not in AR:
            notes.append(f"不認得的字母 {c}，略過"); continue
        p = AR[c]
        if c == "ة" and vowel:
            p = "t"
        ph.append(p)
        if SHADDA in d:
            ph.append(p)
        if vowel:
            ph.append(vowel)
        elif SUKUN not in d and not last and not (k + 1 < len(units) and units[k + 1][0] in "اىوي" and not units[k + 1][1]):
            missing += 1
    if missing:
        notes.append(f"有 {missing} 個字母沒標元音，當無元音（ـْ）處理")
    return ph


# ---------- 音素 → 漢字 ----------
def pick(cell, note, label):
    if not cell or not cell["main"] or cell["main"][0] in ("—", ""):
        note.append(f"{label}：表上此格為空")
        return "?"
    if len(cell["main"]) > 1 or cell["alt"]:
        note.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['main'][1:] + cell['alt'])}")
    return cell["main"][0]


def col(p):
    return COLMAP.get(p, p)


def show(p):
    return SHOW.get(p, p)


def prep(ph, notes):
    """去掉隔開符、雙寫輔音、詞尾 ة。"""
    out = []
    for p in ph:
        if p == "|":
            continue
        if out and p == out[-1] and p not in VOWELS:
            if p in ("y", "w") and len(out) > 1 and out[-2] == "a":
                out.append(p); continue          # ayy、aww：前一個併入 ay／aw
            notes.append(f"雙寫 {show(p)} 只譯一次")
            continue
        out.append(p)
    if len(out) >= 2 and out[-1] == "h" and out[-2] == "a":
        out.pop(); notes.append("詞尾 h（ة）不譯")
    return out


def syllabify(ph):
    """回傳 (詞首多餘輔音, [[onset, nucleus, coda[]], …])。"""
    vidx = [k for k, p in enumerate(ph) if p in VOWELS]
    if not vidx:
        return list(ph), []
    pre, syl = [], []
    first = vidx[0]
    lead = ph[:first]
    if lead:
        pre, on = lead[:-1], lead[-1]
    else:
        on = ""
    for j, k in enumerate(vidx):
        nxt = vidx[j + 1] if j + 1 < len(vidx) else len(ph)
        cons = ph[k + 1:nxt]
        if j + 1 < len(vidx):
            if cons:
                coda, nxt_on = cons[:-1], cons[-1]
            else:
                coda, nxt_on = [], ""
        else:
            coda, nxt_on = cons, ""
        syl.append([on, ph[k], coda])
        on = nxt_on
    return pre, syl


def render_word(ph, mode, notes):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    ph = prep(ph, notes)
    pre, syl = syllabify(ph)
    res, trace = [], []
    for c in pre:
        ch = pick(zero.get(col(c)), notes, f"{show(c)}（單獨）")
        res.append(ch); trace.append(f"{show(c)}→{ch}")
    for idx, (on, v, coda) in enumerate(syl):
        is_last = idx == len(syl) - 1
        nxt_on = syl[idx + 1][0] if not is_last else ""
        coda = list(coda)
        # m 在 b、p 前按 n 譯
        if coda and coda[-1] == "m" and nxt_on in ("b", "p"):
            coda[-1] = "n"; notes.append("m 在 b/p 前按 n 譯")
        # 詞中 ء／ع 不帶元音：省譯，前面短元音按長元音
        k = 0
        while k < len(coda):
            if coda[k] in ("'", "`") and not (is_last and k == len(coda) - 1):
                notes.append(f"詞中 {show(coda[k])} 省譯，前面元音按長元音")
                v = LONG.get(v, v)
                coda.pop(k); continue
            k += 1
        # 詞尾 ء／ع
        final_glottal = None
        if is_last and coda and coda[-1] in ("'", "`"):
            final_glottal = coda.pop()
            if not coda and v in ("ā", "ī", "ū"):
                notes.append(f"詞尾 {show(final_glottal)} 前為長元音，省譯")
                final_glottal = None
        oc = col(on) if on else "'"
        nucleus, label = ROW[v], v
        if v == "a" and coda and coda[0] in ("y", "w"):
            nucleus = "ay" if coda[0] == "y" else "aw"; label = nucleus; coda.pop(0)
        extra = ""
        if coda and coda[0] == "n":
            coda.pop(0)
            if nucleus in ("ay", "aw"):
                extra = "因" if nucleus == "ay" else "温"
                notes.append(f"{nucleus}n：{nucleus} 行加「{extra}」（GB/T 5.3.4 yn／wn）")
            else:
                nucleus = {"a": "an", "ā": "an", "i": "in", "u": "un"}[nucleus]; label = v + "n"
        cell = rows.get(nucleus, {}).get(oc)
        used = (nucleus, oc, cell)
        ch = pick(cell, notes, f"{show(on)}{label}")
        res.append(ch); trace.append(f"{show(on)}{label}→{ch}")
        if extra:
            res.append(extra); trace.append(f"n→{extra}")
        # 音節尾輔音
        while coda:
            c = coda.pop(0)
            if mode == "place" and coda and coda[0] == "n" and col(c) in rows.get("n", {}) and (len(coda) == 1 or coda[1] not in VOWELS):
                coda.pop(0)
                ch = pick(rows["n"][col(c)], notes, f"{show(c)}n")
                res.append(ch); trace.append(f"{show(c)}n→{ch}（GB/T 5.3.4）")
                continue
            ch = pick(zero.get(col(c)), notes, f"{show(c)}（音節尾）")
            res.append(ch); trace.append(f"{show(c)}→{ch}")
        if final_glottal:
            ch = pick(zero.get(final_glottal), notes, f"{show(final_glottal)}（詞尾）")
            res.append(ch); trace.append(f"{show(final_glottal)}→{ch}（詞尾，前為短元音或輔音）")
    # 地名單音節詞用兩字（GB/T 5.1.9）
    if mode == "place" and len(syl) == 1 and not pre and len(res) == 1:
        nucleus, oc, cell = used
        if cell and cell.get("mono"):
            res = [cell["mono"]]; notes.append(f"單音節詞用兩字：{cell['mono']}（GB/T 5.1.9）")
        elif nucleus in ("ay", "aw"):
            res = [pick(rows["ā"].get(oc), [], ""), "伊" if nucleus == "ay" else "乌"]
            notes.append(f"單音節詞用兩字：拆成 {''.join(res)}（GB/T 5.1.9）")
        else:
            notes.append("單音節詞，GB/T 5.1.9 要求用兩個漢字，請自行處理")
    s = "".join(res)
    if s.startswith("夫"):
        s = "弗" + s[1:]
    sy_txt = "-".join("".join(show(x) for x in ([o] if o else []) + [v] + c) for o, v, c in syl)
    if pre:
        sy_txt = "".join(show(x) for x in pre) + "-" + sy_txt
    return s, sy_txt, trace


def _key(word):
    s = unicodedata.normalize("NFD", word.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("ʿ", "`").replace("ʾ", "'").replace("’", "'").replace("‘", "`").replace("ʻ", "`").replace("ʼ", "'")


def _plain(word):
    return re.sub(r"[`'ʹ|]", "", _key(word))


def tokens(text):
    return [p for p in re.split(r"[\s\-‐–]+", text.strip()) if p]


def translit_word(word, mode, final=False):
    notes = []
    ph = arabic_phones(word, notes) if is_arabic(word) else latin_phones(word, notes)
    # 名稱最後一詞的 -at／-et（拉丁轉寫的 ة）：後面沒有他詞，不發音，省譯（GB/T 5.3.2.1；Baḥrat→拜赫拉）
    if final and not is_arabic(word) and len(ph) >= 3 and ph[-1] == "t" and ph[-2] == "a" and ph[-3] not in VOWELS:
        ph = ph[:-1]
        notes.append("名稱末詞的 -at（ة）不譯；若是真正的 t 請用阿拉伯字母輸入")
    s, sy, tr = render_word(ph, mode, notes)
    return s, sy, tr, notes, ph


def translit(text, mode):
    """回傳 (譯名, info)。info＝[(原詞, 音節切分, 每字來源, 註記)]。"""
    toks = tokens(text)
    parts, info = [], []       # parts: [譯名, 是否與前一詞連寫]
    i = 0
    while i < len(toks):
        w = toks[i]
        k, pl = _key(w), _plain(w)
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        # 定冠詞
        if nxt is not None and not is_arabic(w):
            if pl in ARTICLES and not re.search(r"[āâá]", unicodedata.normalize("NFC", w.lower())):
                info.append((w, "", ["定冠詞省譯"], [])); i += 1; continue
            m = re.fullmatch(r"[ae](sh|th|dh|[tdrzsnṭṣḍẓ])", unicodedata.normalize("NFC", w.lower()))
            if m:
                nph = latin_phones(nxt, [])
                first = next((p for p in nph if p != "|"), "")
                cons = {"sh": "sh", "th": "th", "dh": "dh"}.get(m.group(1), m.group(1))
                if first == cons or col(first) == col(cons) and m.group(1) in "tdsz":
                    info.append((w, "", ["同化的定冠詞省譯"], [])); i += 1; continue
        # Āl 家族
        if pl == "al" and re.search(r"[āâá]", unicodedata.normalize("NFC", w.lower())) and nxt is not None:
            parts.append(["阿勒", False]); info.append((w, "", ["Āl（家族）→阿勒，與後一詞連寫"], []))
            i += 1
            s, sy, tr, nt, _ = translit_word(nxt, mode)
            parts.append([s, True]); info.append((nxt, sy, tr, nt)); i += 1; continue
        # ʿAbd al- / ʿAbd Allāh
        if pl == "abd" and nxt is not None:
            np_ = _plain(nxt)
            if np_ in ("allah", "allāh"):
                parts.append(["阿卜杜拉", False]); info.append((w + " " + nxt, "", ["ʿAbd Allāh→阿卜杜拉（附錄B慣例）"], [])); i += 2; continue
            if np_ in ARTICLES or re.fullmatch(r"[ae](sh|th|dh|[tdrzsn])", np_):
                parts.append(["阿卜杜勒", False]); info.append((w + " " + nxt, "", ["ʿAbd al-→阿卜杜勒（附錄B慣例）"], [])); i += 2
                if i < len(toks):
                    s, sy, tr, nt, _ = translit_word(toks[i], mode)
                    # 人名：阿卜杜勒-X（中維 阿迪勒·阿卜杜勒-迈赫迪）；地名：阿卜杜勒·X（GB/T 表2 阿卜杜勒·蒙伊姆）
                    parts.append([s, "-" if mode == "person" else "·"]); info.append((toks[i], sy, tr, nt)); i += 1
                continue
        m = re.fullmatch(r"abd[aeuo]l([a-z].+)", pl)
        if m and not is_arabic(w):
            rest = w[len(w) - len(m.group(1)):]
            s, sy, tr, nt, _ = translit_word(rest, mode)
            parts.append(["阿卜杜勒" + s, False]); info.append((w, "abdul-" + sy, ["Abdul-→阿卜杜勒（附錄B慣例）"] + tr, nt)); i += 1; continue
        if pl in PARTICLE or k in PARTICLE:
            zh = PARTICLE.get(pl, PARTICLE.get(k))
            parts.append([zh, False]); info.append((w, "", [f"{w}→{zh}（附錄B／新華社慣例）"], [])); i += 1; continue
        m = re.fullmatch(r"(ab[uū]|abou)['`](.+)", unicodedata.normalize("NFC", k))
        if m and not is_arabic(w):
            rest = w[len(w) - len(m.group(2)) - 1:]
            s, sy, tr, nt, _ = translit_word(rest, mode, final=nxt is None)
            parts.append(["阿布" + s, False]); info.append((w, "abū-" + sy, ["Abū→阿布（附錄B慣例）"] + tr, nt)); i += 1; continue
        s, sy, tr, nt, _ = translit_word(w, mode, final=nxt is None)
        parts.append([s, False]); info.append((w, sy, tr, nt)); i += 1
    # 組合
    if mode == "person":
        out = ""
        for j, (s, join) in enumerate(parts):
            if isinstance(join, str):
                out += join + s
            else:
                out += s if (j == 0 or join) else "·" + s
        return out, info
    words = []
    for s, join in parts:
        if join and words:
            words[-1] += (join if isinstance(join, str) else "") + s
        else:
            words.append(s)
    out = "".join(words)
    if len(words) >= 2 and len(out) >= 8:
        out = words[0] + "-" + "".join(words[1:])
    # 地名開頭、結尾的避諱字（表注5）
    if out.startswith("南"):
        out = "楠" + out[1:]
    if out.startswith("西"):
        out = "锡" + out[1:]
    if out.endswith("海"):
        out = out[:-1] + "亥"
    return out, info


def generic_variant(text):
    toks = tokens(text)
    while toks and _plain(toks[0]) in ARTICLES and len(toks) > 1:
        toks = toks[1:]
    if len(toks) < 2:
        return None
    k = _key(toks[0])
    zh = GENERIC.get(k) or GENERIC.get(_plain(toks[0]))
    if not zh:
        return None
    return " ".join(toks[1:]), zh


def person_place_variant(text):
    """人名用地名表譯一次（中維表注：常見人名的實際譯法反而常合地名表，如 Ḥusayn 侯赛因）；與人名表結果相同時回傳 None。"""
    a, _ = translit(text, "person")
    b, _ = _translit_person_with(text, "place")
    return b if b != a else None


def _translit_person_with(text, table_mode):
    """照人名的切分與「·」，但查 table_mode 的表（不套地名專用的開頭／結尾避諱字與 8 字加「-」規則）。"""
    global TABLE
    saved = TABLE["person"]
    try:
        TABLE["person"] = TABLE[table_mode]
        return translit(text, "person")
    finally:
        TABLE["person"] = saved


def run_tests(path):
    """跑 ar_translit_test.tsv：模式<Tab>原文<Tab>預期譯名<Tab>出處；預期與主譯名或通名意譯版本相符即算通過。"""
    ok, bad, alt_ok = 0, [], []
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        mode, src, exp, origin = (line.rstrip("\n").split("\t") + [""] * 4)[:4]
        mode = "person" if mode.strip() in ("person", "-p", "p") else "place"
        got, _ = translit(src, mode)
        cands = [S(got)]
        if mode == "place" and generic_variant(src):
            g = generic_variant(src)
            cands.append(S(translit(g[0], mode)[0] + g[1]))
        if mode == "person":
            pv = person_place_variant(src)
            if pv:
                cands.append(S(pv))
        if S(exp) == cands[0]:
            ok += 1
        elif S(exp) in cands:
            ok += 1; alt_ok.append((mode, src, exp))
        else:
            bad.append((mode, src, exp, " ／ ".join(cands), origin))
    print(f"通過 {ok}／{ok + len(bad)}（其中 {len(alt_ok)} 筆靠另列版本：通名意譯或人名的地名表版本）")
    for a in alt_ok:
        print("另列版本通過：", "	".join(a))
    for b in bad:
        print("不通過：", "\t".join(b))


def main(argv):
    if argv[:1] == ["--test"]:
        run_tests(argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ar_translit_test.tsv"))
        return
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
        try:
            zh, info = translit(w, mode)
        except ValueError as e:
            print(f"{w}\t（無法譯寫：{e}）")
            continue
        line = f"{w}\t{S(zh)}"
        if mode == "place":
            g = generic_variant(w)
            if g:
                try:
                    stem_zh, _ = translit(g[0], mode)
                    line += f"\t通名意譯：{S(stem_zh + g[1])}"
                except ValueError:
                    pass
        if mode == "person":
            pv = person_place_variant(w)
            if pv:
                line += f"	地名表版本：{S(pv)}"
        print(line)
        if verbose:
            for part, sy, tr, nt in info:
                print(f"    {part}：{sy}｜{S('，'.join(tr))}")
                for x in dict.fromkeys(nt):
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
