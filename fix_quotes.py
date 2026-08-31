# -*- coding: utf-8 -*-
"""修复 lessons_part*.py 中字符串内容里的 ASCII 引号问题。
原理：按 Python 字符串字面量扫描；遇到 " 时向前看——
  若 " 后（跳过空白）是 , ] } : 或行尾 => 真终止符（保留）
  否则 => 字符串内容里的引号，替换为中文引号（“/”），并继续留在字符串内
"""
import glob, os

def fix_file(path):
    src = open(path, encoding="utf-8").read()
    out = []
    i = 0
    n = len(src)
    in_str = False      # 是否在字符串内
    in_comment = False  # 是否在注释内（仅 # 行注释）
    quote_open = False  # 中文引号开关：False=>下一个内引号用 “，True=>用 」
    fixed = 0
    while i < n:
        ch = src[i]
        nxt = src[i+1] if i+1 < n else ""
        if in_comment:
            out.append(ch)
            if ch == "\n":
                in_comment = False
            i += 1
            continue
        if not in_str:
            if ch == "#":
                in_comment = True
                out.append(ch); i += 1; continue
            if ch == '"':
                in_str = True
                out.append(ch); i += 1; continue
            out.append(ch); i += 1; continue
        # 在字符串内
        if ch == "\\":
            out.append(ch)
            if nxt:
                out.append(nxt); i += 2
            else:
                i += 1
            continue
        if ch == '"':
            # 向前看决定是终止符还是内容引号
            j = i + 1
            while j < n and src[j] in " \t":
                j += 1
            nxt_sig = src[j] if j < n else ""
            if nxt_sig in ",]}:":  # 真终止符
                in_str = False
                out.append(ch); i += 1
            else:                  # 内容引号
                out.append("”" if quote_open else "“")
                quote_open = not quote_open
                fixed += 1
                i += 1
            continue
        out.append(ch); i += 1

    new = "".join(out)
    if new != src:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return fixed, new

def main():
    total = 0
    for p in sorted(glob.glob("build/lessons_part*.py")):
        fixed, _ = fix_file(p)
        print(os.path.basename(p), "fixed inner quotes:", fixed)
        total += fixed
    print("total fixed:", total)

if __name__ == "__main__":
    main()
