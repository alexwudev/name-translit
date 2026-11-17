"""西班牙語音譯工具：輸入西班牙文地名或人名，依中維「外語譯音表/西班牙語」吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 es_translit_table.json（由 es_translit_build_table.py 從譯音表維基原始碼重建）：
  人名表＝新華社《世界人名翻译大辞典》（2007）；
  地名表＝GB/T 17693.5-2009《外语地名汉字译写导则 西班牙语》（表 1 與注 1–8；第 5 章細則、表 2–4 示例、
          附錄 A 常用人名、附錄 B 常用通名另從標準 PDF 讀出，寫在本檔）。
  兩表都是中國大陸標準，頁面明說不適用於台灣譯名：台灣已有通行譯名時以通行為準，本工具只給參考。
  譯名一律以繁體字輸出。

輸入格式：直接輸入西班牙文拼寫（大小寫不拘），重音符號（á é í ó ú）、ñ、ü 要照原文保留：
  西班牙文拼寫幾乎就是讀音，表也是依字母排的，所以不必輸入國際音標；
  重音符號用來判斷元音分讀（Benalúa→貝納盧阿、Jaén→哈恩），漏打會把該分讀的元音合譯。

用法：
  python -X utf8 es_translit.py Córdoba "Almadén de la Plata" "Río Grande"   （預設地名表）
  python -X utf8 es_translit.py -p "Mario Vargas Llosa" "Hugo Chávez"         （-p 人名表，名與姓間加「·」）
  python -X utf8 es_translit.py -v Extremadura                                 （-v 列出音節切分與每個字的來源）
  python -X utf8 es_translit.py -f 名單.txt                                    （每行一個原文）
  其他選項：-w 用女名用字（瑪、娜、莉、麗、琳、莎、婭…）；-l 地名的 ll 按拉丁美洲讀音（y 列，Castilla→卡斯蒂亞）；
           -r 純照表譯，不套附錄 A 慣用人名；--test 檔.tsv 跑測試（每行：模式<Tab>原文<Tab>預期<Tab>出處）。
  模組用法：from es_translit import translit, S；translit(text, "place"|"person") 回傳 (譯名, info)，
           譯名是表上原字（地名表為簡體），S() 轉繁體；另有 generic_variant(text) 給通名意譯版本。

處理的規則：
  - 拼寫→讀音：h 不發音（ch 除外；元音間的 h 視為分讀界線，Zahara→薩阿拉）；ph→f、th→t、tch→ch、ck/cq→k；
    qu、gu、gü 加元音當一個輔音（que→克、gui→吉、gua→瓜、güe→圭）；c、g 在 e、i 前照表上 ce/ci/ge/gi 那格；
    rr→r、ss→s，其他雙寫輔音按一個；z 照 s 列；w 照 v 列；y 在元音前是輔音（y 列），否則當元音 i。
  - b、v（人名表說明）：b 在詞中（m、n 後除外）照 v 列（Gabriel→加夫列爾），v 在詞首照 b 列（Vargas→巴爾加斯）；
    地名表：b、v 在詞首或 m、n 後照 b 列，其餘照 v 列（Córdoba→科爾多瓦、Villas→比利亞斯）。
  - m 在 b、p 前按 n 譯（Cambre→坎布雷、Pampa→潘帕、Compostela→孔波斯特拉）。
  - x：在輔音前按 s 列；在元音之間、詞尾（人名表：元音前）按「克」加 s 列（Extremadura→埃斯特雷馬杜拉、Loxicha→洛克西查）。
  - cc（地名）：在 a、o、u 前按一個 c（Occopata→奧科帕塔），在 e、i 前按「克」加 c（Occitania→奧克西塔尼亞）；
    人名表 cc 與 c 同欄，按一個 c。sc 在 e、i 前按 s 列（Oscilación→奧西拉西翁）。
  - ll：人名與地名預設照「利」列（西班牙本土、人名命名的地名）；-l 改照 y 列（拉丁美洲讀音），地名有 ll 時也會另列這個版本。
  - 元音：只合譯表上有的組合（ai/ay/ae、au/ao、ei/ey、ia、ie、iu、ua、ue/uei/uey、ui/uy、uo、ou）；
    oa、oe、io 分開譯（ion 例外照 ion 列）；重音落在弱元音上（í、ú）時與相鄰元音分讀（ía 例外仍照 ia 列，María→瑪麗亞）；
    兩個強元音中後一個帶重音也分讀（Jaén→哈恩）。uai 按 u 加 ai；ain 按 ai 加「恩」；ian 按 i 列加「安」。
  - 音節尾的 n 併入元音列（an、en、in、on、un、ien、ion、uan、uen…）；其餘音節尾輔音用零行字（爾、斯、克…）。
  - 音節切分：元音間的輔音群，pl pr bl br fl fr cl cr gl gr tr dr kl kr tl 整組歸下一音節，其餘最後一個歸下一音節。
  - 同一格有兩個字（特/泰、赫/黑、克/凱、奧/歐）時取第一個，-v 會列出另一個；表上空格先改用相近欄（gu→g、ñ→n、ll→l…），
    再不行就輔音零行字加元音零行字，並在 -v 註明。
  - 弗用於譯名詞首，夫用於詞中與詞尾；地名的东、南、西在開頭改栋、楠、锡，海在結尾改亥（注 4）。
  - 地名細則：san、santa、santo 譯「聖」；連詞 y 譯「和」（5.1.4.1）；冠詞與介詞照音譯（El Dorado→埃爾多拉多）；
    多詞地名譯名達 8 字時（5.1.12 寫「超過八個字」，但示例 Guadalupe Victoria 8 字也加，從示例），有介詞 de/del 就在介詞前加「-」（Almadén de la Plata→阿爾馬登-德拉普拉塔），
    否則各詞間加「-」（Guadalupe Victoria→瓜達盧佩-維多利亞），冠詞與 San 跟著後一詞。
  - 附錄 A 常用人名（Carlos→卡洛斯、José→何塞、Santiago→聖地亞哥…62 個）預設直接套用（導則 4.3 慣用譯名沿用；
    新華社人名辭典對這些名字也用同樣的慣譯）；-r 關掉。
  - 通名意譯（附錄 B 常用者）另列一欄：首詞是 Río、Sierra、Lago、Isla、Cabo、Puerto… 時，
    去掉通名與其後的 de/del/冠詞，專名音譯加通名（Sierra de Guadarrama→瓜達拉馬山）。通名常也是專名的一部分
    （Monte Alegre→蒙特阿萊格雷），所以主欄一律全音譯，由使用者自選。

沒做或做不到的：
  - 導則 4.3 的其他慣用譯名（La Paz→拉巴斯、Madrid→馬德里）、5.1.5／5.1.7／5.1.8 意譯的專名（Islas de Barlovento→向風群島、
    Treinta y Tres→三十三人城）、5.1.3.2 說明位置的介詞短語（Aranda de Duero→杜羅河畔阿蘭達）、5.1.6 以人名命名的地名要加「·」，
    都要查詞典或人工判斷，工具不處理。
  - 新華社人名辭典的大量慣譯（García→加西亞、Javier→哈維爾、音節尾 r 常省譯）不照表，工具照表譯，會與辭典不同；
    人名請先查《世界人名翻译大辞典》、新華社資料庫或中維條目。
  - 重音符號漏打時無法判斷分讀；外來名字（英語、加泰隆語、巴斯克語、納瓦特爾語的 x、tz、tl 等）照西班牙語拼寫規則譯，可能不準。
  - 詞首 x 在元音前一律按「克」加 s（墨西哥地名常讀 [x] 或 [s]，如 Xalapa），請自行查證。
  - 人名的名與姓之間、介詞 de 一律加「·」；新華社對複姓（García Márquez）與 y 的連字號寫法未自動處理。
"""
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
import opencc  # pip install --user opencc-python-reimplemented
# 譯名一律以繁體字輸出；s2t 會把音譯用的里、于、占、托、采轉成裏、於、佔、託、採，要轉回
_s2t = opencc.OpenCC("s2t").convert
S = lambda x: "".join(_s2t(c) for c in x).translate(str.maketrans("裏於佔託採佈羣誇", "里于占托采布群夸"))  # 逐字轉繁（整串轉會出「拉剋」）；音譯用字被誤轉的轉回
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_translit_table.json"), encoding="utf-8"))

