#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «Замена и ремонт тачпада MacBook» — спойк хаба:
/remont-macbook/zamena-tachpada/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ЭТА СТРАНИЦА. Замер Ahrefs (country=ua, 28.07.2026): «замена тачпада
macbook air» 80, «замена тачпада macbook pro» 80, «ремонт тачпада macbook pro»
80 — суммарно ~240 запросов в месяц, и ни одной страницы под них у нас нет.

ДВА ВАЖНЫХ НАБЛЮДЕНИЯ ИЗ ДАННЫХ, ОПРЕДЕЛИВШИХ СТРАНИЦУ.
1) Спрос строго МОДЕЛЬНЫЙ: варианты с «air» и «pro» дают по 80, а общий
   «замена тачпада macbook» без модели — ноль. Поэтому Air и Pro названы
   отдельно в title, H1, подзаголовках и FAQ.
2) Страница СОВМЕЩЁННАЯ, «замена + ремонт»: «замена» даёт 160, «ремонт» 80,
   интент один и тот же. Плодить две страницы на слабом домене нельзя — тот же
   приём, что с combined-страницей экрана iPhone.

ПРО ЦЕНУ. В прайсе хаба MacBook строки «тачпад» нет вообще, поматричных цен у
MacBook тоже нет. Цифры не выдумываем: страница честно отправляет за ценой на
бесплатную диагностику. Когда владелец добавит услугу в прайс — сюда придёт
цена тем же способом, что и на странице аккумулятора (hub_price()).

ГЛАВНАЯ СМЫСЛОВАЯ СВЯЗКА: неработающий тачпад на MacBook чаще всего вызывает
ВЗДУТАЯ БАТАРЕЯ, которая давит на него снизу. Поэтому страница честно ведёт
часть трафика на лендинг аккумулятора — и наоборот. Это не перелинковка ради
перелинковки, а реальный диагностический факт.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/zamena-tachpada"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_price():
    """Цена тачпада из прайса хаба: (строка цены, срок, нижняя граница числом).

    Нижняя граница нужна отдельно — она идёт в title, description и в Offer.
    Возвращаем None, если строки в прайсе нет: тогда страница честно отправляет
    на бесплатную диагностику вместо выдуманной цифры.
    """
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return None
    for r in rows:
        s = r.get("service", "").lower()
        if "тачпад" in s or "трекпад" in s:
            price, time_ = r.get("price", ""), r.get("time", "")
            nums = re.findall(r"\d[\d\s\xa0]*", price)
            if not nums:
                return None
            return price, time_, int(re.sub(r"\D", "", nums[0]))
    return None


CASES = [
    ("trackpad", "Не нажимается, но курсор двигается",
     "Самый частый случай на MacBook. Обычно виновата не механика тачпада, а вздутая батарея под ним — она подпирает панель снизу и не даёт ей продавиться."),
    ("board", "Не реагирует вообще",
     "Курсор не двигается, жесты не работают. Причина — отошедший или повреждённый шлейф, реже сам модуль трекпада после удара или залития."),
    ("glass", "Треснуло стекло трекпада",
     "Панель тачпада стеклянная: после падения или удара крышкой она трескается. Меняется отдельным модулем, разбирать весь топкейс не нужно."),
    ("battery", "Кликает через раз, залипает",
     "Нажатие срабатывает не с первого раза или клавиша «залипла». Часто это начальная стадия вздутия батареи — стоит проверить до того, как тачпад перестанет нажиматься совсем."),
    ("water", "Перестал работать после залития",
     "После пролитой жидкости окисляется шлейф и контакты. Здесь важна не только замена: сначала чистим плату, иначе новый тачпад отработает недолго."),
    ("wrench", "Ложные клики и рывки курсора",
     "Курсор дёргается, система регистрирует нажатия сами по себе. Проверяем шлейф и калибровку, иногда помогает переподключение без замены."),
]

