/* SPARK — отправка заявки в Supabase (таблица leads) прямым fetch в REST.
   Ноль внешних библиотек. anon-ключ ПУБЛИЧНЫЙ (это норма Supabase) — защита на RLS:
   роль anon может только INSERT, читать базу заявок не может.
   ──────────────────────────────────────────────────────────────────────────
   ЗАПОЛНИ 2 значения в CFG своими (Project Settings -> Data API / API Keys):
     url      — Project URL, вида https://<ref>.supabase.co
     anonKey  — публичный "anon"/"publishable" ключ
   Пока стоят плейсхолдеры (REPLACE_) — модуль СПИТ (ничего не шлёт, ноль ошибок).
   ──────────────────────────────────────────────────────────────────────────
   Ловит клик по активной кнопке .js-submit/#mSubmit (кнопка активна только при
   валидной форме). Дедуп: окно 3 сек на кнопку. Антиспам: honeypot + тайм-трап.
   Событие в dataLayer (для GTM) шлёт отдельный analytics.js — тут только запись в БД. */
(function () {
  "use strict";
  var CFG = {
    url: "REPLACE_WITH_SUPABASE_URL",          // https://<ref>.supabase.co
    anonKey: "REPLACE_WITH_SUPABASE_ANON_KEY"  // публичный anon-ключ
  };
  function ready(v) { return v && v.indexOf("REPLACE_") !== 0; }
  if (!ready(CFG.url) || !ready(CFG.anonKey)) return; // спит до заполнения

  var loadedAt = Date.now();

  // honeypot: скрытое поле в каждую форму; бот заполнит -> дропаем
  function addHoneypot() {
    var forms = document.querySelectorAll("#spkExitModal, #bookFormInline, .modal-card");
    for (var i = 0; i < forms.length; i++) {
      if (forms[i].querySelector(".spk-hp")) continue;
      var inp = document.createElement("input");
      inp.type = "text"; inp.className = "spk-hp"; inp.tabIndex = -1;
      inp.setAttribute("autocomplete", "off"); inp.setAttribute("aria-hidden", "true");
      inp.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none";
      forms[i].appendChild(inp);
    }
  }
  if (document.readyState !== "loading") addHoneypot();
  else document.addEventListener("DOMContentLoaded", addHoneypot);

  function val(box, sel) { var el = box.querySelector(sel); return el ? (el.value || "").trim() : ""; }

  function utm() {
    try {
      var q = new URLSearchParams(location.search), o = {}, k,
          keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
      for (var i = 0; i < keys.length; i++) { k = q.get(keys[i]); if (k) o[keys[i].slice(4)] = k.slice(0, 120); }
      return Object.keys(o).length ? o : null;
    } catch (e) { return null; }
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    var btn = t && t.closest ? t.closest(".js-submit, #mSubmit") : null;
    if (!btn || btn.disabled) return;
    var now = Date.now();
    if (now - (parseInt(btn.getAttribute("data-spk-lead") || "0", 10)) < 3000) return; // дедуп
    btn.setAttribute("data-spk-lead", String(now));

    var box = btn.closest("#spkExitModal, #bookFormInline, .modal-card, form") || document;

    // антиспам: honeypot заполнен ИЛИ отправка <1.5с после загрузки -> тихо выходим
    var hp = box.querySelector(".spk-hp");
    if ((hp && hp.value) || (now - loadedAt) < 1500) return;

    var phone = val(box, ".js-phone") || val(box, "#mPhone");
    if (!phone) return;

    var source = box.id === "spkExitModal" ? "exit_popup"
      : (btn.id === "mSubmit" ? "modal_callback"
      : (box.id === "bookFormInline" ? "inline_form" : "unknown"));

    var row = {
      name: (val(box, ".js-name") || val(box, "#mName")) || null,
      phone: phone.slice(0, 32),
      service: (val(box, ".js-device") || val(box, "#mDevice")) || null,
      source: source,
      page_url: location.pathname.slice(0, 500),
      lang: (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru",
      utm: utm(),
      referrer: (document.referrer || "").slice(0, 500) || null
    };

    // fire-and-forget: UI-успех рисует main.js/exit-popup.js; сеть не блокирует
    try {
      fetch(CFG.url.replace(/\/$/, "") + "/rest/v1/leads", {
        method: "POST",
        headers: {
          "apikey": CFG.anonKey,
          "Authorization": "Bearer " + CFG.anonKey,
          "Content-Type": "application/json",
          "Prefer": "return=minimal"   // anon не имеет SELECT -> не просим строку назад
        },
        body: JSON.stringify(row),
        keepalive: true                // долетит, даже если страница закрывается
      })["catch"](function () {});
    } catch (e) {}
  }, true);
})();
