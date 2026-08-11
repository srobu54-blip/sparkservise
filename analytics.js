/* SPARK — аналитика/счётчики с само-настройкой из БД (без пересбора сайта).
   ──────────────────────────────────────────────────────────────────────────
   ID счётчиков хранятся в Supabase (таблица site_settings) и правятся в админке
   (/admin/ → Настройки). Этот скрипт читает их в рантайме и сам подключает:
     ga4_id            — Google Analytics 4 (G-XXXXXXX): gtag + page_view
     meta_pixel_id     — Meta Pixel: fbq init + PageView, событие Lead на заявке
     google_ads_id     — Google Ads (AW-XXXXXXXXX) + google_ads_label: конверсия на заявке
                         с Enhanced Conversions (телефон/имя)
     gsc_verification  — meta google-site-verification (лучше DNS; тут best-effort)
   Пустые поля -> ничего не грузится. ?popup=1 / ?test=1 -> конверсии НЕ шлём (тест).
   Плюс на каждую заявку кладём событие generate_lead в dataLayer (на случай GTM).
   ────────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";
  var SB = {
    url: "https://xvqqoyttvfmrjvufkkzm.supabase.co",
    anon: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2cXFveXR0dmZtcmp2dWZra3ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM0MDQwMDgsImV4cCI6MjA5ODk4MDAwOH0.yaUDu6A4ajFSKx7Xn51BEUgMgkpF47HOhRocCYfjpSU"
  };
  window.dataLayer = window.dataLayer || [];
  var TEST = /[?&](popup|test)=1/.test(location.search);
  var lang = (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru";
  var seq = 0, T = {};   // T — активные ID после загрузки настроек
  function uid() { return "spk-" + Date.now().toString(36) + "-" + (++seq) + "-" + Math.floor(Math.random() * 1e9).toString(36); }
  function natPhone(v) { var d = (v || "").replace(/\D/g, ""); if (d.indexOf("380") === 0) d = d.slice(3); else if (d.indexOf("38") === 0) d = d.slice(2); if (d.indexOf("0") === 0) d = d.slice(1); return d.length === 9 ? d : ""; }
  function ok(v) { return v && String(v).trim() && String(v).indexOf("REPLACE_") !== 0; }

  // ── подгрузка настроек (кэш на сессию, чтобы не дёргать БД на каждой странице) ──
  function withSettings(cb) {
    try { var c = sessionStorage.getItem("spk_cfg"); if (c) { cb(JSON.parse(c)); return; } } catch (e) {}
    try {
      fetch(SB.url + "/rest/v1/site_settings?id=eq.1&select=gtm_id,ga4_id,meta_pixel_id,tiktok_pixel_id,google_ads_id,google_ads_label,gsc_verification",
        { headers: { apikey: SB.anon, Authorization: "Bearer " + SB.anon } })
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (a) { var cfg = (a && a[0]) || {}; try { sessionStorage.setItem("spk_cfg", JSON.stringify(cfg)); } catch (e) {} cb(cfg); })
        ["catch"](function () { cb({}); });
    } catch (e) { cb({}); }
  }

  function loadGtag(firstId) {
    if (window.gtag) return;
    var s = document.createElement("script"); s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + firstId; document.head.appendChild(s);
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date());
  }
  function initPixel(id) {
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    fbq("init", id); fbq("track", "PageView");
  }
  function initGTM(id) {
    (function (w, d, s, l, i) { w[l] = w[l] || []; w[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" }); var f = d.getElementsByTagName(s)[0], j = d.createElement(s), dl = l != "dataLayer" ? "&l=" + l : ""; j.async = true; j.src = "https://www.googletagmanager.com/gtm.js?id=" + i + dl; f.parentNode.insertBefore(j, f); })(window, document, "script", "dataLayer", id);
  }
  function initTikTok(id) {
    !function (w, d, t) { w.TiktokAnalyticsObject = t; var ttq = w[t] = w[t] || []; ttq.methods = ["page", "track", "identify", "instances", "debug", "on", "off", "once", "ready", "alias", "group", "enableCookie", "disableCookie", "holdConsent", "revokeConsent", "grantConsent"]; ttq.setAndDefer = function (t, e) { t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))); }; }; for (var i = 0; i < ttq.methods.length; i++)ttq.setAndDefer(ttq, ttq.methods[i]); ttq.instance = function (t) { for (var e = ttq._i[t] || [], n = 0; n < ttq.methods.length; n++)ttq.setAndDefer(e, ttq.methods[n]); return e; }; ttq.load = function (e, n) { var r = "https://analytics.tiktok.com/i18n/pixel/events.js", o = n && n.partner; ttq._i = ttq._i || {}; ttq._i[e] = [], ttq._i[e]._u = r; ttq._t = ttq._t || {}; ttq._t[e] = +new Date; ttq._o = ttq._o || {}; ttq._o[e] = n || {}; n = document.createElement("script"); n.type = "text/javascript", n.async = !0, n.src = r + "?sdkid=" + e + "&lib=" + t; e = document.getElementsByTagName("script")[0]; e.parentNode.insertBefore(n, e); }; ttq.load(id); ttq.page(); }(window, document, "ttq");
  }

  withSettings(function (cfg) {
    T.gtm = ok(cfg.gtm_id) ? cfg.gtm_id.trim() : "";
    T.ga4 = ok(cfg.ga4_id) ? cfg.ga4_id.trim() : "";
    T.ads = ok(cfg.google_ads_id) ? cfg.google_ads_id.trim() : "";
    T.label = ok(cfg.google_ads_label) ? cfg.google_ads_label.trim() : "";
    T.px = ok(cfg.meta_pixel_id) ? cfg.meta_pixel_id.trim() : "";
    T.tt = ok(cfg.tiktok_pixel_id) ? cfg.tiktok_pixel_id.trim() : "";
    if (T.gtm) initGTM(T.gtm);                 // контейнер сам подтянет generate_lead из dataLayer
    if (T.ga4 || T.ads) {
      loadGtag(T.ga4 || T.ads);
      if (T.ga4) gtag("config", T.ga4, { allow_enhanced_conversions: true });
      if (T.ads) gtag("config", T.ads, { allow_enhanced_conversions: true });
    }
    if (T.px) initPixel(T.px);
    if (T.tt) initTikTok(T.tt);
    if (ok(cfg.gsc_verification) && !document.querySelector('meta[name="google-site-verification"]')) {
      var m = document.createElement("meta"); m.name = "google-site-verification"; m.content = cfg.gsc_verification.trim(); document.head.appendChild(m);
    }
  });

  // ── generate_lead: успешная отправка формы (один слушатель на все 3 формы) ──
  document.addEventListener("click", function (e) {
    var t = e.target;
    var btn = t && t.closest ? t.closest(".js-submit, #mSubmit") : null;
    if (!btn || btn.disabled) return;
    var now = Date.now();
    if (now - (parseInt(btn.getAttribute("data-spk-t") || "0", 10)) < 3000) return;   // дедуп 3с
    btn.setAttribute("data-spk-t", String(now));

    var box = btn.closest("#spkExitModal, #bookFormInline, .modal-card, form") || document;
    function val(sel) { var el = box.querySelector(sel); return el ? (el.value || "").trim() : ""; }
    var form_id = btn.closest("#spkExitModal") ? "exit_popup" : btn.id === "mSubmit" ? "modal_callback" : btn.closest("#bookFormInline") ? "inline_form" : "form";
    var name = val(".js-name") || val("#mName");
    var service = val(".js-device") || val("#mDevice");
    var nat = natPhone(val(".js-phone") || val("#mPhone"));
    var e164 = nat ? "+380" + nat : "";
    var eid = uid();

    // 1) dataLayer (для GTM, если когда-нибудь подключат контейнер)
    var ev = { event: "generate_lead", event_id: eid, form_id: form_id, language: lang, test_mode: TEST, user_data: {} };
    if (e164) ev.user_data.phone_number = e164;
    if (name) ev.user_data.address = { first_name: name };
    if (service) ev.service = service;
    window.dataLayer.push(ev);

    if (TEST) return;   // в тест-режиме реальные конверсии не шлём

    // 2) GA4 — событие заявки
    if (T.ga4 && window.gtag) gtag("event", "generate_lead", { form_id: form_id, service: service || "", language: lang });

    // 3) Google Ads — конверсия с расширенными данными (телефон/имя)
    if (T.ads && T.label && window.gtag) {
      var ud = {}; if (e164) ud.phone_number = e164; if (name) ud.address = { first_name: name };
      if (Object.keys(ud).length) gtag("set", "user_data", ud);
      gtag("event", "conversion", { send_to: T.ads + "/" + T.label, value: 0, currency: "UAH" });
    }

    // 4) Meta Pixel — Lead с advanced matching (дедуп по event_id)
    if (T.px && window.fbq) {
      var am = {}; if (nat) am.ph = "380" + nat; if (name) am.fn = name.toLowerCase();
      if (am.ph || am.fn) { try { fbq("init", T.px, am); } catch (_) {} }
      fbq("track", "Lead", { content_name: service || "", value: 0, currency: "UAH" }, { eventID: eid });
    }

    // 5) TikTok — событие заявки
    if (T.tt && window.ttq) { try { ttq.track("SubmitForm", { content_type: "lead", content_name: service || "" }); } catch (_) {} }
  }, true);

  /* ── ВОРОНКА ФОРМЫ: form_view → form_start → form_ready → generate_lead ──
     Зачем. До сих пор было видно только «пришёл» и «обратился»: за 30 дней
     611 пользователей и 63 ключевых события, а на каком шаге теряются
     остальные — вслепую. Эти три события закрывают разрыв:
       form_view   — доскроллили до формы
       form_start  — коснулись первого поля
       form_ready  — заполнили так, что кнопка отправки разблокировалась
     Провал между form_ready и generate_lead — самый обидный и сегодня
     невидимый: человек всё ввёл и передумал на кнопке.

     Как. Логику валидации не дублируем — она живёт в wireForm() (main.js и
     exit-popup.js). Мы только СМОТРИМ на её результат: состояние кнопки
     проверяется после каждого ввода. Поэтому работает и для exit-попапа,
     который вставляется в DOM позже (см. exit-popup.js — modal.id задаётся
     в рантайме), и MutationObserver не нужен.

     Персональных данных в этих событиях НЕТ — телефон и имя уходят только
     в generate_lead, как и раньше. */
  function formIdOf(el) {
    if (!el || !el.closest) return "";
    if (el.closest("#spkExitModal")) return "exit_popup";
    if (el.closest("#bookFormInline")) return "inline_form";
    if (el.closest(".modal-card")) return "modal_callback";
    return "";
  }
  function step(name, form_id) {
    window.dataLayer.push({ event: name, form_id: form_id, language: lang, test_mode: TEST });
  }

  // form_view — только для встроенной формы: модалка и exit-попап открываются
  // по действию, там «показ» гарантирован, а попап и так шлёт exit_popup_show.
  try {
    var inlineForm = document.getElementById("bookFormInline");
    if (inlineForm && window.IntersectionObserver) {
      // Одна доля тут не годится: форма ~790px, и на невысоком экране доля
      // 0.4 недостижима физически — событие не выстрелит никогда. Меряем
      // видимую ВЫСОТУ в пикселях: 150px — это заголовок с первым полем,
      // то есть форму человек действительно увидел (для низких форм берём
      // 60% высоты, иначе порог был бы недостижим и для них).
      // ⚠ Порогов нужно НЕСКОЛЬКО. С одним threshold:0 колбэк вызывается
      // только в момент пересечения границы — когда видно пару пикселей;
      // проверка высоты не пройдёт, а пока форма остаётся в кадре, повторных
      // вызовов не будет, и событие потеряется навсегда.
      var io = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          var en = entries[i], h = en.boundingClientRect.height;
          if (en.isIntersecting && en.intersectionRect.height >= Math.min(150, h * 0.6)) {
            step("form_view", "inline_form"); io.disconnect(); return;
          }
        }
      }, { threshold: [0, 0.1, 0.2, 0.35, 0.5, 0.75, 1] });
      io.observe(inlineForm);
    }
  } catch (_) {}

  document.addEventListener("input", function (e) {
    var f = e.target;
    if (!f || !f.closest) return;
    if (!f.closest(".js-name, .js-phone, .js-device, #mName, #mPhone, #mDevice")) return;
    var box = f.closest("#spkExitModal, #bookFormInline, .modal-card");
    if (!box) return;                       // без контейнера метки ставить некуда
    var id = formIdOf(f);
    if (!id) return;

    if (!box.hasAttribute("data-spk-start")) {
      box.setAttribute("data-spk-start", "1");
      step("form_start", id);
    }
    // состояние кнопки wireForm() обновляет в своём обработчике ввода —
    // читаем после него, поэтому откладываем на следующий тик
    setTimeout(function () {
      if (box.hasAttribute("data-spk-ready")) return;
      var btn = box.querySelector(".js-submit, #mSubmit");
      if (btn && !btn.disabled) {
        box.setAttribute("data-spk-ready", "1");
        step("form_ready", id);
      }
    }, 0);
  }, true);
})();
