-- ============================================================================
-- Добавляет услугу «Замена стекла (сепарация)» всем моделям iPhone.
--
-- Значение [0,0] — цена-сентинел: сайт показывает «Уточняйте при заявке».
-- Как только проставите реальные цифры в админке, они сразу появятся на сайте.
--
-- ⚠️ ПОРЯДОК КЛЮЧЕЙ ВАЖЕН. Live-обновление цен на хабе сопоставляет услуги
--    ПО ПОЗИЦИИ, а не по названию. Поэтому ключ вставляется строго ПОСЛЕ
--    «Замена экрана (дисплея)», а не в конец объекта.
--
-- Обновляются ОБА столбца: prices (черновик) и published_prices (то, что на
-- сайте). Если обновить только один — структуры разойдутся, и live-обновление
-- цен отключится (оно сверяет количество услуг).
--
-- Идемпотентно: повторный запуск ничего не сломает, строки с уже добавленным
-- ключом пропускаются.
--
-- Запускать: Supabase → SQL Editor → вставить целиком → Run.
-- ============================================================================

-- 1) Черновик (prices)
update public.model_prices m
set prices = x.new_json
from (
  select mp.id,
         ('{' || string_agg(part, ',' order by ord) || '}')::json as new_json
  from public.model_prices mp,
  lateral (
      select ord * 2 as ord,
             to_json(t.key)::text || ':' || t.value::text as part
      from json_each(mp.prices) with ordinality as t(key, value, ord)
    union all
      select ord * 2 + 1,
             '"Замена стекла (сепарация)":[0,0]'
      from json_each(mp.prices) with ordinality as t(key, value, ord)
      where t.key = 'Замена экрана (дисплея)'
  ) s
  where not (mp.prices::jsonb ? 'Замена стекла (сепарация)')
    and (mp.prices::jsonb ? 'Замена экрана (дисплея)')
  group by mp.id
) x
where m.id = x.id;

-- 2) Опубликованный снимок (published_prices) — то, что печётся на сайт
update public.model_prices m
set published_prices = x.new_json
from (
  select mp.id,
         ('{' || string_agg(part, ',' order by ord) || '}')::json as new_json
  from public.model_prices mp,
  lateral (
      select ord * 2 as ord,
             to_json(t.key)::text || ':' || t.value::text as part
      from json_each(mp.published_prices) with ordinality as t(key, value, ord)
    union all
      select ord * 2 + 1,
             '"Замена стекла (сепарация)":[0,0]'
      from json_each(mp.published_prices) with ordinality as t(key, value, ord)
      where t.key = 'Замена экрана (дисплея)'
  ) s
  where mp.published_prices is not null
    and not (mp.published_prices::jsonb ? 'Замена стекла (сепарация)')
    and (mp.published_prices::jsonb ? 'Замена экрана (дисплея)')
  group by mp.id
) x
where m.id = x.id;

-- 3) Проверка: у всех ли моделей появилась услуга и на своём ли она месте
select id,
       label,
       (prices::jsonb ? 'Замена стекла (сепарация)')            as есть_в_черновике,
       (published_prices::jsonb ? 'Замена стекла (сепарация)')  as есть_на_сайте,
       (select ord from json_each(prices) with ordinality as t(k, v, ord)
         where k = 'Замена стекла (сепарация)')                 as позиция,
       (prices->'Замена стекла (сепарация)')::text              as цена
from public.model_prices
order by sort;

-- Ожидается: у всех строк оба флага = true, позиция = 2, цена = [0,0].

-- ============================================================================
-- ОТКАТ (если что-то пойдёт не так) — удаляет услугу обратно:
--
-- update public.model_prices
-- set prices = (prices::jsonb - 'Замена стекла (сепарация)')::json,
--     published_prices = case when published_prices is null then null
--       else (published_prices::jsonb - 'Замена стекла (сепарация)')::json end;
--
-- ⚠️ Откат через jsonb ПЕРЕСОРТИРУЕТ ключи по алфавиту. После отката
--    обязательно запустите пересборку сайта (build.sh), чтобы порядок
--    в TIERS восстановился из базы.
-- ============================================================================