VOW = "aeiouáéíóúü"
STRONG = "aeoáéó"
STRIP = str.maketrans("áéíóúü", "aeiouu")
CLUSTER = {"pl", "pr", "bl", "br", "vl", "vr", "fl", "fr", "cl", "cr", "kl", "kr", "gl", "gr", "tr", "dr", "tl"}
FALLBACK = {"gu": "g", "gü": "g", "gh": "g", "qu": "k", "ñ": "n", "ll": "l", "y": "", "k": "c"}
# 人名表沒有的拼法組合（荷蘭、英語式拼寫）不拿來合譯
SKIP_KEYS = {"aa", "ah", "een", "aan", "ung", "ing", "yhe", "yie"}

# GB/T 17693.5-2009 附錄 A 西班牙語地名中常用人名譯寫表（鍵去掉重音、小寫）
APPENDIX_A = {
    "agustin": "阿古斯丁", "alberto": "阿尔韦托", "alejandro": "亚历杭德罗", "alfonso": "阿方索", "ana": "安娜",
    "andres": "安德烈斯", "anton": "安东", "antonio": "安东尼奥", "asuncion": "亚松森", "bolivar": "玻利瓦尔",
    "carlos": "卡洛斯", "catalina": "卡塔利娜", "catarina": "卡塔里娜", "cecilia": "塞西利娅", "cervantes": "塞万提斯",
    "cid": "熙德", "colon": "科隆", "concepcion": "康塞普西翁", "constancia": "康斯坦西亚", "cristobal": "克里斯托瓦尔",
    "domingo": "多明各", "don": "唐", "doña": "唐娜", "eduardo": "爱德华多", "elena": "埃莱娜", "eugenio": "欧亨尼奥",
    "eulalia": "欧拉利娅", "fernando": "费尔南多", "francisco": "弗朗西斯科", "franco": "佛朗哥", "gomez": "戈麦斯",
    "gonzalez": "冈萨雷斯", "isabel": "伊莎贝尔", "jimenez": "希门尼斯", "joaquin": "华金", "jorge": "豪尔赫",
    "jose": "何塞", "juan": "胡安", "juana": "胡安娜", "juanito": "华尼托", "leon": "莱昂", "luis": "路易斯",
    "magdalena": "玛格达莱娜", "manuel": "曼努埃尔", "margarita": "玛加丽塔", "maria": "玛丽亚", "mariana": "玛丽亚娜",
    "marina": "马丽娜", "marta": "玛尔塔", "martin": "马丁", "nicolas": "尼古拉斯", "o'higgins": "奥伊金斯",
    "pablo": "巴勃罗", "quixote": "吉诃德", "rafael": "拉斐尔", "rita": "丽塔", "rosa": "罗莎", "rosalia": "罗萨莉娅",
    "sanchez": "桑切斯", "santiago": "圣地亚哥", "silva": "席尔瓦", "sofia": "索菲亚", "teresa": "特雷莎",
    "vicente": "维森特", "victoria": "维多利亚",
}
# 附錄 B 常用通名（只收常見者；一詞多義取最常用的意思）
GENERIC = {
    "rio": "河", "río": "河", "arroyo": "溪", "lago": "湖", "laguna": "潟湖", "embalse": "水库", "represa": "水库",
    "sierra": "山", "serrania": "山", "serranía": "山", "cordillera": "山脉", "cerro": "山", "monte": "山", "pico": "峰",
    "volcan": "火山", "volcán": "火山", "nevado": "雪山", "isla": "岛", "islas": "群岛", "isleta": "岛", "islote": "岛",
    "cayo": "岛", "archipielago": "群岛", "archipiélago": "群岛", "peninsula": "半岛", "península": "半岛",
    "cabo": "角", "punta": "角", "bahia": "湾", "bahía": "湾", "golfo": "湾", "ensenada": "海湾", "caleta": "湾",
    "estrecho": "海峡", "canal": "运河", "puerto": "港", "valle": "谷地", "llano": "平原", "llanos": "平原",
    "desierto": "沙漠", "costa": "海岸", "playa": "海滩", "salar": "盐沼", "meseta": "高原", "altiplano": "台地",
    "ciudad": "城", "villa": "镇", "provincia": "省", "departamento": "州", "municipio": "市", "distrito": "区",
    "mar": "海", "oceano": "洋", "océano": "洋", "cascada": "瀑布", "salto": "瀑布", "quebrada": "峡",
    "fortin": "堡", "fortín": "堡", "castillo": "城堡", "parque": "公园", "barranco": "峡谷",
}
ARTICLES = {"el", "la", "los", "las"}
PREPS = {"de", "del"}
SAINTS = {"san", "santa", "santo"}


