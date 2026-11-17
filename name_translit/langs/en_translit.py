"""英語音譯工具：輸入英語地名或人名（拼寫，或拼寫加國際音標），依中維「外語譯音表/英語」吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 en_translit_table.json（由 en_translit_build_table.py 從中維原始碼重建）：
  人名表＝新華社《世界人名翻译大辞典》；地名表＝GB/T 17693.1-2008《外语地名汉字译写导则 英语》；
  另收 GB/T 17693.1 附錄 C「英語地名常用構詞成分譯寫表」237 條（-ton 顿、-field 菲尔德、-ford 福德…，自國標 PDF 轉錄）。
  兩表都是中國大陸標準，譯名一律以繁體字輸出；倫敦、華盛頓、牛頓這類已有慣用譯名的，以慣用譯名為準，不必跑工具。
  譯音表只適用於《世界人名翻譯大辭典》《英語姓名譯名手冊》《世界地名譯名詞典》沒有收錄的名字；查得到辭典就以辭典為準。

輸入格式（英語表是依「讀音」排的，拼寫推不出可靠讀音，所以接受國際音標）：
  1. 拼寫加音標（最準）：  Avoca/əˈvəʊkə/   或  "Avoca [əˈvəʊkə]"   或  Avoca=əˈvəʊkə
     音標照英文維基、牛津、朗文等辭典寫法（英式、美式都可，ɚ、ɝ、捲舌 r 會自動轉成非捲舌讀法）；
     工具會把音標逐一對到拼寫字母，以便套用表上依拼寫訂的規則（a 在詞首詞尾、s 一律按「斯」、-ia、詞尾 r…）
     與構詞成分表。多詞地名每個詞各自附音標：  "Lake Talquin/tælˈkwɪn/"
  2. 只給音標：  -i 參數，或整個引數寫成 /…/、[…]，或含 ə ɪ ʊ ɒ θ ʃ ŋ ˈ 等音標專用符號時自動判斷。
     沒有拼寫就無法套用依拼寫訂的規則與構詞成分表（-v 會註明）。
  3. 只給拼寫：  依常見英語拼寫規則推測讀音（不發音的 e、magic e、gh、kn、-tion、雙寫輔音…），
     非重讀元音一律「形譯」（照字母譯），結果只能當參考；拿不準時請補音標。

用法：
  python -X utf8 en_translit.py Glenfield Lisburn "Kineton/ˈkaɪntən/"     （預設地名表）
  python -X utf8 en_translit.py -p "Gordon/ˈɡɔːdən/ Brown/braʊn/" Jasper     （-p 人名表，名與姓間加「·」）
  python -X utf8 en_translit.py -i "ˈpaɪəˈnɪə"                               （-i 輸入全部當音標）
  python -X utf8 en_translit.py --test                                        （跑 en_translit_test.tsv）
  注意：Git Bash 會把「/」開頭的引數當成路徑改寫（/ˈpaɪə/ 變成 C:/Program Files/Git/…），
  只給音標時請用 -i 或 […]；「拼寫/音標/」不以 / 開頭，不受影響。
  python -X utf8 en_translit.py -v Hampton                                    （-v 列出切分與每字來源）
  python -X utf8 en_translit.py -F -p Clara                                   （-F 女名用字：娜、瑪、莉、琳、絲…）
  python -X utf8 en_translit.py -f 名單.txt                                   （每行一個）
  模組：from en_translit import translit, S；translit(text, mode) 回傳 (譯名（簡體）, info)，mode＝"place"／"person"。

已處理的表上規則：
  - 音節：輔音＋元音合成一格；元音後的 n／ŋ 併入鼻音列（æn→an 列、ɑːn ɒn aʊn ʌŋ→ang 列、ən ɜːn→en 列、ɪn→in 列、
    ɪŋ→ing 列、uːn oʊn→un 列、ʊŋ→ung 列）；aɪn、eɪn、juːn 不併，按艾／埃／尤行加「恩」（Kineton 凱恩頓）。
  - 輔音＋j＋uː→ju 列（紐、柳）；輔音＋j＋其他元音→i 列（尼、利），jən→in 列。
  - [tr][dr] 按特／德加 r 行；m 在 b、p 前按 n（b 不發音時照 m：Lamb 拉姆）；
    成音節 l、m、n 與前面的輔音之間加 ə（Ouzel 烏澤爾、Listen 利森）；ɔɪ 按奧行加「伊」（Floyd 弗洛伊德）。
  - 詞尾 r／re 讀 ə（ɪə eə ʊə aɪə 的 ə）時譯「爾」，eə 按埃行加爾（Clare 克萊爾、Pioneer 派厄尼爾）；
    單音節以 r 結尾加「爾」（Parr 帕爾）；但輔音後的 -er 讀 ə 照 er 列（Jenner 詹納、Jasper 賈斯珀）。
  - 字母 s 不論讀 s 或 z 都按「斯」列（Flores 弗洛里斯、Lisburn 利斯本）；人名表的「濁輔音清化…按形譯」同樣處理。
  - 詞尾 -ia 的 a 譯「亞」（Virginia 弗吉尼亞、Amelia 阿米利亞）。
  - 地名表 4.3.1.2–3：字母 a 在首、末音節讀 ə 按 a 列（Avoca 阿沃卡）；e、o 在首音節讀 ə 按 e、o 列（Perutz 佩魯茨、
    Possession 波塞申）；o 在 go ko mo no 讀 ə 按戈科莫諾；詞首 o 按「奧」不按「歐」（Otis 奧蒂斯）。
    人名表只做「a 在詞首讀 ə 按 a 列」，另依新華社慣例把詞尾 -a 的 ə 按 a 列（Augusta 奧古斯塔）。
  - 字母組合 ai、ay 在詞首讀 e／eɪ 按「艾」行（Aid 艾德、Ayr 艾爾）。
  - 單音節地名的雙元音 eɪ、aɪ 在詞尾時拆成兩個單元音（Fay 費伊）。
  - th 在輔音前或詞尾讀 θ 譯「思」（頁面說明的實務慣例）。
  - 弗用於譯名詞首、夫用於詞中與詞尾（只限輔音單獨的 f v w；er 列的弗照表）。
  - 地名：東／南／西在詞首改棟／楠／錫，海在詞尾改亥（GB 的望文生義規則）。
  - 構詞成分（GB 附錄 C）：詞首、詞尾符合時整段照表（-ton 頓、-field 菲爾德、bow- 鮑…），人名也套用（新華社慣例大致相同，-son 例外見限制）。
  - 地名通名意譯、方位與大小新舊形容詞意譯（GB 4.1.9、4.2.1）：Lake Talquin 塔爾昆湖、East Linton 東林頓；
    但詞中只剩通名時形容詞照音譯（Great Island 格雷特島）。詞首冠詞 The 省譯；and、with 譯成「-」；St／Saint 譯「聖」。
  - Mc／Mac 加大寫字母開頭的姓譯「麥克」（McDonald 麥克唐納）；人名的單字母縮寫（J.）省譯。
  - 同一格有兩個字時取第一個；女名用字只在 -F 時套用；-v 會列出另一個。

限制（做不到或沒做）：
  - 只給拼寫時，讀音是猜的：重音、元音弱化、不發音字母都可能猜錯（Amelia 會猜成梅而非米）；請盡量附音標。
  - 「元音在非重音節時一般形譯」（人名表）新華社實際並不一致（Robert 羅伯特而非羅貝特），本工具只做上列幾條。
  - 新華社常用姓名後綴（-son 譯遜或森、-ton 頓）各有慣例，工具一律照 GB 構詞成分表（-son 森），Jackson 會得傑克森而非傑克遜。
  - 介詞短語意譯（Shoreham-by-Sea 濱海肖勒姆）、以人名命名的地名加「·」、8 字以上加連接號、連詞 or 括注等 GB 4.1 的整名規則沒做。
  - 拼寫與音標對不起來時（音標漏寫或拼錯），只按音標譯，依拼寫的規則略過，-v 會註明。
  - 辭典慣用字無法由表推出：Martin 表上得「馬廷」，新華社作「馬丁」；Augusta 的重讀 ʌ 新華社照字母 u 譯「古」，
    表上 ʌ 屬 a 列得「加」；Jones 瓊斯、Kevin 凱文、Daniel 丹尼爾同理。這類名字請以辭典為準。
  - -F 女名用字只套在人名的第一個詞（名字），姓不套；構詞成分的字只換利、里、尼、納、林、斯六個。
  - 只給拼寫時 th 一律當 θ（Theresa 會得塞蕾莎，新華社作特蕾莎），h、gh、ough 等也只按最常見讀法。
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
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "en_translit_table.json"), encoding="utf-8"))
AFFIX = TABLE["affix"]

# ---------- 音素 ----------
VSET = {"AA", "AE", "UH", "E", "EI", "ER", "SC", "I", "O", "OU", "U", "AI", "AU", "OI"}
ROW = {"AA": "a", "AE": "a", "UH": "a", "E": "e", "EI": "ei", "ER": "er", "SC": "er", "I": "i",
       "O": "o", "OU": "ou", "U": "u", "AI": "ai", "AU": "au"}
NAS = {("AE", "n"): "an", ("AE", "ŋ"): "an", ("UH", "n"): "an",
       ("AA", "n"): "ang", ("AA", "ŋ"): "ang", ("UH", "ŋ"): "ang", ("O", "n"): "ang", ("O", "ŋ"): "ang", ("AU", "n"): "ang",
       ("E", "n"): "en", ("E", "ŋ"): "en", ("ER", "n"): "en", ("ER", "ŋ"): "en", ("SC", "n"): "en", ("SC", "ŋ"): "en",
       ("I", "n"): "in", ("I", "ŋ"): "ing", ("U", "n"): "un", ("OU", "n"): "un", ("U", "ŋ"): "ung", ("OU", "ŋ"): "ung"}
COL = {"b": "b", "p": "p", "d": "d", "t": "t", "g": "g", "k": "k", "v": "v", "w": "w", "f": "f", "z": "z", "dz": "z",
       "ts": "ts", "s": "s", "ð": "s", "θ": "s", "ʒ": "ʒ", "ʃ": "ʃ", "ʤ": "ʤ", "ʧ": "ʧ", "h": "h", "m": "m", "n": "n",
       "ŋ": "n", "l": "l", "r": "r", "j": "j", "gw": "gw", "kw": "kw", "hw": "hw"}
OBSTR = set("bpdtgkvfzsʒʃʤʧ") | {"ð", "θ", "ts", "dz"}
FEMALE = set("婭娅瑪玛娜莉麗丽琳妮珍絲丝莎黛蕾蘿萝娃")

# 音標符號 → 記號（長的先比）
IPA_SEQ = [
    ("aɪə", ["AI", "SC"]), ("aʊə", ["AU", "SC"]),
    ("eɪ", ["EI"]), ("ei", ["EI"]), ("aɪ", ["AI"]), ("ai", ["AI"]), ("aʊ", ["AU"]), ("au", ["AU"]),
    ("ɔɪ", ["OI"]), ("ɔi", ["OI"]), ("oɪ", ["OI"]), ("oi", ["OI"]),
    ("oʊ", ["OU"]), ("əʊ", ["OU"]), ("əu", ["OU"]), ("ou", ["OU"]), ("oː", ["OU"]),
    ("ɪə", ["I", "SC"]), ("iə", ["I", "SC"]), ("eə", ["E", "SC"]), ("eː", ["E", "SC"]),
    ("ʊə", ["U", "SC"]), ("uə", ["U", "SC"]), ("ɔə", ["O", "SC"]),
    ("ɑː", ["AA"]), ("aː", ["AA"]), ("ɑ", ["AA"]), ("æ", ["AE"]), ("a", ["AE"]), ("ʌ", ["UH"]),
    ("ɜː", ["ER"]), ("əː", ["ER"]), ("ɜ", ["ER"]), ("ə", ["SC"]), ("e", ["E"]),
    ("iː", ["I"]), ("i", ["I"]), ("ɪ", ["I"]), ("ɔː", ["O"]), ("ɒ", ["O"]), ("ɔ", ["O"]), ("o", ["OU"]),
    ("uː", ["U"]), ("u", ["U"]), ("ʊ", ["U"]),
    ("ʤ", ["ʤ"]), ("ʧ", ["ʧ"]), ("ŋ", ["ŋ"]), ("θ", ["θ"]), ("ð", ["ð"]), ("ʃ", ["ʃ"]), ("ʒ", ["ʒ"]),
] + [(c, [c]) for c in "bpdtgkvwfzshmnlrj"]
IPA_CHARS = set("ˈˌəɪʊɒɔɑæʌɜθðʃʒŋɹːɛɚɝʤʧɡɫʍɐᵻ")


def is_ipa(s):
    s = s.strip()
    return (s[:1] in "/[" and s[-1:] in "/]") or any(c in IPA_CHARS for c in s)


def parse_ipa(s):
    s = s.strip().strip("/[]")
    for a, b in (("d͡ʒ", "ʤ"), ("t͡ʃ", "ʧ"), ("dʒ", "ʤ"), ("tʃ", "ʧ"), ("ɡ", "g"), ("ɹ", "r"), ("ɾ", "t"), ("ɻ", "r"),
                 ("ʁ", "r"), ("ɫ", "l"), ("ʍ", "hw"), ("x", "k"), ("ɚ", "ər"), ("ɝ", "ɜːr"), ("ɛ", "e"), ("ɐ", "ʌ"),
                 ("ɨ", "ɪ"), ("ᵻ", "ɪ"), ("ᵿ", "ʊ"), ("ʉ", "uː"), ("ɵ", "ə"), (":", "ː"), ("ʔ", "t"), ("y", "j")):
        s = s.replace(a, b)
    # 成音節符號：在前面加 ə
    s = re.sub(r"([lmn])̩", r"ə\1", s)
    s = s.replace("'", "ˈ")
    s = re.sub(r"[.‿()\s͡ʰ̩̃̚-]", "", s)
    out, i, stress = [], 0, False
    while i < len(s):
        if s[i] in "ˈˌ":
            stress = True; i += 1; continue
        for pat, toks in IPA_SEQ:
            if s.startswith(pat, i):
                for t in toks:
                    ph = {"p": t, "g": None, "li": None, "raw": pat}
                    if t in VSET and stress:
                        ph["st"] = True; stress = False
                    out.append(ph)
                i += len(pat)
                break
        else:
            i += 1  # 不認得的符號（ː 殘餘等）略過
    # 元音後的 ə 接 r＋元音時只是雙元音的尾巴，不另譯（Clara ˈklɛərə 克萊拉）
    out = [ph for k, ph in enumerate(out)
           if not (ph["p"] == "SC" and k > 0 and out[k - 1]["p"] in VSET and k + 2 < len(out)
                   and out[k + 1]["p"] == "r" and out[k + 2]["p"] in VSET)]
    # 捲舌 r：元音後、不接元音的 r 拿掉（轉成英式非捲舌讀法）；詞尾 r 前是 ə 且 ə 前是輔音的也拿掉（Taylor 泰勒）
    res = []
    for k, ph in enumerate(out):
        if ph["p"] == "r" and k > 0 and out[k - 1]["p"] in VSET:
            nxt = out[k + 1]["p"] if k + 1 < len(out) else None
            if nxt is None:
                if out[k - 1]["p"] == "SC":
                    continue  # -ər：輔音後照 er 列（Taylor 泰勒）；元音後的 ə 由詞尾 r 規則譯爾（Blair 布萊爾）
                res.append(ph); continue
            if nxt not in VSET and nxt != "j":
                continue
        res.append(ph)
    return res


# ---------- 拼寫切分與對齊 ----------
VDIG = ["eau", "ough", "augh", "igh", "ai", "ay", "au", "aw", "ea", "ee", "ei", "ey", "eu", "ew", "ie",
        "oa", "oe", "oi", "oy", "oo", "ou", "ow", "ue", "ui"]
CDIG = ["tch", "sch", "ch", "ck", "dg", "gh", "ph", "sh", "th", "wh", "qu", "ng"]
CCOMP = {"b": "b", "c": "k s ʃ ʧ", "d": "d ʤ t", "f": "f v", "g": "g ʤ ʒ", "h": "h", "j": "ʤ j h ʒ", "k": "k",
         "l": "l", "m": "m", "n": "n ŋ", "p": "p", "q": "k", "r": "r", "s": "s z ʃ ʒ", "t": "t ʃ ʧ θ ð d",
         "v": "v f", "w": "w v", "x": "k s g z", "y": "j", "z": "z s", "tch": "ʧ", "sch": "s k ʃ", "ch": "ʧ k ʃ ʤ",
         "ck": "k", "dg": "ʤ", "gh": "g f", "ph": "f v p", "sh": "ʃ", "th": "θ ð t", "wh": "w h", "qu": "k w",
         "ng": "ŋ n g ʤ"}
CCOMP = {k: set(v.split()) for k, v in CCOMP.items()}


def graphemes(w):
    out, i = [], 0
    while i < len(w):
        for d in VDIG:
            if w.startswith(d, i):
                out.append((d, i, "V")); i += len(d); break
        else:
            for d in CDIG:
                if w.startswith(d, i):
                    out.append((d, i, "C")); i += len(d); break
            else:
                c = w[i]
                j = i + 1
                if c not in "aeiouy":
                    while j < len(w) and w[j] == c:
                        j += 1
                out.append((w[i:j], i, "V" if c in "aeiou" else ("Y" if c == "y" else "C")))
                i = j
    return out


def gcost(g, cls, seq):
    if not seq:
        if cls == "C" and g[0] == "r":
            return 0.3
        return 0.5 if g == "e" else 1.0
    cost = 0.4 * (len(seq) - 1)
    base = g[0] if len(g) > 1 and g[0] == g[-1] and cls == "C" else g
    for p in seq:
        if p in VSET:
            cost += 0 if cls in "VY" else (1.5 if g[0] in "lr" else 3)
        elif cls in "VY":
            cost += 0 if p in ("j", "w") else 3
        else:
            ok = CCOMP.get(base, {base})
            cost += 0 if p in ok else 2
    return cost


def align(word, P):
    """把音素對到拼寫字位；回傳 True／False（對不起來）。"""
    G = graphemes(word)
    n, m = len(G), len(P)
    INF = 1e9
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(n):
        g, li, cls = G[i]
        for j in range(m + 1):
            if dp[i][j] >= INF:
                continue
            for k in range(0, 4):
                if j + k > m:
                    break
                c = dp[i][j] + gcost(g, cls, [P[x]["p"] for x in range(j, j + k)])
                if c < dp[i + 1][j + k]:
                    dp[i + 1][j + k] = c; bk[i + 1][j + k] = k
    if dp[n][m] >= INF or dp[n][m] > 2.5 + 0.6 * n:
        return False
    j = m
    for i in range(n, 0, -1):
        k = bk[i][j]
        for x in range(j - k, j):
            P[x]["g"], P[x]["li"] = G[i - 1][0], G[i - 1][1]
        j -= k
    return True


# ---------- 只有拼寫時推測讀音 ----------
def g2p(w):
    n = len(w)
    V = "aeiouy"
    out = []
    add = lambda p, g, li: out.append({"p": p, "g": g, "li": li, "raw": None})
    nvow = len(re.findall(r"[aeiouy]+", w))
    end, magic, sylle = n, None, False
    if n > 4 and w.endswith("es") and w[-3] not in V and w[-4] in V and w[-5] not in "aeiou":
        # 複數、屬格的 -es 前面是 magic e（Jones 瓊斯、Yates 耶茨）
        g = g2p(w[:-1])
        g.append({"p": "s", "g": "s", "li": n - 1, "raw": None})
        return g
    if n > 2 and w[-1] == "e" and w[-2] not in V and re.search(r"[aeiouy]", w[:-2]):
        end = n - 1
        if w[-2] == "l" and w[-3] not in V + "l":
            sylle = True
        elif w[-3] in V and (n < 4 or w[-4] not in "aeiou"):
            magic = n - 3
        nvow -= 1
    i = 0

    def rctl(k):  # 元音後接 r，r 後是輔音或詞尾
        if k < end and w[k] == "r":
            if k + 1 >= end:
                return "end"
            if w[k + 1] not in V and w[k + 1] != "r":
                return "cons"
            if w[k + 1] == "r" and (k + 2 >= end or w[k + 2] not in V):
                return "cons"
        return None

    while i < end:
        c = w[i]
        rest = w[i:end]
        if c in V and not (c == "y" and i == 0 and i + 1 < end and w[i + 1] in V):
            dg = next((d for d in VDIG if rest.startswith(d)), None)
            if dg:
                j = i + len(dg)
                fin = j >= end
                p = {"eau": ["OU"], "ough": ["AU"], "augh": ["O"], "igh": ["AI"], "ai": ["EI"], "ay": ["EI"],
                     "au": ["O"], "aw": ["O"], "ea": ["I"], "ee": ["I"], "ei": ["EI"], "ey": ["EI"],
                     "eu": ["j", "U"], "ew": ["j", "U"], "ie": ["I"], "oa": ["OU"], "oe": ["OU"], "oi": ["OI"],
                     "oy": ["OI"], "oo": ["U"], "ou": ["AU"], "ow": ["AU"], "ue": ["U"], "ui": ["U"]}[dg]
                if dg in ("ai", "ay") and i == 0:
                    p = ["AI"]
                if dg == "ea" and re.match(r"(gr|br|st)eak?t?$", w[max(0, i - 2):end]):
                    p = ["EI"]  # great break steak
                if dg == "ey" and fin and nvow > 1:
                    p = ["I"]
                if dg == "ow" and fin:
                    p = ["OU"]
                if dg == "ou" and w[j:j + 1] == "s" and j + 1 >= end and nvow > 1:
                    p = ["SC"]
                if dg in ("eu", "ew") and out and out[-1]["p"] in ("r", "l", "ʤ", "ʃ", "ʧ", "s", "z", "j"):
                    p = ["U"]
                for x in p:
                    add(x, dg, i)
                rc = rctl(j)
                if rc == "cons":
                    j += 1
                    while j < end and w[j] == "r":
                        j += 1
                i = j
                continue
            rc = rctl(i + 1)
            prev = w[i - 1] if i else ""
            nx = w[i + 1:i + 2] if i + 1 < end else ""
            openv = i + 2 < end and w[i + 1] not in V and w[i + 2] in V and w[i + 1] not in "rx"
            if rc:
                fin = rc == "end"
                if c == "a":
                    p = "AE" if (fin and nvow > 1) else ("O" if prev == "w" else "AA")
                elif c == "o":
                    p = "SC" if (fin and nvow > 1) else ("ER" if prev == "w" else "O")
                else:
                    p = "SC" if (fin and nvow > 1) else "ER"
                add(p, c, i)
                j = i + 1
                if fin and nvow > 1:
                    i = end; continue  # 多音節詞尾 -er -ar -or 讀弱元音，不譯 r
                if rc == "cons":
                    while j < end and w[j] == "r":
                        j += 1
                i = j
                continue
            if c == "a":
                if rest.startswith("all") or rest.startswith("alk") or rest.startswith("alm"):
                    add("O", c, i)
                    if rest.startswith("alk") or rest.startswith("alm"):
                        i += 2; continue
                elif i == magic:
                    add("EI", c, i)
                elif prev == "w" or w[max(0, i - 2):i] == "qu":
                    add("O", c, i)
                else:
                    add("AE", c, i)
            elif c == "e":
                if i == magic:
                    add("I", c, i)
                elif i == end - 1 and nvow == 1 and i > 0:
                    add("I", c, i)
                else:
                    add("E", c, i)
            elif c in "iy":
                if i == magic:
                    add("AI", c, i)
                elif c == "y" and i == end - 1:
                    add("I", c, i)
                else:
                    add("I", c, i)
            elif c == "o":
                if i == magic or i == end - 1:
                    add("OU", c, i)
                elif rest.startswith("olk") or rest.startswith("olm"):
                    add("OU", c, i); i += 2; continue
                elif rest.startswith("old") or rest.startswith("olt"):
                    add("OU", c, i)
                else:
                    add("O", c, i)
            elif c == "u":
                on = out[-1]["p"] if out else ""
                if i == magic or openv:
                    if on in ("", "r", "l", "j", "ʤ", "ʃ", "ʧ", "s", "z", "d", "t", "θ"):
                        add("U", c, i)
                    else:
                        add("j", c, i); add("U", c, i)
                elif prev in "bpf" and prev and (rest.startswith("ul") or rest.startswith("ush") or rest.startswith("ut")):
                    add("U", c, i)
                else:
                    add("UH", c, i)
            i += 1
            continue
        # 輔音
        if c == "y":
            add("j", "y", i); i += 1; continue
        if rest.startswith(("tio", "sio", "cia", "tia", "cio", "sia")) and i > 0:
            add("ʃ", rest[:2], i); i += 2
            if rest[2] in "o" or (rest[2] == "a" and i + 1 < end):
                add("SC", rest[2], i); i += 1
            continue
        if rest.startswith("ture") or (rest.startswith("tur") and i + 3 == end):
            add("ʧ", "t", i); add("SC", "u", i + 1); i = end; continue
        if rest.startswith("tch"):
            add("ʧ", "tch", i); i += 3; continue
        if rest.startswith("sch"):
            add("ʃ", "sch", i); i += 3; continue
        if rest.startswith("chr"):
            add("k", "ch", i); i += 2; continue
        if rest.startswith("ch"):
            add("ʧ", "ch", i); i += 2; continue
        if rest.startswith("ck"):
            add("k", "ck", i); i += 2; continue
        if rest.startswith("dg"):
            add("ʤ", "dg", i); i += 2 + (1 if w[i + 2:i + 3] == "e" and i + 3 >= end else 0); continue
        if rest.startswith("gh"):
            if i == 0:
                add("g", "gh", i)
            i += 2; continue
        if rest.startswith("ph"):
            add("f", "ph", i); i += 2; continue
        if rest.startswith("sh"):
            add("ʃ", "sh", i); i += 2; continue
        if rest.startswith("th"):
            add("θ", "th", i); i += 2; continue
        if rest.startswith("wh"):
            add("w", "wh", i); i += 2; continue
        if rest.startswith("qu"):
            add("k", "qu", i); add("w", "qu", i); i += 2; continue
        if i == 0 and rest[:2] in ("kn", "wr", "gn", "ps"):
            i += 1; continue
        if rest.startswith("gn") and i + 2 >= end:
            add("n", "gn", i); i += 2; continue
        if rest.startswith("mb") and i + 2 >= end:
            add("m", "mb", i); i += 2; continue
        if rest.startswith("ng"):
            after = w[i + 2:i + 3] if i + 2 < end else ""
            if after and after in "eiy":
                add("n", "n", i); add("ʤ", "g", i + 1)
            elif after and after in "aou":
                add("ŋ", "n", i); add("g", "g", i + 1)
            else:
                add("ŋ", "ng", i)
            i += 2; continue
        if c == "n" and w[i + 1:i + 2] in ("k", "c", "q") and i + 1 < end:
            add("ŋ", "n", i); i += 1; continue
        j = i + 1
        while j < end and w[j] == c:
            j += 1
        g = w[i:j]
        nxt = w[j:j + 1] if j < end else ""
        if c == "c":
            if g == "cc" and nxt and nxt in "eiy":
                add("k", "cc", i); add("s", "cc", i)
            else:
                add("s" if nxt and nxt in "eiy" else "k", g, i)
        elif c == "g":
            add("ʤ" if (nxt and nxt in "eiy" and g == "g") or (nxt == "" and end < n) else "g", g, i)
        elif c == "x":
            if i == 0:
                add("z", g, i)
            else:
                add("k", g, i); add("s", g, i)
        elif c == "j":
            add("ʤ", g, i)
        elif c == "h":
            if i > 0 and j >= end:
                pass  # 詞尾的 h 不發音
            else:
                add("h", g, i)
        elif c == "w":
            add("w", g, i)
        elif c in "bdfklmnprstvz":
            if c == "r" and i > 0 and w[i - 1] in V and (not nxt or nxt not in V):
                if j >= end:
                    add("r", g, i)  # 單音節詞尾 r（Parr）
            else:
                add(c, g, i)
        i = j
    if sylle:
        add("SC", "le", n - 2); add("l", "le", n - 2)
    return out


# ---------- 合成譯寫單位 ----------
def prep(P):
    """合併 ts dz gw kw hw、m 在 b p 前作 n、成音節 l m n 加 ə。"""
    out = []
    i = 0
    while i < len(P):
        a = P[i]
        b = P[i + 1] if i + 1 < len(P) else None
        c = P[i + 2] if i + 2 < len(P) else None
        if b and (a["p"], b["p"]) in (("t", "s"), ("d", "z")) and (c is None or c["p"] not in VSET) \
                and (a["g"] is None or a["g"] != b["g"] or True):
            out.append(dict(a, p="ts" if a["p"] == "t" else "dz")); i += 2; continue
        if b and c and (a["p"], b["p"]) in (("g", "w"), ("k", "w"), ("h", "w")) and c["p"] in VSET:
            out.append(dict(a, p=a["p"] + "w")); i += 2; continue
        out.append(dict(a)); i += 1
    for k, ph in enumerate(out):
        if ph["p"] == "m" and k + 1 < len(out) and out[k + 1]["p"] in ("b", "p"):
            ph["p"] = "n"; ph["mnote"] = True
    res = []
    for k, ph in enumerate(out):
        if ph["p"] in ("l", "m", "n") and k > 0 and out[k - 1]["p"] in OBSTR and \
                (k + 1 >= len(out) or out[k + 1]["p"] not in VSET):
            res.append({"p": "SC", "g": None, "li": None, "raw": "syll"})
        res.append(ph)
    return res


def translit_word(word, ipa, mode, female=False):
    """回傳 (譯名, 切分說明, 註記)。word 可為 None（只有音標）。"""
    notes = []
    w = word.lower() if word else None
    if w:
        w = re.sub(r"[^a-z]", "", w.translate(str.maketrans("áàâäéèêëíìîïóòôöúùûüçñ", "aaaaeeeeiiiioooouuuucn")))
    pre_zh, suf_zh, aff_note = "", "", []
    if ipa:
        P = parse_ipa(ipa)
        aligned = bool(w) and align(w, P)
        if w and not aligned:
            notes.append("拼寫與音標對不起來，依拼寫的規則略過")
            w = None
    else:
        P = None  # 切掉構詞成分後再推讀音
        notes.append("依拼寫推測讀音")
    known = bool(w)
    # 構詞成分（GB 附錄 C）
    if known:
        lo, hi = 0, len(w)
        for k in sorted((k for k in AFFIX if k.startswith("-")), key=len, reverse=True):
            a = k.strip("-")
            stem = w[:-len(a)]
            if w.endswith(a) and len(stem) >= 2 and re.search(r"[aeiouy]", stem):
                cut = len(stem)
                # 有音標時：構詞成分的第一個字母不發音就不套（Listen 的 t 不發音，不當 -ten）
                if P is not None and not any(ph["li"] <= cut < ph["li"] + len(ph["g"]) for ph in P):
                    aff_note.append(f"{k} 的首字母不發音，不套構詞成分"); continue
                hi = cut; suf_zh = AFFIX[k]; aff_note.append(f"構詞成分 {k}→{AFFIX[k]}"); break
        for k in sorted((k for k in AFFIX if k.endswith("-")), key=len, reverse=True):
            a = k.strip("-")
            rest = w[len(a):hi]
            if w.startswith(a) and (rest == "" and suf_zh or re.search(r"[aeiouy]", rest) and len(rest) >= 2):
                lo = len(a); pre_zh = AFFIX[k]; aff_note.append(f"構詞成分 {k}→{AFFIX[k]}"); break
        if P is None:
            P = g2p(w[lo:hi]) if hi > lo else []
            for ph in P:
                ph["li"] += lo
        elif lo or hi < len(w):
            # 字位跨過切點的（possession 的 ss）歸構詞成分
            P = [ph for ph in P if ph["li"] is not None and lo <= ph["li"] and ph["li"] + len(ph["g"]) <= hi]
        notes += aff_note
        if suf_zh and P and P[-1]["p"] == "m" and w[hi] in "bp":
            P[-1] = dict(P[-1], p="n"); notes.append("m 在 b、p 前按 n")
        # 字母 s 不論讀 s 或 z 都按「斯」列（地名表規則）；濁輔音清化或清輔音濁化按形譯（人名表規則）
        for ph in P:
            g = ph["g"] or ""
            if ph["p"] == "z" and "s" in g and "z" not in g:
                ph["p"] = "s"; notes.append("字母 s 讀 z 仍按斯列")
            elif ph["p"] == "s" and "z" in g:
                ph["p"] = "z"
        wl = w[lo:hi]
        full_end = hi == len(w)
    else:
        wl, full_end = None, True
    P = prep(P)
    units = build_units(P, mode, wl, lo if known else 0, full_end, w, notes)
    zh, trace = render(units, mode, female, notes, pre_zh)
    if female and suf_zh:
        suf_zh = suf_zh.translate(str.maketrans("利里尼纳林斯", "莉丽妮娜琳丝"))
    zh = pre_zh + zh + suf_zh
    if mode == "place" and zh:
        for a, b in (("东", "栋"), ("南", "楠"), ("西", "锡")):
            if zh.startswith(a):
                zh = b + zh[1:]; notes.append(f"詞首{a}改{b}")
        if zh.endswith("海"):
            zh = zh[:-1] + "亥"; notes.append("詞尾海改亥")
    seg = " ".join(u["src"] for u in units)
    if pre_zh:
        seg = f"[{pre_zh}] " + seg
    if suf_zh:
        seg += f" [{suf_zh}]"
    return zh, seg, trace, notes


def build_units(P, mode, w, lo, full_end, wfull, notes):
    n = len(P)
    isV = lambda k: 0 <= k < n and P[k]["p"] in VSET
    vidx = [k for k in range(n) if isV(k)]
    nv = len(vidx)
    has_stress = any(P[k].get("st") for k in vidx)
    letters = w is not None
    units = []

    def U(col, row=None, lit=None, src=""):
        units.append({"col": col, "row": row, "lit": lit, "src": src})

    def g_of(k):
        return (P[k]["g"] or "") if letters else ""

    def at_word_end(k):
        if not letters or P[k]["li"] is None or not full_end:
            return False
        return P[k]["li"] + len(P[k]["g"] or "") >= len(wfull)

    def vrow(k, onset):
        """元音列（套用依拼寫的規則）。"""
        v = P[k]["p"]
        row = ROW[v]
        g = g_of(k)
        syl = vidx.index(k)
        first, last = syl == 0, syl == nv - 1
        li = P[k]["li"]
        if letters and li is not None:
            if v in ("E", "EI") and li == lo == 0 and g in ("ai", "ay"):
                notes.append("詞首 ai／ay 按艾行"); return "ai"
            if v == "SC":
                if g.startswith("a") and ((mode == "place" and (first or last)) or (first and li == 0) or
                                          (mode == "person" and last and at_word_end(k))):
                    notes.append("a 讀 ə 按 ɑː 行"); return "a"
                if mode == "place" and g.startswith("e") and first:
                    notes.append("e 在首音節讀 ə 按 e 行"); return "e"
                if mode == "place" and g.startswith("o") and (first or onset in ("g", "k", "m", "n")):
                    notes.append("o 讀 ə 按 o 行"); return "o"
            if v == "OU" and li == 0 and g.startswith("o") and mode == "place":
                notes.append("詞首 o 按奧"); return "o"
            # 人名表：元音在非重音節一般形譯（照字母譯）；r 跟在後面成 er／or 的照 er 列
            if mode == "person" and len(g) == 1 and g in "aeiouy" and not P[k].get("st") and \
                    (v == "SC" or (has_stress and v in ("I", "U", "AE", "UH", "E", "O"))):
                nxt = wfull[li + 1:li + 2] if full_end or li + 1 < len(wfull) else ""
                after = wfull[li + 2:li + 3]
                if not (nxt == "r" and (not after or after not in "aeiouy")):
                    r2 = {"a": "a", "e": "e", "i": "i", "y": "i", "o": "o", "u": "u"}[g]
                    if r2 != row:
                        notes.append(f"非重音節 {g} 形譯，按 {r2} 列")
                    return r2
        return row

    def ends_r():
        return letters and full_end and re.search(r"(r|re|rr|rre)$", wfull) is not None

    def is_ia(k):
        """詞尾 -ia 的 a。"""
        if k != n - 1:
            return False
        prev = P[k - 1]["p"] if k > 0 else ""
        if letters:
            return (P[k]["g"] or "").startswith("a") and prev in ("I", "j") and wfull.endswith("a")
        return prev == "j" or (prev == "I" and P[k]["raw"] == "iə")

    i = 0
    while i < n:
        p = P[i]["p"]
        if p in VSET:
            onset, vi = "", i
        elif isV(i + 1):
            onset, vi = p, i + 1
        elif p != "j" and i + 2 < n and P[i + 1]["p"] == "j" and isV(i + 2):
            v = P[i + 2]["p"]
            if v == "U":
                U(COL[p], "ju", src=f"{p}j{v}")
                i += 3
                continue
            if v == "SC" and i + 3 < n and P[i + 3]["p"] == "n" and not isV(i + 4):
                U(COL[p], "in", src=f"{p}jən"); i += 4; continue
            U(COL[p], "i", src=f"{p}(j)")
            if is_ia(i + 2):
                U("", lit="亚", src="-ia"); notes.append("詞尾 ia 的 a 譯亞"); i += 3; continue
            if v == "SC":
                i += 3; continue  # j 已帶 i 音，弱 ə 不另譯（Daniel 丹尼爾）
            i += 1  # j 留給下一格當聲母
            continue
        else:
            if p == "θ" and (i + 1 >= n or P[i + 1]["p"] not in VSET):
                U("s", lit="思", src="θ"); notes.append("th 在輔音前或詞尾讀 θ 譯思")
            elif p == "j":
                U("j", src="j")
            else:
                U(COL[p], src=p)
            i += 1
            continue
        v = P[vi]["p"]
        col = COL[onset] if onset else ""
        if v == "OI":
            U(col, "o", src=f"{onset}ɔɪ"); U("", "i", src="(ɪ)")
            i = vi + 1
            continue
        if not onset and v == "SC" and vi > 0 and isV(vi - 1):
            if is_ia(vi):
                U("", lit="亚", src="-ia"); notes.append("詞尾 ia 的 a 譯亞"); i = vi + 1; continue
            if vi == n - 1 and (ends_r() or (not letters and P[vi]["raw"] in ("ɪə", "eə", "ʊə", "uə", "ɔə", "aɪə", "aʊə", "eː"))):
                U("", lit="尔", src="ə(r)"); notes.append("詞尾 r 的 ə 譯爾"); i = vi + 1; continue
        if not onset and v == "AE" and is_ia(vi):
            U("", lit="亚", src="-ia"); notes.append("詞尾 ia 的 a 譯亞"); i = vi + 1; continue
        if not onset and v != "SC" and vi > 0 and P[vi - 1]["p"] in ("I", "EI", "AI"):
            onset = "j"; notes.append("前一元音為 i 類，元音間加 j 滑音（Fayette 費耶特）")
        col = COL[onset] if onset else ""
        row = vrow(vi, onset)
        j = vi + 1
        src = f"{onset}{v}"
        eff = v if row == ROW[v] else {"a": "AE", "e": "E", "o": "O"}.get(row)  # 依拼寫改列時，鼻音列也跟著改
        if j < n and P[j]["p"] in ("n", "ŋ") and (eff, P[j]["p"]) in NAS:
            k2 = j + 1
            nasal_ok = P[j]["p"] == "ŋ" or not (isV(k2) or (k2 + 1 < n and P[k2]["p"] == "j" and isV(k2 + 1)))
            if nasal_ok:
                row = NAS[(eff, P[j]["p"])]
                src += P[j]["p"]
                j += 1
        # 單音節地名詞尾的雙元音拆開（Fay 費伊）
        if mode == "place" and nv == 1 and v in ("EI", "AI") and j >= n and full_end:
            U(col, "e" if v == "EI" else "a", src=src); U("", "i", src="(ɪ)")
            notes.append("單音節雙元音拆成兩個單元音")
            i = j
            continue
        U(col, row, src=src)
        i = j
    # 詞尾 r（英式音標沒有 r）：長元音、單音節加爾
    if letters and ends_r() and n and P[-1]["p"] in VSET and not (units and units[-1]["lit"] == "尔"):
        last = P[-1]["p"]
        if last in ("AA", "O", "ER", "E", "I", "U") or nv == 1:
            if not (last in ("I", "U", "E") and nv > 1):
                U("", lit="尔", src="(r)"); notes.append("詞尾 r 加爾")
    return units


def pick(cell, label, notes, female):
    if not cell or not cell["main"]:
        notes.append(f"{label}：表上此格為空")
        return None
    ch = cell["main"][0]
    if female:
        fem = [a for a in cell["alt"] if a in FEMALE]
        if fem:
            return fem[0]
    others = [a for a in cell["alt"] if a != "弗"]
    if others:
        notes.append(f"{label}：取「{ch}」，另有 {'、'.join(others)}")
    return ch


def render(units, mode, female, notes, pre_zh):
    t = TABLE[mode]
    out, trace = [], []
    for k, u in enumerate(units):
        if u["lit"]:
            ch = u["lit"]
        elif u["row"] is None:
            cell = t["zero"].get(u["col"])
            ch = pick(cell, f"{u['src']}（單獨）", notes, female)
            if ch in ("夫", "弗") and u["col"] in ("f", "v", "w"):
                ch = "弗" if (k == 0 and not pre_zh) else "夫"
        else:
            cell = t["rows"][u["row"]].get(u["col"])
            ch = pick(cell, u["src"], notes, female)
            if ch is None and u["col"] in ("gw", "kw", "hw"):
                # 表上空格：拆成 g／k／h 單獨＋w 行
                a = {"gw": "g", "kw": "k", "hw": "h"}[u["col"]]
                ch = (t["zero"][a]["main"][0] if a != "h" else "") + (pick(t["rows"][u["row"]].get("w"), u["src"], notes, female) or "")
            if ch is None:
                # 空格：元音單獨＋輔音單獨的後備
                ch = (pick(t["zero"].get(u["col"]), u["src"], notes, female) or "") + (pick(t["rows"][u["row"]].get(""), u["src"], notes, female) or "")
        out.append(ch or "?")
        trace.append(f"{u['src']}→{ch}")
    return "".join(out), trace


# ---------- 整個名稱 ----------
GEN_POST = {"county": "县", "river": "河", "lake": "湖", "lakes": "湖群", "island": "岛", "islands": "群岛", "isle": "岛",
            "mountain": "山", "mountains": "山脉", "range": "岭", "bay": "湾", "peak": "峰", "hill": "山", "hills": "丘陵",
            "creek": "溪", "point": "角", "glacier": "冰川", "canal": "运河", "sea": "海", "valley": "谷", "falls": "瀑布",
            "harbour": "港", "harbor": "港", "reservoir": "水库", "desert": "沙漠", "forest": "森林", "strait": "海峡",
            "gulf": "湾", "beach": "滩", "brook": "河", "cape": "角", "channel": "水道", "inlet": "湾", "lagoon": "潟湖",
            "plateau": "高原", "plain": "平原", "parish": "教区", "village": "村", "state": "州", "province": "省",
            "district": "区", "station": "站", "street": "街", "square": "广场", "park": "公园", "bridge": "桥"}
GEN_PRE = {"lake": "湖", "mount": "山", "fort": "堡", "cape": "角", "port": "港"}
MODIF = {"north": "北", "south": "南", "east": "东", "west": "西", "new": "新", "great": "大", "little": "小", "old": "旧",
         "northern": "北", "southern": "南", "eastern": "东", "western": "西"}


def split_input(text, force_ipa=False):
    """切成 [(拼寫或 None, 音標或 None)]。"""
    text = text.strip()
    if force_ipa or (is_ipa(text) and not re.search(r"[A-Za-z]{2,}[/\[=]", text) and not re.match(r"^[A-Za-z'.-]+\s*[/\[]", text)):
        return [(None, x) for x in re.split(r"\s+", text.strip("/[] ")) if x]
    out = []
    for m in re.finditer(r"([A-Za-zÀ-ÿ'’.&-]+)\s*(?:=\s*([^\s/\[\]]+)|[/\[]([^/\]]+)[/\]])?", text):
        out.append((m.group(1), m.group(2) or m.group(3)))
    return out


def translit(text, mode="place", female=False, force_ipa=False):
    """回傳 (譯名（簡體字形；要繁體請包 S()）, info 串列)。"""
    words = split_input(text, force_ipa)
    info = []
    zh_parts = []

    def one(wd, ipa, fem=female):
        if wd and not ipa:
            m = re.match(r"^(Mc|Mac)([A-Z].*)$", wd)
            if m:
                zh, seg, tr, nt = translit_word(m.group(2), None, mode, fem)
                info.append((wd, "Mc/Mac→麦克 " + seg, tr, nt))
                return "麦克" + zh
        zh, seg, tr, nt = translit_word(wd, ipa, mode, fem)
        info.append((wd or ipa, seg, tr, nt))
        return zh

    if mode == "person":
        for wd, ipa in words:
            if wd and not ipa and re.fullmatch(r"[A-Za-z]\.?", wd):
                continue  # 單字母縮寫省譯
            fem = female and not zh_parts  # 女名用字只用在名字（第一個詞），不用在姓
            parts = [one(x, ipa if len(wd.split("-")) == 1 else None, fem) for x in wd.split("-") if x] if wd else [one(None, ipa, fem)]
            zh_parts.append("-".join(parts))
        return "·".join(zh_parts), info
    # 地名
    words = [(re.sub(r"['’]s$", "", wd) if wd else wd, ipa) for wd, ipa in words]
    if words and words[0][0] and words[0][0].lower() == "the" and len(words) > 1:
        words = words[1:]
    low = [(wd or "").lower().rstrip(".") for wd, _ in words]
    pre_gen, post_gen, mods = "", "", ""
    body = list(range(len(words)))
    if len(body) > 1 and low[-1] in GEN_POST:
        post_gen = GEN_POST[low[-1]]; body = body[:-1]
    elif len(body) > 1 and low[0] in GEN_PRE:
        pre_gen = GEN_PRE[low[0]]; body = body[1:]
    while len(body) > 1 and low[body[0]] in MODIF and not words[body[0]][1]:
        mods += MODIF[low[body[0]]]; body = body[1:]
    saint = ""
    if len(body) > 1 and low[body[0]] in ("st", "saint"):
        saint = "圣"; body = body[1:]
    seg = []
    for k in body:
        wd, ipa = words[k]
        if low[k] in ("and", "&", "with"):
            seg.append("-"); continue
        seg.append(one(wd, ipa))
    zh = mods + saint + "".join(seg) + (post_gen or pre_gen)
    return zh, info


def run_tests(path):
    """--test：跑 en_translit_test.tsv（模式<Tab>原文<Tab>預期<Tab>出處；模式可加 -F 表示女名用字）。"""
    ok, bad = 0, []
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        mode, src, exp, ref = (line.rstrip("\n").split("\t") + [""] * 4)[:4]
        fem = mode.endswith("-F")
        got = S(translit(src, mode.replace("-F", ""), fem)[0])
        if got == S(exp):
            ok += 1
        else:
            bad.append((mode, src, S(exp), got, ref))
    print(f"通過 {ok}／{ok + len(bad)}")
    for m, s, e, g, r in bad:
        print(f"  ✘ {m}\t{s}\t預期 {e}\t得到 {g}\t（{r}）")


def main(argv):
    if argv[:1] == ["--test"]:
        return run_tests(argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "en_translit_test.tsv"))
    mode, verbose, female, force_ipa, words = "place", False, False, False, []
    it = iter(argv)
    for a in it:
        if a == "-p":
            mode = "person"
        elif a == "-v":
            verbose = True
        elif a == "-F":
            female = True
        elif a == "-i":
            force_ipa = True
        elif a == "-f":
            words += [l.strip() for l in open(next(it), encoding="utf-8") if l.strip() and not l.startswith("#")]
        else:
            words.append(a)
    if not words:
        sys.exit(__doc__)
    print(f"# 依{'人名' if mode == 'person' else '地名'}表譯寫（中國大陸標準，譯名一律以繁體字輸出；台灣有通行譯名時以通行為準）")
    for w in words:
        zh, info = translit(w, mode, female, force_ipa)
        print(f"{w}\t{S(zh)}")
        if verbose:
            for part, seg, tr, nt in info:
                print(f"    {part}：{seg}｜{S('，'.join(tr))}")
                for x in dict.fromkeys(nt):
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
