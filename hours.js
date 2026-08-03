/* hours.js — живой статус работы. График: Пн-Сб 10:00-19:00, воскресенье — выходной.
   Два места на странице:

   1) ТОПБАР (только десктоп, с 680px) — [data-hours]. Раньше там было статичное
      «Сегодня работаем · 10:00-19:00», то есть в воскресенье и по ночам сайт врал.
      Теперь в HTML запечён честный график, а скрипт уточняет статус на сегодня.

   2) МОБИЛЬНАЯ ПАНЕЛЬ звонка — [data-hours-bar]. Появляется ТОЛЬКО когда закрыто:
      в рабочие часы панель выглядит ровно как раньше и лишней высоты не занимает.
      Смысл не в информировании, а в конверсии: ночью кнопка «Позвонить» — тупик,
      человек жмёт, никто не берёт трубку, человек уходит. Строка честно говорит,
      что сейчас закрыто, и переводит на заявку с обещанием перезвонить утром
      (кнопка «Записаться» там и так основная, красная).

   Время берём в Europe/Kyiv через Intl, а НЕ через локальный new Date(): посетитель
   в другом поясе или с криво выставленными часами иначе увидит «уже закрыто» у
   работающей мастерской и не позвонит.

   Любая ошибка/старый браузер → в топбаре остаётся запечённый график, на мобильной
   панели не появляется ничего. Сломать нельзя. */
(function () {
  var top = document.querySelector('[data-hours]'),
      bar = document.querySelector('[data-hours-bar]');
  if (!top && !bar) return;

  var topText = top && top.querySelector('.tb-hours'),
      topDot  = top && top.querySelector('.dot'),
      barText = bar && bar.querySelector('.cb-text');

  var OPEN = 10, CLOSE = 19;          // Пн-Сб; воскресенье закрыто целиком
  var UK = (document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('uk') === 0;

  // T — топбар (нейтральная справка), B — панель звонка (ведёт к действию)
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
  var B = UK ? {
    dayoff:   'Сьогодні вихідний · передзвонимо в понеділок',
    soon:     'Ще зачинено · передзвонимо о 10:00',
    tomorrow: 'Вже зачинено · передзвонимо завтра о 10:00',
    monday:   'Вже зачинено · передзвонимо в понеділок'
  } : {
    dayoff:   'Сегодня выходной · перезвоним в понедельник',
    soon:     'Ещё закрыто · перезвоним в 10:00',
    tomorrow: 'Уже закрыто · перезвоним завтра в 10:00',
    monday:   'Уже закрыто · перезвоним в понедельник'
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

  function state(n) {
    if (n.wd === 0) return 'dayoff';                  // воскресенье
    if (n.h < OPEN) return 'soon';                    // утро буднего дня
    if (n.h < CLOSE) return 'open';                   // рабочие часы
    return n.wd === 6 ? 'monday' : 'tomorrow';        // после 19:00; сб → понедельник
  }

  function paint() {
    var n;
    try { n = kyiv(); } catch (e) { return; }   // нет Intl/тайзоны — оставляем как есть
    if (!n) return;
    var k = state(n), isOpen = k === 'open';

    if (topText) {
      topText.textContent = T[k];
      if (topDot) {                             // зелёная точка только когда реально открыто
        topDot.style.background = isOpen ? '' : '#9aa0ad';
        topDot.style.boxShadow = isOpen ? '' : '0 0 0 3px rgba(154,160,173,.20)';
      }
    }
    if (bar) {                                  // в рабочие часы панель не трогаем вовсе
      if (isOpen) bar.classList.remove('on');
      else { if (barText) barText.textContent = B[k]; bar.classList.add('on'); }
    }
  }

  paint();
  setInterval(paint, 60000);   // вкладка может «пережить» 10:00 или 19:00
})();