def low(w):
    return unicodedata.normalize("NFC", w.lower())


def plain(w):
    return low(w).translate(STRIP)  # 去重音（ñ 保留），查附錄與通名用


def tokens(word, mode, latam=False):
    """把一個詞拆成 [('C', 欄, 原字) | ('V', 元音) | ('|',)]。"""
    w = low(word).replace("'", "").replace("’", "")
    for a, b in (("tch", "ch"), ("ph", "f"), ("th", "t"), ("ck", "k"), ("cq", "k")):
        w = w.replace(a, b)
    out, i, n = [], 0, len(w)
    while i < n:
        c, nx = w[i], w[i + 1] if i + 1 < n else ""
        nx2 = w[i + 2] if i + 2 < n else ""
        if c in VOW and c != "ü":
            out.append(("V", c)); i += 1; continue
        if c == "h":
            if out and out[-1][0] == "V" and nx in VOW:
                out.append(("|",))  # 元音間的 h：分讀
            i += 1; continue
        if c == "c" and nx == "h":
            out.append(("C", "ch", "ch")); i += 2; continue
        if c == "g" and nx == "h":
            out.append(("C", "gh", "gh")); i += 2; continue
        if c == "q" and nx == "u" and nx2 and nx2 in VOW:
            out.append(("C", "qu", "qu")); i += 2; continue
        if c == "q":
            out.append(("C", "k", "q")); i += 1; continue
        if c == "g" and nx == "ü" and nx2 and nx2 in VOW:
            out.append(("C", "gü", "gü")); i += 2; continue
        if c == "g" and nx == "u" and nx2 and nx2 in VOW and nx2 not in "uú":
            out.append(("C", "gu", "gu")); i += 2; continue
        if c == "l" and nx == "l":
            out.append(("C", "y" if latam else "ll", "ll")); i += 2; continue
        if c == "c" and nx == "c":
            if mode == "place" and nx2 and nx2 in "eiéí":
                out.append(("C", "k", "c")); out.append(("C", "c", "c"))
            else:
                out.append(("C", "c", "cc"))
            i += 2; continue
        if c == "s" and nx == "c" and nx2 and nx2 in "eiéí":
            out.append(("C", "s", "sc")); i += 2; continue
        if c == "x":
            prev_v = bool(out) and out[-1][0] == "V"
            if nx and nx not in VOW:
                out.append(("C", "s", "x"))
            elif mode == "person" or not nx or prev_v or not out:
                out.append(("C", "k", "x")); out.append(("C", "s", "x"))
            else:
                out.append(("C", "s", "x"))
            i += 1; continue
        if c == "y":
            if nx and nx in VOW and nx != "ü":
                out.append(("C", "y", "y"))
            else:
                out.append(("V", "i"))
            i += 1; continue
        if c == nx and c not in "lc":  # rr、ss 與其他雙寫輔音按一個
            i += 1; continue
        if c in "bvw":
            first = not out
            after_mn = bool(out) and out[-1][0] == "C" and out[-1][2] in ("m", "n")
            if mode == "place":
                col = "b" if (c != "w" and (first or after_mn)) else "v"
            elif c == "b":
                col = "b" if (first or after_mn) else "v"
            elif c == "v":
                col = "b" if first else "v"
            else:
                col = "v"
            out.append(("C", col, c)); i += 1; continue
        if c == "m" and nx in ("b", "p", "v"):
            out.append(("C", "n", "m")); i += 1; continue
        col = {"z": "s", "ç": "s"}.get(c, c)
        if c == "k" and mode == "place":
            col = "k"
        if c.isalpha():
            out.append(("C", col, c))
        i += 1
    return out


