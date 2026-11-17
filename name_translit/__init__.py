"""外語地名人名音譯（芬、俄、印尼、英、法、德、西、波斯、阿拉伯、希伯來語），依中文維基外語譯音表與中國國標。"""
import contextlib
import importlib
import io
import os
import sys

LANGS = {"fi": "芬蘭語", "ru": "俄語（西里爾字母）", "id": "印尼語", "en": "英語（拼寫或「拼寫/國際音標/」）",
         "fr": "法語", "de": "德語", "es": "西班牙語", "fa": "波斯語（拉丁轉寫）", "ar": "阿拉伯語（拉丁轉寫或標短元音的阿拉伯字母）",
         "he": "希伯來語（拉丁轉寫；只有人名表）"}
_HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "langs")


def module(lang):
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    return importlib.import_module(f"{lang}_translit")


def run(lang, words, mode="place", verbose=False):
    """回傳 [{"src", "zh", "extra": {說明: 版本}, "detail": [逐字說明行]}]，與命令列輸出一致。"""
    argv = (["-p"] if mode == "person" else []) + (["-v"] if verbose else []) + list(words)
    mod = module(lang)  # 先匯入：各工具匯入時會 reconfigure 標準輸出

    class _Buf(io.StringIO):
        def reconfigure(self, *a, **k):
            pass
    buf = _Buf()
    with contextlib.redirect_stdout(buf):
        mod.main(argv)
    out = []
    for line in buf.getvalue().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if out:
                out[-1]["detail"].append(line.strip())
            continue
        cols = line.split("\t")
        extra = {}
        for c in cols[2:]:
            k, _, v = c.partition("：")
            extra[k] = v
        out.append({"src": cols[0], "zh": cols[1] if len(cols) > 1 else "", "extra": extra, "detail": []})
    return out
