"""德語音譯工具：輸入德文地名或人名（德語正寫法拼寫），依中維「外語譯音表/德語」吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 de_translit_table.json（由 de_translit_build_table.py 從中維頁面原始碼重建）：
  地名表＝GB/T 17693.3-2009《外语地名汉字译写导则 德语》（民政部地名研究所），另讀過該國標的掃描 PDF，
          取用其中的附錄 A 人名例、附錄 B 通名意譯表、附錄 C 常用構詞成分譯寫表（寫在本檔 COMPONENTS／GENERIC）。
  人名表＝新華社《世界人名翻译大辞典》（2007）。
  兩表都是中國大陸標準，譯名一律以繁體字輸出；台灣有通行譯名、或屬慣譯名（慕尼黑、漢堡、萊比錫、隆美爾）時以通行為準，
  本工具只給參考。

用法：
  python -X utf8 de_translit.py Gütersloh Eberswalde "Bernkastel-Kues"   （預設地名表）
  python -X utf8 de_translit.py -p "Heinz Guderian" "Erich Hoepner"       （-p 人名表，名與姓間加「·」）
  python -X utf8 de_translit.py -v Leverkusen                              （-v 列出音節切分與每字來源）
  python -X utf8 de_translit.py -f 名單.txt                                （每行一個原文）
  模組用法：from de_translit import translit, S；translit(原文, "place"|"person") 回傳 (譯名, info)；
            地名另有 variants(原文) 回傳「通名意譯」「修飾詞意譯」等版本。

輸入格式：德語正寫法（可含 ä ö ü ß；也接受 ae／oe／ue 寫法）。譯音表依讀音排，本工具用德語拼寫規則推讀音，
  不接受國際音標輸入。

處理的表上規則（含說明與補充說明）：
  - 字母組：bb pp dd tt gg ck ff mm ll rr 等雙寫按單輔音；nn 前一個 n 併入元音（Johannes→約翰內斯）。
    th、dt→t；ph、v→f（v 在兩元音之間按 w 列：Leverkusen→萊沃庫森）；rh→r；ß、ss→s；tz、z、zz、ds、ths→ts；
    tsch、tzsch、zsch、tch、tzch→「奇」列；pf 按 p、f 分譯；x、chs 按 k＋s（Sachsen→薩克森）；
    c 在 a o u l r 前按 k、在 e i y ä ö 前按 ts；ch 在 i e ä ö ü ei eu l r n 後按「希」列、在 a o u au 後按「赫」列，
    詞首 ch 在 a o u l r 前按 k（Christ→克里斯特）；詞尾 -ig 的 g 譯「希」；詞首 sp、st 的 s 譯「施」；
    h 在元音後、輔音或詞尾前為長音符號不譯，詞首、輔音後、兩元音間譯「赫」列；qu 按補充說明譯夸／奎／昆。
  - 元音：aa ah→a；ee eh ä äh ae→e 行；ie ih→i；oo oh→o；ö öh oe oey→ö 行；ü üh ue ui→ü 行；y 在元音後＝i、
    在輔音後＝ü（詞尾 -ky＝基）；ei ey ai ay→ei 行；eu äu→eu 行；oi→o 行；詞尾 -ow→o（Teltow→泰爾托）。
  - 鼻音尾：元音＋n／ng 併入 an、ang、en、in、ing、on、un、ein、eun 行（ön、än、eng→en；ün→in；地名 ung→on 行）。
    兩元音間的 ng 拆成 n｜g（-lingen→林根）。
  - 非重讀 e（第二音節起的單寫 e）按 ö（厄）行譯：Gütersloh→居特斯洛、Diemel→迪默爾；
    單寫 e 後接雙寫輔音視為重讀（Valepp→法萊普）。詞尾 -oe 的 e 為長音符號（Itzehoe→伊策霍）。
  - 雙寫輔音只譯一次；nn 只在兩元音之間拆開（Johannes），詞尾、輔音前的 nn 按 n（Hofmann→霍夫曼）。
    rh 只在詞首（Rheine）、rrh 按 r；詞中 rh 視為語素界線（Oberhausen→奧伯豪森）。
  - r：非重讀 -er 的 r 不譯（地名一律；人名只在 t d b p l 後不譯，-ner 譯「納」，其餘譯「爾」：Müller 米勒、Fischer 菲舍爾、
    Werner 維爾納）；元音＋er（Bauer、Meyer）譯「爾」；音節尾 r 後面還有同音節輔音時不譯（Waldberg→瓦爾德貝格、
    Hartl→哈特爾、Bernkastel→貝恩卡斯特爾）；單獨在音節尾的 r 譯「爾」（Herzog→赫爾佐格、Jürgen→于爾根）。
  - m 在 b、p 前按 n（Klempau→克倫保）。
  - 地名：詞首東／南／西改棟／楠／錫，詞尾海改亥；弗用於詞首、夫用於詞中詞尾；詞首（含意譯修飾詞之後）wei、wai 譯「魏」；
    附錄 C 常用構詞成分（-burg 堡、-dorf 多夫、-stein 施泰因、-stadt 施塔特、-ber 伯、-ner 訥…）在詞尾時照附錄譯；
    獨立成詞的通名（See、Berg、Kanal…）、修飾詞（Ober、Nieder、Neu、Alt、Groß…）照國標 5.1.9、5.2.1 意譯，
    Bad 照國標例音譯「巴特」；連寫的通名、修飾詞另列「意譯版本」由使用者自選（Oberhausen 慣譯奧伯豪森，不能一律意譯）。
    整個地名只有一個單音節詞時，鼻音不併入元音、改成兩字（國標 5.1.5：Bonn→博恩，國標慣譯為波恩）。
    詞尾 -aer 按 Dehnungs-e 譯 a（Kevelaer→凱沃拉爾）。通名前的派生形容詞 -er 按原形譯（國標 5.1.3：
    Haltener Talsperre→哈爾滕水庫）；詞首冠詞省譯（5.1.2），詞中冠詞、介詞音譯（Unter den Linden→溫特登林登）。
  - 人名：wei、wai 譯「魏」（補充說明）；詞首 dei 用「戴」（表上「代(戴)」）；von 譯「馮」、zu 譯「楚」（新華社慣例）；
    詞尾 -stein、-stadt、-stedt、-burg 照國標附錄 C（Eckstein→埃克施泰因）。
  - S()：除照 fi_translit 把 裏於佔託採佈羣 轉回外，另把 s2t 轉出的「誇」轉回音譯用字「夸」（Quarten→夸爾滕）。
  - 同一格有兩個字（萨/扎、因/云）取第一個（ün 取云）；女性用字（玛、娜、莉、丽、琳…）不自動套用，-v 會列出。

限制（做不到或沒做）：
  - 重音只用「第一音節重讀」推定；非首音節重讀的外來名（Berlin、Elisabeth）、首音節不重讀的前綴（be-、ge-、ver-）會譯錯 e。
  - 複合詞內部的語素界線無法從拼寫判斷：第二語素開頭的 sp／st（Eisenstein 已用附錄 C 處理，其他如 Weidenstetten 不行）、
    第二語素的重讀 e、連接用的 s（人名＋通名時省略，只處理 Ludwigs-、-igs 型）都可能出錯。
  - 下萊茵、威斯特法倫的 Dehnungs-e（Coesfeld、Soest、Raesfeld）除詞尾 -aer 外無法辨認，會照 ö／ä 譯。
  - 少數 y、eu 的例外讀音（Syke、Amadeus）、斯拉夫來源的 -ow 以外例外，照一般規則譯。
  - 新華社人名辭典的個別譯名（Ludwig 路德維希的「路」、Martin 馬丁不譯 r、Schmidt 施密特的「密」）多為慣例，表上推不出。
  - 音節尾 r 的去留新華社並不一致（Affermann 阿費爾曼、Ackermann 阿克曼），本工具照上述規則一律處理。
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
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "de_translit_table.json"), encoding="utf-8"))

VOWL = "aeiouyäöü"
# 國標附錄 C「德语地名常用构词成分译写表」（地名用；在詞尾、前面還有元音時才套用）
COMPONENTS = {
    "ach": "阿赫", "bach": "巴赫", "baum": "鲍姆", "bauer": "鲍尔", "ber": "伯", "berg": "贝格", "born": "博恩",
    "bronn": "布龙", "bruck": "布鲁克", "brück": "布吕克", "brunn": "布伦", "büll": "比尔", "buch": "布赫",
    "burg": "堡", "by": "比", "chen": "兴", "cken": "肯", "den": "登", "der": "德", "dow": "多",
    "dorf": "多夫", "feld": "费尔德", "felder": "费尔德", "fer": "弗", "furth": "富特", "gen": "根", "ger": "格",
    "grün": "格林", "hain": "海恩", "heid": "海德", "heim": "海姆", "hofen": "霍芬", "holz": "霍尔茨",
    "horst": "霍斯特", "hütten": "许滕", "kamp": "坎普", "ken": "肯", "ker": "克", "kirch": "基希",
    "kirchen": "基兴", "land": "兰", "laun": "劳恩", "leben": "雷本", "len": "伦", "ler": "勒", "lingen": "林根",
    "loch": "洛赫", "loh": "洛", "los": "洛斯", "meer": "梅尔", "mel": "默尔", "mer": "默", "mert": "梅特",
    "moos": "莫斯", "münd": "明德", "münde": "明德", "nach": "纳赫", "ner": "讷", "per": "珀", "point": "波因特",
    "ren": "伦", "reuth": "罗伊特", "run": "伦", "runn": "伦", "schaid": "沙伊德", "scheid": "沙伊特",
    "scheit": "沙伊特", "schen": "申", "scher": "舍", "sen": "森", "ser": "瑟", "ssig": "斯希", "sig": "斯希",
    "stadt": "施塔特", "statt": "施塔特", "stedt": "施泰特", "stein": "施泰因", "tach": "塔赫", "tal": "塔尔",
    "ten": "滕", "ter": "特", "thal": "塔尔", "than": "坦", "thann": "坦", "torf": "托夫", "tsch": "奇",
    "tum": "图姆", "um": "乌姆", "ver": "沃", "wald": "瓦尔德", "wang": "旺", "weier": "韦尔", "weiler": "韦勒",
    "worm": "沃姆", "zell": "采尔", "zen": "岑", "zer": "策",
}
# 人名也套用的構詞成分（多為詞中 st 讀 scht 的語素，表上規則推不出）：Eckstein→埃克施泰因、Vandenburg→范登堡
PERSON_COMP = {"stein", "stadt", "statt", "stedt", "burg"}
# 人名中的貴族前置詞（新華社慣例，如 Erich von Manstein→埃里希·馮·曼施泰因）
PARTICLE = {"von": "冯", "vom": "冯", "van": "范", "zu": "楚", "zur": "楚尔"}
# 國標附錄 B 通名意譯（取第一義）：獨立成詞時直接意譯；連寫在詞尾時列為「通名意譯」版本
GENERIC = {
    "see": "湖", "berg": "山", "bach": "河", "insel": "岛", "gebirge": "山脉", "kanal": "运河", "bucht": "湾",
    "hafen": "港", "fluss": "河", "wald": "森林", "talsperre": "水库", "stausee": "水库", "sund": "海峡",
    "tal": "河谷", "bergland": "山地", "becken": "盆地", "bodden": "浅海湾", "brücke": "桥", "burg": "堡",
    "dorf": "村", "ebene": "平原", "fels": "岩", "forst": "森林", "gipfel": "峰", "hochland": "高原",
    "horn": "峰", "hügel": "丘陵", "kap": "角", "kirche": "教堂", "land": "地区", "meer": "海", "moor": "沼泽",
    "quelle": "泉", "stadt": "城", "strom": "河", "teich": "池塘", "turm": "塔", "halbinsel": "半岛",
}
# 國標 5.1.9 對專名起修飾作用的形容詞意譯（獨立成詞或以連字號分開時）
MODIFIER = {
    "ober": "上", "obere": "上", "oberer": "上", "nieder": "下", "neu": "新", "neue": "新",
    "neuer": "新", "neuen": "新", "alt": "旧", "alte": "旧", "alter": "旧", "alten": "旧", "groß": "大",
    "große": "大", "großer": "大", "großen": "大", "gross": "大", "klein": "小", "kleine": "小", "kleiner": "小",
    "hohe": "上", "hohen": "上", "hoher": "上", "sankt": "圣", "st.": "圣",
    "nord": "北", "süd": "南", "ost": "东", "west": "西", "mittel": "中",
}
FUSED_MOD = ["nieder", "ober", "unter", "alten", "neu", "groß", "klein", "hohen"]
ARTICLES = {"der", "die", "das", "den", "dem", "des"}
SPECIAL_WORD = {"bad": "巴特"}  # 國標例：Bad Oeynhausen→巴特恩豪森

NASAL = {"a": "an", "e": "en", "E": "en", "ö": "en", "i": "in", "ü": "in", "o": "on", "u": "un",
         "ei": "ein", "eu": "eun"}
NASAL_NG = {"a": "ang", "i": "ing", "e": "en", "E": "en", "ö": "en", "o": "on", "ü": "ing"}
ROWOF = {"a": "a", "e": "e", "E": "e", "i": "i", "o": "o", "ö": "ö", "u": "u", "ü": "ü", "au": "au", "ei": "ei", "eu": "eu"}
ONSET2 = {(a, b) for a in ("b", "d", "g", "k", "p", "t", "f") for b in ("r", "l")} - {("d", "l"), ("t", "l")}
ONSET2 |= {("sch", "r"), ("sch", "l"), ("sch", "m"), ("sch", "n"), ("sch", "w"), ("sch", "p"), ("sch", "t"),
           ("k", "n"), ("g", "n"), ("ts", "w"), ("k", "w")}


# ---------- 拼寫 → 音段 ----------
def prep(w):
    w = w.lower().replace("ß", "ss")
    w = re.sub(r"aer$", "ar", w)  # Dehnungs-e（Kevelaer、Laer）
    w = re.sub(r"ow$", "o", w)   # 斯拉夫來源的 -ow
    w = re.sub(r"ky$", "ki", w)
    w = w.replace("äu", "eu").replace("aeu", "eu")
    w = re.sub(r"oe$", "o", w)   # 詞尾 -oe 的 e 是長音符號（Itzehoe→伊策霍）
    w = re.sub(r"(?<![qae])ue", "ü", w)  # Bauer、Neue 的 ue 不是 ü
    w = w.replace("ae", "ä").replace("oey", "ö").replace("oe", "ö").replace("oi", "o")
    w = re.sub(r"(?<![qae])ui", "ü", w)
    w = w.replace("ey", "ei").replace("ay", "ei").replace("ai", "ei")
    w = re.sub(r"^y(?=[aeiouäöü])", "j", w)
    w = re.sub(r"(?<=[aeiouäöü])y", "i", w)
    w = w.replace("y", "ü")
    w = w.replace("ph", "f").replace("th", "t").replace("dt", "t").replace("rrh", "r").replace("ck", "k")
    w = re.sub(r"^rh", "r", w)  # 詞中的 rh 多是語素界線（Oberhausen），只處理詞首 Rh、rrh
    w = w.replace("chs", "ks").replace("x", "ks")
    # 長音 h：元音後、接輔音或詞尾
    w = re.sub(r"(?<=[aeiouäöü])h(?![aeiouäöü])", "", w)
    w = re.sub(r"(?<=[aeiouäöü])h(?=[aeiouäöü])", "H", w)  # 兩元音間 h 要譯（Johannes）
    return w


def tokens(w):
    """回傳 [(kind, val, src)]：kind='C' 輔音（val＝欄鍵）或 'V' 元音（val＝行鍵；'e' 可能是非重讀 e，'E' 一定重讀）。"""
    out, i, n = [], 0, len(w)
    while i < n:
        c = w[i]
        rest = w[i:]
        prev = out[-1] if out else None
        if c in "aeiouäöü":
            for k, v in (("aa", "a"), ("ee", "E"), ("oo", "o"), ("ie", "i"), ("ei", "ei"), ("eu", "eu"), ("au", "au")):
                if rest.startswith(k):
                    out.append(("V", v, k)); i += 2; break
            else:
                out.append(("V", "E" if c == "ä" else c, c)); i += 1
            continue
        for k, v in (("tzsch", "tsch"), ("zsch", "tsch"), ("tsch", "tsch"), ("tzch", "tsch"), ("tch", "tsch"),
                     ("sch", "sch"), ("ths", "ts"), ("tz", "ts"), ("ts", "ts"), ("ds", "ts"), ("zz", "ts"), ("qu", "qu")):
            if rest.startswith(k):
                out.append(("C", v, k)); i += len(k); break
        else:
            if rest.startswith("ch"):
                nxt = w[i + 2:i + 3]
                if not out:
                    col = "k" if nxt in ("a", "o", "u", "l", "r", "") else "ch"
                elif prev[0] == "V":
                    col = "h" if prev[1] in ("a", "o", "u", "au") else "ch"
                else:
                    col = "ch"
                out.append(("C", col, "ch")); i += 2; continue
            if c == "c":
                nxt = w[i + 1:i + 2]
                out.append(("C", "ts" if nxt in ("e", "i", "ä", "ö", "ü") else "k", "c")); i += 1; continue
            if c == "z":
                out.append(("C", "ts", "z")); i += 1; continue
            if c == "v":
                nxt = w[i + 1:i + 2]
                between = prev and prev[0] == "V" and nxt in VOWL
                out.append(("C", "w" if between else "f", "v")); i += 1; continue
            if c == "H":
                out.append(("C", "h", "h")); i += 1; continue
            if c == "s" and i == 0 and w[1:2] in ("p", "t"):
                out.append(("C", "sch", "s")); i += 1; continue
            if c in "bpdtgkwfsmnlrjh":
                out.append(("C", c, c)); i += 1; continue
            i += 1  # 其他符號略去
    # 詞尾 -ig 的 g（含 -igs）譯「希」
    if len(out) >= 2 and out[-1][1] == "g" and out[-2][2] == "i":
        out[-1] = ("C", "ch", "g")
    # 雙寫輔音按單輔音；兩元音間的 nn 保留兩個（前一個併入元音：Johannes→約翰內斯）。
    # 單寫 e 後接雙寫輔音（Valepp、-stetten）視為重讀 e。
    res = []
    for k, t in enumerate(out):
        if res and t[0] == "C" and res[-1][0] == "C" and res[-1][1] == t[1]:
            if len(res) >= 2 and res[-2][0] == "V" and res[-2][1] == "e":
                res[-2] = ("V", "E", "e")
            if t[1] == "n" and k + 1 < len(out) and out[k + 1][0] == "V":
                res.append(t)
            continue
        res.append(t)
    return res


def syllabify(toks):
    """切成 [onset, nucleus(token), coda] 串列。"""
    vidx = [k for k, t in enumerate(toks) if t[0] == "V"]
    if not vidx:
        return [[toks, None, []]]
    sy = []
    start = 0
    for j, v in enumerate(vidx):
        onset = toks[start:v]
        if j + 1 < len(vidx):
            cl = toks[v + 1:vidx[j + 1]]
            if len(cl) == 0:
                coda, nxt = [], v + 1
            elif len(cl) >= 2 and (cl[-2][1], cl[-1][1]) in ONSET2:
                coda, nxt = cl[:-2], vidx[j + 1] - 2
            else:
                coda, nxt = cl[:-1], vidx[j + 1] - 1
        else:
            coda, nxt = toks[v + 1:], len(toks)
        sy.append([onset, toks[v], coda])
        start = nxt
    return sy


# ---------- 查表 ----------
def pick(cell, notes, label, second=False):
    if not cell or not cell["main"]:
        notes.append(f"{label}：表上此格為空")
        return None
    if len(cell["main"]) > 1 or cell["alt"]:
        notes.append(f"{label}：取「{cell['main'][1 if second and len(cell['main']) > 1 else 0]}」，表上另有 {'、'.join(cell['main'] + cell['alt'])}")
    return cell["main"][1 if second and len(cell["main"]) > 1 else 0]


def cons_alone(col, t, notes, label):
    if col == "qu":
        return "克"
    ch = pick(t["zero"].get(col), notes, f"{label}（單獨）")
    return ch or "?"


def syl_char(col, row, t, notes, label, second=False):
    """輔音欄＋元音行；表上該格空時拆成輔音零行＋元音零行。"""
    if col == "qu":
        if row in ("a",):
            return "夸"
        if row in ("e", "i"):
            return "奎"
        if row in ("en", "in", "un"):
            return "昆"
        return "克" + (syl_char("w", row, t, notes, label) or "")
    ch = pick(t["rows"].get(row, {}).get(col), notes, label, second)
    if ch:
        return ch
    if row in ("ein", "eun", "ing", "ang", "en", "in", "an", "on", "un"):
        base = {"ein": "ei", "eun": "eu", "ing": "i", "ang": "a", "en": "e", "in": "i", "an": "a", "on": "o", "un": "u"}[row]
        a = syl_char(col, base, t, notes, label)
        return a + ("恩" if row != "ing" and row != "ang" else "恩格")
    a = cons_alone(col, t, notes, label) if col else ""
    b = pick(t["rows"].get(row, {}).get(""), notes, label) or "?"
    return a + b


def translit_word(word, mode, mono_check=True):
    t = TABLE[mode]
    low = word.lower()
    w = prep(word)
    toks = tokens(w)
    sy = syllabify(toks)
    res, trace, notes = [], [], []
    nsyl = len(sy)
    for idx, (onset, nuc, coda) in enumerate(sy):
        last = idx == nsyl - 1
        if nuc is None:  # 沒有元音
            for c in onset:
                res.append(cons_alone(c[1], t, notes, c[2])); trace.append(f"{c[2]}→{res[-1]}")
            continue
        for c in onset[:-1]:
            ch = cons_alone(c[1], t, notes, c[2])
            res.append(ch); trace.append(f"{c[2]}（單獨）→{ch}")
        col = onset[-1][1] if onset else ""
        csrc = onset[-1][2] if onset else ""
        v = nuc[1]
        schwa = v == "e" and idx > 0
        row = "ö" if schwa else ROWOF[v]
        coda = list(coda)
        # m 在 b、p 前按 n
        nxt_on = sy[idx + 1][0] if idx + 1 < nsyl else []
        for k in range(len(coda)):
            nx = (coda[k + 1:] + list(nxt_on))[:1]
            if coda[k][1] == "m" and nx and nx[0][1] in ("b", "p"):
                coda[k] = ("C", "n", "m")
        # 鼻音併入
        merged = False
        if coda and coda[0][1] == "n":
            if len(coda) >= 2 and coda[1][1] == "g" and v in NASAL_NG:
                nr = NASAL_NG[v]
                if v == "u":
                    nr = "on" if mode == "place" else "un"
                row = nr; coda = coda[2:]; merged = True
            elif v in NASAL:
                row = NASAL[v]; coda = coda[1:]; merged = True
        # 單音節專名把鼻音併入時（國標 5.1.5，Bonn→波恩）改回兩字
        if merged and mode == "place" and nsyl == 1 and mono_check and len(coda) == 0 and len(onset) <= 1:
            row = "ö" if schwa else ROWOF[v]
            coda = [("C", "n", "n")]
            merged = False
            notes.append("單音節專名：鼻音不併入（國標 5.1.5）")
        # 元音＋er（Bauer、Meyer）：e 不譯
        hiatus_schwa = schwa and not onset and not merged
        label = f"{csrc}{nuc[2]}" + ("（非重讀）" if schwa and not merged else "")
        if hiatus_schwa:
            ch = ""
            trace.append(f"{nuc[2]}（元音後非重讀 e）→不譯")
        else:
            second = row == "in" and v == "ü" and col == ""
            # 魏：wei／wai（人名一律；地名只在詞首）
            if col == "w" and row in ("ei", "ein") and (mode == "person" or idx == 0):
                ch = "魏" if row == "ei" else "魏因"
                notes.append("wei／wai 譯魏（補充說明）")
            elif mode == "person" and schwa and last and coda and coda[0][1] == "r" and len(coda) == 1 and col == "n":
                ch = "纳"
                notes.append("人名詞尾 -ner 譯納（新華社慣例：Werner、Wagner）")
            else:
                ch = syl_char(col, row, t, notes, label, second)
            if mode == "person" and idx == 0 and col == "d" and row == "ei":
                ch = "戴"; notes.append("詞首代改戴（表上（戴）用於詞首）")
            trace.append(f"{label}→{ch}")
        res.append(ch)
        # 音節尾輔音
        for k, c in enumerate(coda):
            if c[1] == "r":
                after = coda[k + 1:]
                drop = False
                if schwa and not merged and not hiatus_schwa:
                    if not last or mode == "place":
                        drop = True
                    elif col in ("t", "d", "b", "p", "l", "n"):
                        drop = True
                elif after:
                    drop = True
                if drop:
                    trace.append("r→不譯"); continue
            ch2 = cons_alone(c[1], t, notes, c[2])
            res.append(ch2); trace.append(f"{c[2]}→{ch2}")
    s = "".join(res)
    if mode == "place" and s:
        for a, b in (("东", "栋"), ("南", "楠"), ("西", "锡")):
            if s.startswith(a):
                s = b + s[1:]; notes.append(f"詞首{a}改{b}")
        if s.endswith("海"):
            s = s[:-1] + "亥"; notes.append("詞尾海改亥")
    if s and s[0] == "夫":  # 零行「夫(弗)」：弗用於詞首（ö 行本來就是「弗」的格照表不動：Pfieffe→普菲弗）
        s = "弗" + s[1:]
    sy_txt = "-".join("".join(x[2] for x in on) + (nu[2] if nu else "") + "".join(x[2] for x in co) for on, nu, co in sy)
    return s, sy_txt, trace, notes


def comp_split(word, mode="place"):
    """詞尾是附錄 C 構詞成分、前面仍有元音時拆開（人名只用 PERSON_COMP 這幾個）。"""
    low = word.lower().replace("ß", "ss")
    keys = COMPONENTS if mode == "place" else PERSON_COMP
    for k in sorted(keys, key=len, reverse=True):
        kk = k.replace("ß", "ss")
        if low.endswith(kk) and len(low) > len(kk):
            stem = word[: len(word) - len(kk)] if len(word) == len(low) else word[: -len(k)]
            if len(kk) <= 3 and len(stem) >= 2 and stem[-1].lower() == kk[0] and stem[-2].lower() in VOWL:
                # Ammer＝Am-mer：短詞尾前的雙寫輔音只譯一次（Fuchsstadt 這類真複合詞不動）
                stem = stem[:-1]
            if not any(c in VOWL for c in stem.lower()):
                continue
            if len(kk) <= 3 and len(stem) < 2:
                continue
            return stem, k
    return None


def translit_one(word, mode="place", mono_check=True):
    low = word.lower()
    if mode == "place" and low in SPECIAL_WORD:
        return SPECIAL_WORD[low], low, [f"{word}→{SPECIAL_WORD[low]}（國標例）"], []
    sp = comp_split(word, mode)
    if sp:
        stem, k = sp
        notes = []
        if mode == "place" and stem.lower().endswith("igs") and k in ("burg", "hafen", "berg", "feld", "dorf", "heim", "stadt"):
            stem = stem[:-1]; notes.append("人名＋構詞成分之間的 s 不譯（國標 5.1.6）")
        s1, sy1, tr1, nt1 = translit_word(stem, mode, mono_check=False)
        s = s1 + COMPONENTS[k]
        if mode == "place" and s.endswith("海"):
            s = s[:-1] + "亥"
        return s, f"{sy1}+{k}", tr1 + [f"-{k}→{COMPONENTS[k]}（國標附錄 C）"], notes + nt1
    return translit_word(word, mode, mono_check)


def translit(text, mode="place"):
    out, info = [], []
    parts = re.split(r"(\s+|-)", text.strip())
    words = [p for p in parts if p and not p.isspace()]
    mono = len([p for p in words if p != "-"]) == 1
    first_real = True
    for i, part in enumerate(words):
        if part == "-":
            if mode == "place" and out and out[-1] not in ("-",) and not out[-1].endswith(tuple(MODIFIER.values())):
                out.append("-")
            continue
        low = part.lower()
        if mode == "place":
            if low in ARTICLES and first_real and i + 1 < len(words):
                info.append((part, "", ["詞首冠詞省譯（國標 5.1.2）"], [])); continue
            if low in MODIFIER and i + 1 < len(words):
                out.append(MODIFIER[low]); info.append((part, "", [f"{part}→{MODIFIER[low]}（修飾詞意譯，國標 5.1.9）"], []))
                first_real = False; continue
            if low in GENERIC and i > 0:
                out.append(GENERIC[low]); info.append((part, "", [f"{part}→{GENERIC[low]}（通名意譯，國標 5.2.1）"], []))
                continue
            nxt = words[i + 1].lower() if i + 1 < len(words) else ""
            pre = []
            if nxt in GENERIC and low.endswith("er") and len(low) > 4:
                part = part[:-2]; pre = ["派生形容詞 -er 按專名原形譯（國標 5.1.3）"]
            s, sy, tr, nt = translit_one(part, "place", mono)
            nt = pre + nt
        elif low in PARTICLE and i + 1 < len(words):
            s, sy, tr, nt = PARTICLE[low], "", [f"{part}→{PARTICLE[low]}（新華社慣例）"], []
        else:
            s, sy, tr, nt = translit_one(part, mode)
        first_real = False
        out.append(s); info.append((part, sy, tr, nt))
    if mode == "person":
        return "·".join(x for x in out if x != "-"), info
    txt = "".join(out)
    return txt.strip("-"), info


def variants(text):
    """地名的意譯版本：連寫在詞首的修飾詞（Oberweißbach→上魏斯巴赫）、連寫在詞尾的通名（Ammersee→阿默湖）。"""
    vs = []
    low = text.lower()
    if " " in low or "-" in low:
        return vs
    for m in FUSED_MOD:
        if low.startswith(m) and len(low) - len(m) >= 4 and low[len(m)] not in VOWL:
            rest = text[len(m):]
            s, _ = translit(rest, "place")
            vs.append(("修飾詞意譯", MODIFIER.get(m, MODIFIER.get(m.rstrip("en"), "?")) + s))
            break
    for g in sorted(GENERIC, key=len, reverse=True):
        if low.endswith(g) and len(low) - len(g) >= 3:
            if COMPONENTS.get(g) == GENERIC[g]:
                break  # 構詞成分本身已意譯（-burg 堡），不再另列（2026-11-17：Wolfsburg 曾多出「沃爾夫堡」）
            stem = text[: -len(g)]
            if stem.lower().endswith("s") and len(stem) > 3:
                stem = stem[:-1]  # 連接用的 s 省略（國標 5.1.6）
            s, _ = translit(stem, "place")
            vs.append(("通名意譯", s + GENERIC[g]))
            break
    return vs


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
            for name, v in variants(w):
                line += f"\t{name}：{S(v)}"
        print(line)
        if verbose:
            for part, sy, tr, nt in info:
                print(f"    {part}：{sy}｜{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