def syllables(toks):
    """切成 [onset 輔音串, 元音串（含 '|'）, coda 輔音串]。"""
    syl, i, n = [], 0, len(toks)
    cur_on = []
    while i < n and toks[i][0] == "C":
        cur_on.append(toks[i]); i += 1
    if i >= n:
        return [[cur_on, [], []]]
    while i < n:
        nuc = []
        while i < n and toks[i][0] in ("V", "|"):
            nuc.append(toks[i]); i += 1
        cons = []
        while i < n and toks[i][0] == "C":
            cons.append(toks[i]); i += 1
        if i >= n:
            syl.append([cur_on, nuc, cons]); break
        if len(cons) >= 2 and (cons[-2][2][-1:] + cons[-1][2][:1]) in CLUSTER and cons[-2][2] not in ("x", "cc", "sc"):
            coda, nxt = cons[:-2], cons[-2:]
        elif cons:
            coda, nxt = cons[:-1], cons[-1:]
        else:
            coda, nxt = [], []
        syl.append([cur_on, nuc, coda])
        cur_on = nxt
    return syl


def split_vowels(nuc, rows):
    """把元音（含分讀記號）切成表上有的組。回傳 [(鍵, 原字串)]。"""
    keys = sorted((k for k in rows if all(ch in "aeiou" for ch in k) and k not in SKIP_KEYS), key=len, reverse=True)
    groups, buf = [], ""
    for t in nuc:
        if t[0] == "|":
            if buf:
                groups.append(buf); buf = ""
        else:
            buf += t[1]
    if buf:
        groups.append(buf)
    parts = []
    for g in groups:
        i = 0
        while i < len(g):
            if g[i:i + 3].translate(STRIP) == "uai":
                parts.append(("u", g[i])); i += 1; continue
            for k in keys:
                seg = g[i:i + len(k)]
                if len(seg) < len(k) or seg.translate(STRIP) != k:
                    continue
                ok = True
                for j in range(1, len(seg)):
                    if seg[j] in "íú" or (seg[j] in "áéó" and seg[j - 1] in STRONG):
                        ok = False
                    if seg[j - 1] in "íú" and not (seg[j - 1] == "í" and seg[j] in "aá" and len(seg) == 2):
                        ok = False
                if ok:
                    parts.append((k, seg)); i += len(k); break
            else:
                parts.append((g[i].translate(STRIP), g[i])); i += 1
    return parts


