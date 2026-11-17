"""法語音譯工具：輸入法文地名或人名（法文正字法拼寫），依中維「外語譯音表/法語」吐出漢字譯名（繁體）。

2026-11-17 寫。譯音表存在同目錄 fr_translit_table.json（由 fr_translit_build_table.py 解析中維原始碼重建）：
  地名表＝GB/T 17693.2-1999《外语地名汉字译写导则 法语》；
  人名表＝新華社《世界人名翻译大辞典》，另照中維「補充說明」收入《法语姓名译名手册（第二版）》附錄的常用前後綴。
  兩表都是中國大陸標準，頁面明說只適用於辭典與新華社資料庫尚未收錄的名字：
  巴黎、里昂、戴高樂、霞飛這類已有通行譯名的，以通行譯名為準，本工具只給參考。譯名一律以繁體字輸出。

用法：
  python -X utf8 fr_translit.py Bergerac Périgueux "Charleville-Mézières"   （預設地名表）
  python -X utf8 fr_translit.py -p "Raoul Salan" "Jean de Lattre de Tassigny"  （-p 人名表，名與姓間加「·」）
  python -X utf8 fr_translit.py -v Aurillac                                 （-v 列出讀音切分與每字來源）
  python -X utf8 fr_translit.py -f 名單.txt                                 （每行一個原文）
  python -X utf8 fr_translit.py -t [fr_translit_test.tsv]                   （跑測試檔，列出不通過的各筆）
  模組用法：from fr_translit import translit, S；translit("Bergerac", "place") 回傳 (簡體譯名, info)，S() 轉繁體。

輸入格式：法文原拼寫，要保留重音符號（é è ê à ç ï ô œ…）。譯音表的行列雖以字母標示，實際是依讀音分的
  （c、g 的軟硬音分欄，e 依開閉音節分行），所以本工具先依法語正字法把拼寫轉成「輔音欄＋元音行」的讀音序列，
  再查表。不接受國際音標輸入。

處理規則（表上的說明＋法語正字法）：
  - 不發音字母：h 不發音（在兩元音間時把前後隔成兩個音節）；詞尾 s、x、z、t、d、p、g 一般不發音
    （-st、-ct、-lt 的 t 照讀；元音後的 p 照讀；x 只在 au、eu、ou、oi、ieu 及多音節詞的 -aix 後不讀，其餘讀 [ks]）；
    詞尾 -nc、-rc 的 c 不讀（Leclerc 勒克萊爾）；-ient 的 en 讀 [ɑ̃]。
  - e 的讀法：é è ê ë、ei、ey、e 在雙寫輔音或兩個輔音前（閉音節）、詞尾 -er、-ez、-et、單音節詞的 -es 按「埃」行；
    詞首開音節與單音節詞的 e 按「厄」行；兩個輔音字母（ch、ph、th、gn 算一個）後的開音節 e 也按「厄」行；
    元音＋一個輔音＋e＋輔音＋元音時 e 不發音（地名，Rochefort 羅什福爾）；人名表只有開音節 e 一行，新華社譯名
    照譯（Augereau 奧熱羅、Pichegru 皮舍格呂），所以人名的詞中 e 一律按「厄」行。詞尾 e 不發音；地名表另有
    「e（詞尾）」行，輔音＋詞尾 e 照該行譯（-ne 訥、-le 勒、-re 爾、-ve 沃、-ce／-se 斯、-ge 日…）；人名表沒有此行，
    輔音單獨譯，但依新華社實例 -lle 與輔音後的 -le 譯「勒」（Nivelle 尼韋勒、Langle 朗格勒）、-ne／-nne 譯「納」（Lannes 拉納）。
  - 鼻化元音：in im yn ym ain aim ein eim un um、an am en em aen aon ean、on om、ien yen、ion yon、oin oim
    後面不接元音、也不是 nn／mm 時才按鼻化元音行譯，否則按一般音節譯。
  - 半元音：i、y 在元音前（輔音後先照「伊」行譯 i，再把後面的元音照「[伊]」欄譯）；y 在詞首或兩元音間按「[伊]」欄；
    -ill- 在元音後、-il 在元音後的詞尾發 [j]，在輔音後發 [ij]；[j]＋詞尾 e 譯「耶」（-ille 耶、-illy／-illi 伊）。
    ou、oi、oy、oua 照「烏」「瓦」行。
  - 輔音：c、g 在 e i y 前讀 [s]、[ʒ]（改查 s、j 欄）；ge 在 a o u 前讀 [ʒ]；gu 在 e i y 前讀 [g]；qu、q、ck、cq 讀 [k]；
    ch 在 l、r 前讀 [k]；ph→f、th→t、gn→[ɲ]；s 一律查 s 欄（表依字母分欄，兩元音間讀 [z] 的 s 在 GB 譯名中
    仍用斯、蘇：Mulhouse 米盧斯、Vesoul 沃蘇勒）；ss→s；x→[ks]（人名查 x 欄，地名譯「克」＋s 欄）；雙寫輔音只譯一次；
    -tion 的 t 讀 [s]（表上「t 在 i 前有時發 [s]」只做了 -tion）；s 在 n 前不發音（人名表說明，地名一併套用）。
  - ville 讀 [vil] 譯「維爾」，詞中出現也一樣（Villepin 德維爾潘）；詞首 Mill-、Vill-、Lill-、Gill- 的 ill 讀 [il]。
  - 地名：詞首 Mont 後接 r 以外的輔音時 t 不讀；-tier(s) 捷、-tière 蒂耶爾；詞首東／南／西改棟／楠／錫，
    詞尾海改亥；詞尾的 l 譯「勒」（表上 l 欄「爾（勒）」，GB 譯名 Laval 拉瓦勒、Épinal 埃皮納勒）。
  - 人名：照補充說明的前後綴（Dé-／De-／Des- 德、Dei-／Dey-／Dai- 戴、Rai-／Ray- 雷、Bai-／Bay- 貝、Chau- 肖、Ju- 朱、
    Am-／An- 安、Sch- 施；-ville 維爾、-bourg 堡、-court 古、-man(n) 曼、-land 蘭、-tier(s) 捷、-ton(s) 東、-tre(s) 特、
    -sin(s) 森、-fin 芬、-win 溫、-tz 茨、-tze 策、-dt 特、-zaine 贊、-zine 津、-kine 金、-moune 蒙、-ian／-oin 安…）；
    「埃」行 d 在詞首、詞尾用「德」；de、du、des、d'、le、la 等冠詞與介詞併入後面的姓，不加「·」。
  - Saint／Sainte 譯「聖」；地名中的冠詞、介詞、Saint 與相鄰部分連寫，兩個實詞之間保留連字號（沙勒維爾-梅濟耶爾）。
  - 弗只用於詞首，詞中、詞尾用夫；同一格有兩個字（戈/若、科/索）時已依讀音選欄；女性用字（瑪、娜、麗…）不自動套用，
    -v 會列出另一個字。

限制（做不到或沒做的）：
  - 法語拼寫不能完全推出讀音：詞尾輔音讀不讀（Arras、Reims 的 s、Rodez 的 z、Nevers、Quimper 的 r 都要讀）、
    外來名字（德語、布列塔尼語、奧克語、科西嘉語源）的讀法、-ent 在動詞中不讀等，本工具一律照一般規則，表上說明
    「須查閱發音工具書」的情形無法自動判斷。
  - 只依譯音表，不收辭典逐條收錄的譯名：辭典、新華社資料庫已有的人名（皮埃爾 Pierre、米歇爾 Michel、亨利 Henri）
    與《世界地名譯名詞典》已有的地名，常與照表譯的結果不同，應以辭典為準。
  - 補充說明裡 -tcha、-tche、-tsch、-scia、-szyn 等外來語詞尾只做了詞尾形式，不處理詞中出現的情形。
  - 不接受國際音標輸入。
  - 新華社與 GB 譯名常省略「輔音＋ar＋輔音」裡的 r（Tarbes 塔布、Chartres 沙特爾、Martine 瑪蒂娜、Carnot 卡諾），
    但也有保留的（Carcassonne 卡爾卡松、Marmont 馬爾蒙、Darlan 達爾朗）。表上 r 單獨一律譯「爾」，本工具照表，不省略。
  - 女性用字（瑪、娜、麗、蕾…）不自動套用（Mireille 照表得「米雷耶」，新華社作「米蕾耶」）。
  - 簡轉繁逐字轉換（整串轉換會把「拉克」轉成「拉剋」），再把裏、於、佔、託、採、佈、羣轉回音譯用字。

測試：fr_translit_test.tsv（236 筆；地名 124、人名名與姓 112，預期譯名取中維條目在「大陸簡體」下的標題），
  2026-11-17 結果：地名 88/124、人名 69/112。不通過的多是辭典逐條收錄的慣譯，見上面限制。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import opencc  # pip install --user opencc-python-reimplemented

# 譯名一律以繁體字輸出；逐字轉換（整串轉會把「拉克」轉成「拉剋」）；s2t 會把音譯用的里、于、占、托、采轉成裏、於、佔、託、採，要轉回
_s2t = opencc.OpenCC("s2t").convert
S = lambda x: "".join(_s2t(c) for c in x).translate(str.maketrans("裏於佔託採佈羣誇", "里于占托采布群夸"))  # 逐字轉繁（整串轉會出「拉剋」）；音譯用字被誤轉的轉回
TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_translit_table.json"),
                       encoding="utf-8"))

VOWELS = set("aeiouyàâäéèêëîïôöùûüœæ")
FRONT = set("eiyéèêëîï")
BACK = set("aoâôuûàù")
ONSET2 = {"bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "tr", "vr", "ch", "ph", "th", "gn", "gu", "qu"}
DIGRAPH = ("ch", "ph", "th", "gn", "qu", "gu", "rh", "lh")
CHAIN = {"g": ["gu", "gh", "g"], "j": ["j", "ge", "g"], "k": ["k", "c"], "s": ["s", "c"]}
FUNC = {"le", "la", "les", "l", "de", "du", "des", "d", "en", "sur", "sous", "lès", "lez", "aux", "au", "à", "et"}
SAINT = {"saint": "圣", "sainte": "圣", "st": "圣", "ste": "圣"}

# 人名：《法语姓名译名手册》附錄常用前後綴（中維補充說明）；長的先比
P_SUFFIX = [("bourgh", "堡"), ("bourg", "堡"), ("burg", "堡"), ("court", "古"), ("ville", "维尔"),
            ("thoons", "东"), ("thons", "东"), ("thon", "东"), ("tons", "东"), ("ton", "东"),
            ("tiers", "捷"), ("tier", "捷"), ("thier", "捷"), ("tres", "特"), ("tre", "特"),
            ("mann", "曼"), ("mans", "曼"), ("man", "曼"), ("land", "兰"), ("sins", "森"), ("sin", "森"),
            ("zaine", "赞"), ("zine", "津"), ("ckine", "金"), ("kine", "金"), ("moune", "蒙"), ("caen", "康"),
            ("raie", "雷"), ("raye", "雷"), ("rai", "雷"), ("bayes", "贝"), ("baye", "贝"), ("bay", "贝"),
            ("tsche", "切"), ("tsch", "奇"), ("tche", "奇"), ("tcha", "查"), ("tchi", "奇"), ("dzé", "泽"),
            ("szyn", "申"), ("scia", "夏"), ("tze", "策"), ("tzi", "齐"), ("tz", "茨"), ("dt", "特"),
            ("fin", "芬"), ("win", "温")]
L_SUFFIX = [("ville", "维尔"), ("tiers", "捷"), ("tier", "捷"), ("tière", "蒂耶尔"), ("tiere", "蒂耶尔")]


def isv(c):
    return c in VOWELS


def tail(w, whole=True):
    """處理詞尾不發音的字母。回傳 (core, fe)：core 是實際要讀的部分，fe 是必須按「埃」行讀的 e 的位置（-1 表示沒有）。"""
    n = len(w)
    mono = whole and len(re.findall(r"[aeiouyàâäéèêëîïôöùûüœæ]+", w)) <= 1
    for end in ("ers", "ets", "ez", "er", "et"):
        if w.endswith(end) and n > len(end):
            pos = n - len(end)
            if end == "er" and mono:  # 單音節 -er（mer、fer）r 照讀
                return w, pos
            return w[:pos + 1], pos
    if w.endswith("es") and mono and n > 2:
        return w[:-1], n - 2
    core = w
    while len(core) > 1 and core[-1] in "sxztdpg":
        c, prev = core[-1], core[-2]
        if c == "x" and not (re.search(r"(au|eu|ou|oi|œu)x$", core) or (re.search(r"aix$", core) and not mono)):
            break
        if c == "t" and prev in "scl":
            break
        if c == "p" and isv(prev):
            break
        if c == "g" and prev not in "nr":
            break
        core = core[:-1]
    if core.endswith("nc") or core.endswith("rc"):
        core = core[:-1]
    return core, -1


def cons_after(w, j):
    k = j
    while k < len(w) and not isv(w[k]) and w[k] != "|":
        k += 1
    return w[j:k], (k < len(w) and isv(w[k]))


def n_cons_before(w, i):
    """e 前面的輔音字母數（ch、ph、th、gn、qu、gu 算一個；雙寫輔音算兩個），以及前面有沒有元音。"""
    k = i - 1
    while k >= 0 and not isv(w[k]) and w[k] != "|":
        k -= 1
    run = w[k + 1:i]
    cnt = len(run)
    for d in DIGRAPH:
        cnt -= run.count(d)
    return cnt, k >= 0


def nas(w, j):
    """位置 j 的 n／m 能否與前面的元音構成鼻化元音。"""
    if j >= len(w) or w[j] not in "nm":
        return False
    if j + 1 >= len(w):
        return True
    nx = w[j + 1]
    return not isv(nx) and nx != w[j]


def segment(w, mode, initial=True, final=True):
    """把拼寫轉成讀音序列：("C", 欄) 或 ("V", 行)。欄 y＝[j]，x＝[ks]；行 e_end＝地名表的詞尾 e。"""
    ient = final and bool(re.search(r"ients?$", w))
    core, fe = tail(w, initial) if final else (w, -1)
    w = core
    n = len(w)
    mono = initial and len(re.findall(r"[aeiouyàâäéèêëîïôöùûüœæ]+", w)) <= 1
    segs = []
    i = 0

    def prev_c():
        return bool(segs) and segs[-1][0] == "C"

    def add(t, k, src):
        segs.append((t, k, src))

    while i < n:
        ch = w[i]
        r = w[i:]
        if ch == "|" or ch == "h":  # 單獨的 h 不發音；兩元音間的 h 把前後隔開
            i += 1
            continue
        if not isv(ch):
            # ---- 輔音 ----
            nx = w[i + 1] if i + 1 < n else ""
            if r.startswith("sch"):
                add("C", "ch", "sch"); i += 3; continue
            if r.startswith("cqu"):
                add("C", "k", "cqu"); i += 3; continue
            if r.startswith("ch"):
                nn_ = w[i + 2] if i + 2 < n else ""
                add("C", "k" if nn_ in ("l", "r") else "ch", "ch"); i += 2; continue
            two = {"ph": "f", "th": "t", "gh": "g", "rh": "r", "lh": "l", "sh": "ch", "kh": "k", "ck": "k", "cq": "k",
                   "qu": "k", "gn": "gn"}
            if r[:2] in two:
                add("C", two[r[:2]], r[:2]); i += 2; continue
            if r.startswith("cc"):
                if i + 2 < n and w[i + 2] in FRONT:
                    add("C", "k", "c"); i += 1; continue  # cc 在 e、i 前讀 [ks]：先出 k，第二個 c 讀 s
                add("C", "k", "cc"); i += 2; continue
            if ch == "c":
                add("C", "s" if nx in FRONT else "k", "c"); i += 1; continue
            if ch == "ç":
                add("C", "s", "ç"); i += 1; continue
            if ch == "q":
                add("C", "k", "q"); i += 1; continue
            if ch == "g":
                if nx == "u" and i + 2 < n and w[i + 2] in FRONT:
                    add("C", "g", "gu"); i += 2; continue
                if nx == "e" and i + 2 < n and w[i + 2] in BACK:
                    add("C", "j", "ge"); i += 2; continue
                if nx == "g":
                    add("C", "g", "gg"); i += 2; continue
                add("C", "j" if nx in FRONT else "g", "g"); i += 1; continue
            if ch == "s":
                if nx == "s":
                    add("C", "s", "ss"); i += 2; continue
                if nx == "c" and i + 2 < n and w[i + 2] in FRONT:
                    add("C", "s", "sc"); i += 2; continue
                if nx == "n" and i > 0 and isv(w[i - 1]):
                    segs.append(("-", "s", "s（n 前不發音）")); i += 1; continue
                add("C", "s", "s"); i += 1; continue
            if ch == "t" and r.startswith("tion") and not (i > 0 and w[i - 1] in "sx"):
                add("C", "s", "t（-tion）"); i += 1; continue
            if ch == "w":
                add("C", "v", "w"); i += 1 + (nx == "w"); continue
            if ch == "x":
                add("C", "x", "x"); i += 1; continue
            col = ch
            if col not in "bpdtfvzjklmnr":
                segs.append(("-", ch, f"{ch}（表上沒有，略過）")); i += 1; continue
            if nx == ch:
                add("C", col, ch + ch); i += 2; continue
            add("C", col, ch); i += 1; continue

        # ---- 元音 ----
        def m(s):
            return r.startswith(s)

        nx = w[i + 1] if i + 1 < n else ""
        # y 當輔音 [j]：詞首或元音後、且後接元音
        if ch == "y" and (i == 0 or isv(w[i - 1])) and nx and isv(nx):
            add("C", "y", "y"); i += 1; continue
        if mode == "person" and final and prev_c() and r in ("ière", "iere", "ierre"):
            add("V", "iere", r); add("C", "r", "r"); i = n; continue
        if m("eau"):
            add("V", "o_", "eau"); i += 3; continue
        if m("ieu"):
            add("V", "ieu", "ieu"); i += 3; continue
        if ient and m("ien") and i + 3 == n:  # 詞尾 -ient 讀 [jɑ̃]（Lorient）
            if prev_c():
                add("V", "i", "i")
            add("C", "y", "i"); add("V", "an", "en(t)"); i += 3; continue
        if (m("ien") or m("yen")) and nas(w, i + 2):
            add("V", "ien", r[:3]); i += 3; continue
        if (m("ion") or m("yon") or m("iom") or m("yom")) and nas(w, i + 2):
            add("V", "ion", r[:3]); i += 3; continue
        if (m("oin") or m("oim")) and nas(w, i + 2):
            add("V", "oin", r[:3]); i += 3; continue
        if (m("ain") or m("aim") or m("ein") or m("eim")) and nas(w, i + 2):
            add("V", "in", r[:3]); i += 3; continue
        if (m("aen") or m("aon") or m("ean")) and nas(w, i + 2):
            add("V", "an", r[:3]); i += 3; continue
        if m("oua"):
            add("V", "oi", "oua"); i += 3; continue
        if r == "oie":
            add("V", "oi", "oie"); i += 3; continue
        if m("oi") or m("oî"):
            add("V", "oi", r[:2]); i += 2; continue
        if r == "oye":
            add("V", "oi", "oye"); i += 3; continue
        if m("oy") and i == 0 and n > 2 and isv(w[2]):
            add("V", "o", "o"); i += 1; continue
        if m("oy"):
            if i + 2 < n and isv(w[i + 2]):
                add("V", "oi", "o(y)"); i += 1; continue  # y 留給下一步當 [j]
            add("V", "oi", "oy"); i += 2; continue
        # 元音＋-il（詞尾）／-ill-：[j]
        for vg, row in (("œu", "eu"), ("eu", "eu"), ("ue", "eu"), ("œ", "eu"), ("ou", "ou"), ("a", "a"), ("e", "E")):
            if m(vg) and (r[len(vg):] == "il" or r[len(vg):].startswith("ill")):
                if vg == "ue" and not (i > 0 and w[i - 1] in "cg"):
                    continue
                add("V", row, vg)
                k = len(vg) + (3 if r[len(vg):].startswith("ill") else 2)
                add("C", "y", r[len(vg):k]); i += k
                break
        else:
            if m("œu") or m("eu") or m("eû"):
                add("V", "eu", r[:2]); i += 2; continue
            if ch == "œ":
                add("V", "eu", "œ"); i += 1; continue
            if r == "aye":
                add("V", "ai", "aye"); i += 3; continue
            if m("ay") and i + 2 < n and isv(w[i + 2]):
                add("V", "a", "a(y)"); i += 1; continue
            if m("ai") or m("aî") or m("ay"):
                add("V", "ai", r[:2]); i += 2; continue
            if m("aou") and not m("aoul"):
                add("V", "o_", "aou"); i += 3; continue
            if m("au"):
                add("V", "o_", "au"); i += 2; continue
            if m("où") or m("oû") or m("ou"):
                add("V", "ou", r[:2]); i += 2; continue
            if ch in "aàâä" and nas(w, i + 1):
                add("V", "an", r[:2]); i += 2; continue
            if ch == "e" and nas(w, i + 1) and not (i == fe):
                add("V", "an", r[:2]); i += 2; continue
            if ch == "o" and nas(w, i + 1):
                add("V", "on", r[:2]); i += 2; continue
            if ch in "uû" and nas(w, i + 1):
                add("V", "in", r[:2]); i += 2; continue
            if ch in "iy" and nas(w, i + 1):
                add("V", "in", r[:2]); i += 2; continue
            if (m("ui") or m("uy")) and not (i + 2 < n and isv(w[i + 2])):
                add("V", "u", r[:2]); i += 2; continue
            if m("ie") or m("iè"):
                rest = r[2:]
                if rest == "" and fe != i + 1:  # 詞尾 -ie：e 不發音（Marie）
                    add("V", "i", "i(e)"); i += 2; continue
                if fe == i + 1 or (rest and not isv(rest[0])):
                    add("V", "ie", r[:2]); i += 2; continue
            if (m("ei") or m("ey") or m("eî")):
                if m("ey") and i + 2 < n and isv(w[i + 2]):
                    add("V", "E", "e(y)"); i += 1; continue
                add("V", "E", r[:2]); i += 2; continue
            if ch in "éèêëæ":
                add("V", "E", ch); i += 1; continue
            if ch == "e":
                after, has_v = cons_after(w, i + 1)
                nb, has_pv = n_cons_before(w, i)
                if i == fe:
                    add("V", "E", "e"); i += 1; continue
                if after == "" and i == n - 1 and not final:  # 詞幹尾 e，後面還接後綴（Charle-ville）：當開音節
                    if not has_pv or nb >= 2:
                        add("V", "e", "e（開音節）"); i += 1; continue
                    segs.append(("-", "e", "e（不發音）")); i += 1; continue
                if after == "" and not has_v and i == n - 1:  # 詞尾 e
                    if mono and segs and not any(s[0] == "V" for s in segs):
                        add("V", "e", "e（單音節詞）"); i += 1; continue
                    if final and prev_c() and (mode == "place" or segs[-1][1] in ("y", "n") or segs[-1][2] == "ll"
                                                  or (segs[-1][1] == "l" and len(segs) > 1 and segs[-2][0] == "C")):
                        add("V", "e_end", "e（詞尾）"); i += 1; continue
                    segs.append(("-", "e", "e（詞尾不發音）")); i += 1; continue
                if after == "":  # e 直接接元音
                    if i > 0 and w[i - 1] in "gj":
                        segs.append(("-", "e", "e（軟化 g、j）")); i += 1; continue
                    add("V", "E", "e"); i += 1; continue
                closed = (len(after) >= 2 and not (after[:2] in ONSET2 and has_v)) or (len(after) == 1 and not has_v)
                if (len(after) >= 2 and after[0] == after[1]) or after[:1] == "x":
                    closed = True
                if closed:
                    add("V", "E", "e（閉音節）"); i += 1; continue
                if (not has_pv and initial) or mono:
                    add("V", "e", "e（詞首開音節）"); i += 1; continue
                if nb >= 2:
                    add("V", "e", "e（兩輔音後）"); i += 1; continue
                if mode == "person":  # 人名表只有開音節 e 行，新華社譯名照譯（Augereau 奧熱羅、Pichegru 皮舍格呂）
                    add("V", "e", "e（開音節，人名照譯）"); i += 1; continue
                segs.append(("-", "e", "e（不發音）")); i += 1; continue
            if ch in "iîïy":
                if w[i + 1:i + 3] == "ll" and i == 1 and initial and w[0] in "mvlg":
                    add("V", "i", ch); add("C", "l", "ll"); i += 3; continue
                if w[i + 1:i + 3] == "ll":
                    if prev_c() or not segs:
                        add("V", "i", ch)
                    add("C", "y", "ll"); i += 3; continue
                if nx and isv(nx):
                    if prev_c():
                        add("V", "i", ch)
                    add("C", "y", ch); i += 1; continue
                add("V", "i", ch); i += 1; continue
            if ch in "aàâä":
                add("V", "a", ch); i += 1; continue
            if ch == "o":
                add("V", "o", ch); i += 1; continue
            if ch in "ôö":
                add("V", "o_", ch); i += 1; continue
            if ch in "uùûü":
                add("V", "u", ch); i += 1; continue
            segs.append(("-", ch, f"{ch}（未處理）")); i += 1
    return segs


def first(cell):
    return cell["main"][0] if cell and cell["main"] else ""


def look(rows, row, col):
    for c in CHAIN.get(col, [col]):
        v = first(rows.get(row, {}).get(c))
        if v:
            return v, c
    return "", col


def render(segs, mode, initial=True, final=True):
    t = TABLE[mode]
    rows, zero = t["rows"], t["zero"]
    out, trace, notes = [], [], []
    real = [s for s in segs if s[0] != "-"]
    for s in segs:
        if s[0] == "-":
            trace.append(f"{s[2]}→∅")
    i = 0
    while i < len(real):
        typ, key, src = real[i]
        nxt = real[i + 1] if i + 1 < len(real) else None
        at_start = initial and not out
        if typ == "C" and nxt and nxt[0] == "V":
            row, col = nxt[1], key
            if col == "x" and mode == "place":
                v, _ = look(rows, row, "s")
                ch = "克" + v
            elif row == "e_end" and col == "y":
                ch = "耶"
            elif row == "e_end" and mode == "person":  # 人名表沒有詞尾 e 行；新華社慣例 -lle 勒、-nne 納
                ch = {"l": "勒", "n": "纳"}[col]
            else:
                ch, used = look(rows, row, col)
                if not ch and col == "y":
                    ch = first(rows[row].get(""))
                if not ch:
                    ch = first(zero.get(col)).strip("[]") + first(rows[row].get(""))
                    notes.append(f"{src}{nxt[2]}：表上此格為空，改用輔音＋元音分開譯")
                cell = rows.get(row, {}).get(used if ch else col)
                if cell and (len(cell["main"]) > 1 or cell["alt"]):
                    notes.append(f"{src}{nxt[2]}：取「{ch}」，表上此格為 {'/'.join(cell['main'])}"
                                 + (f"（{'、'.join(cell['alt'])}）" if cell["alt"] else ""))
                # 位置用字
                if cell and cell["alt"]:
                    is_end = final and i + 2 >= len(real)
                    if mode == "person" and row == "E" and col == "d" and (at_start or is_end):
                        ch = "德"; notes.append("「埃」行 d 在詞首詞尾用「德」")
                    if mode == "place" and at_start and cell["alt"][0] in ("锡", "楠", "栋"):
                        ch = cell["alt"][0]; notes.append(f"地名開頭避免望文生義，用「{ch}」")
            out.append(ch); trace.append(f"{src}+{nxt[2]}→{ch}")
            i += 2
            continue
        if typ == "C":
            if key == "x":
                ch = "克斯"
            else:
                ch = first(zero.get(key)).strip("[]") or "?"
                if key == "l" and mode == "place" and final and nxt is None:
                    ch = "勒"; notes.append("地名詞尾 l 用「勒」")
                if ch == "夫" and at_start:
                    ch = "弗"
            out.append(ch); trace.append(f"{src}→{ch}")
            i += 1
            continue
        ch = first(rows.get(key, {}).get("")) or "?"
        out.append(ch); trace.append(f"{src}→{ch}")
        i += 1
    return "".join(out), trace, notes


def split_affix(w, mode, allow_prefix=True, allow_suffix=True):
    """人名前後綴、地名固定詞尾。回傳 (前綴譯名, 詞幹, 後綴譯名, 說明)。"""
    pre, post, note = "", "", []
    if mode == "person" and allow_prefix:
        for a, b, cond in (("dé", "德", r"[^aeiouy]"), ("des", "德", r"[^aeiouy]"), ("dei", "戴", r"[^aeiouyl]"),
                           ("dey", "戴", r"[^aeiouy]"), ("dai", "戴", r"[^aeiouyl]"), ("rai", "雷", r"[^aeiouyl]"),
                           ("ray", "雷", r"[^aeiouy]"), ("bai", "贝", r"[^aeiouyl]"), ("bay", "贝", r"[^aeiouy]"),
                           ("chau", "肖", r"."), ("ju", "朱", r"[^aeiouy]|i[nm]"), ("am", "安", r"[bfprst]"),
                           ("an", "安", r"[^aeiouyn]"), ("sch", "施", r"[^aeiouy]")):
            if w.startswith(a) and len(w) > len(a) and re.match(cond, w[len(a):]):
                pre, w = b, w[len(a):]
                note.append(f"前綴 {a}- 譯「{b}」（法語姓名譯名手冊）")
                break
    if mode == "person":
        suf = P_SUFFIX
    else:
        suf = L_SUFFIX
        if allow_prefix and len(w) > 4 and w.startswith("mont") and w[4] != "r" and not isv(w[4]):
            w = "mon" + w[4:]
            note.append("詞首 Mont 後接 r 以外的輔音，t 不讀")
    for a, b in (sorted(suf, key=lambda x: -len(x[0])) if allow_suffix else []):
        if w.endswith(a) and len(w) > len(a) + 1:
            post, w = b, w[:-len(a)]
            if not isv(a[0]) and w[-1] == a[0]:  # 雙寫輔音跨後綴（Lat-tre）只譯一次
                w = w[:-1]
            note.append(f"詞尾 -{a} 譯「{b}」")
            break
    else:
        if not allow_suffix:
            pass
        elif mode == "person" and re.search(r"[^aeiouy]ian$", w) and len(w) > 4:
            post, w = "安", w[:-2]; note.append("詞尾 -ian：「伊」行加「安」")
        elif mode == "person" and re.search(r"[^aeiouy]oin$", w):
            post, w = "安", w[:-3] + "ou"; note.append("詞尾 -oin：「烏」行加「安」")
    return pre, w, post, note


def _word(w, mode, initial=True, final=True, allow_prefix=True):
    """一個詞（不含連字號）；詞中的 ville 讀 [vil] 譯「維爾」（Villepin 德維爾潘），前後兩段分開譯。"""
    k = w.find("ville")
    if k >= 0 and not w.endswith("ville"):
        a, b = w[:k], w[k + 5:]
        s1, y1, t1, n1 = _word(a, mode, initial, False, allow_prefix) if a else ("", "", [], [])
        s2, y2, t2, n2 = _word(b, mode, False, final, False)
        return s1 + "维尔" + s2, f"{y1}+ville+{y2}", t1 + ["ville→维尔"] + t2, n1 + ["詞中 ville 譯「維爾」"] + n2
    pre, stem, post, note = split_affix(w, mode, allow_prefix and initial, final)
    if post == "维尔" and stem and not isv(stem[-1]):
        stem = tail(stem, False)[0]
    segs = segment(stem, mode, initial=initial and not pre, final=final and not post) if stem else []
    s, trace, notes = render(segs, mode, initial=initial and not pre, final=final and not post)
    seg_txt = " ".join(f"{k}" if t == "C" else f"[{k}]" for t, k, _ in segs if t != "-")
    return pre + s + post, (pre + "+" if pre else "") + seg_txt + ("+" + post if post else ""), trace, note + notes


def translit_word(word, mode, elided=False):
    """elided：前面併入了省略的 d'／l'，不套用人名前綴規則（d'Estaing 德斯坦）。"""
    w = word.lower().replace("’", "'").replace("'", "")
    if w in SAINT:
        return SAINT[w], w, ["Saint→圣"], []
    s, seg_txt, trace, notes = _word(w, mode, allow_prefix=not elided)
    if s.startswith("夫"):
        s = "弗" + s[1:]
    s = s[0] + s[1:].replace("弗", "夫") if s and mode == "place" else s
    if mode == "place":
        for a, b in (("东", "栋"), ("南", "楠"), ("西", "锡")):
            if s.startswith(a):
                s = b + s[1:]; notes.append(f"詞首{a}改{b}")
        if s.endswith("海"):
            s = s[:-1] + "亥"; notes.append("詞尾海改亥")
    return s, seg_txt, trace, notes


