#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prerender_hub_prices.py — server-render (пред-пейнт) прайс-таблицы хаба iPhone.

ПРОБЛЕМА (SEO-причина №3): в статике <tbody id="priceBody"> пуст — строки прайса
рисует JS renderTable() уже в браузере. Краулер/парсер, который не исполняет JS
(или исполняет ограниченно), видит ПУСТУЮ таблицу → теряется весь ценовой контент:
реальные цены, названия услуг, сроки. Для коммерческого хаба это как раз тот
уникальный, релевантный текст, который должен быть в HTML.

ФИКС: при билде запекаем строки ПЕРВОГО тира (curTier=0) прямо в <tbody>, ТОЧНО
повторяя вывод renderTable(). JS на загрузке перезапишет их тем же контентом (или
живой ценой из CMS) → визуально ничего не меняется, layout shift = 0, а в HTML
теперь есть цены.

Работает и для RU, и для UA хаба. Язык подписей и условий (Діагностика/Безкоштовно,
indexOf('води') и т.д.) НЕ хардкодится — извлекается из renderTable() самого файла,
поэтому вывод совпадает с тем, что этот же файл рисует в браузере.

Запуск: в build.sh ПОСЛЕ pull_prices (обновляет TIERS) и ПОСЛЕ make_ua (UA-хаб
генерится из RU). Идемпотентно: повторный запуск переписывает <tbody> заново.

Fail-safe: если в файле не нашли TIERS / renderTable / priceBody — файл пропускаем,
exit 0. Сломать сборку нельзя.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUBS = [
    os.path.join(ROOT, "remont-iphone", "index.html"),
    os.path.join(ROOT, "ua", "remont-iphone", "index.html"),
]


def log(msg):
    print(f"[prerender_hub_prices] {msg}")


def fmt(n: int) -> str:
    """Повторяет Number.toLocaleString('ru-RU'): разряды через неразрывный пробел."""
    return f"{int(n):,}".replace(",", " ")


def first_tier(src: str):
    """Первый объект TIERS → (label, [(svc, lo, hi), ...], time) либо None."""
    m = re.search(
        r"var TIERS=\[\s*\{id:'[^']+',label:'([^']*)',prices:\{([^}]*)\},time:'([^']*)'\}",
        src,
    )
    if not m:
        return None
    label, prices_inner, tier_time = m.group(1), m.group(2), m.group(3)
    svcs = re.findall(r"'([^']+)':\[(\d+),(\d+)\]", prices_inner)
    if not svcs:
        return None
    return label, [(s, int(lo), int(hi)) for s, lo, hi in svcs], tier_time


def render_strings(src: str):
    """Достаём из renderTable() строки, зависящие от языка (RU/UA)."""
    diag = re.search(
        r'html\+=\'<tr><td class="svc-name free">([^<]*)</td>'
        r'<td class="pr free">([^<]*)</td>'
        r'<td class="time">([^<]*)</td></tr>\';',
        src,
    )
    tmap = re.search(
        r"var time=k\.indexOf\('([^']*)'\)>-1\?'([^']*)'"
        r":k\.indexOf\('([^']*)'\)>-1\?'([^']*)':t\.time;",
        src,
    )
    # подпись для цены-сентинела [0,0] («уточняйте при заявке») — берём из самой страницы,
    # чтобы UA-версия подхватила свой перевод, а не русскую строку
    onreq = re.search(r"var pr=\(!p\[0\]&&!p\[1\]\)\?'([^']*)'", src)
    if not diag or not tmap:
        return None
    return {
        "diag": diag.group(1), "free": diag.group(2), "atyou": diag.group(3),
        "water": tmap.group(1), "wtime": tmap.group(2),
        "plat": tmap.group(3), "ptime": tmap.group(4),
        "on_request": onreq.group(1) if onreq else "Уточняйте при заявке",
    }


def build_rows(tier, s) -> str:
    label, svcs, tier_time = tier
    ind = "            "  # 12 пробелов — под отступ таблицы
    rows = [
        f'{ind}<tr><td class="svc-name free">{s["diag"]}</td>'
        f'<td class="pr free">{s["free"]}</td>'
        f'<td class="time">{s["atyou"]}</td></tr>'
    ]
    for svc, lo, hi in svcs:
        if s["water"] in svc:
            time = s["wtime"]
        elif s["plat"] in svc:
            time = s["ptime"]
        else:
            time = tier_time
        if not lo and not hi:
            pr = s["on_request"]
        else:
            pr = f"{fmt(lo)} ₴" if lo == hi else f"{fmt(lo)} — {fmt(hi)} ₴"
        rows.append(
            f'{ind}<tr><td class="svc-name">{svc}</td>'
            f'<td class="pr">{pr}</td>'
            f'<td class="time">{time}</td></tr>'
        )
    return "\n" + "\n".join(rows) + "\n          "


def process(path: str) -> bool:
    if not os.path.exists(path):
        return False
    src = open(path, encoding="utf-8").read()
    if 'id="priceBody"' not in src:
        return False
    tier = first_tier(src)
    strings = render_strings(src)
    if not tier or not strings:
        log(f"{os.path.relpath(path, ROOT)}: не нашёл TIERS/renderTable — пропускаю")
        return False
    inner = build_rows(tier, strings)
    out = re.sub(
        r'(<tbody id="priceBody">).*?(</tbody>)',
        lambda mm: mm.group(1) + inner + mm.group(2),
        src, count=1, flags=re.S,
    )
    if out == src:
        log(f"{os.path.relpath(path, ROOT)}: прайс уже пред-рендерен — правки не нужны")
        return False
    open(path, "w", encoding="utf-8").write(out)
    log(f"{os.path.relpath(path, ROOT)}: пред-рендерено строк {len(tier[1]) + 1} "
        f"(модель «{tier[0]}») ✓")
    return True


def main():
    changed = 0
    for hub in HUBS:
        try:
            if process(hub):
                changed += 1
        except Exception as e:
            log(f"{os.path.relpath(hub, ROOT)}: ошибка ({e}) — пропускаю")
    log(f"готово, обновлено файлов: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
