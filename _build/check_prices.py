#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_prices.py — гейт сборки: ни одна цена на сайте не спорит с прайсом.

Зачем этот шаг существует. Правило «любая цифра выводится из прайса, иначе
протухнет молча» действовало и раньше, но покрытие было неполным: его применили
к хабу и к авторским текстам моделей, а посадочные страницы держали свои
таблицы ЛИТЕРАЛАМИ — с комментарием «(из TIERS)», которого код не делал.

Аудит 29.07.2026 поймал 4 расхождения до 2,3×: /remont-iphone/zamena-ekrana/
обещала за экран iPhone 17 Pro Max 11 000 ₴ при прайсе 20 000 — 25 000 ₴.

Коварство этого класса в том, что ГЛАЗАМИ дефект не виден: price-live.js
переписывает ячейку в браузере через долю секунды. Заниженную цену видят
только Google, AI-краулеры и посетители без JS — то есть ровно те, кто
формирует выдачу. Поэтому нужна проверка HTML, а не проверка глазами.

⚠ УРОК ПРО САМ ЭТОТ ГЕЙТ. Первая версия требовала, чтобы в ячейке рядом стоял
data-price-label, и молча покрывала 6 страниц из 83, печатая при этом бодрое
«все цены совпадают». Модельные страницы размечают ячейки ОДНИМ data-svc —
модель подразумевается самой страницей. Проверка, которая уверенно зелёная на
одной десятой материала, хуже отсутствующей. Отсюда счётчик покрытия ниже:
если число страниц вдруг упало — гейт ослеп, а не сайт починился.

Разбираются два вида разметки:
  лендинги      <td class="pr" data-price-label="iPhone 13" data-svc="…">
  модели        <td class="pr" data-svc="…">          ← модель из пути страницы
Ключи data-svc КАНОНИЧЕСКИЕ (русские) и на украинских страницах тоже — так
задумано, они совпадают с прайсом и CMS; переводится только видимая подпись.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble_model as MOD          # SPEC — авторитетная карта модель→slug

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'_build', 'node_modules', '.git', 'admin'}

CELL = re.compile(r'<td class="pr"([^>]*)>([^<]*)</td>')
ATTR = re.compile(r'data-(price-label|svc)="([^"]*)"')
BADGE = re.compile(r'🛠 <b>(?:от|від) ([^<]+?) ₴</b>')

SLUG2LABEL = {v[1]: v[0] for v in MOD.SPEC.values()}


def money(n):
    return format(int(n), ',d').replace(',', ' ')


def norm(s):
    """Сравниваем по сути, а не по типографике.

    Разряды разделяются то обычным пробелом, то неразрывным, то узким; тире
    бывает –, — или -. Это оформление, а не цена. На этом первая версия дала
    182 «ошибки» на совпадающих числах.
    """
    s = re.sub(r'[\s   ]', '', s)
    return re.sub(r'[–—−-]', '-', s)


def tiers():
    """{label: {услуга: (lo, hi)}} — единственный источник, var TIERS."""
    out = {}
    for tid, prices in MOD.PRICES_ALL.items():
        out[MOD.SPEC[tid][0]] = {k: tuple(v) for k, v in prices.items()}
    return out


def expected(lo, hi):
    if not lo and not hi:
        return None                       # сентинел «уточняйте при заявке»
    return norm(money(lo)) if lo == hi else norm(f'{money(lo)}-{money(hi)}')


def pages():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                yield os.path.join(root, f)


def page_model(rel):
    """Модель страницы по её пути: remont-iphone/<slug>/ → «iPhone 13»."""
    parts = rel.replace(os.sep, '/').split('/')
    if 'remont-iphone' in parts:
        i = parts.index('remont-iphone')
        if i + 1 < len(parts):
            return SLUG2LABEL.get(parts[i + 1])
    return None


T = tiers()
bad, badge_bad = [], []
checked = badge_checked = n_pages = 0

for path in sorted(pages()):
    html = open(path, encoding='utf-8', errors='replace').read()
    hits = CELL.findall(html)
    if not hits:
        continue
    rel = os.path.relpath(path, REPO)
    default_label = page_model(rel)
    seen_here = False
    mins = []

    for attrs, shown in hits:
        a = dict((k, v) for k, v in ATTR.findall(attrs))
        svc = a.get('svc')
        if not svc:
            continue                      # «Диагностика — Бесплатно» и т.п.
        label = a.get('price-label') or default_label
        prices = T.get(label or '')
        if not prices or svc not in prices:
            continue
        exp = expected(*prices[svc])
        got = norm(shown.replace('₴', ''))
        if exp is None:
            continue                      # цена не назначена — сверять нечего
        seen_here = True
        checked += 1
        if got != exp:
            bad.append((rel, label, svc, got, exp))
        lo = prices[svc][0]
        if lo:
            mins.append(lo)

    if seen_here:
        n_pages += 1

    # ── бейдж «🛠 от X ₴» в первом экране: обязан быть минимумом ПО СТРАНИЦЕ ──
    # Раньше сюда шла цена АККУМУЛЯТОРА, и вход завышался в 1,2-4 раза:
    # iPhone 16 Pro обещал «от 4 200 ₴» при реальном минимуме 1 200 ₴. Это первое,
    # что видит человек из поиска, поэтому проверяется отдельно от ячеек.
    m = BADGE.search(html)
    if m and mins:
        badge_checked += 1
        if norm(m.group(1)) != norm(money(min(mins))):
            badge_bad.append((rel, norm(m.group(1)), norm(money(min(mins)))))

print(f'  страниц с ценами: {n_pages}, сверено ячеек: {checked}, '
      f'бейджей: {badge_checked}')

if bad:
    print(f'\n  ❌ ЦЕНА НА СТРАНИЦЕ НЕ СОВПАДАЕТ С ПРАЙСОМ — {len(bad)} шт.:')
    for rel, label, svc, got, exp in bad[:20]:
        print(f'     {rel}\n       {label} · {svc}: страница «{got}», прайс «{exp}»')
    if len(bad) > 20:
        print(f'     … и ещё {len(bad) - 20}')

if badge_bad:
    print(f'\n  ❌ БЕЙДЖ «от X ₴» ≠ МИНИМУМУ ПО СТРАНИЦЕ — {len(badge_bad)} шт.:')
    for rel, got, exp in badge_bad[:12]:
        print(f'     {rel}: бейдж «{got}», минимум «{exp}»')
    if len(badge_bad) > 12:
        print(f'     … и ещё {len(badge_bad) - 12}')

if bad or badge_bad:
    print('\n  Цифры на странице обязаны выводиться из прайса, а не вписываться руками.')
    print('  Образцы: assemble_model.models_for() и _min_price в _build/assemble_model.py.')
    sys.exit(1)

if n_pages < 80:
    print(f'  ⚠ покрытие подозрительно мало ({n_pages} стр.) — проверь, не сменилась ли')
    print('    разметка ячеек: гейт мог ослепнуть и молча пропускать расхождения.')

print('  ✅ цены и бейджи на страницах совпадают с прайсом')
