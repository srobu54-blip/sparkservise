#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «MacBook после залития» — спойк хаба:
/remont-macbook/zalitie/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ЭТА СТРАНИЦА. «Восстановление после залития» — 1 500 — 6 000 ₴, вторая
по чеку строка прайса MacBook, страницы не было. Интент срочный: человек ищет
в тот же час, когда пролил, и такой трафик конвертит лучше всего.

ЧЕМ ОТЛИЧАЕТСЯ ОТ СТРАНИЦЫ ПРО iPhone ПОСЛЕ ВОДЫ. Двумя вещами, и обе
принципиальны.
1) Жидкость с клавиатуры идёт прямо на плату — она лежит непосредственно под
   клавишами. У телефона путь длиннее.
2) Аккумулятор MacBook остаётся подключённым к плате даже у выключенного
   ноутбука, то есть под напряжением, и окисление идёт быстрее. Снять его —
   первое, что делает сервис, и именно поэтому «подожду, высохнет» здесь
   дороже, чем с телефоном.

ПЕРЕКРЁСТНЫЕ ССЫЛКИ. Залитие тянет за собой клавиатуру и тачпад — обе
страницы уже есть, ведём на них честно: сначала плата, потом узлы.

ПРО ЦЕНУ. Тянется из прайса хаба через hub_price(), литералов нет.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/zalitie"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_price():
    """Цена восстановления после залития из прайса хаба."""
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return None
    for r in rows:
        if "залит" in r.get("service", "").lower():
            price, time_ = r.get("price", ""), r.get("time", "")
            nums = re.findall(r"\d[\d\s\xa0]*", price)
            if not nums:
                return None
            return price, time_, int(re.sub(r"\D", "", nums[0]))
    return None


CASES = [
    ("water", "Пролили на клавиатуру",
     "Кофе, чай, вода, пиво. На MacBook плата лежит прямо под клавишами, поэтому жидкость попадает на неё почти сразу — путь короче, чем у телефона."),
    ("board", "Не включается после залития",
     "Не реагирует на кнопку и на зарядку. Не пытайтесь включать: каждая попытка подать питание на мокрую плату дожигает то, что ещё цело."),
    ("keyboard", "Работает, но отказали клавиши или трекпад",
     "Ноутбук включился, а часть клавиш молчит или трекпад не нажимается. Значит, жидкость уже внутри и пошло окисление — плату надо мыть, пока это ещё чистка."),
    ("battery", "Выключается сам, греется, быстро садится",
     "Влага замыкает цепи питания, а аккумулятор в MacBook остаётся подключённым к плате даже у выключенного ноутбука — окисление идёт под напряжением."),
    ("cleaning", "Пролили сладкое: кофе с сахаром, сок, газировку",
     "Хуже чистой воды. Сахар и кислота оставляют липкий проводящий налёт, который сам не высохнет и продолжает разъедать дорожки."),
    ("fan", "Уже высох и работает",
     "Самый обманчивый случай. Вода ушла, окисел остался — ноутбук может отработать неделю или месяц и отказать насовсем, когда ремонт будет стоить кратно дороже."),
]

STEPS = [
    ("Привозите как есть, не включая",
     "Выключите долгим нажатием кнопки питания, отключите зарядку, переверните «домиком» и везите. Чем раньше — тем дешевле ремонт.", ""),
    ("Снимаем аккумулятор в первую очередь",
     "Это главное, что нельзя сделать дома: в MacBook батарея остаётся подключённой к плате и держит её под напряжением. Пока питание есть, окисление идёт быстрее.", ""),
    ("Ультразвуковая чистка платы",
     "Плата отмывается в ультразвуковой ванне — окисел уходит из-под чипов и разъёмов, куда не добраться кистью. Затем сушка и проверка цепей под микроскопом.", "от 2 часов"),
    ("Восстанавливаем то, что пострадало",
     "Меняем выгоревшие элементы, восстанавливаем дорожки, при необходимости — шлейфы, клавиатуру, трекпад. Цену называем до работ, гарантия 12 месяцев.", "12 месяцев"),
]

