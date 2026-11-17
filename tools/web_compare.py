"""網頁版（Pyodide）與 Python 命令列逐筆比對：用九種語言的測試詞，兩邊結果必須完全相同。

用法：python -X utf8 tools/web_compare.py
會在本機開一個臨時 HTTP 服務、用無頭 Chrome 載入網頁跑完全部測試詞，比對後關閉服務。
"""
import csv
import functools
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import name_translit  # noqa: E402

CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
cases = []
for lang in name_translit.LANGS:
    p = os.path.join(ROOT, "name_translit", "langs", f"{lang}_translit_test.tsv")
    if not os.path.exists(p):
        continue
    for row in csv.reader(open(p, encoding="utf-8"), delimiter="\t"):
        if len(row) >= 2 and row[0] in ("place", "person") and row[1].strip():
            cases.append((lang, row[0], row[1].strip()))
groups = {}
for lang, mode, w in cases:
    groups.setdefault((lang, mode), []).append(w)
expected = {f"{l}|{m}": name_translit.run(l, ws, m) for (l, m), ws in groups.items()}

page = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
job = json.dumps([[l, m, ws] for (l, m), ws in groups.items()], ensure_ascii=False)
inj = ("<pre id=\"__result\"></pre><script>(async()=>{while(!ready)await new Promise(r=>setTimeout(r,200));"
       "const J=" + job + ";const out={};try{for(const [l,m,ws] of J){py.globals.set('_a',py.toPy([l,ws,m]));"
       "out[l+'|'+m]=JSON.parse(py.runPython('json.dumps(name_translit.run(_a[0],_a[1],_a[2]),ensure_ascii=False)'));}"
       "document.getElementById('__result').textContent=JSON.stringify(out);}catch(e){document.getElementById('__result').textContent='ERR '+e.message;}})();</script></body>")
test_page = os.path.join(ROOT, "_web_compare.html")
open(test_page, "w", encoding="utf-8").write(page.replace("</body>", inj))

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass
handler = functools.partial(Quiet, directory=ROOT)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
try:
    url = f"http://127.0.0.1:{srv.server_address[1]}/_web_compare.html"
    prof = tempfile.mkdtemp(prefix="nt_cmp_")
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", "--virtual-time-budget=180000", "--enable-logging=stderr", "--v=0",
                        "--timeout=180000", "--dump-dom", url], capture_output=True, timeout=300)
    dom = r.stdout.decode("utf-8", "replace")
    for l in r.stderr.decode("utf-8", "replace").splitlines():
        if "CONSOLE" in l or "Uncaught" in l:
            print("瀏覽器：", l[-300:])
    st = re.search(r'<span id="status">(.*?)</span>', dom)
    print("狀態：", st.group(1) if st else "?")
finally:
    srv.shutdown()
    os.remove(test_page)
m = re.search(r'<pre id="__result">(.*?)</pre>', dom, re.S)
if not m or not m.group(1).strip():
    sys.exit("網頁沒有跑出結果（Pyodide 可能沒載入完成）")
import html
raw = html.unescape(m.group(1))
if raw.startswith("ERR"):
    sys.exit(raw[-1500:])
got = json.loads(raw)
same = diff = 0
for k, exp in expected.items():
    for a, b in zip(exp, got.get(k, [])):
        if (a["zh"], a["extra"]) == (b["zh"], b["extra"]):
            same += 1
        else:
            diff += 1
            print(f"不同 {k} {a['src']}\n  PY {a['zh']} {a['extra']}\n  WEB {b['zh']} {b['extra']}")
    if len(got.get(k, [])) != len(exp):
        print(f"筆數不同 {k}：PY {len(exp)}、WEB {len(got.get(k, []))}")
print(f"網頁與 Python 比對：相同 {same}｜不同 {diff}｜共 {len(cases)} 筆")