def pick(cell, note, label, female=False):
    if not cell or not cell["main"]:
        return None
    if female:
        for a in cell["alt"]:
            if a in FEMALE:
                return a
    if len(cell["main"]) > 1 or cell["alt"]:
        note.append(f"{label}：取「{cell['main'][0]}」，另有 {'、'.join(cell['main'][1:] + cell['alt'])}")
    return cell["main"][0]


FEMALE = set("娅婭玛瑪娜莉丽麗琳妮蕾黛莎丝絲珍蓮莲萝蘿")


def lookup(rows, zero, vkey, col, note, label, female):
    """查（元音列, 輔音欄）；空格依序改用相近欄、輔音零行＋元音零行。"""
    row = rows.get(vkey)
    if row is not None:
        cell = row.get(col)
        # un/uen 同列兩字（地名 m 欄「蒙/门」）：un 取前、uen 取後
        if cell and len(cell["main"]) == 2 and vkey == "uen" and col == "m":
            return cell["main"][1]
        ch = pick(cell, note, label, female)
        if ch:
            return ch
        fb = FALLBACK.get(col)
        if fb is not None and fb != col:
            ch = pick(row.get(fb), note, label, female)
            if ch:
                note.append(f"{label}：表上此格空，改用 {fb or '元音'} 欄「{ch}」")
                return ch
    # 再不行：輔音零行＋元音逐字
    head = ""
    if col:
        zc = zero.get(col) or zero.get(FALLBACK.get(col, ""), None)
        head = (zc["main"][0] if zc and zc["main"] else "?")
    tail = ""
    sub = vkey
    if row is None or not row.get("") or not row[""]["main"]:
        tail = "".join(rows[c][""]["main"][0] for c in sub if c in rows)
    else:
        tail = row[""]["main"][0]
    note.append(f"{label}：表上無此格，按「{head}」加「{tail}」")
    return head + tail


