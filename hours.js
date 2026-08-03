/* hours.js — живой статус работы в топбаре: «сегодня работаем» / «сегодня выходной» /
   «откроемся в 10:00». График заведения: Пн-Сб 10:00-19:00, воскресенье — выходной.

   Почему не просто new Date(): время берём в Europe/Kyiv, а НЕ в поясе посетителя.
   Иначе человек из другого часового пояса (или просто с криво выставленными часами)
   увидит «уже закрыто», когда мастерская открыта, — и не позвонит.

   Разметка в HTML остаётся правдивой и БЕЗ JS: там запечён график
   «Пн-Сб 10:00-19:00 · Вс — выходной», а скрипт лишь уточняет статус на сегодня.
   Раньше в топбаре стояло статичное «Сегодня работаем · 10:00-19:00» — в воскресенье
   и по ночам сайт врал. Любая ошибка/старый браузер → остаётся запечённый график,
   сломать нельзя. */
(function () {
  var host = document.querySelector('[data-hours]');
  if (!host) return;
  var out = host.querySelector('.tb-hours'), dot = host.querySelector('.dot');
  if (!out) return;

  var OPEN = 10, CLOSE = 19;          // Пн-Сб; воскресенье закрыто целиком
  var UK = (document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('uk') === 0;
  var T = UK ? {
    open:     'Сьогодні працюємо · 10:00-19:00',
    dayoff:   'Сьогодні вихідний · Пн-Сб 10:00-19:00',
    soon:     'Зачинено · відчинимо о 10:00',
    tomorrow: 'Зачинено · відчинимо завтра о 10:00',
    monday:   'Зачинено · відчинимо в понеділок о 10:00'
  } : {
    open:     'Сегодня работаем · 10:00-19:00',
    dayoff:   'Сегодня выходной · Пн-Сб 10:00-19:00',
    soon:     'Закрыто · откроемся в 10:00',
    tomorrow: 'Закрыто · откроемся завтра в 10:00',
    monday:   'Закрыто · откроемся в понедельник в 10:00'
  };

  // День недели и час по Киеву. hour12:false у части движков отдаёт «24» вместо «00».
  function kyiv() {
    var p = {};
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Kyiv', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false
    }).formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
    var wd = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(p.weekday);
    var h = parseInt(p.hour, 10);
    if (wd < 0 || isNaN(h)) return null;
    return { wd: wd, h: h === 24 ? 0 : h };
  }

  function paint() {
    var n;
    try { n = kyiv(); } catch (e) { return; }   // нет Intl/тайзоны — оставляем график
    if (!n) return;

    var txt, isOpen = false;
    if (n.wd === 0) txt = T.dayoff;                          // воскресенье
    else if (n.h < OPEN) txt = T.soon;                       // утро буднего дня
    else if (n.h < CLOSE) { txt = T.open; isOpen = true; }   // рабочие часы
    else txt = (n.wd === 6) ? T.monday : T.tomorrow;         // после 19:00; сб → понедельник

    out.textContent = txt;
    if (dot) {                                  // зелёная точка только когда реально открыто
      dot.style.background = isOpen ? '' : '#9aa0ad';
      dot.style.boxShadow = isOpen ? '' : '0 0 0 3px rgba(154,160,173,.20)';
    }
  }

  paint();
  setInterval(paint, 60000);   // вкладка может «пережить» 10:00 или 19:00
})();
