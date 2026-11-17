# 外語譯名音譯（name-translit）

芬蘭語、俄語、印尼語的地名與人名，依中文維基百科「[外語譯音表](https://zh.wikipedia.org/wiki/Wikipedia:外語譯音表)」與中國國家／行業標準音譯成中文，輸出繁體字形。純前端網頁，所有運算在瀏覽器內完成。

## 依據

| 語言 | 地名 | 人名 |
| --- | --- | --- |
| 芬蘭語 | GB/T 17693.20-2025《外語地名漢字譯寫導則 芬蘭語》 | 新華社《世界人名翻譯大辭典》 |
| 俄語 | GB/T 17693.4-2009《外語地名漢字譯寫導則 俄語》（含中維對 гу→古、пун→蓬 的勘誤） | 新華社《世界人名翻譯大辭典》《俄語姓名譯名手冊》；含 н 雙拼詞幹表 |
| 印尼語 | MZ/T 127-2019《外語地名漢字譯寫導則 印度尼西亞語》 | 新華社《世界人名翻譯大辭典》 |

譯音表內容取自中文維基百科（CC BY-SA 4.0）與上述標準。這些都是中國大陸標準：台灣已有通行譯名、或中文維基已有條目名時，以通行譯名為準。

## 命令列與 AI 呼叫

不用架伺服器：任何裝有 Node.js、能上網的電腦（或 AI 代理），一行就能查：

```bash
npx -y github:alexwudev/name-translit fi place Kuuterselkä Vuosalmi
npx -y github:alexwudev/name-translit ru person "Константин Рокоссовский"
npx -y github:alexwudev/name-translit id place "Sungai Tembesi" --json
```

- 第一個參數是語言（`fi` 芬蘭語、`ru` 俄語西里爾字母、`id` 印尼語），第二個是 `place` 地名或 `person` 人名，後面接一個或多個原文；沒給原文時從標準輸入讀，每行一個。
- `--json` 輸出 JSON，方便程式或 AI 解析；`-v` 顯示音節切分與每個字的來源。
- 命令列與網頁共用 `translit.js`、`data.js`，結果相同。
- 給 AI 讀的完整呼叫說明：[`llms.txt`](https://alexwudev.github.io/name-translit/llms.txt)（網頁版底部也有）。

## 檔案

- `index.html`：網頁介面
- `translit.js`：音譯規則（由 Python 版逐行移植）
- `data.js`：三張譯音表（繁體字形），由 `tools/build_data.py` 產生
- `cli.js`、`package.json`：命令列版（`npx -y github:alexwudev/name-translit …`）
- `tools/test.js`：與 Python 版的比對測試（`node tools/test.js`）