def translit(text, mode):
    """回傳 (譯名（簡體）, info)。人名：名與姓間加「·」，冠詞介詞併入後面的姓；地名：冠詞、介詞、Saint 連寫。"""
    info = []
    if mode == "person":
        words = [x for x in re.split(r"\s+", text.strip()) if x]
        out, buf = [], ""
        for wd in words:
            low = wd.lower().replace("’", "'")
            elided = bool(re.match(r"^[dl]'", low))
            sub = []
            for hi, h in enumerate(wd.split("-")):
                if not h:
                    continue
                s, sy, tr, nt = translit_word(h, mode, elided and hi == 0)
                info.append((h, sy, tr, nt)); sub.append(s)
            joined = "".join(sub) if any(h.lower() in SAINT for h in wd.split("-")) else "-".join(sub)
            if low in FUNC:
                buf += joined
            else:
                out.append(buf + joined); buf = ""
        if buf:
            out.append(buf)
        return "·".join(out), info
    parts = [x for x in re.split(r"[\s\-]+", text.strip()) if x]
    res = ""
    prev_full = False
    for p in parts:
        low = p.lower().replace("’", "'")
        elided = bool(re.match(r"^[dl]'", low))
        s, sy, tr, nt = translit_word(p, mode, elided)
        info.append((p, sy, tr, nt))
        full = low not in FUNC and low not in SAINT and not elided
        if res and prev_full and full:
            res += "-"
        res += s
        prev_full = full
    return res, info


def run_tests(path):
    """測試檔每行：模式<Tab>原文<Tab>預期譯名<Tab>出處；印出不通過的各筆與通過數。"""
    ok = tot = 0
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        mode, src, exp = line.rstrip("\n").split("\t")[:3]
        got = S(translit(src, mode)[0])
        tot += 1
        if got == S(exp):
            ok += 1
        else:
            print(f"✘ {mode}\t{src}\t預期 {S(exp)}\t得到 {got}")
    print(f"通過 {ok}/{tot}")


def main(argv):
    mode, verbose, words = "place", False, []
    it = iter(argv)
    for a in it:
        if a == "-t":
            run_tests(next(it, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_translit_test.tsv")))
            return
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
        print(f"{w}\t{S(zh)}")
        if verbose:
            for part, sy, tr, nt in info:
                print(f"    {part}：{sy}｜{S('，'.join(tr))}")
                for x in nt:
                    print(f"      註：{S(x)}")


if __name__ == "__main__":
    main(sys.argv[1:])
