"""把 Project/tools 的三張譯音表轉成繁體字形，打包成網頁用的 data.js。

用法：python -X utf8 tools/build_data.py <Python 版工具資料夾>
譯音表來源見 README。繁簡轉換用 OpenCC s2t，音譯用字被誤轉的（裏於佔託採）轉回。
"""
import json
import os
import sys

import opencc

sys.stdout.reconfigure(encoding="utf-8")
SRC = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TRANSLIT_SRC", "")).rstrip("/\\") + "/"  # Python 版工具與譯音表所在資料夾
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.js")
_s2t = opencc.OpenCC("s2t").convert
S = lambda x: _s2t(x).translate(str.maketrans("裏於佔託採佈羣", "里于占托采布群"))


def conv(o):
    if isinstance(o, str):
        return S(o)
    if isinstance(o, list):
        return [conv(x) for x in o]
    if isinstance(o, dict):
        return {k: conv(v) for k, v in o.items()}  # 鍵是外文拼寫，不轉
    return o


data = {}
for lang in ("fi", "ru", "id"):
    t = json.load(open(SRC + f"{lang}_translit_table.json", encoding="utf-8"))
    data[lang] = conv(t)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("// 自動產生，勿手改：python -X utf8 tools/build_data.py\n")
    f.write("const TABLES = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write("if (typeof module !== 'undefined') module.exports = TABLES;\n")
print("已寫出", OUT, os.path.getsize(OUT), "bytes")
