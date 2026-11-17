"""name-translit <語言> <place|person> [原文…] [-v] [--json]

  語言：fi 芬蘭語、ru 俄語（西里爾字母）、id 印尼語、en 英語、fr 法語、de 德語、es 西班牙語、fa 波斯語（拉丁轉寫）、ar 阿拉伯語、he 希伯來語（拉丁轉寫）
  place 地名、person 人名；原文可給多個，沒給時從標準輸入每行讀一個。
  -v 顯示音節與逐字來源；--json 輸出 JSON。
  依中文維基外語譯音表與中國國標音譯，輸出繁體字形；台灣已有通行譯名時以通行譯名為準。
"""
import json
import sys

from . import LANGS, run


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    argv = list(sys.argv[1:] if argv is None else argv)
    flags = {a for a in argv if a in ("-v", "--json", "-h", "--help")}
    args = [a for a in argv if a not in flags]
    if "-h" in flags or "--help" in flags or len(args) < 2:
        print(__doc__)
        return 0 if ("-h" in flags or "--help" in flags) else 1
    lang, mode, *words = args
    if lang not in LANGS:
        print(f"不支援的語言：{lang}（可用：{'、'.join(LANGS)}）")
        return 1
    if mode not in ("place", "person"):
        print(f"類別要是 place 或 person：{mode}")
        return 1
    if not words:
        words = [l.strip() for l in sys.stdin if l.strip()]
    res = run(lang, words, mode, verbose="-v" in flags)
    if "--json" in flags:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    for r in res:
        extra = "".join(f"\t{k}：{v}" for k, v in r["extra"].items())
        print(f"{r['src']}\t{r['zh']}{extra}")
        for d in r["detail"]:
            print("    " + d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
