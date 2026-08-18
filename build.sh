#!/usr/bin/env bash
#
# build.sh — полная детерминированная пересборка сайта SPARK.
# Порядок выведен из зависимостей скриптов (докстринги _build/*.py).
#
# Использование:
#   bash build.sh                 # обычная пересборка
#   BUILD_SKIP_PULL=1 bash build.sh   # не тянуть цены из Supabase (только локальные)
#
# В Vercel:  Build Command = bash build.sh   (Output Directory = .)
# pull_prices — fail-safe: нет БД/сети → сборка идёт на ценах из коммита.

set -euo pipefail
cd "$(dirname "$0")"

PY=python3
$PY --version

step () { echo ""; echo "▶ $*"; }

# 1) Единый источник цен: Supabase → var TIERS (fail-safe, может ничего не менять)
if [ "${BUILD_SKIP_PULL:-0}" != "1" ]; then
  step "pull_prices — Supabase → var TIERS"
  $PY _build/pull_prices.py
fi

# 2) Хабы устройств (iPad/MacBook/iMac/Watch/AirPods; iPhone-хаб не трогается)
step "assemble — хабы устройств";           $PY _build/assemble.py
# 3) Spoke-страницы моделей iPhone из TIERS
step "assemble_model — модели iPhone";       $PY _build/assemble_model.py
# 4) Посадочная «Замена аккумулятора»
step "assemble_battery — АКБ";               $PY _build/assemble_battery.py
# 4.1) Посадочная «Замена стекла Apple Watch» (нет контент-json → шаг пропускается)
step "assemble_watch_glass — стекло Watch";  $PY _build/assemble_watch_glass.py
# 4.2) Посадочная «Замена экрана (дисплея) iPhone» — combined (экран + стекло)
step "assemble_screen — экран iPhone";       $PY _build/assemble_screen.py
# 4.3) Посадочная «Замена заднего стекла iPhone»
step "assemble_backglass — заднее стекло";   $PY _build/assemble_backglass.py
# 4.3.1) Посадочная «Ремонт Face ID» и 4.3.2) «Ремонт после воды». Обе закрывают
#      разрыв, найденный 18.08: статьи блога «Не работает Face ID» и «iPhone упал
#      в воду» собирают показы по теме, но вели человека в общий хаб — коммерческой
#      страницы под них не существовало. Для сравнения: единственная статья с парной
#      посадочной («греется» → аккумулятор) ссылается на неё 4 раза, и это лучшая
#      сервисная страница сайта — 948 показов при CTR 4,9%.
step "assemble_faceid — Face ID";            $PY _build/assemble_faceid.py
step "assemble_water — после воды";          $PY _build/assemble_water.py
# 4.4) Посадочная «Замена аккумулятора MacBook» — крупнейший сервисный кластер
#      MacBook по спросу (~1900 запросов/мес против 30 у клавиатуры).
step "assemble_macbook_battery — АКБ MacBook"; $PY _build/assemble_macbook_battery.py
# 4.5) Посадочная «Замена/ремонт тачпада MacBook» (~240 запросов/мес, страницы не было)
step "assemble_macbook_trackpad — тачпад";     $PY _build/assemble_macbook_trackpad.py
# 4.6) Посадочная «MacBook не заряжается» (~260 запросов/мес, KD 0). Взят ремонтный
#      кластер, а не торговый: «зарядка для macbook» — интент покупки (CPC 15-20 ₴),
#      там магазины, сервису его не выиграть. Цены тянутся из прайса хаба.
step "assemble_macbook_charging — зарядка";    $PY _build/assemble_macbook_charging.py
# 4.7) Посадочная «Чистка MacBook от пыли + термопаста». Кластер MacBook по GSC —
#      1859 показов и ОДИН клик при позиции 21, крупнейший неотработанный на сайте.
#      У чистки страницы не было вовсе, поэтому в GSC 17 показов: ранжироваться нечему.
#      Две головы: «чистка макбука» 150 и «чистка клавиатуры macbook» 150 — под вторую
#      отдельный H2-блок. Цена тянется из строки прайса хаба через hub_price().
step "assemble_macbook_cleaning — чистка";     $PY _build/assemble_macbook_cleaning.py
# 5) Страницы услуг (разблокировка, диагностика, восстановление)
step "assemble_service — услуги";            $PY _build/assemble_service.py
# 5.1) Посадочная «Разлочка iPhone от оператора» — спойк /razblokirovka-iphone/.
#      Кластер разблокировки — единственный коммерческий кластер сайта без
#      локального пака (DR 0 сидят в топ-5), а разлочка — самый дорогой чек
#      внутри него. Цены тянутся из прайса родителя, ПОСЛЕ assemble_service.
step "assemble_sim_unlock — разлочка";       $PY _build/assemble_sim_unlock.py
# 6) Блог
step "assemble_blog — блог";                 $PY _build/assemble_blog.py
# 7) Под-модели не-iPhone устройств
step "assemble_device_model — устройства";   $PY _build/assemble_device_model.py
# 8) Мини-фото моделей в iPhone-хаб (до make_ua)
step "apply_model_photos — фото моделей";    $PY _build/apply_model_photos.py
# 9) Калькулятор на главной (main.js) ← TIERS
step "sync_calc — калькулятор главной";      $PY _build/sync_calc.py
# 9.1) Цифры хаба iPhone (hero + FAQ про экран) ← TIERS. Только RU: UA соберётся
#      из него в make_ua, числа в перевод подставит числовой fallback.
step "sync_hub_facts — цены хаба iPhone";    $PY _build/sync_hub_facts.py

