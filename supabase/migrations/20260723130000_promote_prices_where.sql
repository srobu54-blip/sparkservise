-- promote_prices: копирует черновик цен (prices) в опубликованный снимок
-- (published_prices) по всем моделям. Зовётся из админки (sb.rpc) от JWT админа.
--
-- Фикс 2026-07-23: раньше тело было `update model_prices set published_prices = prices`
-- без WHERE — база отклоняла его ("UPDATE requires a WHERE clause", защита от
-- массовых апдейтов). Добавлен WHERE id is not null: условие есть, обновляются
-- все строки. (Сравнение prices через is distinct from не подходит — колонки
-- типа json, у которого нет оператора равенства.)
--
-- SECURITY DEFINER + grant authenticated: чтобы админ (роль authenticated) мог
-- выполнить промоут, а тело обновляло таблицу с правами владельца (в обход RLS).

create or replace function public.promote_prices()
returns void
language sql
security definer
set search_path = public
as $$
  update public.model_prices
     set published_prices = prices
   where id is not null;
$$;

grant execute on function public.promote_prices() to authenticated;