STEPS = [
    ("Бесплатная диагностика",
     "Первым делом смотрим батарею: если тачпад не нажимается, чаще всего причина именно в ней, а сам модуль исправен.", ""),
    ("Называем причину и цену",
     "Говорим честно, что именно менять — тачпад, шлейф или батарею. Цену и срок согласуем до начала работ, оплата по факту.", ""),
    ("Ремонт или замена",
     "Меняем модуль трекпада или шлейф, при залитии сначала чистим плату. После сборки калибруем нажатие.", ""),
    ("Проверка и гарантия",
     "Тестируем клик по всей площади панели и жесты macOS, выдаём гарантию 12 месяцев на деталь и работу.", "12 месяцев"),
]

FAQ = [
    ("Сколько стоит замена тачпада на MacBook?",
     "Зависит от модели и от того, что именно вышло из строя: сам модуль трекпада, шлейф или дело в батарее, которая давит снизу. Диагностика бесплатная — назовём точную цену до начала работ, без предоплаты."),
    ("Тачпад перестал нажиматься, но курсор двигается. Что это?",
     "В подавляющем большинстве случаев на MacBook это вздутая батарея: она расширяется и подпирает панель трекпада снизу, поэтому та физически не может продавиться. Сам тачпад при этом исправен — после замены аккумулятора нажатие возвращается. Пользоваться таким ноутбуком не стоит."),
    ("Можно ли заменить только тачпад, не меняя топкейс?",
     "На большинстве моделей да — трекпад снимается отдельным модулем, и замена укладывается в цену из прайса. Но на MacBook Air с M2 и на MacBook Pro 14″ и 16″ 2021 года и новее трекпад конструктивно связан с топкейсом: там одна деталь стоит дороже всей замены на старых моделях, поэтому цену считаем отдельно и называем до работ. Ещё один частый случай — виноват не сам трекпад, а его шлейф; это дешевле, и мы скажем об этом на диагностике, а не поменяем модуль там, где хватало шлейфа."),
    ("Треснуло стекло тачпада — его меняют целиком?",
     "Да, панель трекпада меняется модулем: отдельно стекло на нём не переклеивают, это ненадёжно. Работа занимает немного времени, разбирать весь корпус не нужно."),
    ("Тачпад отказал после пролитой жидкости — что делать?",
     "Не включайте ноутбук и привезите как есть. После залития окисляются шлейф и контакты, поэтому сначала чистим плату, а уже потом решаем по тачпаду — иначе новый модуль быстро выйдет из строя по той же причине."),
    ("Чем отличается тачпад от трекпада?",
     "Это одно и то же — сенсорная панель под клавиатурой. Apple называет её трекпадом, в обиходе чаще говорят «тачпад». На ремонт название никак не влияет."),
    ("Сколько времени занимает замена?",
     "Обычно справляемся в день обращения, если нужная деталь есть в наличии. Точный срок скажем после бесплатной диагностики — заранее назовите модель и год MacBook."),
    ("Какая гарантия на замену тачпада?",
     "12 месяцев на деталь и на работу мастера. Гарантия вписывается в чек, который выдаём вместе с ноутбуком."),
]

SEO = [
    "Тачпад MacBook выходит из строя по трём типовым причинам: вздутие аккумулятора под панелью, повреждение шлейфа и последствия залития. Отдельно стоит трещина на стеклянной поверхности трекпада после падения. Сервисный центр SPARK в Одессе меняет и ремонтирует трекпады на MacBook Air и MacBook Pro всех поколений — с бесплатной диагностикой и гарантией 12 месяцев.",
    "Важный момент, из-за которого не стоит спешить с заменой: если тачпад перестал нажиматься, но курсор по-прежнему двигается, сам модуль почти всегда исправен. Панель подпирает снизу разбухшая батарея, и достаточно заменить аккумулятор, чтобы нажатие вернулось. Поэтому диагностику мы начинаем именно с батареи — так вы не платите за деталь, которая не сломана.",
    "Работаем в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком. Оплата по факту, без предоплаты. Назовите модель и год MacBook по телефону — подскажем, есть ли нужный трекпад в наличии.",
]

