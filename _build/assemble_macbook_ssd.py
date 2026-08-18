#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «Замена и апгрейд SSD в MacBook» — спойк хаба:
/remont-macbook/apgrejd-ssd/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ИМЕННО SSD, А НЕ «УСКОРЕНИЕ MACBOOK». «Ускорение» — не услуга, а
результат: в прайсе такой строки нет, и страница под неё вышла бы тонкой и
без цены. «Замена / апгрейд SSD» — реальная строка прайса (1 200 — 3 000 ₴),
под неё есть и цена, и понятный объём работ. Информационный интент
(«как ускорить старый макбук», «почему нельзя добавить память») забирает
парная статья блога, коммерческий — эта страница. Интенты разведены
намеренно: ровно на этом мы 18.08 поймали столкновение лендинга зарядки
со статьёй.

ГЛАВНОЕ, ЧТО ДОЛЖНА СКАЗАТЬ СТРАНИЦА. Апгрейд возможен не у всех: с 2016
года накопитель распаян на плате, а с 2018 ещё и привязан к чипу T2.
Поэтому страница начинается с проверки модели, а не с продажи работы —
человеку с MacBook M2 честнее сразу сказать «нельзя», чем звать на диагностику.

ПРО ЦЕНУ. Тянется из прайса хаба через hub_price(), литералов нет.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/apgrejd-ssd"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_price():
    """Цена апгрейда SSD из прайса хаба."""
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return None
    for r in rows:
        if "ssd" in r.get("service", "").lower():
            price, time_ = r.get("price", ""), r.get("time", "")
            nums = re.findall(r"\d[\d\s\xa0]*", price)
            if not nums:
                return None
            return price, time_, int(re.sub(r"\D", "", nums[0]))
    return None


CASES = [
    ("ssd", "Мало места, диск постоянно забит",
     "Свободного меньше десяти процентов — и тормозить начинает вся система: macOS использует место на диске как продолжение оперативной памяти."),
    ("fan", "Загружается медленно, всё думает",
     "Если в ноутбуке ещё обычный жёсткий диск, замена на SSD — самый заметный апгрейд из возможных: загрузка ускоряется в разы."),
    ("board", "Старый накопитель исчерпал ресурс",
     "Появились ошибки записи, система подвисает на ровном месте, диск то виден, то нет. У накопителя есть выработка, и она конечна."),
    ("cleaning", "Хочу больше объёма без внешнего диска",
     "Штатных 128 или 256 ГБ сегодня не хватает почти никому. Там, где накопитель съёмный, объём поднимается разом и без коробочки на проводе."),
    ("wrench", "Не знаю, можно ли на моей модели",
     "Самый частый вопрос. Скажите модель и год из меню «Об этом Mac» — ответим сразу, ещё по телефону, и бесплатно."),
    ("keyboard", "Хочу второй диск вместо привода",
     "На MacBook Pro 2012 года и старше вместо оптического привода ставится второй накопитель — система на SSD, файлы на прежнем диске."),
]

STEPS = [
    ("Проверяем модель — можно ли вообще",
     "Первый и главный шаг. С 2016 года накопитель распаян на плате, с 2018 привязан к чипу T2. Если апгрейд на вашей модели невозможен, скажем это сразу и бесплатно.", ""),
    ("Подбираем накопитель",
     "Под старые Air и Retina Pro нужен современный NVMe и переходник под разъём Apple, под модели до 2012 — обычный SSD. Объём выбираете вы, мы говорим, что подходит.", ""),
    ("Переносим систему и данные",
     "Клонируем содержимое старого накопителя на новый, чтобы вы получили ноутбук в привычном виде, а не пустую систему. Старый диск отдаём вам.", ""),
    ("Проверка и гарантия",
     "Проверяем скорость чтения и записи, загрузку и работу системы. Гарантия 12 месяцев на работу, на сам накопитель — гарантия производителя.", "12 месяцев"),
]