FAQ = [
    ("Пролил на MacBook. Что делать прямо сейчас?",
     "Выключите долгим нажатием кнопки питания — не закрывайте крышку и не отправляйте в сон. Отключите зарядку. Переверните ноутбук и поставьте «домиком», клавиатурой вниз, чтобы жидкость выходила, а не шла глубже. И везите как есть: каждый час работает против вас."),
    ("Можно ли просто высушить и пользоваться дальше?",
     "Так делают чаще всего, и именно поэтому ремонт потом обходится дороже. Жидкость испаряется, а соли и сахар остаются на плате и продолжают разъедать дорожки под чипами. Ноутбук может отработать неделю или месяц, а потом отказать окончательно — уже с заменой платы вместо чистки."),
    ("Почему нельзя оставить как есть до выходных?",
     "Из-за аккумулятора. В MacBook он остаётся подключённым к плате даже у выключенного ноутбука, и часть цепей всё время под напряжением. Ток плюс влага — это ускоренная коррозия. Снять батарею без разборки нельзя, поэтому чем раньше ноутбук попадёт в сервис, тем меньше успеет разъесть."),
    ("Сколько стоит восстановление MacBook после залития?",
     "Разброс большой, потому что случаи разные: одному ноутбуку хватает промывки платы, другому нужна замена выгоревших элементов, клавиатуры или трекпада. Точную сумму называем после бесплатной диагностики, до начала работ."),
    ("Рис помогает?",
     "Нет. Он не вытягивает влагу из-под микросхем, зато рисовая пыль забивается в разъёмы и вентиляционные решётки. Пока ноутбук лежит в крупе, окисление идёт своим ходом, и вы теряете самое ценное время."),
    ("Феном посушить можно?",
     "Не стоит. Горячий воздух гонит жидкость глубже под чипы и экранирующие крышки, туда, откуда её потом сложнее вымыть, а нагрев вредит проклейке и шлейфам. Просто переверните «домиком» и везите."),
    ("Данные на диске сохранятся?",
     "На моделях, где накопитель съёмный, данные обычно удаётся снять даже при мёртвой плате. На новых MacBook память распаяна на плате — тогда всё зависит от того, насколько она пострадала. Скажем честно после вскрытия; при необходимости есть отдельная услуга восстановления данных."),
    ("Какая гарантия на ремонт после залития?",
     "12 месяцев на выполненные работы. Оговорка честная: гарантия распространяется на то, что мы сделали, — заменённые элементы и восстановленные цепи. Отвечать за всю плату, по которой прошла жидкость, не может ни один сервис, и мы предупреждаем об этом сразу, а не постфактум."),
]

SEO = [
    "Залитый MacBook — самый срочный случай в ремонте ноутбуков Apple, и причина в конструкции. Плата лежит непосредственно под клавиатурой, поэтому пролитый кофе или вода попадают на неё почти мгновенно, без длинного пути, который есть у телефона. Дальше начинается окисление, и оно не прекращается после того, как жидкость испарилась: соли и сахар остаются на контактах и продолжают разъедать дорожки под микросхемами.",
    "Есть вторая особенность, из-за которой ждать здесь дороже, чем с телефоном. Аккумулятор MacBook остаётся подключённым к плате даже у выключенного ноутбука — часть цепей всё время под напряжением. Влага плюс ток дают ускоренную коррозию, а снять батарею без разборки корпуса нельзя. Поэтому первое, что делает мастер, — обесточивает плату, и поэтому же счёт идёт на часы, а не на дни.",
    "Что можно сделать до сервиса: выключить долгим нажатием кнопки питания, отключить зарядку и поставить ноутбук «домиком» клавиатурой вниз, чтобы жидкость выходила наружу. Чего делать нельзя: включать «проверить, работает ли», сушить феном и засыпать рисом. В SPARK плату промывают в ультразвуковой ванне и восстанавливают под микроскопом, диагностика бесплатная, цену называем до работ. Мы в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком, ежедневно с 10:00 до 19:00 — если пролили сегодня, приезжайте сегодня.",
]

