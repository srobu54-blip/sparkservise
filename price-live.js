/* price-live.js — мгновенное обновление цен на сайте из CMS (Supabase published_prices).
   Работает на статических прайс-страницах (модели, АКБ) и RU, и UA.

   Как это работает:
   - Прайс-ячейки помечены канонической (RU) метаданной: data-svc="Замена экрана (дисплея)",
     а модель — data-price-model="16pm" (или data-price-label="iPhone 16 Pro Max").
     Метка НЕ переводится → скрипт одинаково находит цену и на RU, и на UA.
   - Скрипт тянет опубликованный снимок цен и переписывает текст ячеек.
   - Мгновенно применяет кэш сессии (без мигания), затем — свежие данные.
   - Любая ошибка/недоступность → на странице остаются запечённые цены. Сломать нельзя.
   Цены на сборке (build.sh) остаются источником для SEO — это лишь клиентский «поверх». */
(function () {
  if (!document.querySelector("[data-svc]")) return;   // не прайс-страница — выходим

  var SB = "https://xvqqoyttvfmrjvufkkzm.supabase.co",
      AK = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2cXFveXR0dmZtcmp2dWZra3ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM0MDQwMDgsImV4cCI6MjA5ODk4MDAwOH0.yaUDu6A4ajFSKx7Xn51BEUgMgkpF47HOhRocCYfjpSU",
      CACHE = "spark_live_prices_v1";

  function money(n) { return Number(n).toLocaleString("ru-RU"); }

  function apply(byId, byLabel) {
    document.querySelectorAll("[data-svc]").forEach(function (cell) {
      var host = cell.hasAttribute("data-price-model") || cell.hasAttribute("data-price-label")
        ? cell : (cell.closest("[data-price-model]") || cell.closest("[data-price-label]"));
      if (!host) return;
      var pm = host.getAttribute("data-price-model"), pl = host.getAttribute("data-price-label");
      var prices = (pm && byId[pm]) || (pl && byLabel[pl]);
      if (!prices) return;
      var p = prices[cell.getAttribute("data-svc")];
      if (!p || !p.length) return;
      var dash = ((cell.getAttribute("data-price-dash") || host.getAttribute("data-price-dash")) === "en") ? " – " : " — ";
      cell.textContent = (!+p[0] && !+p[1]) ? "Уточняйте при заявке"
        : (+p[0] === +p[1]) ? money(p[0]) + " ₴" : money(p[0]) + dash + money(p[1]) + " ₴";
    });
  }

  // 1) мгновенно — из кэша сессии (если уже тянули на прошлой странице)
  try {
    var c = sessionStorage.getItem(CACHE);
    if (c) { var d = JSON.parse(c); apply(d.byId || {}, d.byLabel || {}); }
  } catch (e) {}

  // 2) свежий снимок из Supabase
  try {
    fetch(SB + "/rest/v1/model_prices?select=id,label,prices,published_prices&order=sort.asc",
          { headers: { apikey: AK, Authorization: "Bearer " + AK } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (rows) {
        if (!rows || !rows.length) return;
        var byId = {}, byLabel = {};
        rows.forEach(function (r) { var pr = r.published_prices || r.prices; byId[r.id] = pr; byLabel[r.label] = pr; });
        try { sessionStorage.setItem(CACHE, JSON.stringify({ byId: byId, byLabel: byLabel })); } catch (e) {}
        window.SPARK_LIVE = { byId: byId, byLabel: byLabel };
        apply(byId, byLabel);
        document.dispatchEvent(new CustomEvent("spark:prices", { detail: window.SPARK_LIVE }));
      })["catch"](function () {});
  } catch (e) {}
})();
