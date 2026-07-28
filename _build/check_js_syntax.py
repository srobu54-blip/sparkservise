#!/usr/bin/env python3
# check_js_syntax.py — гейт сборки: инлайн-скрипты каждой страницы должны парситься.
#
# Зачем этот шаг существует. Ветка js каталога переводов подставляет UA-строку
# внутрь готового JS-литерала. Украинский апостроф («Ім'я», «роз'єм») — рабочая
# буква, в русском её нет. Один неэкранированный апостроф обрывал строку, ронял
# ВЕСЬ инлайн-скрипт страницы, и блоки с reveal-анимацией навсегда оставались
# opacity:0. Внешне это выглядело как «пустая страница», причём строго на UA:
# легло 76 из 77 украинских страниц при полностью живых русских.
#
# Коварство в том, что HTML остаётся валидным, ссылки на месте, сервер отдаёт 200,
# а sitemap и краулер-проверки ничего не замечают. Поймать это может только парсер
# JS — поэтому проверка вынесена в отдельный обязательный шаг.
#
# Нет node → шаг не падает, а громко предупреждает (Vercel-сборка не должна
# ломаться из-за отсутствия интерпретатора, которого пайплайн иначе не требует).
import os, re, sys, json, shutil, hashlib, subprocess, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'_build', 'node_modules', '.git'}
SCRIPT_RE = re.compile(r'<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>', re.S | re.I)

node = shutil.which('node')
if not node:
    print('  ⚠ node не найден — проверка синтаксиса JS пропущена.')
    print('    Это единственный шаг, который ловит оборванные строки в UA-переводах.')
    sys.exit(0)


def pages():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                yield os.path.join(root, f)


cache = {}          # sha1 тела → (ok, первая строка ошибки)
broken = []         # (относительный путь, номер скрипта, ошибка)
n_pages = n_scripts = 0

with tempfile.TemporaryDirectory() as td:
    probe = os.path.join(td, 'probe.js')
    for path in sorted(pages()):
        n_pages += 1
        html = open(path, encoding='utf-8', errors='replace').read()
        rel = os.path.relpath(path, REPO)
        for idx, (attrs, body) in enumerate(SCRIPT_RE.findall(html), 1):
            if 'ld+json' in attrs.lower():
                continue          # JSON-LD — это данные, у него свой валидатор
            n_scripts += 1
            key = hashlib.sha1(body.encode('utf-8', 'replace')).hexdigest()
            if key not in cache:
                with open(probe, 'w', encoding='utf-8') as fh:
                    fh.write(body)
                r = subprocess.run([node, '--check', probe],
                                   capture_output=True, text=True)
                if r.returncode == 0:
                    cache[key] = (True, '')
                else:
                    msg = next((l.strip() for l in r.stderr.splitlines()
                                if 'Error' in l), 'syntax error')
                    cache[key] = (False, msg)
            ok, msg = cache[key]
            if not ok:
                broken.append((rel, idx, msg))

print(f'  страниц: {n_pages}, инлайн-скриптов: {n_scripts}, '
      f'уникальных тел: {len(cache)}')

if broken:
    by_page = {}
    for rel, idx, msg in broken:
        by_page.setdefault(msg, []).append(rel)
    print(f'\n  ❌ СЛОМАННЫЙ JS на {len({b[0] for b in broken})} стр.:')
    for msg, rels in by_page.items():
        print(f'     {msg}')
        for rel in rels[:8]:
            print(f'       — {rel}')
        if len(rels) > 8:
            print(f'       … и ещё {len(rels) - 8}')
    print('\n  Чаще всего это неэкранированная кавычка из ветки js каталога')
    print('  переводов (украинский апостроф). Смотри js_sub() в _build/make_ua.py.')
    sys.exit(1)

print('  ✅ синтаксис JS чист на всех страницах')