FAQ = [
    ("На каких MacBook можно заменить SSD?",
     "На MacBook Pro без Retina 2012 года и старше — там обычный накопитель на 2,5 дюйма. На MacBook Air 2013-2017 и MacBook Pro Retina 2013-2015 накопитель съёмный, в собственном формате Apple, и через переходник в него встаёт современный NVMe. Начиная с 2016 года накопитель распаян на плате, а с 2018 ещё и привязан к чипу T2 — там замена невозможна. Скажите модель и год, ответим по телефону."),
    ("Сколько стоит замена SSD в MacBook?",
     "Стоимость работы — по прайсу выше, сам накопитель оплачивается отдельно и зависит от объёма, который вы выберете. Цену назовём до начала работ. Если апгрейд на вашей модели невозможен, вы узнаете об этом бесплатно и сразу."),
    ("Насколько ускорится ноутбук?",
     "Сильнее всего разница на моделях с обычным жёстким диском: загрузка системы и запуск программ ускоряются в разы, и ощущается это как другой компьютер. При замене старого штатного накопителя на современный NVMe прирост тоже заметен, особенно на тяжёлых файлах, фото и видео."),
    ("Данные и программы сохранятся?",
     "Да, мы переносим содержимое старого накопителя на новый, чтобы ноутбук остался в привычном виде — с вашими файлами, программами и настройками. Старый диск возвращаем вам, он остаётся резервной копией."),
    ("Можно ли вместо этого добавить оперативной памяти?",
     "Почти никогда. Память распаяна на плате на всех MacBook, кроме Pro без Retina 2012 года и старше, а на компьютерах с процессорами Apple она встроена прямо в чип. Добавить её физически некуда. Подробный разбор по годам — в статье {{ARTICLE}}."),
    ("Подойдёт ли обычный SSD из магазина?",
     "Зависит от модели. В MacBook Pro без Retina 2012 и старше — да, туда идёт обычный SSD на 2,5 дюйма. В Air 2013-2017 и Retina Pro 2013-2015 нужен NVMe плюс переходник под разъём Apple. На Retina-моделях 2012 и начала 2013 разъём выглядит так же, но работает по другому протоколу — современный накопитель там не запустится, и это частая причина неудачных самостоятельных покупок."),
    ("Сколько занимает работа?",
     "Сама замена быстрая. Основное время уходит на перенос данных и зависит от их объёма — точный срок скажем, когда узнаем, сколько занято на диске."),
    ("Какая гарантия?",
     "12 месяцев на работу мастера. На сам накопитель действует гарантия производителя, её условия передаём вместе с ноутбуком."),
]

SEO = [
    "Замена накопителя — единственный апгрейд, который остался доступным владельцам MacBook, и то не всем. Оперативная память распаяна на плате начиная с тонких корпусов, а на компьютерах с процессорами Apple она встроена прямо в чип и не меняется в принципе. С накопителем ситуация лучше: на MacBook Pro без Retina 2012 года и старше стоит обычный диск, а на MacBook Air 2013-2017 и Retina Pro 2013-2015 накопитель съёмный — в собственном формате Apple, но через переходник в него встаёт современный NVMe.",
    "Прирост зависит от того, что стояло раньше. Если в ноутбуке ещё жёсткий диск, разница ощущается сразу: загрузка системы и запуск программ ускоряются в разы, и машина перестаёт задумываться на ровном месте. Если менять старый штатный SSD на современный, прирост скромнее, зато вместе с ним приходит объём — а именно нехватка места чаще всего и заставляет искать апгрейд. Отдельная возможность есть у MacBook Pro 2012 года: вместо оптического привода туда ставится второй накопитель, и система с файлами разъезжаются по разным дискам.",
    "Мы начинаем не с работы, а с проверки модели: если у вас MacBook 2016 года или новее, накопитель распаян на плате, и честный ответ здесь — «нельзя». Такому ноутбуку скорость возвращают другими способами, и о них мы написали отдельно. Данные при замене переносим на новый накопитель, старый отдаём вам. Работаем в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком, оплата по факту, без предоплаты.",
]

