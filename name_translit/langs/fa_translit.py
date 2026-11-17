"""波斯語音譯工具：輸入波斯語地名或人名的拉丁轉寫，依中國標準吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 fa_translit_table.json（由 fa_translit_build_table.py 重建）：
  地名表＝GB/T 17693.9-2017《外语地名汉字译写导则 第9部分：波斯语》表1
    （中維「外語譯音表/波斯語」地名節只附 PDF 連結；PDF 是掃描本，表格人工轉錄）；
  人名表＝中維「外語譯音表/波斯語」人名節（新華社《世界人名翻译大辞典》）。
  兩表都是中國大陸標準，譯名一律以繁體字輸出；德黑蘭、伊斯法罕這類常識性譯名，
  以及穆罕默德、侯賽因、阿里這類伊斯蘭慣用人名以通行譯名為準，不必跑工具。

輸入格式：只收拉丁轉寫，不收波斯文字母。
  波斯文不標短元音（a、e、o），光看字母無法確定讀音，輸入波斯文時工具會拒絕並提示改輸入轉寫。
  轉寫照 GB/T 17693.9 附錄 C（即聯合國 1967 年系統）：ā ī ū 長元音、a e o 短元音、ey／ow 雙元音、
  š č ž 或 sh ch zh、kh（x）、q／gh、ʿ 或 ' 表示 ع／ء。也接受常見英文拼法（â、ou、ei、w），
  但英文拼法常把長短元音混寫（Rouhani、Mousavi），結果不一定準。
  沒有長音符號時 a 一律當 ā／a 同列（表上兩者同列），不影響結果；i／ī、u／ū 也同列。
  sh、ch、kh、zh、gh 一律當一個輔音；遇到 s＋h 分讀（Es-hāq）請寫 s'h 或用 š 區分。

用法：
  python -X utf8 fa_translit.py "Bandar-e Genāve" Dizaj-e Bālā Hājilafte      （預設地名表）
  python -X utf8 fa_translit.py -p "Hasan Rūhāni" "Ja'far Panāhi"               （-p 人名表，名與姓間加「·」）
  python -X utf8 fa_translit.py -v Owriyā                                       （-v 列出音節與每字來源）
  python -X utf8 fa_translit.py -f 名單.txt                                     （每行一個原文）
  python -X utf8 fa_translit.py -t fa_translit_test.tsv                         （跑測試詞）
  地名有通名或方位、大小、新舊修飾詞時，另列「通名意譯」版本（Bandar-e Genāve→蓋納韋港）。
  詞中有 GB/T 17693.9 附錄 A 的常用人名時，另列「附錄A慣譯」（Ebrāhim＝易卜拉欣）。

處理規則：
  共同：
  - 相同輔音連寫按一個譯（Darrasi→達拉西、Mellat→梅拉特、Sadd→薩德；5.3.4）。
  - 音節尾的 n 併入元音列（an／ān、en、in／īn、on、un／ūn）；表上沒有的組合，元音與「恩」分開譯。
  - ʿ（ع）後接元音按零聲母譯；單獨出現（後接輔音或在詞尾）不譯（Ja'far→賈法爾；5.3.3）。
  - ey／ay／ow 後面接元音時，y、w 歸下一音節當聲母（Fereydūn 的 y 不算，因後接輔音）。
  地名（GB/T 17693.9-2017）：
  - 詞尾 h 前面是短元音（a、e、o）時不譯（Khāneh→哈內）；前面是長元音或輔音照譯（Kūtāh→庫塔赫；5.3.1）。
  - ow／ou 在詞首譯「歐」（Owriyā→歐里亞），在詞中、詞尾照 ū 列譯（Moujūd→穆朱德；5.3.2）。
  - ey 照 e 列譯，ay 照 ai 列譯（Meydān→梅丹）。
  - 連接被修飾語與修飾語的「埃扎菲」-e 不譯；前一詞以 ā、ū、ou 結尾時的 -ye 譯「伊」（Bālā-ye Dizeh→巴拉伊-迪澤；5.3.5）。
  - 單音節詞用兩個漢字（Fin→菲恩、Khān→哈恩、pā→普阿、now→諾烏、deh→代赫；5.1.6）。
  - 兩個以上的詞構成的專名，第一個詞後加連接號（Ja'far Darrasi→賈法爾-達拉西；5.1.5）。
  - 地名開頭的東、南、西、北改棟、楠、錫、貝（表注3）。
  - 阿拉伯語冠詞寫成 al- 時譯「阿爾」（5.1.8）；與後詞連寫（Alnaqi）無法辨認，照音節譯。
  人名（新華社）：
  - 詞尾 h 一律不譯；ia、ie 照 i 列加「亞」「耶」；m 在 b、p 前按 n 譯；夫用於詞中與詞尾、弗用於詞首。
  - ey／ei 照 ei 列，ow／au 照 au 列，ou／ū／u 照 ū 列。
  - 連字號連起的複名照留「-」（Mir-Hosein→米爾-霍塞恩），名與姓之間加「·」。
  - 同一格有兩個字時取第一個；女性用字（莎、瑪、娜、娃、婭、麗、莉、琳、珍；地名表的婭、瑪、娜、
    莉、麗、莎、蒂、妮、琳，表注4用於以女性名命名的地名）不自動套用，-v 會列出另一個字。

限制（做不到或沒做的）：
  - 波斯文原文不收（見上）；附加短元音符號的波斯文也沒做。
  - 拉丁轉寫看不出的讀音差異（ai 是雙元音還是 a＋ʿi：Raisi 要寫 Ra'isi；s＋h 分讀）只能靠輸入區分。
  - 人名以人名表逐音節譯；新華社辭典另有收錄的慣用譯名（侯賽因、易卜拉欣、伊巴迪、哈什米）
    工具不知道，附錄 A 只涵蓋地名標準所列的百餘個。
  - 「以人名命名的地名用『·』」（5.1.7）、「具特定意義的專名意譯」（5.1.3、5.1.4，如日期、烈士名）
    需要語意判斷，工具不做。
  - 通名意譯只認附錄 B 的常用通名與幾個方位、大小、新舊修飾詞，其餘通名照音譯。
  - 標準示例本身有少數與表不一致之處（Jilow→吉魯，表上 l＋ū 是盧；zeytūn→澤圖恩，
    表上 tūn 是通；siyāh→西亞赫，未依注3改錫），工具照表譯。
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
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fa_translit_table.json"), encoding="utf-8"))

AIN = "ʿ"
SHORT = {"a", "e", "o"}           # 5.3.1 的短元音（u 在轉寫中也是短 o 的變體）
VOWELS = set("aeiouāīūēō")
# 輔音 → 表上的欄
COL = {"b": "b", "p": "p", "t": "t", "s": "s", "j": "j", "č": "č", "ch": "č", "c": "č", "h": "h", "kh": "h", "x": "h",
       "d": "d", "z": "z", "r": "r", "zh": "zh", "ž": "zh", "š": "š", "sh": "š", "f": "f", "g": "g", "q": "g", "gh": "g",
       "k": "k", "l": "l", "m": "m", "n": "n", "v": "v", "w": "v", "y": "y", AIN: "ʿ"}
DIGRAPHS = ("kh", "gh", "sh", "ch", "zh")
NASAL = {"a": "ān", "e": "en", "i": "īn", "o": "on", "ū": "ūn"}

# 附錄 B.1 常用地名通名（意譯）；鍵用 norm() 正規化
GENERIC = {
    "ab anbar": "水庫", "absar": "瀑布", "abgarm": "溫泉", "ataskade": "祭火壇", "azadrah": "高速公路", "asar-e bastani": "古蹟",
    "batlaq": "沼澤", "baq": "花園", "bozorgrah": "公路", "bolaqi": "泉", "bana-ye yadbud": "紀念場所", "bandargah": "海港",
    "bise": "樹林", "park": "公園", "pol": "橋", "tappe": "丘陵", "tappeha": "丘陵", "tappehay": "丘陵", "takhte": "高地",
    "tunel": "隧道", "jazire": "島", "jangal": "森林", "chah": "井", "chah ab": "水井", "chah gaz": "天然氣井",
    "chah naft": "油井", "cheshme": "泉", "daqi": "山", "daneshgah": "大學", "darya": "海", "darre": "山谷",
    "daryache": "湖", "dasht": "平原", "damaqe": "海角", "deh": "村", "dahane": "山口", "rud": "河", "rudkhane": "河",
    "zendan": "監獄", "sahel": "海岸", "shahr": "市", "shahrak": "小區", "forudgah": "機場", "qaravolkhane": "哨所",
    "qasr": "宮", "qal'e": "堡", "qale": "堡", "qolle": "峰", "karkhane": "廠", "kavir": "鹽漠", "kuh": "山",
    "kuhha": "山脈", "kuhhay": "山脈", "mandab": "濕地", "mojtama'": "綜合區", "mojtama": "綜合區",
    "mojtama'-e san'ati": "工業園區", "mahalle": "區", "mordab": "沼澤", "mazra'e": "農田", "mazrae": "農田",
    "masjed": "清真寺", "meydan": "廣場", "bandar": "港", "ostan": "省", "shahrestan": "縣",
}
# 5.1.2 修飾詞（方位、大小、新舊），放在專名前
MODIFIER = {"payin": "下", "bala": "上", "kuchek": "小", "kucek": "小", "bozorg": "大", "now": "新", "no": "新",
            "kohne": "舊", "kuhne": "舊", "sharqi": "東", "qarbi": "西", "gharbi": "西", "shomali": "北", "jonubi": "南",
            "olya": "上", "sofla": "下", "vosta": "中", "markazi": "中"}
# 附錄 A 波斯語地名中常用人名譯名（規範性附錄；新華社慣譯，多半不照表）
APPENDIX_A = {
    "aras": "阿拉什", "arman": "阿爾曼", "arya": "雅利安", "azar": "阿扎爾", "ebrahim": "易卜拉欣", "ahmad": "艾哈邁德",
    "ardasir": "阿爾達希爾", "ardashir": "阿爾達希爾", "esma'il": "易斯瑪儀", "esmail": "易斯瑪儀", "eskandar": "埃斯坎達爾",
    "askan": "阿什坎", "ashkan": "阿什坎", "afshin": "阿夫欣", "akbar": "阿克巴爾", "omid": "奧米德", "amir": "阿米爾",
    "babak": "巴巴克", "baqher": "巴蓋爾", "baqer": "巴蓋爾", "bahram": "巴赫拉姆", "behzad": "貝赫扎德",
    "behruz": "貝赫魯茲", "bahman": "巴赫曼", "parviz": "帕爾維茲", "torab": "圖拉卜", "tarane": "塔拉內",
    "teymur": "帖木兒", "jamshid": "賈姆希德", "javad": "賈瓦德", "changiz": "成吉思", "hassan": "哈桑", "hasan": "哈桑",
    "hossein": "侯賽因", "hosein": "侯賽因", "hamid": "哈米德", "khaled": "哈立德", "khadije": "赫蒂徹",
    "khorshid": "霍爾希德", "dariush": "大流士", "davud": "達烏德", "doniya": "多尼婭", "ramin": "拉明",
    "rostam": "羅斯塔姆", "rashid": "拉希德", "reza": "禮薩", "zoleykha": "佐列哈", "zahra": "扎赫拉", "zeyd": "宰德",
    "zaynab": "宰奈卜", "saman": "薩曼", "sa'id": "薩伊德", "said": "薩伊德", "soltan": "蘇丹", "solayman": "蘇萊曼",
    "sangar": "桑賈爾", "sohrab": "蘇赫拉布", "sorush": "索魯什", "siyavash": "夏沃什", "seyf": "賽義夫",
    "seyyed": "賽義德", "simin": "西敏", "shapur": "沙普爾", "shahrokh": "沙哈魯", "shahin": "沙欣", "sadeq": "薩迪克",
    "saleh": "薩利赫", "taher": "塔黑爾", "'abbas": "阿巴斯", "abbas": "阿巴斯", "'aziz": "阿齊茲", "aziz": "阿齊茲",
    "'ali": "阿里", "ali": "阿里", "fateme": "法蒂瑪", "fatemah": "法蒂瑪", "farrokh": "法羅赫", "farid": "法里德",
    "fereydun": "費雷敦", "qader": "卡迪爾", "qasem": "加塞姆", "kazem": "卡齊姆", "kamran": "卡姆朗", "karim": "卡里姆",
    "kurosh": "居魯士", "kamal": "卡馬勒", "keyvan": "凱萬", "lale": "拉蕾", "leyli": "蕾莉", "mohammad": "穆罕默德",
    "mahmud": "馬赫穆德", "morteza": "莫爾塔扎", "maryam": "瑪麗亞姆", "mas'ud": "馬斯烏德", "masud": "馬斯烏德",
    "mansur": "曼蘇爾", "manuchehr": "曼努切赫爾", "mehdi": "邁赫迪", "musa": "穆薩", "mahtab": "瑪赫塔卜",
    "mehran": "梅赫蘭", "mehrdad": "梅赫爾達德", "milad": "米拉德", "mina": "米娜", "nader": "納迪爾",
    "nasrin": "納斯琳", "naser": "納賽爾", "nasrolla": "納斯魯拉", "nasrollah": "納斯魯拉", "navid": "納維德",
    "hashem": "哈希姆", "homa": "胡馬", "hushang": "胡山", "yaseman": "亞塞曼", "yusef": "優素福",
}


def norm(w):
    """查通名、修飾詞、附錄 A 用的寬鬆鍵：去長音符號、š→sh、詞尾 eh→e、ou/ow→u。"""
    w = w.lower().strip()
    for a, b in (("š", "sh"), ("č", "ch"), ("ž", "zh"), ("x", "kh"), ("ʿ", "'"), ("‘", "'"), ("’", "'"), ("ʻ", "'"),
                 ("`", "'"), ("ʾ", "'"), ("ē", "e"), ("ō", "o")):
        w = w.replace(a, b)
    w = "".join(c for c in unicodedata.normalize("NFD", w) if not unicodedata.combining(c))
    w = re.sub(r"eh\b", "e", w)
    w = w.replace("ou", "u").replace("ow", "u") if w not in ("now",) else w
    w = w.replace("ei", "ey")
    return w


def prep(word):
    w = word.lower()
    for a, b in (("â", "ā"), ("á", "ā"), ("î", "ī"), ("í", "ī"), ("û", "ū"), ("ú", "ū"), ("ē", "e"), ("ō", "o"),
                 ("ğ", "gh"), ("ẓ", "z"), ("ż", "z"), ("ź", "z"), ("ẕ", "z"), ("ṣ", "s"), ("ṯ", "s"), ("ś", "s"),
                 ("ṭ", "t"), ("ḥ", "h"), ("ẖ", "h"), ("ḏ", "z"), ("ḍ", "z")):
        w = w.replace(a, b)
    w = re.sub(r"[ʿʻ‘’'`ʾ´]", AIN, w)
    return w


def units(w):
    """切成 [('C', 輔音) | ('V', 元音)]。"""
    out, i = [], 0
    while i < len(w):
        d = w[i:i + 2]
        if d in DIGRAPHS:
            out.append(("C", d)); i += 2; continue
        c = w[i]
        if c in VOWELS:
            out.append(("V", c))
        elif c in COL:
            out.append(("C", c))
        # 其他符號（數字、句點）略過
        i += 1
    # 相同輔音連寫按一個（5.3.4）
    ded = []
    for u in out:
        if ded and u[0] == "C" and ded[-1][0] == "C" and COL[ded[-1][1]] == COL[u[1]] and u[1] != AIN:
            continue
        ded.append(u)
    return ded


def merge_vowels(u, mode):
    """把雙元音併成一個 V：ey/ei、ay/ai、ow/ou/au；y、w 後面接元音時當聲母。"""
    out, i = [], 0
    isv = lambda k: k < len(u) and u[k][0] == "V"
    while i < len(u):
        t, x = u[i]
        if t == "V" and i + 1 < len(u):
            nt, nx = u[i + 1]
            # 母音＋y/w（後面不是元音）
            if nt == "C" and nx in ("y", "w") and not isv(i + 2):
                if x in ("e", "a") and nx == "y":
                    out.append(("V", x + "y")); i += 2; continue
                if x == "o" and nx == "w":
                    out.append(("V", "ow")); i += 2; continue
                if x == "a" and nx == "w":
                    out.append(("V", "aw")); i += 2; continue
            if nt == "V":
                pair = x + nx
                if pair in ("ou", "ow"):
                    out.append(("V", "ou")); i += 2; continue
                if pair in ("ei", "ai", "au"):
                    out.append(("V", {"ei": "ey", "ai": "ay", "au": "aw"}[pair])); i += 2; continue
        out.append((t, x)); i += 1
    return out


def rowkey(v, mode, initial):
    """元音（含雙元音）→ 表上的列鍵。"""
    if mode == "place":
        return {"a": "a", "ā": "a", "e": "e", "ey": "e", "i": "i", "ī": "i", "o": "o", "u": "ū", "ū": "ū",
                "ou": "ū", "ow": "ū", "ay": "ai", "aw": "ū"}[v]
    return {"a": "a", "ā": "a", "e": "e", "ey": "ei", "i": "i", "ī": "i", "o": "o", "u": "ū", "ū": "ū",
            "ou": "ū", "ow": "au", "ay": "ai", "aw": "au"}[v]


def pick(cell, notes, label):
    if not cell or not cell["main"]:
        notes.append(f"{label}：表上此格為空")
        return "?"
    if len(cell["main"]) > 1 or cell["alt"]:
        notes.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['main'][1:] + cell['alt'])}")
    return cell["main"][0]


def translit_word(word, mode):
    """回傳 (譯名, trace, notes, flags)。flags 供單音節規則與 -ye 判斷用。"""
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    w = prep(word)
    u = merge_vowels(units(w), mode)
    res, trace, notes = [], [], []
    flags = {"nuclei": 0, "dropped_h": False, "nasal": None, "diph": None, "open": None, "last_v": None}
    n = len(u)
    i = 0
    prev_v = None  # 前一個元音（判斷 ia/ie、詞尾 h）
    while i < n:
        typ, x = u[i]
        onset = ""
        if typ == "C":
            nxt = u[i + 1] if i + 1 < n else None
            if nxt and nxt[0] == "V":
                onset = x; i += 1; typ, x = u[i]
            else:
                last = i + 1 >= n
                if x == AIN:
                    trace.append("ʿ→（不譯）"); i += 1; continue
                if x == "h" and last and (mode == "person" or (prev_v in SHORT)):
                    trace.append("h→（詞尾不譯）"); flags["dropped_h"] = True; i += 1; continue
                c = x
                if mode == "person" and c == "m" and nxt and nxt[1] in ("b", "p"):
                    c = "n"
                col = COL[c]
                ch = pick(zero.get(col), notes, f"{x}（單獨）")
                if mode == "person" and col == "f" and not res and zero[col]["alt"]:
                    ch = zero[col]["alt"][0]  # 弗用於詞首
                res.append(ch); trace.append(f"{x}→{ch}"); i += 1; continue
        # 元音（可能帶聲母）
        v = x
        flags["nuclei"] += 1
        key = rowkey(v, mode, not res)
        col = COL[onset] if onset else ""
        j = i + 1
        coda_n = False
        # 音節尾 n（或人名中 b/p 前的 m）併入元音列
        if j < n and u[j][0] == "C" and (j + 1 >= n or u[j + 1][0] == "C"):
            cn = u[j][1]
            nxt2 = u[j + 1][1] if j + 1 < n else ""
            if cn == "n" or (mode == "person" and cn == "m" and nxt2 in ("b", "p")):
                if v in ("a", "ā", "e", "i", "ī", "o", "u", "ū", "ou") and NASAL.get(key) in rows:
                    key = NASAL[key]; coda_n = True
        # 人名 ia、ie：i 列後的 a、e 譯亞、耶
        if mode == "person" and not onset and prev_v in ("i", "ī") and v in ("a", "ā", "e") and not coda_n:
            ch = "亞" if v in ("a", "ā") else "耶"
            trace.append(f"{v}→{ch}（i{v} 規則）")
        else:
            cell = rows.get(key, {}).get(col)
            if mode == "place" and not onset and not res and v in ("ow", "ou") and cell and cell["alt"]:
                ch = cell["alt"][0]; trace.append(f"{v}→{ch}（詞首 ow 譯歐，5.3.2）")
            else:
                ch = pick(cell, notes, f"{onset}{v}{'n' if coda_n else ''}")
                trace.append(f"{onset}{v}{'n' if coda_n else ''}→{ch}")
        res.append(ch)
        flags.update(open=(onset, v, key), nasal=(onset, v) if coda_n else None,
                     diph=v if v in ("ey", "ay", "ow", "aw") else None, last_v=v)
        prev_v = v if not coda_n else None
        i = j + (1 if coda_n else 0)
    s = "".join(res)
    # 單音節詞用兩個漢字（5.1.6）
    if mode == "place" and flags["nuclei"] == 1 and len(s) == 1:
        on, v, key = flags["open"]
        col = COL[on] if on else ""
        if flags["dropped_h"]:
            s += pick(zero["h"], notes, "h"); notes.append("單音節詞，詞尾 h 照譯（5.1.6）")
        elif flags["nasal"]:
            base = rowkey(v, mode, True)
            s = pick(rows[base].get(col), notes, on + v) + pick(zero["n"], notes, "n")
            notes.append("單音節詞，n 單獨譯恩（5.1.6）")
        elif flags["diph"]:
            base = {"ey": "e", "ay": "a", "ow": "o", "aw": "a"}[flags["diph"]]
            glide = "y" if flags["diph"] in ("ey", "ay") else "v"
            s = pick(rows[base].get(col), notes, on + base) + pick(zero[glide], notes, glide)
            notes.append("單音節詞，雙元音拆成兩字（5.1.6）")
        elif on:
            s = pick(zero.get(col), notes, on) + pick(rows[key].get(""), notes, v)
            notes.append("單音節詞，聲母與元音分開譯（5.1.6）")
    if mode == "person" and s.startswith("夫"):
        s = "弗" + s[1:]
    return s, trace, notes, flags


def split_words(text):
    """切成詞與連接符：回傳 [(詞, 前面的連接符)]，連接符是 ' ' 或 '-'；埃扎菲 -e／-ye 標成 ('#e'/'#ye')。"""
    toks = re.findall(r"[^\s\-]+|[\s\-]+", text.strip())
    out, sep = [], ""
    for tk in toks:
        if re.fullmatch(r"[\s\-]+", tk):
            sep = "-" if "-" in tk else " "
            continue
        low = tk.lower()
        if sep and low in ("e", "ye", "-e", "-ye") and out:
            out.append(("#" + low, sep))
        else:
            out.append((tk, sep))
        sep = ""
    return out


def phonetic(words, mode):
    """words：[(詞, 連接符)]（已去掉通名、修飾詞）→ 音譯字串與 info。"""
    parts, info = [], []
    for k, (wd, sep) in enumerate(words):
        if wd.startswith("#"):
            # 埃扎菲：-e 不譯；前一詞以 ā、ū、ou 結尾時 -ye 譯伊（5.3.5）
            if wd == "#ye" and parts and info and info[-1][3]["last_v"] in ("ā", "ū", "ou", "ow") \
                    and re.search(r"(ā|â|ū|û|ou|ow|a|u)$", info[-1][0].lower()):
                parts[-1] = (parts[-1][0] + "伊", parts[-1][1])
                info[-1][2].append("後接 -ye：譯伊（5.3.5）")
            continue
        if mode == "place" and wd.lower() in ("al", "el", "ol"):
            parts.append(("阿爾", sep)); info.append((wd, ["al→阿爾（5.1.8）"], [], {"last_v": None})); continue
        s, tr, nt, fl = translit_word(wd, mode)
        parts.append((s, sep)); info.append((wd, tr, nt, fl))
    if not parts:
        return "", info
    if mode == "person":
        out = parts[0][0]
        for s, sep in parts[1:]:
            out += ("-" if sep == "-" else "·") + s
    else:
        out = parts[0][0] + ("-" + "".join(s for s, _ in parts[1:]) if len(parts) > 1 else "")  # 5.1.5
        # 表注3：地名開頭的東南西北改棟楠錫貝
        for a, b in (("东", "栋"), ("南", "楠"), ("西", "锡"), ("北", "贝")):
            if out.startswith(a):
                out = b + out[1:]; info[0][2].append(f"地名開頭{a}改{b}（表注3）")
    return out, info


def translit(text, mode):
    """純音譯（通名、修飾詞也音譯）。回傳 (譯名, info)；info 每項 (原詞, trace, notes, flags)。"""
    if re.search(r"[؀-ۿ]", text):
        raise ValueError("波斯文字母不標短元音，無法確定讀音；請改輸入拉丁轉寫（GB/T 17693.9 附錄 C）")
    return phonetic(split_words(text), mode)


def generic_variant(text):
    """地名：通名意譯、修飾詞意譯版本。沒有通名或修飾詞時回傳 None。"""
    words = split_words(text)
    core = [w for w in words]
    suffix, prefix, hit = "", "", False
    # 開頭的通名（後面接埃扎菲或其他詞），由外而內：Jangal-e Qal'e Kati→卡提堡森林
    while len(core) > 1 and not core[0][0].startswith("#"):
        k1 = norm(core[0][0])
        k2 = norm(core[0][0] + " " + core[1][0]) if len(core) > 2 and not core[1][0].startswith("#") else None
        if k2 and k2 in GENERIC and len([w for w in core[2:] if not w[0].startswith("#")]) >= 1:
            suffix = GENERIC[k2] + suffix; core = core[2:]; hit = True
        elif k1 in GENERIC and len([w for w in core[1:] if not w[0].startswith("#")]) >= 1:
            suffix = GENERIC[k1] + suffix; core = core[1:]; hit = True
        else:
            break
        while core and core[0][0].startswith("#"):
            core = core[1:]
        if core:
            core[0] = (core[0][0], "")
    # 結尾的修飾詞與通名：Nāteq-e Pāyin→下納泰格、Yokhāri Mahalleh→約哈里區
    while len([w for w in core if not w[0].startswith("#")]) > 1:
        last = core[-1][0]
        k = norm(last)
        if k in MODIFIER:
            prefix = MODIFIER[k] + prefix
        elif k in GENERIC:
            suffix = GENERIC[k] + suffix
        else:
            break
        hit = True
        core = core[:-1]
        while core and core[-1][0].startswith("#"):
            core = core[:-1]
    if not hit:
        return None
    zh, _ = phonetic(core, "place")
    return prefix + zh + suffix


def appendix_a(text):
    hits = []
    for wd, _ in split_words(text):
        k = norm(wd)
        if k in APPENDIX_A:
            hits.append(f"{wd}＝{APPENDIX_A[k]}")
    return hits


def run_tests(path):
    """-t fa_translit_test.tsv：每行 模式<Tab>原文<Tab>預期<Tab>出處；模式 place／place-generic／person。
    預期譯名照出處原樣（大陸簡體）寫，比對前轉成繁體。"""
    ok = bad = 0
    for ln in open(path, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"):
            continue
        mode, src, exp, *ref = ln.rstrip("\n").split("\t")
        if mode == "place-generic":
            got = generic_variant(src) or translit(src, "place")[0]
        else:
            got = translit(src, mode)[0]
        if S(got) == S(exp):
            ok += 1
        else:
            bad += 1
            print(f"不通過\t{mode}\t{src}\t預期 {S(exp)}\t得到 {S(got)}\t{ref[0] if ref else ''}")
    print(f"通過 {ok}／{ok + bad}")


def main(argv):
    mode, verbose, words = "place", False, []
    it = iter(argv)
    for a in it:
        if a == "-t":
            return run_tests(next(it))
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
    print(f"# 依波斯語{'人名' if mode == 'person' else '地名'}表譯寫（中國大陸標準，繁體輸出；常識性與伊斯蘭慣用譯名以通行為準）")
    for w in words:
        try:
            zh, info = translit(w, mode)
        except ValueError as e:
            print(f"{w}\t（{e}）")
            continue
        line = f"{w}\t{S(zh)}"
        if mode == "place":
            g = generic_variant(w)
            if g:
                line += f"\t通名意譯：{S(g)}"
        a = appendix_a(w)
        if a:
            line += f"\t附錄A慣譯：{S('、'.join(a))}"
        print(line)
        if verbose:
            for part, tr, nt, _ in info:
                print(f"    {part}：{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
