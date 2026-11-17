"""從 Python 版工具資料夾同步九種語言的音譯工具進 name_translit/langs/，並產生網頁用的檔案清單與逐字繁體對照。

用法：python -X utf8 tools/build_py.py <Python 版工具資料夾>
"""
import json
import os
import re
import shutil
import sys

import opencc

sys.stdout.reconfigure(encoding="utf-8")
LANGS = ["fi", "ru", "id", "en", "fr", "de", "es", "fa", "ar", "he"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "name_translit", "langs")
FIX = str.maketrans("裏於佔託採佈羣誇", "里于占托采布群夸")


def main(src):
    os.makedirs(DST, exist_ok=True)
    files = []
    for k in LANGS:
        for suf in ("_translit.py", "_translit_table.json", "_translit_test.tsv"):
            f = os.path.join(src, k + suf)
            if os.path.exists(f):
                shutil.copy2(f, os.path.join(DST, k + suf))
                files.append(k + suf)
    # 網頁（Pyodide）沒有 opencc：預先把所有可能出現的漢字逐字轉好，與 Python 版的逐字轉換結果相同
    s2t = opencc.OpenCC("s2t").convert
    chars = set()
    for f in files:
        chars |= set(re.findall(r"[一-鿿]", open(os.path.join(DST, f), encoding="utf-8").read()))
    cmap = {c: s2t(c).translate(FIX) for c in sorted(chars) if s2t(c).translate(FIX) != c}
    json.dump(cmap, open(os.path.join(ROOT, "s2t_map.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    json.dump({"langs": LANGS, "files": [f for f in files if not f.endswith(".tsv")]},
              open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"已同步 {len(files)} 個檔案；逐字繁體對照 {len(cmap)} 字")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