RELATED = [
    ("../../blog/kak-uskorit-stary-macbook/", "Статья: как ускорить старый MacBook"),
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/chistka/", "Чистка MacBook и замена термопасты"),
    ("../../remont-macbook/zamena-akkumulyatora/", "Замена аккумулятора MacBook"),
    ("../../remont-macbook/zamena-ekrana/", "Замена экрана MacBook"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["Апгрейд SSD в MacBook", "Мало места на диске", "Стоит жёсткий диск, хочу SSD",
             "Не знаю, можно ли на моей модели", "Второй диск вместо привода", "Другое (опишу в разговоре)"]

ART = '<a href="../../blog/kak-uskorit-stary-macbook/">«Как ускорить старый MacBook»</a>'


def hero_svg():
    grad = D._GRAD % {"p": "mss"}
    bars = "".join(
        '<rect x="%g" y="%g" width="150" height="14" rx="7" fill="%s"/>' % (
            120, 120 + i * 26, "#E11D2A" if i == 1 else "rgba(255,255,255,.14)")
        for i in range(3))
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена и апгрейд SSD в MacBook">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#msss)"/>'
      '<rect x="70" y="52" width="260" height="158" rx="10" fill="none" stroke="#878d99" stroke-width="5"/>'
      + bars +
      '<rect x="120" y="120" width="150" height="14" rx="7" fill="rgba(255,255,255,.14)"/>'
      '<rect x="120" y="146" width="112" height="14" rx="7" fill="#E11D2A"/>'
      '<path d="M286 132 l14 14 -14 14" fill="none" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="M50 216 H350 L364 240 H36 Z" fill="#E11D2A" opacity=".92"/>'
      + D._check(300, 180, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Новый накопитель</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одесса · данные переносим</text>'
      '</svg>\n      </div>')


def build():
    pr = hub_price()
    quick = ("💾 <b>%s · %s</b>" % (esc(pr[0]), esc(pr[1]))) if pr else "💾 <b>Диагностика бесплатно</b>"

    price_short = ("от %s ₴" % format(pr[2], ",d").replace(",", " ")) if pr else None
    title = ("Замена SSD в MacBook в Одессе — %s | SPARK" % price_short) if price_short \
            else "Замена и апгрейд SSD в MacBook в Одессе | SPARK"
    desc = ("Апгрейд SSD в MacBook Air и Pro в Одессе: больше объёма и скорости, данные переносим. "
            "Сначала проверим, съёмный ли накопитель на вашей модели. %s."
            % (price_short.capitalize() if price_short else "Цена после диагностики"))
    kw = ("замена ssd macbook, апгрейд ssd macbook, увеличить память macbook, "
          "замена диска macbook, ssd для macbook air, ssd для macbook pro, "
          "апгрейд макбука одесса, поменять жёсткий диск на ssd macbook")
    h1 = "Замена и апгрейд SSD в MacBook в Одессе"
    sub = ("Ставим современный накопитель на MacBook Air и MacBook Pro: больше объёма, быстрее загрузка, "
           "данные переносим на новый диск. Начинаем с проверки модели — на MacBook 2016 года и новее "
           "накопитель распаян, и об этом честнее узнать сразу.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Замена и апгрейд SSD в MacBook в Одессе", "serviceType": "Замена и апгрейд SSD в MacBook",
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
        {"@type": "ListItem", "position": 3, "name": "Апгрейд SSD", "item": CANON}]}
    # В JSON-LD токен ссылки схлопывается в текст: разметка не должна нести HTML.
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a.replace("{{ARTICLE}}", "«Как ускорить старый MacBook»")}}
        for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Замена и апгрейд SSD в MacBook в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Апгрейд SSD</span></div>\n  </div>\n\n')

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
          '        <span class="sec-tag">Зачем меняют</span>\n        <h2>С чем приходят на апгрейд</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    p += ('  <section class="sec sec-bg" id="models">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Проверьте свою модель</span>\n        <h2>На каких MacBook апгрейд возможен, а на каких нет</h2>\n'
          '        <p class="lead-p">Модель и год — в меню «Об этом Mac». С этого начинается любой разговор об апгрейде.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>MacBook Pro без Retina, 2012 и старше.</b> Полный апгрейд: обычный SSD на 2,5 дюйма, плюс можно поставить второй накопитель вместо оптического привода. Здесь же, единственный случай на всю линейку, добавляется и оперативная память.</span></li>'
          '<li><span class="ck">✓</span><span><b>MacBook Air 2013-2017 и Retina Pro 2013-2015.</b> Накопитель съёмный, в собственном формате Apple — ставим современный NVMe через переходник. Память распаяна и не меняется.</span></li>'
          '<li><span class="ck">✓</span><span><b>Retina Pro 2012 и начала 2013 — осторожно.</b> Разъём выглядит так же, но работает по другому протоколу: современный NVMe там не запустится. Частая причина неудачных самостоятельных покупок.</span></li>'
          '<li><span class="ck">✓</span><span><b>2016 года и новее — апгрейд невозможен.</b> Накопитель распаян на плате, с 2018 года ещё и привязан к чипу T2. Мы скажем это сразу и бесплатно, а как вернуть скорость такому ноутбуку — разобрали в статье ' + ART + '.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Апгрейд SSD за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Скажем «нельзя», если нельзя</h3><p>На моделях с 2016 года накопитель распаян. Узнаете об этом сразу и бесплатно.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На работу мастера, на накопитель — гарантия производителя.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Переносим данные</h3><p>Получаете ноутбук в привычном виде, а старый диск остаётся у вас как копия.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена и апгрейд SSD в MacBook в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a).replace("{{ARTICLE}}", ART)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы об апгрейде SSD</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Назовите модель — скажем, возможен ли апгрейд</h2>\n'
          '          <p>Модель и год есть в меню «Об этом Mac». Ответим по телефону, ехать ради этого не нужно.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: апгрейд SSD в MacBook</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Апгрейд SSD в MacBook").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    pr = hub_price()
    print("✓ %s/index.html (%d симв., %d случаев, %d FAQ, цена: %s)"
          % (SLUG, len(h), len(CASES), len(FAQ), pr[0] if pr else "нет строки"))


if __name__ == "__main__":
    main()