def translit_word(word, mode, latam=False, female=False):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    toks = tokens(word, mode, latam)
    sy = syllables(toks)
    res, notes, trace = [], [], []

    def zchar(col, label):
        if mode == "place" and col == "k":
            col = "c"
        cell = zero.get(col) or zero.get(FALLBACK.get(col, ""))
        ch = pick(cell, notes, label) if cell else None
        return ch or "?"

    for idx, (on, nuc, coda) in enumerate(sy):
        for c in on[:-1]:
            ch = zchar(c[1], f"{c[2]}（單獨）"); res.append(ch); trace.append(f"{c[2]}→{ch}")
        c0 = on[-1] if on else None
        if not nuc:
            if c0:
                ch = zchar(c0[1], f"{c0[2]}（單獨）"); res.append(ch); trace.append(f"{c0[2]}→{ch}")
            for c in coda:
                ch = zchar(c[1], f"{c[2]}（音節尾）"); res.append(ch); trace.append(f"{c[2]}→{ch}")
            continue
        parts = split_vowels(nuc, rows)
        rest = list(coda)
        # 音節尾 n 併入元音列
        if rest and rest[0][1] == "n" and rest[0][2] in ("n", "m") and not (len(rest) > 1 and rest[1][1] == "y"):
            k, s = parts[-1]
            if k + "n" in rows and k + "n" not in SKIP_KEYS:
                parts[-1] = (k + "n", s + "n"); rest = rest[1:]
            elif len(k) == 2 and k[0] == "i" and k[1:] + "n" in rows:  # ian→i＋an
                parts[-1:] = [("i", s[0]), (k[1:] + "n", s[1:] + "n")]; rest = rest[1:]
        for pi, (vk, vs) in enumerate(parts):
            col = c0[1] if (pi == 0 and c0) else ""
            if mode == "place" and col == "k":
                col = "qu" if vk[0] in "ei" else "c"
            lab = f"{c0[2] if (pi == 0 and c0) else ''}{vs}"
            ch = lookup(rows, zero, vk, col, notes, lab, female)
            res.append(ch); trace.append(f"{lab}→{ch}")
        for c in rest:
            ch = zchar(c[1], f"{c[2]}（音節尾）"); res.append(ch); trace.append(f"{c[2]}→{ch}")
    s = "".join(res)
    if s.startswith("夫"):
        s = "弗" + s[1:]
    s = s[:1] + s[1:].replace("弗", "夫")
    sy_txt = "-".join("".join(c[2] for c in on) + "".join(x[1] if x[0] == "V" else "|" for x in nuc)
                      + "".join(c[2] for c in coda) for on, nuc, coda in sy)
    return s, sy_txt, trace, notes


def _word(part, mode, latam, female, raw, info):
    key = plain(part)
    if not raw and key in APPENDIX_A:
        zh = APPENDIX_A[key]
        info.append((part, "附錄A", [f"附錄 A 慣用：{zh}"], []))
        return zh
    s, sy, tr, nt = translit_word(part, mode, latam, female)
    info.append((part, sy, tr, nt))
    return s


