#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вставляет favicon-ссылки в <head> КАЖДОЙ HTML-страницы после <meta name="viewport">.
Пути АБСОЛЮТНЫЕ от корня (/favicon.svg и т.д.) — сайт отдаётся с корня (Vercel/домен),
работает на любой глубине без ../. Идемпотентно: блок между маркерами spark-favicon.
Запускать в пайплайне после сборки страниц (порядок с inject_analytics/inline_css не важен —
трогаем <head>, не CSS). Ассеты генерит make_favicon.py."""
import os, re, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK = ('<!--spark-favicon-->'
         '<link rel="icon" href="/favicon.ico" sizes="32x32">'
         '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
         '<link rel="apple-touch-icon" href="/apple-touch-icon.png">'
         '<link rel="manifest" href="/site.webmanifest">'
         '<!--/spark-favicon-->')
VIEWPORT = re.compile(r'(<meta\s+name="viewport"[^>]*>)')
MARKED = re.compile(r'<!--spark-favicon-->.*?<!--/spark-favicon-->', re.S)

def process(f):
    t = open(f, encoding="utf-8").read()
    if "<!--spark-favicon-->" in t:                      # обновить существующий блок
        nt = MARKED.sub(BLOCK, t, count=1)
    elif VIEWPORT.search(t):                             # вставить после viewport
        nt = VIEWPORT.sub(lambda m: m.group(1) + BLOCK, t, count=1)
    else:
        return False
    if nt != t:
        open(f, "w", encoding="utf-8").write(nt)
        return True
    return False

def main():
    n = tot = 0
    files = glob.glob(os.path.join(REPO, "**", "*.html"), recursive=True)
    for f in files:
        if "_build" in f:
            continue
        tot += 1
        if process(f):
            n += 1
    print("favicon-ссылки вставлены/обновлены: %d из %d HTML" % (n, tot))

if __name__ == "__main__":
    main()
