-- SPARK — таблица заявок (leads) + строгий RLS.
-- Модель доступа:
--   anon (браузер посетителя, публичный anon-ключ) — ТОЛЬКО INSERT и ТОЛЬКО в
--     разрешённые колонки; читать/менять/удалять НЕ может (нельзя выкачать базу заявок).
--   authenticated (админ, вошёл через Supabase Auth) — SELECT всех заявок + UPDATE
--     только статуса/заметки.
-- Проект создан с ВЫКЛЮЧЕННЫМ «Automatically expose new tables», поэтому гранты
-- прописываем явно (без них таблица недоступна из Data API вообще).

create table if not exists public.leads (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text,
  phone       text not null,
  service     text,                              -- что чинит / текст услуги
  source      text not null default 'unknown',   -- exit_popup | modal_callback | inline_form | unknown
  page_url    text,                              -- откуда отправлено
  lang        text,                              -- ru | uk
  utm         jsonb,                             -- {source,medium,campaign,term,content}
  referrer    text,
  status      text not null default 'new',       -- new | in_progress | done | spam
  note        text,
  constraint leads_phone_len   check (char_length(phone) between 5 and 32),
  constraint leads_name_len    check (name    is null or char_length(name)    <= 120),
  constraint leads_service_len check (service is null or char_length(service) <= 200),
  constraint leads_page_len    check (page_url is null or char_length(page_url) <= 500),
  constraint leads_source_chk  check (source in ('exit_popup','modal_callback','inline_form','unknown')),
  constraint leads_status_chk  check (status in ('new','in_progress','done','spam'))
);

create index if not exists leads_created_at_idx on public.leads (created_at desc);
create index if not exists leads_status_idx     on public.leads (status);

alter table public.leads enable row level security;

-- ── гранты (чистый лист, затем точечно) ──
revoke all on public.leads from anon, authenticated;
grant usage on schema public to anon, authenticated;
-- anon вставляет ТОЛЬКО эти колонки (id/created_at/status/note остаются на дефолтах →
-- спамер не может выставить status='done' или подделать дату)
grant insert (name, phone, service, source, page_url, lang, utm, referrer)
  on public.leads to anon;
-- админ читает всё, меняет только статус и заметку
grant select on public.leads to authenticated;
grant update (status, note) on public.leads to authenticated;

-- ── RLS-политики ──
drop policy if exists anon_insert_leads on public.leads;
create policy anon_insert_leads on public.leads
  for insert to anon
  with check (
    char_length(phone) between 5 and 32
    and source in ('exit_popup','modal_callback','inline_form','unknown')
    and status = 'new'
  );

drop policy if exists auth_select_leads on public.leads;
create policy auth_select_leads on public.leads
  for select to authenticated
  using (true);

drop policy if exists auth_update_leads on public.leads;
create policy auth_update_leads on public.leads
  for update to authenticated
  using (true)
  with check (status in ('new','in_progress','done','spam'));
