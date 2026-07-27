#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_hub_facts.py — синхронизирует ЦИФРЫ на хабе iPhone с живым прайсом (var TIERS).

ПРОБЛЕМА. На /remont-iphone/ цены были захардкожены в двух местах, мимо прайса, и
за время правок разъехались с ним — причём в самых заметных точках страницы:
  • hero-картинка обещала «Замена экрана от 1 200 ₴», тогда как блок .quick на ТОМ
    ЖЕ первом экране показывал «от 600 ₴» (реальный минимум). Вдвое дороже.
  • FAQ-ответ про стоимость экрана называл 1 200–7 500 ₴ в видимом тексте и
    800–8 800 ₴ в разметке, при фактических 600–11 000 ₴. Неверны обе версии.
Цены приходят из Supabase (pull_prices.py → var TIERS) и меняются, поэтому любая
захардкоженная цифра протухает молча. Здесь они выводятся из TIERS при каждой сборке.

Правим ТОЛЬКО русский хаб: украинский генерируется из него make_ua.py, а числа в
готовый перевод подставляет числовой fallback (см. tr_by_template в make_ua.py) —
скелет фразы не меняется, меняются только цифры, что как раз его случай.

Идемпотентно: регионы переписываются целиком по структуре, а не по плейсхолдеру,
поэтому повторный запуск даёт тот же результат.
Fail-safe: не нашли TIERS или регион — пропускаем и выходим с 0, сборку не ломаем.

Запуск: в build.sh ПОСЛЕ pull_prices (TIERS уже свежие) и ДО make_ua (чтобы
украинская страница собралась с исправленными числами).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = os.path.join(ROOT, "remont-iphone", "index.html")

# подпись в hero-SVG -> ключ услуги в TIERS
HERO_MAP = {
    "Замена экрана":  "Замена экрана (дисплея)",
    "Замена батареи": "Замена аккумулятора",
    "Ремонт Face ID": "Face ID",
    "После воды":     "После воды",
}

# Ответ FAQ про стоимость экрана — единый текст для видимого блока и для JSON-LD.
# Модели намеренно названы обобщённо («от iPhone SE до последних Pro Max»), чтобы
# фраза не устаревала с выходом новых моделей; конкретика живёт в прайс-таблице.
FAQ_Q = "Сколько стоит замена экрана iPhone?"
FAQ_TPL = ("Стоимость замены экрана iPhone зависит от модели: от {lo} ₴ до {hi} ₴. "
           "Ремонтируем все модели — от iPhone SE до последних Pro Max. "
           "Точную цену мастер назовёт после бесплатной диагностики.")


def log(msg):
    print(f"[sync_hub_facts] {msg}")


def fmt(n):
    """Как Number.toLocaleString('ru-RU') на странице: разряды неразрывным пробелом."""
    return f"{int(n):,}".replace(",", " ")


def price_range(src):
    """{услуга: (min lo, max hi)} по ВСЕМ тирам TIERS."""
    agg = {}
    for _label, inner, _t in re.findall(
            r"\{id:'[^']+',label:'([^']*)',prices:\{([^}]*)\},time:'([^']*)'\}", src):
        for svc, lo, hi in re.findall(r"'([^']+)':\[(\d+),(\d+)\]", inner):
            lo, hi = int(lo), int(hi)
            if lo <= 0 and hi <= 0:      # 0,0 = «уточняйте при заявке», не цена
                continue
            cur = agg.get(svc)
            agg[svc] = (min(cur[0], lo), max(cur[1], hi)) if cur else (lo, hi)
    return agg


def fix_hero(src, rng):
    """Цена в hero-SVG = минимум услуги по прайсу."""
    n = 0
    for label, svc in HERO_MAP.items():
        if svc not in rng:
            log(f"услуги {svc!r} нет в TIERS — подпись {label!r} пропущена")
            continue
        want = f"от {fmt(rng[svc][0])} ₴"
        pat = re.compile(
            r"(>%s</text>\s*<text[^>]*text-anchor=\"end\"[^>]*>)(от [^<]*)(</text>)"
            % re.escape(label))
        new, cnt = pat.subn(lambda m: m.group(1) + want + m.group(3), src)
        if cnt:
            src, n = new, n + cnt
        else:
            log(f"не нашёл подпись {label!r} в hero — пропуск")
    return src, n


def fix_faq(src, rng):
    """Диапазон в ответе про стоимость экрана — и в видимом тексте, и в JSON-LD."""
    svc = HERO_MAP["Замена экрана"]
    if svc not in rng:
        log("нет данных по замене экрана — FAQ пропущен")
        return src, 0
    lo, hi = rng[svc]
    answer = FAQ_TPL.format(lo=fmt(lo), hi=fmt(hi))
    n = 0
    # видимый <details>
    vis = re.compile(r"(<summary>%s</summary><div class=\"a\">)(.*?)(</div>)" % re.escape(FAQ_Q), re.S)
    src, c = vis.subn(lambda m: m.group(1) + answer + m.group(3), src)
    n += c
    if not c:
        log("видимый блок ответа про экран не найден")
    # JSON-LD
    ld = re.compile(r'("name":"%s","acceptedAnswer":\{"@type":"Answer","text":")(.*?)("\}\})'
                    % re.escape(FAQ_Q), re.S)
    src, c = ld.subn(lambda m: m.group(1) + answer + m.group(3), src)
    n += c
    if not c:
        log("ответ про экран в JSON-LD не найден")
    return src, n


def main():
    if not os.path.isfile(HUB):
        log("хаб не найден — пропуск")
        return 0
    src = open(HUB, encoding="utf-8").read()
    orig = src
    rng = price_range(src)
    if not rng:
        log("var TIERS не разобран — пропуск (сборка не ломается)")
        return 0

    src, n_hero = fix_hero(src, rng)
    src, n_faq = fix_faq(src, rng)

    if src != orig:
        open(HUB, "w", encoding="utf-8").write(src)
        log(f"обновлено: hero-цен {n_hero}, блоков FAQ {n_faq}")
    else:
        log(f"цифры уже совпадают с прайсом (hero {n_hero}, FAQ {n_faq}) — правок нет")
    lo, hi = rng.get(HERO_MAP["Замена экрана"], (0, 0))
    log(f"замена экрана по прайсу: {lo}–{hi} ₴")
    return 0


if __name__ == "__main__":
    sys.exit(main())
