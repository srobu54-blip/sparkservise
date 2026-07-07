# SPARK — подключение Supabase, Telegram, счётчиков (чеклист)

Всё в репозитории уже готово и **спит** до заполнения ключей — сайт от этого не ломается.
Ниже по шагам, что вписать и где. Секреты (токены, пароли) в git **не коммитим**.

---

## 1. Приём заявок (таблица `leads`)

**1.1. Применить миграцию.** После связки репо с Supabase (авто-деплой миграций по пушу)
файл `supabase/migrations/20260707120000_leads.sql` применится сам. Либо вручную из CLI:
```bash
supabase link --project-ref <REF>     # REF: Project Settings -> General
supabase db push
```
Либо скопировать SQL в Supabase → SQL Editor и выполнить.

**1.2. Вписать публичные ключи** (Project Settings → API):
- `Project URL` (вида `https://<ref>.supabase.co`)
- `anon` / `publishable` ключ (он **публичный** — попадает в браузер, это норма; защита на RLS)

В ДВА места (одинаковые значения):
- `lead-submit.js` → `CFG.url`, `CFG.anonKey`
- `admin/index.html` → `window.SB_CFG.url`, `window.SB_CFG.anonKey`

После правки `lead-submit.js` — прогнать пайплайн (см. низ файла) и задеплоить.

> Проверка: отправь тестовую заявку с сайта → строка появилась в Table Editor → `leads`.
> `anon` не должен уметь читать: `select` из браузера вернёт пусто/ошибку — это правильно.

---

## 2. Telegram-бот (уведомления о заявках)

**2.1. Создать бота:** @BotFather → `/newbot` → получить `TELEGRAM_BOT_TOKEN`.
Написать боту любое сообщение, затем узнать свой `TELEGRAM_CHAT_ID` (напр. через @userinfobot,
или для группы — добавить бота в группу).

**2.2. Задеплоить функцию** `supabase/functions/notify-telegram`:
```bash
supabase functions deploy notify-telegram
supabase secrets set TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..." WEBHOOK_SECRET="<любая-длинная-строка>"
```

**2.3. Создать Database Webhook** (Supabase → Database → Webhooks → Create):
- Table: `public.leads`, Events: **Insert**
- Type: **Supabase Edge Function** → `notify-telegram`
- HTTP Headers: добавить `x-webhook-secret` = то же значение, что в `WEBHOOK_SECRET`

> Проверка: вставь тестовую строку в `leads` → прилетело сообщение в Telegram.

---

## 3. Мини-админка `/admin/`

**3.1.** Ключи уже вписаны в шаге 1.2.

**3.2. Отключить публичную регистрацию** (КРИТИЧНО — иначе любой сможет зарегаться публичным
ключом и получить доступ): Supabase → Authentication → Sign In / Providers → **отключить Email
signups**. (В `supabase/config.toml` уже стоит `enable_signup = false` — применяется при деплое
конфига, но в дашборде продублируй.)

**3.3. Создать пользователя-админа:** Supabase → Authentication → Users → Add user (email + пароль).

**3.4. Внести админа в allowlist** (только он будет видеть заявки — не любой авторизованный):
скопируй `User UID` созданного юзера и в SQL Editor выполни:
```sql
insert into public.app_admins (user_id) values ('<UID-админа>');
```

> `/admin/` уже `noindex` и не в sitemap. Заявки видит ТОЛЬКО пользователь из `app_admins`
> (RLS через `is_admin()`); `anon` и «просто authenticated» — ничего. Меняет только статус/заметку.

> **Антиспам.** На INSERT стоит throttle: один и тот же телефон не чаще раза в 30 сек (гасит
> наивный флуд и двойные отправки). Клиентские honeypot/тайм-трап (`lead-submit.js`) отсекают
> ботов, идущих через форму, но НЕ защищают прямые запросы в REST. Если пойдёт спам —
> подключить **Cloudflare Turnstile**: капча-токен проверять в Edge-функции-прокси, а прямой
> `insert` у `anon` отобрать (вставку делать от service_role внутри функции). Пока трафик
> небольшой — throttle + honeypot достаточно.

---

## 4. Счётчики: GTM + Search Console

Заполнить `_build/site_ids.json`:
```json
{ "gtm_id": "GTM-XXXXXXX", "google_site_verification": "<токен из GSC, метод «HTML-тег»>" }
```
Прогнать пайплайн → задеплоить. Инъектор `inject_gtm.py` поставит контейнер GTM (head+noscript)
на все страницы и meta-верификацию GSC.

- **GA4 и Meta Pixel** отдельно в HTML **не вставляем** — заводим их как теги **внутри GTM**.
  Событие лида уже лежит в `dataLayer` (`generate_lead` с `user_data` для Enhanced Conversions,
  `event_id` для дедупа Meta) — в GTM повесить триггер «Custom Event: generate_lead»
  (условие `test_mode` ≠ true) → теги Google Ads Conversion и Meta Lead.
- **Search Console:** для домена лучше **Domain property (DNS TXT)** — покрывает http/https/www.
  Meta-тег из `site_ids.json` — запасной вариант (URL-prefix), верифицирует конкретный хост.

---

## Порядок пайплайна (после любой правки RU или JS)
```
python3 _build/assemble*.py            # если менялся контент
python3 _build/make_ua.py              # пересборка /ua/ (сам зовёт i18n_wire)
python3 _build/mark_current_nav.py
python3 _build/inject_analytics.py     # analytics.js + exit-popup.js + lead-submit.js
python3 _build/inject_gtm.py           # GTM + GSC (спит, пока site_ids.json пуст)
python3 _build/inline_css.py
python3 _build/set_og_host.py          # og:image -> живой хост (до переезда домена)
python3 _build/sync_sitemap_dates.py   # ПОСЛЕДНИМ, отдельным коммитом
```

## Что НЕ коммитить в git
Токен бота, `WEBHOOK_SECRET`, пароль БД, пароль админа — только в Supabase Secrets / панели.
Публичные `anon`-ключ и `Project URL` в JS — можно (они и так уходят в браузер).
