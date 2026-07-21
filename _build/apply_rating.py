#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_rating.py — разносит рейтинг и число отзывов из _build/google_rating.json
по всем страницам сайта (видимый текст + разметка aggregateRating).

Зачем отдельным шагом: цифры встречаются и в генерируемых страницах, и в вручную
свёрстанных (index/kontakty/o-kompanii/хаб), и в JSON блога. Единый пост-шаг
избавляет от рассинхрона — раньше значения разъезжались и устаревали.

⚠️ Замены строго по контексту. Строка «4,9» встречается внутри CSS
   (rgba(31,174,90,...)) и SVG-путей (M4.93 4.93l1.41) — слепой replace
   покорёжил бы вёрстку и иконки. Здесь каждый шаблон привязан к своему окружению,
   плюс есть проверка целостности: файл пропускается, если задет SVG/CSS.

Запускать ПОСЛЕ генераторов и make_ua (шаг в build.sh). Идемпотентно.
Нет json → шаг молча пропускается.
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "_build", "google_rating.json")
SKIP_DIRS = ("_build", "og", "admin", "supabase", ".git", ".claude")

# Маркеры, которые ломать нельзя: если их количество изменилось — правка отменяется
GUARD = re.compile(r"rgba\(31,174,\d+|M4\.\d+ 4\.\d+|4\.\d-1\.3A10")


def log(m): print(f"[apply_rating] {m}")


def patterns(rating, reviews):
    """(регэксп, замена) — каждый привязан к своему контексту."""
    r_dot = rating                    # 4.8
    r_com = rating.replace(".", ",")  # 4,8
    n = str(reviews)
    return [
        # разметка
        (re.compile(r'("ratingValue":\s*")[\d.]+(")'),      lambda m: m.group(1) + r_dot + m.group(2)),
        (re.compile(r'("reviewCount":\s*")\d+(")'),         lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'("ratingCount":\s*")\d+(")'),         lambda m: m.group(1) + n + m.group(2)),
        # trustbar: ★ 4.8</span> ... 158 отзывов
        (re.compile(r'(<span class="tb-star">★ )[\d.]+(</span>)'), lambda m: m.group(1) + r_dot + m.group(2)),
        (re.compile(r'(</span>)\d+( отзывов)'),             lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(</span>)\d+( відгуків)'),            lambda m: m.group(1) + n + m.group(2)),
        # текстовые упоминания
        (re.compile(r'\d+( отзывов на Google)'),            lambda m: n + m.group(1)),
        (re.compile(r'\d+( відгуків на Google)'),           lambda m: n + m.group(1)),
        (re.compile(r'(из )\d+( отзывов)'),                 lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(з )\d+( відгуків)'),                 lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(по )\d+( отзывам)'),                 lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(за )\d+( відгуками)'),               lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(на основе )\d+( реальных отзывов)'), lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(на основі )\d+( реальних відгуків)'),lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'(на основе )\d+( отзывов)'),          lambda m: m.group(1) + n + m.group(2)),
        (re.compile(r'\((\d+) отзывов\)'),                  lambda m: "(" + n + " отзывов)"),
        (re.compile(r'[\d.]+(★ на Google)'),                lambda m: r_dot + m.group(1)),
        (re.compile(r'[\d.]+(★ из )'),                      lambda m: r_dot + m.group(1)),
        (re.compile(r'(рейтинг )[\d.]+(★)'),                lambda m: m.group(1) + r_dot + m.group(2)),
        # числовые плашки в вёрстке
        (re.compile(r'(tnum">)[\d,]+(<span class="sub">)'), lambda m: m.group(1) + r_com + m.group(2)),
        (re.compile(r'(sc tnum">)[\d,]+(</div>)'),          lambda m: m.group(1) + r_com + m.group(2)),
        (re.compile(r'(<span>)[\d,]+(<small>рейтинг Google)'), lambda m: m.group(1) + r_com + m.group(2)),
        (re.compile(r'(class="num">)[\d.]+( ★</div>)'),     lambda m: m.group(1) + r_dot + m.group(2)),
        (re.compile(r'(rev-num">)[\d.]+(<span>)'),          lambda m: m.group(1) + r_dot + m.group(2)),
    ]


def walk_html():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(root, f)


def main():
    if not os.path.exists(SRC):
        log("нет google_rating.json — шаг пропущен"); return 0
    try:
        d = json.load(open(SRC, encoding="utf-8"))
        rating, reviews = str(d["rating"]), int(d["reviews"])
    except Exception as e:
        log(f"json не прочитан ({e}) — шаг пропущен"); return 0

    pats = patterns(rating, reviews)
    changed = guarded = 0
    for path in walk_html():
        s = open(path, encoding="utf-8").read()
        before = len(GUARD.findall(s))
        new = s
        for rx, rep in pats:
            new = rx.sub(rep, new)
        if new == s:
            continue
        if len(GUARD.findall(new)) != before:
            log(f"⚠ {os.path.relpath(path, REPO)}: задет SVG/CSS — правка отменена")
            guarded += 1
            continue
        open(path, "w", encoding="utf-8").write(new)
        changed += 1

    log(f"{rating} ★ / {reviews} отзывов → страниц обновлено: {changed}"
        + (f", отменено ради целостности: {guarded}" if guarded else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