RELATED = [
    ("../../remont-macbook/zamena-akkumulyatora/", "Замена аккумулятора MacBook"),
    ("../../remont-macbook/ne-zaryazhaetsya/", "Ремонт зарядки MacBook"),
    ("../../remont-macbook/zamena-ekrana/", "Замена экрана MacBook"),
    ("../../remont-macbook/zalitie/", "MacBook после залития"),
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/macbook-pro/", "Ремонт MacBook Pro"),
    ("../../remont-macbook/macbook-air/", "Ремонт MacBook Air"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["Замена тачпада MacBook", "Тачпад не нажимается", "Тачпад не реагирует",
             "Треснуло стекло тачпада", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "tp"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена тачпада MacBook">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#tps)"/>'
      '<rect x="70" y="52" width="260" height="158" rx="10" fill="none" stroke="#E11D2A" stroke-width="5"/>'
      '<path d="M50 216 H350 L364 240 H36 Z" fill="#E11D2A" opacity=".92"/>'
      # клавиатура намёком
      '<rect x="104" y="86" width="192" height="52" rx="6" fill="rgba(255,255,255,.14)"/>'
      # сам трекпад — выделен
      '<rect x="152" y="150" width="96" height="46" rx="8" fill="#fff"/>'
      '<circle cx="200" cy="173" r="7" fill="#E11D2A"/>'
      + D._check(300, 178, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Трекпад работает</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')


def build():
    pr = hub_price()
    quick = ("🖱 <b>%s · %s</b>" % (esc(pr[0]), esc(pr[1]))) if pr else "🖱 <b>Диагностика бесплатно</b>"

    price_short = ("от %s ₴" % format(pr[2], ",d").replace(",", "\u00a0")) if pr else None
    title = ("Замена тачпада MacBook в Одессе — %s | SPARK" % price_short) if price_short \
            else "Замена тачпада MacBook в Одессе — ремонт трекпада Air и Pro | SPARK"
    desc = ("Замена и ремонт тачпада MacBook Air и Pro в Одессе: не нажимается, не реагирует, "
            "треснуло стекло. %s, гарантия 12 месяцев, бесплатная диагностика."
            % (price_short.capitalize() if price_short else "Цена после диагностики"))
    kw = ("замена тачпада macbook, замена тачпада macbook air, замена тачпада macbook pro, "
          "ремонт тачпада macbook pro, тачпад macbook не нажимается, ремонт трекпада macbook одесса")
    h1 = "Замена и ремонт тачпада MacBook в Одессе"
    sub = ("Меняем трекпад на MacBook Air и MacBook Pro: не нажимается, не реагирует на жесты, "
           "треснуло стекло или отказал после залития. Диагностику начинаем с батареи — часто "
           "виновата именно она, и менять тачпад не приходится.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Замена тачпада MacBook в Одессе", "serviceType": "Замена тачпада MacBook",
        "description": desc, "areaServed": {"@type": "City", "name": "Одесса"},
        "provider": {"@type": "Organization", "name": "SPARK", "url": "https://sparkservice.od.ua/",
            "telephone": "+380960755452",
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Академика Королёва, 23",
                        "addressLocality": "Одесса", "addressCountry": "UA"}}}
    if pr:
        service["offers"] = {"@type": "Offer", "priceCurrency": "UAH", "price": str(pr[2]),
                             "priceSpecification": {"@type": "PriceSpecification",
                                                    "minPrice": str(pr[2]), "priceCurrency": "UAH"}}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://sparkservice.od.ua/"},
        {"@type": "ListItem", "position": 2, "name": "Ремонт MacBook", "item": "https://sparkservice.od.ua/remont-macbook/"},
        {"@type": "ListItem", "position": 3, "name": "Замена тачпада", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Замена тачпада MacBook в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Замена тачпада</span></div>\n  </div>\n\n')

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт MacBook в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>8 лет</div>\n'
    p += ('        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n'
          '          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>%s</span>\n        </div>\n' % quick)
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic, t, d in CASES)
    p += ('  <section class="sec" id="cases">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>Что случилось с тачпадом</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    # ключевой блок: связь с батареей
    p += ('  <section class="sec sec-bg" id="battery">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Важно знать</span>\n        <h2>Тачпад не нажимается? Скорее всего виновата батарея</h2>\n'
          '        <p class="lead-p">Это самая частая причина на MacBook, и она не имеет отношения к самому трекпаду.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Что происходит.</b> Аккумулятор со временем разбухает и упирается в панель тачпада снизу — она физически не может продавиться, хотя курсор двигается.</span></li>'
          '<li><span class="ck">✓</span><span><b>Что это значит для вас.</b> Сам трекпад исправен. Достаточно <a href="../zamena-akkumulyatora/">заменить аккумулятор</a> — и нажатие возвращается, деталь менять не нужно.</span></li>'
          '<li><span class="ck">✓</span><span><b>Почему мы начинаем с батареи.</b> Чтобы вы не платили за тачпад, который не ломался. Диагностика бесплатная и ни к чему не обязывает.</span></li>'
          '<li><span class="ck">✓</span><span><b>Тянуть не стоит.</b> Вздутие продолжается: дальше перестаёт прилегать крышка, а корпус может деформироваться.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Ремонт тачпада за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Начинаем с батареи</h3><p>Проверим, не в аккумуляторе ли дело — чтобы вы не меняли исправный тачпад.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На деталь и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Чаще всего в день обращения</h3><p>Если нужный трекпад есть в наличии — не придётся ждать неделями.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Ремонт тачпада MacBook в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о ремонте тачпада</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Оставьте номер — скажем причину и цену за 15 минут</h2>\n'
          '          <p>Назовите модель и год MacBook — подскажем, в тачпаде дело или в батарее, и есть ли деталь в наличии.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: ремонт тачпада MacBook</h3>\n'
    p += '''            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
            <div class="mf-field"><label>Телефон</label>
              <div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
              <div class="mf-dots js-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
              <div class="mf-hint js-hint">Введите номер мобильного оператора Украины</div>
            </div>
            <div class="mf-field"><label>Что случилось</label><div class="mf-input"><select class="js-device" aria-label="Что случилось">''' + opts + '''</select></div></div>
            <button class="btn btn-spark mf-submit js-submit" type="button" disabled>Отправить заявку</button>
            <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных.</p>
            <div class="mf-trust"><span><b>✓</b> Бесплатная диагностика</span><span><b>✓</b> Гарантия 12 мес</span><span><b>✓</b> Оплата по факту</span></div>
          </div>
          <div class="sf-success">
            <div class="ms-check"><svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="26" cy="26" r="25" fill="rgba(31,174,90,.10)"/><path d="M15 27l7 7 15-16" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
            <h3>Заявка принята!</h3><p>Перезвоним в течение 15 минут в рабочее время.</p>
            <div class="ms-sum js-summary"></div>
          </div>
        </div>
      </div>
    </div>
  </section>\n\n'''

    p += '''  <section class="sec sec-bg" id="contacts">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Контакты</span><h2>Как нас найти</h2>
        <p class="lead-p">Мы в центре Одессы, рядом с Киевским рынком. Бесплатная диагностика — приходите или вызовите курьера.</p></div>
      <div class="loc-grid reveal">
        <div class="loc-card">
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/><circle cx="12" cy="11" r="2"/></svg></span><div><b>Адрес</b><span>ул. Академика Королёва, 23, Одесса</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span><div><b>Часы работы</b><span>Ежедневно: 10:00-19:00</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 4h4l1.5 5-2 1.2a12 12 0 005.3 5.3l1.2-2 5 1.5v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/></svg></span><div><b>Телефон</b><a href="tel:+380960755452">+38 (096) 075-54-52</a></div></div>
          <a class="btn btn-spark" href="https://www.google.com/maps/dir/?api=1&destination=46.4035605,30.7226524" target="_blank" rel="noopener">Проложить маршрут</a>
        </div>
        <div class="loc-map"><iframe loading="lazy" title="SPARK на карте Одессы" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2751.2871721068323!2d30.720994715589114!3d46.40336147912331!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40c6335e75e1ea93%3A0x24bdf429024f4684!2z0YPQuy4g0JDQutCw0LTQtdC80LjQutCwINCa0L7RgNC-0LvRkdCy0LAsIDIzLA!5e0!3m2!1sru!2sua!4v1667565183335!5m2!1sru!2sua"></iframe></div>
      </div>
    </div>
  </section>
</main>\n\n'''

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт тачпада MacBook").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d случаев, %d FAQ)" % (SLUG, len(h), len(CASES), len(FAQ)))


if __name__ == "__main__":
    main()
