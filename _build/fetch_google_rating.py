#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_google_rating.py — тянет актуальный рейтинг и число отзывов из Google Places API
и кладёт их в _build/google_rating.json. Оттуда их разносит по страницам apply_rating.py.

Зачем: цифры отзывов раньше были зашиты в 5 генераторов и вручную свёрстанные файлы,
из-за чего устаревали (было 4.9/127 при реальных 4.8/158 — завышенный рейтинг в
review-разметке это риск санкций от Google и Bing).

Что нужно (задаётся переменными окружения, в репозиторий ключ не коммитим):
    GOOGLE_PLACES_API_KEY  — ключ Google Cloud с включённым Places API
    GOOGLE_PLACE_ID        — идентификатор точки (ChIJ...). Если не задан, скрипт
                             найдёт его по названию и координатам и подскажет.

Запуск:
    GOOGLE_PLACES_API_KEY=... python3 _build/fetch_google_rating.py
    python3 _build/fetch_google_rating.py --find-place-id   # только найти place_id

Fail-safe: нет ключа / ошибка сети / подозрительный ответ → json НЕ трогаем,
сборка идёт на прежних значениях. Сломать сайт нельзя.

Стоимость: 1 запрос на сборку. Поле rating относится к Atmosphere Data,
это порядка $5 за 1000 запросов — при паре сборок в день расход копеечный.
"""
import json, os, sys, urllib.parse, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "_build", "google_rating.json")

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
PLACE_ID = os.environ.get("GOOGLE_PLACE_ID", "").strip()

# Ориентиры точки из кода сайта (для поиска place_id, если он не задан)
BIZ_NAME = "SPARK сервисный центр Apple"
BIZ_LAT, BIZ_LNG = 46.4035605, 30.7226524


def log(m): print(f"[google_rating] {m}")


def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def find_place_id():
    """Ищет place_id по названию рядом с известными координатами."""
    q = urllib.parse.urlencode({
        "input": BIZ_NAME, "inputtype": "textquery",
        "locationbias": f"point:{BIZ_LAT},{BIZ_LNG}",
        "fields": "place_id,name,formatted_address", "key": API_KEY})
    d = get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json?" + q)
    cands = d.get("candidates") or []
    if not cands:
        log(f"точка не найдена (status={d.get('status')})"); return None
    for c in cands:
        log(f"найдено: {c.get('name')} — {c.get('formatted_address')}")
        log(f"  place_id: {c.get('place_id')}")
    return cands[0].get("place_id")


def fetch(place_id):
    q = urllib.parse.urlencode({
        "place_id": place_id, "fields": "rating,user_ratings_total,name",
        "language": "ru", "key": API_KEY})
    d = get("https://maps.googleapis.com/maps/api/place/details/json?" + q)
    if d.get("status") != "OK":
        log(f"API вернул status={d.get('status')} {d.get('error_message','')}"); return None
    r = d.get("result") or {}
    return r.get("rating"), r.get("user_ratings_total"), r.get("name")


def main():
    if not API_KEY:
        log("нет GOOGLE_PLACES_API_KEY — оставляю прежние значения. OK.")
        return 0

    if "--find-place-id" in sys.argv:
        find_place_id(); return 0

    pid = PLACE_ID or find_place_id()
    if not pid:
        log("не определён place_id — оставляю прежние значения"); return 0

    try:
        got = fetch(pid)
    except Exception as e:
        log(f"ошибка запроса ({e}) — оставляю прежние значения"); return 0
    if not got:
        return 0
    rating, total, name = got

    # ── защита от мусора: не даём испортить сайт кривым ответом ──
    if not isinstance(rating, (int, float)) or not (1.0 <= rating <= 5.0):
        log(f"подозрительный рейтинг {rating} — пропускаю"); return 0
    if not isinstance(total, int) or total < 1:
        log(f"подозрительное число отзывов {total} — пропускаю"); return 0

    prev = {}
    if os.path.exists(OUT):
        try: prev = json.load(open(OUT, encoding="utf-8"))
        except Exception: pass
    # число отзывов не должно падать резко — почти всегда это сбой на стороне API
    if prev.get("reviews") and total < prev["reviews"] * 0.8:
        log(f"число отзывов упало {prev['reviews']} → {total} (>20%) — пропускаю ради безопасности")
        return 0

    data = {"rating": f"{rating:.1f}", "reviews": total, "source": "Google Places API",
            "place_id": pid, "place_name": name}
    if prev.get("rating") == data["rating"] and prev.get("reviews") == data["reviews"]:
        log(f"без изменений: {data['rating']} ★ / {data['reviews']} отзывов")
        return 0

    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"обновлено: {prev.get('rating','?')}/{prev.get('reviews','?')} → "
        f"{data['rating']} ★ / {data['reviews']} отзывов ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
