"""用 Project/tools 的 Python 版產生參考答案，寫 tools/expected.json，給 test.js 比對。"""
import importlib.util
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
SRC = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TRANSLIT_SRC", "")).rstrip("/\\") + "/"  # Python 版工具與譯音表所在資料夾
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SRC + f"{name}_translit.py")
    m = importlib.util.module_from_spec(spec)
    sys.argv = ["x"]
    spec.loader.exec_module(m)
    return m


words = json.load(open(os.path.join(HERE, "testwords.json"), encoding="utf-8"))
out = {}
for lang in ("fi", "ru", "id"):
    m = load(lang)
    for mode, ws in words[lang].items():
        for w in ws:
            zh, _ = m.translit(w, mode)
            rec = {"zh": m.S(zh), "extra": []}
            if lang == "fi" and mode == "place":
                g = m.generic_variant(w)
                if g:
                    rec["extra"].append(["通名意譯", m.S(m.translit(g[0], mode)[0] + g[1])])
            if lang == "id":
                import re
                if re.search(r"e(?!i)", w.lower().replace("ee", "")):
                    alt_src = " ".join(x if x.lower() in m.GENERIC or x.lower() in m.MODIFIER else
                                       re.sub(r"[eE](?=[^aeiouéAEIOU-][aeiouAEIOU]|$|-)", lambda mm: "é" if mm.group(0) == "e" else "É", x)
                                       for x in w.split())
                    alt, _ = m.translit(alt_src, mode)
                    if alt != zh:
                        rec["extra"].append(["e 若讀 é", m.S(alt)])
            out[f"{lang}|{mode}|{w}"] = rec
json.dump(out, open(os.path.join(HERE, "expected.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("參考答案", len(out), "筆")
