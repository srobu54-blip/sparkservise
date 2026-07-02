#!/usr/bin/env python3
# inject_analytics.py — вставляет <script defer src=".../analytics.js"> в <head> всех
# страниц (RU+UA) с правильным относительным путём по глубине. Идемпотентно (маркеры).
# Запускать ПОСЛЕ make_ua.py. analytics.js (в корне) — единственное место с ID конверсий.
import os, re, glob
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (marker_open, marker_close, src) — все defer-скрипты, встраиваемые в <head> каждой страницы
SCRIPTS = [
    ('<!--spark-analytics-->', '<!--/spark-analytics-->', 'analytics.js'),
    ('<!--spark-exit-->', '<!--/spark-exit-->', 'exit-popup.js'),
]

def process(f):
    rel = os.path.relpath(f, REPO).replace(os.sep, '/')
    prefix = '../' * rel.count('/')          # глубина до корня
    t = open(f, encoding='utf-8').read()
    orig = t
    for m0, m1, src in SCRIPTS:
        b = m0 + '<script defer src="' + prefix + src + '"></script>' + m1
        if m0 in t:
            t = re.sub(re.escape(m0) + '.*?' + re.escape(m1), lambda m: b, t, flags=re.S)
        elif '</head>' in t:
            t = t.replace('</head>', b + '\n</head>', 1)
    if t != orig:
        open(f, 'w', encoding='utf-8').write(t)
        return True
    return False

def main():
    n = tot = 0
    for f in glob.glob(os.path.join(REPO, '**', 'index.html'), recursive=True):
        if '_build' in f:
            continue
        tot += 1
        if process(f):
            n += 1
    print("analytics injected/updated: %d из %d страниц" % (n, tot))

if __name__ == '__main__':
    main()
