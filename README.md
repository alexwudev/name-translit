# 外語譯名音譯（name-translit）

芬蘭語、俄語、印尼語、英語、法語、德語、西班牙語、波斯語、阿拉伯語、希伯來語的地名與人名，依中文維基百科「[外語譯音表](https://zh.wikipedia.org/wiki/Wikipedia:外語譯音表)」與中國國家／行業標準音譯成中文，輸出繁體字形。

- 網頁版：https://alexwudev.github.io/name-translit/
- 命令列：`pip install "git+https://github.com/alexwudev/name-translit"` 後 `name-translit <語言> <place|person> <原文…> [--json] [-v]`
- 給 AI 讀的完整說明（輸入格式、另列版本、使用規則）：[llms.txt](https://alexwudev.github.io/name-translit/llms.txt)

網頁用 Pyodide 在瀏覽器裡執行與命令列相同的 Python 程式，結果一致。這些都是中國大陸標準：台灣已有通行譯名、或中文維基已有條目名時，以通行譯名為準。

## 檔案

- `name_translit/langs/<語言>_translit.py`、`_table.json`、`_test.tsv`：各語言的音譯規則、譯音表與測試詞（每支工具檔頭寫明依據、輸入格式與限制）
- `name_translit/__init__.py`、`cli.py`：統一入口
- `index.html`：網頁；`manifest.json`（要載入的檔案清單）、`s2t_map.json`（瀏覽器端的逐字繁體對照）由 `tools/build_py.py` 產生
- `tools/build_py.py <Python 版工具資料夾>`：從本機工具同步並重產上面兩個檔
- `tools/web_compare.py`：用無頭 Chrome 比對網頁與 Python 版的全部測試詞
- `tools/testwords.json`：芬、俄、印尼語的回歸測試詞
