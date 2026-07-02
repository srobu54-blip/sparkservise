/* SPARK exit-intent popup — self-contained, RU+UA, desktop + mobile.
   Показ: ≥30с на странице И ≥50% прокрутки И сработал exit-intent.
   Лимиты: 1 раз за сессию · после закрытия молчит 7 дней · после заявки — никогда.
   Превью без лимитов: добавь ?popup=1 к URL.
   Форма совместима с analytics.js (.js-submit / .js-phone) — лид засчитается при заполненных рекламных ID. */
(function () {
  "use strict";
  if (window.__sparkExit) return;
  window.__sparkExit = 1;

  var lang = (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru";
  var T = {
    ru: {
      badge: "Бесплатная консультация",
      title: "Не нашли что искали?",
      desc: "Оставьте номер телефона — наш специалист свяжется с вами и бесплатно ответит на вопросы.",
      button: "Жду звонка",
      note: "Перезвоним в течение 15 минут. Данные не передаём третьим лицам.",
      hint: "Введите номер мобильного оператора Украины",
      hintFull: "Введите номер полностью",
      hintErr: "Проверьте код оператора",
      hintOk: "номер распознан",
      okTitle: "Заявка принята!",
      okText: "Перезвоним в течение 15 минут в рабочее время.",
      done: "Готово",
      close: "Закрыть",
      device: "Обратный звонок (exit popup)"
    },
    uk: {
      badge: "Безкоштовна консультація",
      title: "Не знайшли те, що шукали?",
      desc: "Залиште номер телефону — наш спеціаліст зв'яжеться з вами й безкоштовно відповість на запитання.",
      button: "Чекаю на дзвінок",
      note: "Передзвонимо протягом 15 хвилин. Дані не передаємо третім особам.",
      hint: "Введіть номер мобільного оператора України",
      hintFull: "Введіть номер повністю",
      hintErr: "Перевірте код оператора",
      hintOk: "номер розпізнано",
      okTitle: "Заявку прийнято!",
      okText: "Передзвонимо протягом 15 хвилин у робочий час.",
      done: "Готово",
      close: "Закрити",
      device: "Зворотний дзвінок (exit popup)"
    }
  }[lang];

  var MIN_MS = 30000, MIN_SCROLL = 0.5, CLOSE_DAYS = 7;
  var K_SEEN = "spark_exit_seen", K_CLOSED = "spark_exit_closed", K_LEAD = "spark_exit_lead";
  var preview = /[?&]popup=1/.test(location.search);
  var start = Date.now(), maxScroll = 0, shown = false, armed = false, root = null;

  function lg(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function ls(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function sg(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ss(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }

  function suppressed() {
    if (preview) return false;
    if (lg(K_LEAD)) return true;
    if (sg(K_SEEN)) return true;
    var c = parseInt(lg(K_CLOSED) || "0", 10);
    return c && (Date.now() - c) < CLOSE_DAYS * 864e5;
  }
  function engaged() {
    return preview || ((Date.now() - start) >= MIN_MS && maxScroll >= MIN_SCROLL);
  }

  // --- глубина прокрутки ---
  addEventListener("scroll", function () {
    var sh = document.documentElement.scrollHeight;
    if (sh > 0) { var p = (scrollY + innerHeight) / sh; if (p > maxScroll) maxScroll = p; }
  }, { passive: true });

  // --- телефон (как в основной форме) ---
  var OPS = [{ n: "Kyivstar", c: ["67", "68", "96", "97", "98", "77"] }, { n: "Vodafone", c: ["50", "66", "95", "99"] }, { n: "lifecell", c: ["63", "73", "93"] }, { n: lang === "uk" ? "оператор" : "оператор", c: ["91", "92", "94"] }];
  function detect(code) { for (var i = 0; i < OPS.length; i++) if (OPS[i].c.indexOf(code) > -1) return OPS[i].n; return null; }
  function rawDigits(v) { var d = v.replace(/\D/g, ""); if (d.indexOf("38") === 0) d = d.slice(2); if (d.length && d[0] !== "0") d = "0" + d; return d.slice(0, 10); }
  function fmt(d) { var o = ""; if (d.length > 0) o = "(" + d.slice(0, 3); if (d.length >= 3) o += ") "; if (d.length > 3) o += d.slice(3, 6); if (d.length > 6) o += "-" + d.slice(6, 8); if (d.length > 8) o += "-" + d.slice(8, 10); return o; }

  var CSS =
    ".spk-exit-ov{position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(10,12,18,.62);opacity:0;visibility:hidden;transition:opacity .28s ease;-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}" +
    ".spk-exit-ov.in{opacity:1;visibility:visible}" +
    ".spk-exit-card{position:relative;width:100%;max-width:412px;background:#fff;border-radius:20px;padding:30px 26px 22px;box-shadow:0 30px 80px -30px rgba(10,12,18,.6);transform:translateY(14px) scale(.97);transition:transform .3s cubic-bezier(.22,.61,.36,1);font-family:inherit}" +
    ".spk-exit-ov.in .spk-exit-card{transform:none}" +
    ".spk-exit-x{position:absolute;top:12px;right:12px;width:34px;height:34px;border:0;background:#f2f3f5;border-radius:50%;font-size:20px;line-height:1;color:#6b7280;cursor:pointer;transition:background .15s,color .15s}" +
    ".spk-exit-x:hover{background:#e7e9ee;color:#10121a}" +
    ".spk-exit-badge{display:inline-block;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--spark,#E11D2A);background:var(--spark-soft,rgba(225,29,42,.09));padding:5px 12px;border-radius:999px;margin-bottom:12px}" +
    ".spk-exit-card h3{font-size:1.42rem;font-weight:750;line-height:1.2;color:var(--ink,#10121a);margin:0 0 8px}" +
    ".spk-exit-desc{font-size:1rem;line-height:1.5;color:var(--muted,#5f6676);margin:0 0 18px}" +
    ".spk-exit-field{display:flex;align-items:center;border:1.5px solid var(--line,#e2e5ea);border-radius:12px;overflow:hidden;transition:border-color .15s}" +
    ".spk-exit-field.valid{border-color:#1FAE5A}.spk-exit-field.invalid{border-color:var(--spark,#E11D2A)}" +
    ".spk-exit-pre{padding:0 10px 0 14px;font-size:1.05rem;font-weight:600;color:var(--ink,#10121a)}" +
    ".spk-exit-field input{flex:1;border:0;outline:0;padding:14px 12px 14px 0;font-size:1.05rem;font-family:inherit;color:var(--ink,#10121a);background:transparent;min-width:0}" +
    ".spk-exit-hint{font-size:.82rem;color:var(--muted,#5f6676);margin:8px 2px 0;min-height:1em}" +
    ".spk-exit-hint.ok{color:#1FAE5A}.spk-exit-hint.err{color:var(--spark,#E11D2A)}" +
    ".spk-exit-btn{width:100%;margin-top:16px;padding:15px;border:0;border-radius:12px;font-size:1.05rem;font-weight:700;font-family:inherit;color:#fff;background:linear-gradient(135deg,#E8222C,#C5141E);cursor:pointer;transition:transform .12s,opacity .15s;box-shadow:0 10px 24px -12px rgba(225,29,42,.6)}" +
    ".spk-exit-btn:hover{transform:translateY(-1px)}.spk-exit-btn:active{transform:scale(.99)}" +
    ".spk-exit-btn:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}" +
    ".spk-exit-note{font-size:.78rem;color:#9aa0ad;text-align:center;margin-top:12px;line-height:1.4}" +
    ".spk-exit-ok{display:none;text-align:center;padding:8px 0}" +
    ".spk-exit-card.done .spk-exit-form{display:none}.spk-exit-card.done .spk-exit-ok{display:block}" +
    ".spk-exit-ok-ic{width:64px;height:64px;margin:6px auto 14px;border-radius:50%;background:rgba(31,174,90,.12);color:#1FAE5A;font-size:32px;line-height:64px;font-weight:700}" +
    ".spk-exit-lock{overflow:hidden}" +
    "@media(max-width:520px){.spk-exit-ov{align-items:flex-end;padding:0}.spk-exit-card{max-width:none;border-radius:20px 20px 0 0;padding:26px 20px 20px;transform:translateY(100%)}}" +
    "@media(prefers-reduced-motion:reduce){.spk-exit-ov,.spk-exit-card{transition:none}.spk-exit-card{transform:none}}";

  function build() {
    var st = document.createElement("style"); st.id = "spk-exit-css"; st.textContent = CSS;
    document.head.appendChild(st);
    root = document.createElement("div");
    root.className = "spk-exit-ov";
    root.innerHTML =
      '<div class="spk-exit-card" role="dialog" aria-modal="true" aria-labelledby="spkExitTitle">' +
        '<button class="spk-exit-x" type="button" aria-label="' + T.close + '">&times;</button>' +
        '<div class="spk-exit-form">' +
          '<span class="spk-exit-badge">' + T.badge + '</span>' +
          '<h3 id="spkExitTitle">' + T.title + '</h3>' +
          '<p class="spk-exit-desc">' + T.desc + '</p>' +
          '<div class="spk-exit-field"><span class="spk-exit-pre">+38</span>' +
            '<input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__" aria-label="' + T.hint + '"></div>' +
          '<div class="spk-exit-hint">' + T.hint + '</div>' +
          '<input class="js-device" type="hidden" value="' + T.device + '">' +
          '<button class="spk-exit-btn js-submit" type="button" disabled>' + T.button + '</button>' +
          '<div class="spk-exit-note">' + T.note + '</div>' +
        '</div>' +
        '<div class="spk-exit-ok">' +
          '<div class="spk-exit-ok-ic">&#10003;</div>' +
          '<h3>' + T.okTitle + '</h3><p class="spk-exit-desc" style="margin-bottom:6px">' + T.okText + '</p>' +
          '<button class="spk-exit-btn spk-exit-done" type="button">' + T.done + '</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(root);

    var card = root.querySelector(".spk-exit-card");
    var phone = root.querySelector(".js-phone");
    var field = root.querySelector(".spk-exit-field");
    var hint = root.querySelector(".spk-exit-hint");
    var submit = root.querySelector(".js-submit");
    var valid = false;

    function check() {
      var d = rawDigits(phone.value); phone.value = fmt(d); valid = false;
      field.classList.remove("valid", "invalid"); hint.className = "spk-exit-hint";
      if (d.length === 0) { hint.textContent = T.hint; }
      else if (d.length < 10) { hint.textContent = T.hintFull; }
      else { var op = detect(d.slice(1, 3)); if (op) { valid = true; hint.textContent = "✓ " + op + " — " + T.hintOk; hint.className = "spk-exit-hint ok"; field.classList.add("valid"); } else { hint.textContent = T.hintErr; hint.className = "spk-exit-hint err"; field.classList.add("invalid"); } }
      submit.disabled = !valid;
    }
    phone.addEventListener("input", check);

    submit.addEventListener("click", function () {
      if (submit.disabled) return;
      ls(K_LEAD, "1");                 // больше не показывать
      card.classList.add("done");      // analytics.js поймает этот же клик по .js-submit
    });
    root.querySelector(".spk-exit-x").addEventListener("click", close);
    root.querySelector(".spk-exit-done").addEventListener("click", close);
    root.addEventListener("click", function (e) { if (e.target === root) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && root.classList.contains("in")) close(); });
    setTimeout(function () { try { phone.focus(); } catch (e) {} }, 340);
  }

  function show() {
    if (shown || suppressed()) return;
    shown = true; ss(K_SEEN, "1");
    build();
    document.documentElement.classList.add("spk-exit-lock");
    requestAnimationFrame(function () { root.classList.add("in"); });
  }
  function close() {
    if (!root) return;
    if (!lg(K_LEAD)) ls(K_CLOSED, String(Date.now()));   // 7 дней тишины (если не отправил)
    root.classList.remove("in");
    document.documentElement.classList.remove("spk-exit-lock");
  }

  // --- триггеры ---
  if (preview) { setTimeout(show, 600); return; }

  // Desktop: курсор ушёл за верхнюю границу окна
  document.addEventListener("mouseout", function (e) {
    if (e.clientY <= 0 && !e.relatedTarget && !e.toElement && engaged()) show();
  });

  // Mobile: ловушка кнопки «назад» + быстрый скролл вверх у топа
  var touch = matchMedia("(hover:none)").matches || "ontouchstart" in window;
  if (touch) {
    function arm() {
      if (armed || shown || suppressed() || !engaged()) return;
      armed = true;
      try { history.pushState({ spkExit: 1 }, "", location.href); } catch (e) {}
    }
    addEventListener("scroll", arm, { passive: true });
    setTimeout(arm, MIN_MS + 200);
    addEventListener("popstate", function () {
      if (armed && !shown && !suppressed()) { try { history.pushState({ spkExit: 1 }, "", location.href); } catch (e) {} show(); }
    });
    var lastY = scrollY, lastT = Date.now();
    addEventListener("scroll", function () {
      var y = scrollY, t = Date.now(), dt = t - lastT;
      if (dt > 0 && (lastY - y) / dt > 1.1 && y < 320 && engaged()) show();
      lastY = y; lastT = t;
    }, { passive: true });
  }
})();
