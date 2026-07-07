-- SPARK — таблица заявок (leads) + строгий RLS.
-- Модель доступа:
--   anon (браузер, публичный anon-ключ) — ТОЛЬКО INSERT и ТОЛЬКО в разрешённые колонки;
--     читать/менять/удалять НЕ может (нельзя выкачать базу заявок).
--   authenticated И состоит в app_admins — SELECT всех заявок + UPDATE только статуса/заметки.
--     ВАЖНО: сам факт «authenticated» НЕ даёт доступа (иначе любой, кто самозарегался через
--     публичный anon-ключ, читал бы все заявки — это дыра). Доступ только у allowlist-админов.
-- Проект создан с ВЫКЛ «Automatically expose new tables» → гранты прописываем явно.

-- ── allowlist админов (кто реально видит заявки) ──
create table if not exists public.app_admins (
  user_id  uuid primary key references auth.users(id) on delete cascade,
  added_at timestamptz not null default now()
);
alter table public.app_admins enable row level security;
revoke all on public.app_admins from anon, authenticated;   -- никто из клиентов не трогает саму таблицу

-- проверка «текущий пользователь — админ». security definer читает app_admins в обход RLS.
create or replace function public.is_admin() returns boolean
  language sql stable security definer set search_path = public as $$
    select exists (select 1 from public.app_admins where user_id = auth.uid())
  $$;

-- ── таблица заявок ──
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
  constraint leads_phone_len    check (char_length(phone) between 5 and 32),
  constraint leads_name_len     check (name     is null or char_length(name)     <= 120),
  constraint leads_service_len  check (service  is null or char_length(service)  <= 200),
  constraint leads_page_len     check (page_url is null or char_length(page_url) <= 500),
  constraint leads_referrer_len check (referrer is null or char_length(referrer) <= 500),
  constraint leads_lang_chk     check (lang is null or lang in ('ru','uk')),
  constraint leads_utm_size     check (utm is null or pg_column_size(utm) <= 2048),
  constraint leads_source_chk   check (source in ('exit_popup','modal_callback','inline_form','unknown')),
  constraint leads_status_chk   check (status in ('new','in_progress','done','spam'))
);

create index if not exists leads_created_at_idx  on public.leads (created_at desc);
create index if not exists leads_status_idx      on public.leads (status);
create index if not exists leads_phone_time_idx  on public.leads (phone, created_at desc);

-- throttle: не принимать тот же телефон чаще раза в 30 сек (гасит наивный флуд и
-- случайные двойные отправки). Полноценный антиспам — captcha/Turnstile (см. SUPABASE_SETUP.md).
create or replace function public.leads_throttle() returns trigger
  language plpgsql security definer set search_path = public as $$
  begin
    if exists (
      select 1 from public.leads
      where phone = new.phone and created_at > now() - interval '30 seconds'
    ) then
      raise exception 'rate_limited' using errcode = '53400';
    end if;
    return new;
  end $$;
drop trigger if exists leads_throttle_trg on public.leads;
create trigger leads_throttle_trg before insert on public.leads
  for each row execute function public.leads_throttle();

alter table public.leads enable row level security;

-- ── гранты (чистый лист, затем точечно) ──
revoke all on public.leads from anon, authenticated;
grant usage on schema public to anon, authenticated;
-- anon вставляет ТОЛЬКО эти колонки (id/created_at/status/note остаются на дефолтах)
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

-- SELECT/UPDATE только у allowlist-админов, НЕ у всей роли authenticated
drop policy if exists auth_select_leads on public.leads;
create policy auth_select_leads on public.leads
  for select to authenticated
  using (public.is_admin());

drop policy if exists auth_update_leads on public.leads;
create policy auth_update_leads on public.leads
  for update to authenticated
  using (public.is_admin())
  with check (public.is_admin() and status in ('new','in_progress','done','spam'));
