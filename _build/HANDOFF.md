# SPARK — HANDOFF (передача проекта)

_Обновлено: 2026-06-25. Всё закоммичено и запушено._

## Что это
Сайт сервисного центра Apple «SPARK» (Одесса). Статический HTML, без сборки/фреймворка. Хостинг — GitHub Pages.

- **Репозиторий:** https://github.com/maxsushek/sparkservise
- **Локально:** `/Users/koristuvac/Downloads/sparkservise-git/`
- **Live (прототип):** https://maxsushek.github.io/sparkservise/
- **Будущий домен:** `sparkservice.od.ua` (на него указывают canonical; сейчас там старый сайт — не репойнтить).

## Деплой
```
cd /Users/koristuvac/Downloads/sparkservise-git
git add -A && git commit -m "..."
PATH="$HOME/bin:$PATH" git push
```
GitHub Pages билдит сам после push. **Очередь билдов часто лагает 1–5 мин** — 404 сразу после push это нормально, проверять через пару минут. `gh` CLI лежит в `~/bin/gh`. Права: `~/.claude/settings.json` → `permissions.defaultMode=bypassPermissions` + allowlist (Edit/Write/Read/Bash).

## Структура: что генерируется, что руками
Папка **`_build/` (в .gitignore, НЕ в репо)** — Python-сборщики + контент JSON. Дизайн-каркас (шапка/футер/форма/модалка/пути) зашит в сборщики → одинаков на всех страницах.

| Сборщик | Что делает | Контент |
|---|---|---|
| `_build/assemble.py` | 5 страниц устройств: `remont-macbook/imac/ipad/apple-watch/airpods` (своя hero-SVG, словарь иконок `ICONS`) | `_build/<slug>.json` |
| `_build/assemble_service.py` | услуги: `razblokirovka-iphone`, `diagnostika`, `vosstanovlenie-dannyh` (импортит каркас из assemble.py) | `_build/service/<slug>.json` |
| `_build/assemble_blog.py` | 3 статьи `/blog/<slug>/` + индекс `/blog/`; TL;DR, HowTo, опрос (`POLL_HTML`) | `_build/blog/<slug>.json` |

**Как править генерируемую страницу:** меняешь JSON (или код сборщика) → `python3 _build/assemble*.py` → commit → push.

**Руками (НЕ сборщик):** `index.html` (главная; правлена внешне — богатая SEO-разметка), `remont-iphone/index.html` (хаб + JS-массив `TIERS` с ценами 37 моделей), `remont-iphone/iphone-17-pro-max/index.html` (модель, реальное фото `iphone-17-pro-max.webp`), `razblokirovka-icloud/index.html`, `kontakty/index.html`.

**Важно про меню/футер:** они есть и в сборщиках, и в руч­ных файлах. При изменении навигации — правь оба assemble.py-шаблона (`NAV`/`FOOTER`) + assemble_blog.py + 5 ручных файлов, потом перезапусти все 3 сборщика. (Так делались: переименование «Разблокировка»→«Услуги», добавление пунктов.)

## Конвенции
- Пути относительные по глубине: главная `./`, 1 уровень `../`, 2 уровня `../../`. **Абсолютных `/...` быть не должно** (ломаются в подпапке github.io). Проверка: `grep -c 'href="/' file`.
- Контекстные ссылки в JSON-контенте — токены `{{L:цель|анкор}}`, резолвятся сборщиком в относительные.
- CTA-кнопка — «Записаться». Прайс в таблицах — диапазон «A — B ₴» (без «от»).
- Общий стиль: `.trustbar` (★4.9 Google · 127 отзывов · 32 000 ремонтов · 9 лет), trust-бейджи у форм (диагностика/гарантия/без предоплаты), `.cta-note` «Перезвоним за 15 минут». Адаптивная прайс-таблица (`.price-table`) — в `styles.css`.
- Schema.org: услуги/ремонт — Service+Breadcrumb+FAQPage; блог — BlogPosting+Breadcrumb+FAQPage(+HowTo); главная — Organization+ElectronicsStore+WebSite; контакты — ElectronicsStore+ContactPage.

## Готовые страницы (все live)
Главная · `/remont-iphone/` · `/remont-iphone/iphone-17-pro-max/` · `/remont-macbook/` · `/remont-imac/` · `/remont-ipad/` · `/remont-apple-watch/` · `/remont-airpods/` · `/razblokirovka-icloud/` · `/razblokirovka-iphone/` · `/diagnostika/` · `/vosstanovlenie-dannyh/` · `/kontakty/` · `/blog/` + 3 статьи (`original-ili-kopiya-displeya-iphone`, `iphone-upal-v-vodu-chto-delat`, `pochemu-bystro-saditsya-batareya`). `sitemap.xml`, `robots.txt`.

