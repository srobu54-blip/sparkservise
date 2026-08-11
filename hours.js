/* hours.js — живой статус работы. График: ЕЖЕДНЕВНО 10:00-19:00, без выходных.
   (До 11.08.2026 воскресенье было выходным; владелец перевёл сервис на семь дней.
   По данным GSC воскресенье было вторым по трафику днём недели — 14,8 клика против
   12,4 в среднем, — и всё это приходило в закрытую мастерскую.)

   Два места на странице:

   1) ТОПБАР (только десктоп, с 680px) — [data-hours]. В HTML запечён честный
      график «Ежедневно 10:00-19:00», скрипт уточняет статус на сейчас.

   2) МОБИЛЬНАЯ ПАНЕЛЬ звонка — [data-hours-bar]. Появляется ТОЛЬКО когда закрыто:
      в рабочие часы панель выглядит как раньше и лишней высоты не занимает.
      Смысл в конверсии: ночью кнопка «Позвонить» — тупик, человек жмёт, никто не
      берёт трубку, человек уходит. Строка честно говорит, что закрыто, и переводит
      на заявку с обещанием перезвонить утром (кнопка «Записаться» там основная).

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

  var OPEN = 10, CLOSE = 19;          // ежедневно, выходных нет
  var UK = (document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('uk') === 0;

  // T — топбар (нейтральная справка), B — панель звонка (ведёт к действию)
  var T = UK ? {
    open:     'Сьогодні працюємо · 10:00-19:00',
    soon:     'Зачинено · відчинимо о 10:00',
    tomorrow: 'Зачинено · відчинимо завтра о 10:00'
  } : {
    open:     'Сегодня работаем · 10:00-19:00',
    soon:     'Закрыто · откроемся в 10:00',
    tomorrow: 'Закрыто · откроемся завтра в 10:00'
  };
  var B = UK ? {
    soon:     'Ще зачинено · передзвонимо о 10:00',
    tomorrow: 'Вже зачинено · передзвонимо завтра о 10:00'
  } : {
    soon:     'Ещё закрыто · перезвоним в 10:00',
    tomorrow: 'Уже закрыто · перезвоним завтра в 10:00'
  };

  // Час по Киеву. hour12:false у части движков отдаёт «24» вместо «00».
  function kyivHour() {
    var p = {};
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Kyiv', hour: '2-digit', minute: '2-digit', hour12: false
    }).formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
    var h = parseInt(p.hour, 10);
    if (isNaN(h)) return null;
    return h === 24 ? 0 : h;
  }

  function paint() {
    var h;
    try { h = kyivHour(); } catch (e) { return; }   // нет Intl/тайзоны — оставляем как есть
    if (h === null) return;

    var k = h < OPEN ? 'soon' : (h < CLOSE ? 'open' : 'tomorrow'),
        isOpen = k === 'open';

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