# 10) UA-страницы из RU по каталогу переводов.
#     make_ua внутри сам зовёт i18n_wire. Он ВОЗВРАЩАЕТ 1 как ПРЕДУПРЕЖДЕНИЕ
#     о непереведённых сегментах (не фатально). Отличаем предупреждение от
#     реального падения: после запуска должно существовать ≥60 UA-страниц.
step "make_ua — украинские страницы (+ i18n_wire внутри)"
$PY _build/make_ua.py || echo "  make_ua: предупреждения (непереведённые сегменты) — это не ошибка, продолжаю"
UA_PAGES=$(find ua -name index.html 2>/dev/null | wc -l | tr -d ' ')
if [ "$UA_PAGES" -lt 60 ]; then
  echo "✖ make_ua собрал лишь $UA_PAGES UA-страниц (<60) — это уже реальный сбой. Стоп."; exit 1
fi
echo "  UA-страниц на месте: $UA_PAGES"
# 11) Подстраховка обвязки (идемпотентно; make_ua её уже вызвал)
step "i18n_wire — hreflang/canonical (подстраховка)";  $PY _build/i18n_wire.py || true
# 12) Активный пункт меню (после i18n_wire — нужны финальные пути)
step "mark_current_nav — активное меню";     $PY _build/mark_current_nav.py

# 12.5) Server-render прайса хаба: запекаем строки в <tbody id="priceBody"> (RU+UA),
#       чтобы цены были в HTML для краулеров. После make_ua (UA-хаб уже собран).
step "prerender_hub_prices — прайс хаба в HTML"; $PY _build/prerender_hub_prices.py

# 12.6) Рейтинг Google → во все страницы (из _build/google_rating.json).
#       Значения обновляет еженедельный GitHub Action (.github/workflows/google-rating.yml).
#       Ключ в Vercel НЕ задаём — иначе платный запрос уйдёт на каждой сборке.
if [ -n "${GOOGLE_PLACES_API_KEY:-}" ]; then
  step "fetch_google_rating — рейтинг из Places API"; $PY _build/fetch_google_rating.py || true
fi
step "apply_rating — рейтинг по страницам";  $PY _build/apply_rating.py

# 13-16) Инъекции в <head> и финальная оптимизация
step "inject_favicon — фавикон";             $PY _build/inject_favicon.py
step "inject_analytics — analytics.js";      $PY _build/inject_analytics.py
step "set_og_host — хост og:image";          $PY _build/set_og_host.py
step "inline_css — инлайн CSS главной";      $PY _build/inline_css.py

# 17) lastmod в sitemap по git (только если репозиторий на месте)
if [ -d .git ]; then
  step "sync_sitemap_dates — даты sitemap";  $PY _build/sync_sitemap_dates.py || true
fi

# 18) Гейт: инлайн-скрипты должны парситься. Ловит оборванные строки от апострофа
#     в UA-переводах — единственный класс багов, который HTML-проверки не видят
#     (страница валидна и отдаёт 200, но весь скрипт мёртв и контент не проявляется).
step "check_js_syntax — синтаксис инлайн-JS";  $PY _build/check_js_syntax.py

# 19) Гейт: ни одна цена на странице не спорит с прайсом. Ловит захардкоженные
#     цифры — этот класс не виден глазами, потому что price-live.js исправляет
#     ячейку в браузере, и заниженную цену получают только Google и краулеры.
step "check_prices — цены против прайса";      $PY _build/check_prices.py

echo ""
echo "✅ build.sh завершён"