## TODO / план
1. **Скупка/выкуп Apple** — новая услуга (предложена, не сделана). Сильный коммерческий интент. Делать тем же конвейером (assemble_service.py + новый slug + иконка).
2. **Supabase для опроса блога** — таблица `poll_votes` (poll, option) + RLS (аноним insert + чтение агрегата), виджет шлёт insert/тянет реальные %. Сейчас localStorage + посеянные счётчики; хук помечен в `POLL_HTML` (`vote()`). Supabase у пользователя подключён через MCP.
3. **Реальные изображения:**
   - Блог: положить `cover.webp` и `inline.webp` в `blog/<slug>/` — появятся вместо заглушек (onerror-fallback).
   - Модели/устройства: фото-обложки.
   - **`og:image`**: весь сайт ссылается на `https://sparkservice.od.ua/og/spark.jpg` (+ `/og/logo.png`) — этих файлов нет. Нужны для превью в соцсетях. Создать `og/` с картинками 1200×630.
4. **Ещё страницы моделей iPhone** (16 Pro Max, 15 Pro Max, 14 Pro…) по шаблону `iphone-17-pro-max`. Ahrefs (Украина) топ-инфо-темы для будущих статей: «iPhone не заряжается» (потенциал ~900, KD 0), «iPhone не включается» (~800, KD 0).
5. **`/o-kompanii/`** — ссылка в футере ведёт на 404, страницы нет.
6. **Домен/i18n (перед запуском):** canonical главной = `https://sparkservice.od.ua/ru/` + hreflang (uk=`/`, ru=`/ru/`), а у подстраниц canonical в корне (`/remont-iphone/` и т.д.) — несогласовано. Решить структуру при подключении реального домена. Кэш-заголовки (10 мин) и security (CSP/HSTS/COOP/XFO) — ограничение GitHub Pages, ставятся на проде за CDN (Cloudflare/Nginx).

## Двуязычность RU + UA — ЕДИНЫЙ ИСТОЧНИК (важно!)
Сайт двуязычный: **RU в корне** (`/<path>/`), **UK в `/ua/<path>/`** (62 пары). RU — ИСТОЧНИК. UA — генерируемый артефакт (НЕ править руками — перезатрётся).

Инструменты в `_build/`:
- `i18n_tok.py` — lossless токенайзер HTML (общий).
- `i18n_ua.json` — каталог переводов `{ru:ua}` (ветки text/attr/jsonld/js). Сюда дописывать перевод НОВЫХ строк.
- `i18n_bootstrap.py` — разовый: пересобирает каталог из существующих RU/UA пар (если надо).
- `make_ua.py` — собирает все `/ua/` из RU по каталогу, в конце сам зовёт `i18n_wire.py`.
- `i18n_wire.py` — детерминированная обвязка (lang/пути/canonical/og:url/reciprocal hreflang/переключатель в топбаре И мобильном меню/JS-редирект/фото из RU-папки/внутренние ссылки prefer-UA/sitemap).

**ВОРКФЛОУ при любой правке/регенерации RU:**
```
python3 _build/assemble_model.py        # и др. генераторы, как обычно (+ sync_calc.py при ценах)
python3 _build/make_ua.py               # пересобрать UA (печатает список НЕПЕРЕВЕДЁННЫХ новых строк)
# дописать перевод новых строк в _build/i18n_ua.json → повторить make_ua.py
```
Цены/числа/латиница нейтральны → проходят насквозь (авто-синхрон цен RU→UA). «Непереведённые» в отчёте, совпадающие с RU (Ремонт/Телефон/Блог/модели), — ложные (ru==ua, выводятся как есть).

⚠ Известный баг: 3 RU service-страницы (`diagnostika`, `vosstanovlenie-dannyh`, `razblokirovka-iphone`) имеют НЕВАЛИДНЫЙ JSON-LD (неэкранированная кавычка от инлайн-`<a>` в FAQ-ответе). `make_ua` для них берёт валидный JSON-LD из текущей UA (fallback) — но он не авто-синхронится. Чинить в источнике: `assemble_service.py` уже использует `json.dumps` (корректно) → перегенерировать эти 3 страницы (`python3 _build/assemble_service.py`) ИЛИ убрать инлайн-`<a>` из FAQ-ответа в `_build/service/*.json`.

## Как продолжить в новом чате
Память (`~/.claude/projects/-Users-koristuvac-Downloads-spark/memory/`) подгружается автоматически — новый чат уже знает архитектуру, правило перелинковки и этот статус. Достаточно открыть новый чат и написать, например: «продолжаем проект SPARK, делаем Скупку Apple» (или что нужно). При желании дай ссылку на этот файл.
