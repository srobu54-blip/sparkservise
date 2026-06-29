#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Инлайн полного styles.css в <head> ГЛАВНОЙ (RU + UA), чтобы убрать render-blocking
внешний CSS на лендинге → быстрее First Paint / Speed Index.
styles.css не содержит url() → инлайн безопасен на любой глубине пути (в т.ч. /ua/).
Идемпотентно: подставляет между маркерами <!--inline-css-->...<!--/inline-css-->.
ЗАПУСКАТЬ ПОСЛЕДНИМ в пайплайне (после make_ua и inject_analytics).
Только главная: на остальных страницах внешний styles.css кэшируется при навигации."""
import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = ["index.html", os.path.join("ua", "index.html")]

def main():
    css = open(os.path.join(REPO, "styles.css"), encoding="utf-8").read()
    assert "</style" not in css.lower(), "styles.css содержит </style> — инлайн небезопасен"
    block = "<!--inline-css--><style>" + css + "</style><!--/inline-css-->"
    for rel in TARGETS:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        if "<!--inline-css-->" in t:
            nt = re.sub(r"<!--inline-css-->.*?<!--/inline-css-->", lambda m: block, t, count=1, flags=re.S)
        else:
            nt = t
            for link in ('<link rel="stylesheet" href="styles.css">',
                         '<link rel="stylesheet" href="../styles.css">'):
                if link in nt:
                    nt = nt.replace(link, block, 1)
                    break
        open(p, "w", encoding="utf-8").write(nt)
        print(("  ✓ updated " if nt != t else "  = nochange ") + rel + " (inline CSS %d B)" % len(css))

if __name__ == "__main__":
    main()