RELATED = [
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/zamena-klaviatury/", "Замена клавиатуры MacBook"),
    ("../../remont-macbook/zamena-tachpada/", "Замена тачпада MacBook"),
    ("../../remont-macbook/zamena-akkumulyatora/", "Замена аккумулятора MacBook"),
    ("../../vosstanovlenie-dannyh/", "Восстановление данных"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["MacBook после залития", "Пролил на клавиатуру", "Не включается после залития",
             "Отказали клавиши или трекпад", "Пролил кофе или сладкое", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "mbw"}
    drops = "".join(
        '<circle cx="%g" cy="%g" r="%g" fill="#4aa3ff" opacity="%.2f"/>' % (
            112 + (i % 6) * 30, 92 + (i // 6) * 24, 2.4 + (i % 3) * 0.8, 0.22 + 0.07 * (i % 4))
        for i in range(18))
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ремонт MacBook после залития">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#mbws)"/>'
      '<rect x="70" y="52" width="260" height="158" rx="10" fill="none" stroke="#878d99" stroke-width="5"/>'
      + drops +
      '<path d="M200 132c0 0-24 26-24 41a24 24 0 0048 0c0-15-24-41-24-41z" fill="none" stroke="#4aa3ff" stroke-width="3.2" stroke-linejoin="round"/>'
      '<path d="M189 175a11 11 0 009 9" fill="none" stroke="#4aa3ff" stroke-width="2.2" stroke-linecap="round"/>'
      '<path d="M50 216 H350 L364 240 H36 Z" fill="#E11D2A" opacity=".92"/>'
      + D._check(300, 178, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Плата отмыта и жива</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одесса · ультразвук</text>'
      '</svg>\n      </div>')


def build():
    pr = hub_price()
    quick = ("💧 <b>%s · %s</b>" % (esc(pr[0]), esc(pr[1]))) if pr else "💧 <b>Диагностика бесплатно</b>"

    price_short = ("от %s ₴" % format(pr[2], ",d").replace(",", " ")) if pr else None
    title = ("Залил MacBook — ремонт после залития, %s | SPARK" % price_short) if price_short \
            else "Ремонт MacBook после залития в Одессе | SPARK"
    desc = ("Пролили на MacBook? Не включайте и не сушите феном. Ультразвуковая чистка платы "
            "и восстановление под микроскопом в Одессе. %s, бесплатная диагностика."
            % (price_short.capitalize() if price_short else "Цена после диагностики"))
    kw = ("залил macbook, пролил на macbook, ремонт macbook после залития, "
          "чистка платы macbook, macbook не включается после воды, пролил кофе на macbook, "
          "восстановление macbook после жидкости одесса")
    h1 = "Ремонт MacBook после залития в Одессе"
    sub = ("Промываем плату в ультразвуковой ванне и восстанавливаем цепи под микроскопом. "
           "На MacBook плата лежит прямо под клавиатурой, а батарея остаётся подключённой даже "
           "у выключенного ноутбука — поэтому здесь счёт идёт на часы.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Ремонт MacBook после залития в Одессе", "serviceType": "Восстановление MacBook после попадания жидкости",
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
        {"@type": "ListItem", "position": 3, "name": "После залития", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Ремонт MacBook после залития в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>После залития</span></div>\n  </div>\n\n')

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
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>Как проявляется залитие</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    p += ('  <section class="sec sec-bg" id="first-aid">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Первая помощь</span>\n        <h2>Что сделать сейчас — и чего не делать никогда</h2>\n'
          '        <p class="lead-p">Стоимость ремонта после залития определяется первым часом. Вот что реально важно.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Выключите долгим нажатием кнопки питания.</b> Не закрывайте крышку и не отправляйте в сон: спящий ноутбук остаётся под питанием, а это худшее, что может быть на мокрой плате.</span></li>'
          '<li><span class="ck">✓</span><span><b>Отключите зарядку и поставьте «домиком».</b> Клавиатурой вниз, углом кверху — так жидкость выходит наружу, а не уходит глубже к плате.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не включайте «проверить».</b> Каждая попытка подать питание на влажную плату замыкает соседние цепи и выжигает то, что залитие ещё не тронуло.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не сушите феном и не засыпайте рисом.</b> Горячий воздух гонит жидкость глубже под чипы, а рис не вытягивает её из-под микросхем, зато забивает разъёмы и решётки пылью.</span></li>'
          '<li><span class="ck">✓</span><span><b>Везите в тот же день.</b> Аккумулятор MacBook остаётся подключённым к плате и держит её под напряжением — снять его без разборки нельзя, а окисление под током идёт быстрее.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Восстановление после залития за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Берём в день обращения</h3><p>После залития счёт идёт на часы, поэтому такие ноутбуки пускаем без очереди.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Ультразвуковая ванна</h3><p>Окисел уходит из-под чипов и разъёмов — там, где кистью не достать.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Сразу обесточиваем плату</h3><p>Снимаем аккумулятор первым делом — пока он подключён, коррозия идёт быстрее.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Ремонт MacBook после залития в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о ремонте после залития</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Пролили на MacBook? Позвоните сейчас</h2>\n'
          '          <p>Здесь счёт идёт на часы. Оставьте номер — перезвоним за 15 минут и скажем, что делать до того, как вы доедете.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: MacBook после залития</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт MacBook после залития").replace("{{MODALOPTIONS}}", opts)
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
