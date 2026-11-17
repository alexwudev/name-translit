"""用無頭 Chrome 載入 index.html，填入測試輸入，印出渲染後的結果表（本機驗證用）。"""
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
NL = chr(92) + "n"
CASES = [("fi", "place", ["Kuuterselkä", "Leitimojärvi", "Ala-Sommee"]),
         ("ru", "person", ["Константин Рокоссовский", "Rzhev"]),
         ("id", "place", ["Sungai Tembesi", "Panggul"])]
tmp = tempfile.mkdtemp(prefix="nt_ui_")
for f in ("data.js", "translit.js"):
    open(os.path.join(tmp, f), "w", encoding="utf-8").write(open(os.path.join(D, f), encoding="utf-8").read())
html = open(os.path.join(D, "index.html"), encoding="utf-8").read()
for lang, mode, lines in CASES:
    inj = (f"document.querySelector('input[name=lang][value={lang}]').checked=true;"
           f"document.querySelector('input[name=mode][value={mode}]').checked=true;"
           f"$('input').value='{NL.join(lines)}';$('verbose').checked=true;render();")
    page = re.sub(r"render\(\);\s*</script>", lambda m: inj + "</script>", html)
    open(os.path.join(tmp, "index.html"), "w", encoding="utf-8").write(page)
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--enable-logging=stderr", "--v=0",
                        "--user-data-dir=" + os.path.join(tmp, "prof"), "--dump-dom",
                        "file:///" + tmp.replace(chr(92), "/") + "/index.html"], capture_output=True)
    dom = r.stdout.decode("utf-8", "replace")
    errs = [l for l in r.stderr.decode("utf-8", "replace").splitlines() if "Uncaught" in l]
    m = re.search(r'id="out">(.*?)</tbody>', dom, re.S)
    body = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))) if m else "找不到"
    print(f"{lang} {mode} → {body[:700]}")
    for e in errs:
        print("  錯誤：", e[-200:])
