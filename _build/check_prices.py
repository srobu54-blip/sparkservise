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

Сверяются все ячейки с data-svc на всех страницах, RU и UA. Живой inline-fetch
к Supabase на хабе iPhone здесь ни при чём: он правит рантайм, а мы проверяем
исходник — он обязан совпадать с var TIERS, который в этот же прогон обновил
pull_prices.
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'_build', 'node_modules', '.git', 'admin'}
HUB = os.path.join(REPO, 'remont-iphone', 'index.html')

CELL = re.compile(
    r'data-price-label="([^"]+)"[^>]*data-svc="([^"]+)"[^>]*>([^<]*)</td>')


def money(n):
    return format(int(n), ',d').replace(',', ' ')


def norm(s):
    """\u0421\u0440\u0430\u0432\u043d\u0438\u0432\u0430\u0435\u043c \u043f\u043e \u0441\u0443\u0442\u0438, \u0430 \u043d\u0435 \u043f\u043e \u0442\u0438\u043f\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0435.

    \u0420\u0430\u0437\u043d\u044b\u0435 \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440\u044b \u0440\u0430\u0437\u0434\u0435\u043b\u044f\u044e\u0442 \u0440\u0430\u0437\u0440\u044f\u0434\u044b \u0442\u043e \u043e\u0431\u044b\u0447\u043d\u044b\u043c \u043f\u0440\u043e\u0431\u0435\u043b\u043e\u043c, \u0442\u043e \u043d\u0435\u0440\u0430\u0437\u0440\u044b\u0432\u043d\u044b\u043c,
    \u0442\u043e \u0443\u0437\u043a\u0438\u043c, \u0438 \u0441\u0442\u0430\u0432\u044f\u0442 \u0440\u0430\u0437\u043d\u044b\u0435 \u0442\u0438\u0440\u0435 (\u2013, \u2014, -). \u042d\u0442\u043e \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u0435, \u0430 \u043d\u0435 \u0446\u0435\u043d\u0430, \u0438
    \u0441\u0440\u0430\u0432\u043d\u0438\u0432\u0430\u0442\u044c \u043f\u043e \u043d\u0438\u043c \u0437\u043d\u0430\u0447\u0438\u0442 \u043b\u043e\u0432\u0438\u0442\u044c \u043b\u043e\u0436\u043d\u044b\u0435 \u0440\u0430\u0441\u0445\u043e\u0436\u0434\u0435\u043d\u0438\u044f \u2014 \u043d\u0430 \u044d\u0442\u043e\u043c \u043c\u043e\u044f \u043f\u0435\u0440\u0432\u0430\u044f
    \u0432\u0435\u0440\u0441\u0438\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438 \u0434\u0430\u043b\u0430 182 \u00ab\u043e\u0448\u0438\u0431\u043a\u0438\u00bb \u043d\u0430 \u0441\u043e\u0432\u043f\u0430\u0434\u0430\u044e\u0449\u0438\u0445 \u0447\u0438\u0441\u043b\u0430\u0445.
    """
    s = re.sub(r'[\s\u00a0\u202f\u2009]', '', s)
    return re.sub(r'[\u2013\u2014\u2212-]', '-', s)


def tiers():
    """{label: {услуга: [lo, hi]}} из единственного источника — var TIERS."""
    s = open(HUB, encoding='utf-8').read()
    body = re.search(r'var TIERS=\[(.*?)\];', s, re.S)
    if not body:
        print('  ⚠ var TIERS не найден в хабе — проверка цен пропущена.')
        sys.exit(0)
    out = {}
    for _tid, label, pr, _t in re.findall(
            r"\{id:'([^']+)',label:'([^']+)',prices:\{([^}]*)\},time:'([^']+)'\}", body.group(1)):
        d = {}
        for k, lo, hi in re.findall(r"'((?:\\.|[^'\\])*)':\[(\d+),(\d+)\]", pr):
            d[re.sub(r'\\(.)', r'\1', k)] = (int(lo), int(hi))
        out[label] = d
    return out


def expected(lo, hi):
    """Варианты написания, которые считаем верными (тире у страниц разные)."""
    if not lo and not hi:
        return None                     # сентинел «уточняйте» — не сверяем
    if lo == hi:
        return {norm(money(lo))}
    a, b = money(lo), money(hi)
    return {norm(f'{a}-{b}')}


def pages():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                yield os.path.join(root, f)


T = tiers()
bad, checked, n_pages = [], 0, 0

for path in sorted(pages()):
    html = open(path, encoding='utf-8', errors='replace').read()
    hits = CELL.findall(html)
    if not hits:
        continue
    n_pages += 1
    rel = os.path.relpath(path, REPO)
    for label, svc, shown in hits:
        prices = T.get(label)
        if not prices or svc not in prices:
            continue                    # услуги нет у модели — не наша забота
        exp = expected(*prices[svc])
        if exp is None:
            continue
        checked += 1
        got = norm(shown.replace('₴', ''))
        if got not in exp:
            bad.append((rel, label, svc, got, ' / '.join(sorted(exp))))

print(f'  страниц с ценами: {n_pages}, сверено ячеек: {checked}')

if bad:
    print(f'\n  ❌ ЦЕНА НА СТРАНИЦЕ НЕ СОВПАДАЕТ С ПРАЙСОМ — {len(bad)} шт.:')
    for rel, label, svc, got, exp in bad[:20]:
        print(f'     {rel}')
        print(f'       {label} · {svc}: на странице «{got}», в прайсе «{exp}»')
    if len(bad) > 20:
        print(f'     … и ещё {len(bad) - 20}')
    print('\n  Цены на странице обязаны выводиться из прайса, а не вписываться руками.')
    print('  Образец, как правильно: assemble_model.models_for() в _build/assemble_model.py.')
    sys.exit(1)

print('  ✅ все цены на страницах совпадают с прайсом')