def translit(text, mode, latam=False, female=False, raw=False):
    info = []
    if mode == "person":
        out = []
        for name in text.strip().split():
            out.append("-".join(_word(p, mode, latam, female, raw, info) for p in name.split("-") if p))
        return "·".join(out), info
    # 地名：分組（冠詞、San 跟後一詞；de/del 開新組並帶到下一個專名詞）
    words = [w for w in re.split(r"[\s]+", text.strip()) if w]
    zh_words, groups, cur, has_prep = [], [], [], False
    for w in words:
        lw = plain(w)
        if lw == "y":
            zh = "和"
        elif lw in SAINTS:
            zh = "圣"
        else:
            zh = _word(w, mode, latam, female, raw, info) if lw not in ("de", "del") else None
            if zh is None:
                zh = "德" if lw == "de" else "德尔"
                info.append((w, "介詞", [f"{w}→{zh}"], []))
        zh_words.append((lw, zh))
    for lw, zh in zh_words:
        if lw in PREPS:
            has_prep = True
            if cur:
                groups.append(cur)
            cur = [zh]
        elif lw == "y":
            if cur:
                groups.append(cur)
            groups.append(["和"]); cur = []
        else:
            cur.append(zh)
            if not (lw in ARTICLES or lw in SAINTS):
                if not has_prep:
                    groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    joined = ["".join(g) for g in groups]
    total = sum(len(x) for x in joined)
    if len(joined) > 1 and total >= 8:  # 5.1.12 寫「超過八個字」，但示例 Guadalupe Victoria（8 字）也加了連接號，從示例
        out = ""
        for k, g in enumerate(joined):
            if k == 0 or g == "和" or joined[k - 1] == "和":
                out += g
            else:
                out += "-" + g
    else:
        out = "".join(joined)
    # 注 4：望文生義
    for a, b in (("东", "栋"), ("南", "楠"), ("西", "锡"), ("東", "棟")):
        if out.startswith(a):
            out = b + out[1:]
    if out.endswith("海"):
        out = out[:-1] + "亥"
    return out, info


def generic_variant(text, latam=False, female=False, raw=False):
    """首詞是常用通名時，回傳專名音譯＋通名意譯（附錄 B）。"""
    words = text.split()
    if len(words) < 2 or plain(words[0]) not in {plain(k) for k in GENERIC}:
        return None
    g = next(v for k, v in GENERIC.items() if plain(k) == plain(words[0]))
    rest = words[1:]
    while rest and plain(rest[0]) in PREPS | ARTICLES:
        rest = rest[1:]
    if not rest:
        return None
    zh, _ = translit(" ".join(rest), "place", latam, female, raw)
    return zh + g


def run_tests(path):
    ok, bad = 0, []
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        mode, src, exp = f[0], f[1], f[2]
        src_note = f[3] if len(f) > 3 else ""
        latam = mode == "place_la"
        m = "person" if mode == "person" else "place"
        got = S(translit(src, m, latam)[0])
        if got == S(exp):
            ok += 1
        else:
            bad.append((mode, src, S(exp), got, src_note))
    print(f"通過 {ok}／{ok + len(bad)}")
    for b in bad:
        print("不通過：" + "\t".join(b))


def main(argv):
    mode, verbose, latam, female, raw, words = "place", False, False, False, False, []
    it = iter(argv)
    for a in it:
        if a == "-p":
            mode = "person"
        elif a == "-v":
            verbose = True
        elif a == "-l":
            latam = True
        elif a == "-w":
            female = True
        elif a == "-r":
            raw = True
        elif a == "--test":
            return run_tests(next(it))
        elif a == "-f":
            words += [l.strip() for l in open(next(it), encoding="utf-8") if l.strip()]
        else:
            words.append(a)
    if not words:
        sys.exit(__doc__)
    print(f"# 依{'人名' if mode == 'person' else '地名'}表譯寫（中國大陸標準，譯名一律以繁體字輸出；台灣有通行譯名時以通行為準）")
    for w in words:
        zh, info = translit(w, mode, latam, female, raw)
        line = f"{w}\t{S(zh)}"
        if mode == "place":
            g = generic_variant(w, latam, female, raw)
            if g:
                line += f"\t通名意譯：{S(g)}"
            if not latam and "ll" in low(w):
                line += f"\tll 按拉丁美洲讀音：{S(translit(w, mode, True, female, raw)[0])}"
        print(line)
        if verbose:
            for part, sy, tr, nt in info:
                print(f"    {part}：{sy}｜{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
