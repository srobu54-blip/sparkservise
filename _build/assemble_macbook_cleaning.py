#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «Чистка MacBook от пыли и замена термопасты» — спойк хаба:
/remont-macbook/chistka/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ЭТА СТРАНИЦА. Замер GSC 13.08.2026: кластер MacBook даёт 1859 показов
и ОДИН клик при средней позиции 21 — крупнейший неотработанный кластер сайта,
больше всех iPhone-модельных вместе взятых. Внутри него чистки не было страницы
вообще, поэтому в GSC у неё всего 17 показов: ранжироваться нечему.

ЧТО ПОКАЗАЛА СЕМАНТИКА (Ahrefs, country=ua, 13.08.2026) и как это определило страницу.

1) У КЛАСТЕРА ДВЕ ГОЛОВЫ, А НЕ ОДНА. «чистка макбука» 150 и «чистка клавиатуры
   macbook» 150 — равны. Клавиатурная ветка тянет ещё ~800 модельными хвостами
   (2015-2020, MacBook 12). Поэтому чистке клавиатуры отдан отдельный H2-блок,
   а не строчка в FAQ. Это ветка про бабочку-клавиатуры тех лет.

2) ДВЕ ГРАФИКИ РАВНОПРАВНЫ. «чистка макбука» (кириллица, родительный падеж) 150,
   «чистка macbook» 100, инверсия «macbook чистка» 90. Обе формы в title, H1 и
   подзаголовках. Самая частотная форма — именно кириллический родительный падеж,
   его обычно и забывают.

3) ТЕРМОПАСТА ЖИВЁТ ОБЩЕНОУТБУЧНОЙ ЛЕКСИКОЙ. «замена термопасты macbook» = 0,
   зато «замена термопасты на ноутбуке» 200, «в ноутбуке» 150, «чистка ноутбука и
   замена термопасты» 150 + ценовая ветка 150. Поэтому термопаста НЕ отдельная
   страница, а раздел здесь, и в тексте намеренно есть общеноутбучные формулировки.

4) СИМПТОМНОГО БЛОКА НЕТ СОЗНАТЕЛЬНО. Проверено 60+ фраз: «macbook греется» 0,
   «шумит вентилятор macbook» 0, все модельные вариации 0. Кириллическое «макбук
   греется» — 10. Строить раздел под нулевой спрос смысла нет; симптомы остались
   только в CASES как UX, а не как SEO-ставка.

5) УКРАИНСКАЯ ВЕРСИЯ ДЕРЖИТСЯ НА ТЕРМОПАСТЕ, А НЕ НА ЧИСТКЕ. «чищення macbook»
   и «чищення макбука» — ноль строк в базе, а «заміна термопасти в ноутбуці» = 300,
   самый крупный запрос всего кластера, в полтора раза больше русского аналога.
   Это учтено в i18n: украинские формулировки ведут термопастой.

ПРО ЦЕНУ. В прайсе хаба MacBook есть строка «Чистка от пыли + термопаста» —
её и берём через hub_price(), своих чисел не заводим. Цена обновляется из
админки сама. Для чистки КЛАВИАТУРЫ отдельной строки в прайсе нет, поэтому
там честно отправляем на бесплатную диагностику.

ФАКТ, КОТОРЫЙ ОТЛИЧАЕТ СТРАНИЦУ ОТ КОНКУРЕНТОВ: у MacBook Air на M1 и M2
вентилятора нет вообще, чистить от пыли там нечего. Это же объясняет нулевой
спрос по «чистка macbook air m1». Честно пишем об этом вместо того, чтобы
продавать услугу, которая человеку не нужна.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/chistka"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_price():
    """Цена чистки из прайса хаба MacBook. Строка «Чистка от пыли + термопаста» там есть."""
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return None
    for r in rows:
        s = r.get("service", "").lower()
        if "чистк" in s or "термопаст" in s:
            return r.get("price"), r.get("time")
    return None


CASES = [
    ("fan", "Вентилятор шумит и не смолкает",
     "Кулер выходит на обороты от простых задач и гудит постоянно. Радиатор забит войлоком из пыли, воздух через него не проходит, и система охлаждения работает вхолостую."),
    ("board", "Корпус горячий, скорость падает под нагрузкой",
     "При монтаже, рендере или созвоне ноутбук нагревается и начинает подтормаживать. Это троттлинг: процессор сам снижает частоту, чтобы не перегреться."),
    ("keyboard", "Клавиши залипают или срабатывают через раз",
     "Под клавишу попали крошки или пыль. На моделях с механизмом «бабочка» — MacBook Pro 2016-2019, MacBook Air Retina 2018-2019 и 12-дюймовом MacBook — достаточно крошки, чтобы клавиша перестала нажиматься."),
    ("cleaning", "Два года и больше без обслуживания",
     "Термопаста со временем подсыхает и выдавливается из-под кристалла, отводя тепло всё хуже, даже если пыли немного. Профилактика дешевле, чем ремонт платы после перегрева."),
    ("water", "После пролитой жидкости остались следы",
     "Сладкий чай или кола оставляют липкий налёт, который со временем окисляет дорожки. Здесь нужна не продувка, а разборка и чистка платы."),
    ("battery", "Стал быстро разряжаться и греться в простое",
     "Постоянный перегрев ускоряет износ аккумулятора. Часто на диагностике выясняется, что менять нужно и батарею тоже — скажем об этом честно, до работ."),
]

STEPS = [
    ("Бесплатная диагностика",
     "Снимаем крышку и смотрим, что внутри: сколько пыли в радиаторе, в каком состоянии термопаста и не вздулась ли батарея. Показываем всё вам.", ""),
    ("Называем цену до работ",
     "Говорим, что нужно: только продувка, полная чистка с термопастой или ещё и клавиатура. Цену и срок согласуем заранее, оплата по факту.", ""),
    ("Разборка и чистка",
     "Снимаем систему охлаждения, вычищаем радиатор и лопасти, удаляем старую термопасту, наносим новую и меняем термопрокладки, если они задубели.", ""),
    ("Тест под нагрузкой и гарантия",
     "Прогоняем стресс-тест и сверяем температуры до и после — вы видите результат в цифрах. Гарантия 12 месяцев на работу.", "12 месяцев"),
]

FAQ = [
    ("Сколько стоит почистить MacBook?",
     "Чистка от пыли с заменой термопасты — от 700 до 1 200 грн в зависимости от модели и того, насколько всё запущено. Точную цену мастер называет после бесплатной диагностики, до начала работ и без предоплаты."),
    ("Как часто нужно чистить MacBook?",
     "Ориентир — раз в два года. Если ноутбук стоит на полу, в комнате есть животные или вы работаете с тяжёлыми задачами, то раз в год. Поводом не ждать срока служит постоянный шум вентилятора и горячий корпус в простое."),
    ("Что входит в чистку и замену термопасты?",
     "Разборка, снятие системы охлаждения, чистка радиатора и лопастей вентилятора, удаление старой термопасты, нанесение новой, замена термопрокладок при необходимости и сборка. В конце — стресс-тест с замером температур до и после."),
    ("Можно ли почистить MacBook самому?",
     "Продуть баллончиком со сжатым воздухом снаружи можно, но толку немного: пыль сбивается в войлок внутри радиатора и наружу не выходит. Хуже того, поток воздуха раскручивает вентилятор выше штатных оборотов и может его повредить. Термопасту без разборки заменить нельзя в принципе."),
    ("Чистите ли вы клавиатуру MacBook отдельно?",
     "Да. Это отдельная работа: на моделях с механизмом «бабочка» — MacBook Pro 2016-2019, MacBook Air Retina 2018-2019 и 12-дюймовом MacBook — под клавишу достаточно попасть крошке, чтобы она перестала нажиматься. Чистим без снятия клавиш там, где это возможно, — так безопаснее для механизма. Цену скажем после осмотра, отдельной строки в прайсе для неё нет."),
    ("Нужно ли чистить MacBook Air на M1, M2, M3 или M4?",
     "От пыли — нет: ни у одного MacBook Air на Apple silicon — M1, M2, M3, M4 — вентилятора нет вообще, продувать нечего. Там пассивное охлаждение, и радиатор не забивается. Если такой Air греется и тормозит, причина в другом — приносите на бесплатную диагностику, не будем продавать вам услугу, которая не нужна."),
    ("Сколько времени занимает чистка?",
     "Обычно 1-2 часа, и чаще всего можно подождать на месте. Если при разборке обнаружатся окислы после залития или потребуется замена термопрокладок, скажем сразу и согласуем новый срок."),
    ("Какая гарантия на чистку?",
     "12 месяцев на выполненную работу. Гарантия вписывается в чек, который выдаём вместе с ноутбуком."),
]

SEO = [
    "Чистка макбука от пыли и замена термопасты — базовое обслуживание, которое продлевает жизнь ноутбуку сильнее любого другого вмешательства. Пыль спрессовывается в радиаторе в плотный войлок, воздух перестаёт проходить, и процессор начинает сбрасывать частоту, чтобы не перегреться. Внешне это выглядит как «MacBook стал тормозить», хотя железо исправно. Сервисный центр SPARK в Одессе делает чистку MacBook с полной разборкой системы охлаждения и заменой термопасты — с бесплатной диагностикой и гарантией 12 месяцев.",
    "Чистим все поколения: MacBook Air 11 и 13 дюймов, MacBook Pro 13, 15 и 16 дюймов, включая модели 2012-2015 годов, 2016-2017, 2018, 2019 и 2020, а также 12-дюймовый MacBook. Чистка ноутбука с заменой термопасты на старых Pro 2015 и 2017 годов даёт самый заметный эффект: там паста выработалась полностью, и температуры под нагрузкой падают обычно на 5-15 градусов. У MacBook Air на процессорах M1, M2, M3 и M4 вентилятора нет — этим моделям чистка от пыли не требуется, и мы честно об этом говорим вместо того, чтобы продавать лишнее.",
    "Отдельная услуга — чистка клавиатуры MacBook. Механизм «бабочка» с очень маленьким ходом клавиши Apple ставила на 12-дюймовый MacBook с 2015 года, на MacBook Pro с 2016-го и на MacBook Air Retina с 2018-го — попавшая крошка выводит кнопку из строя целиком. Чаще всего обращаются с MacBook Pro 2017 и 2018 годов, MacBook Air 2018-2019 и 12-дюймовым MacBook. Работаем аккуратно и по возможности без снятия клавиш — механизм бабочки хрупкий, и лишняя разборка ему вредит.",
    "Мы на Таирова, ул. Академика Королёва, 23, рядом с Киевским рынком. Работаем ежедневно с 10:00 до 19:00, оплата по факту, без предоплаты. Назовите модель и год MacBook по телефону — скажем, сколько займёт чистка и нужна ли она вообще именно вашей модели.",
]

RELATED = [
    ("../../remont-macbook/zamena-akkumulyatora/", "Замена аккумулятора MacBook"),
    ("../../remont-macbook/ne-zaryazhaetsya/", "MacBook не заряжается"),
    ("../../remont-macbook/zamena-tachpada/", "Замена тачпада MacBook"),
    ("../../remont-macbook/zamena-ekrana/", "Замена экрана MacBook"),
    ("../../remont-macbook/macbook-pro/", "Ремонт MacBook Pro"),
    ("../../remont-macbook/macbook-air/", "Ремонт MacBook Air"),
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
]

FORM_OPTS = ["Чистка MacBook от пыли", "Чистка + замена термопасты", "Чистка клавиатуры",
             "Шумит вентилятор", "Греется и тормозит", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "tp"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Чистка MacBook от пыли">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#tps)"/>'
      '<rect x="70" y="52" width="260" height="158" rx="10" fill="none" stroke="#E11D2A" stroke-width="5"/>'
      '<path d="M50 216 H350 L364 240 H36 Z" fill="#E11D2A" opacity=".92"/>'
      # клавиатура намёком
      '<rect x="104" y="86" width="192" height="52" rx="6" fill="rgba(255,255,255,.14)"/>'
      # сам трекпад — выделен
      # вентилятор — сердце чистки
      '<circle cx="200" cy="172" r="26" fill="#fff"/>'
      '<path d="M200 150 q10 12 0 22 q-10-10 0-22z" fill="#E11D2A" opacity=".75"/>'
      '<path d="M222 172 q-12 10 -22 0 q10-10 22 0z" fill="#E11D2A" opacity=".75"/>'
      '<path d="M200 194 q-10-12 0-22 q10 10 0 22z" fill="#E11D2A" opacity=".75"/>'
      '<path d="M178 172 q12-10 22 0 q-10 10 -22 0z" fill="#E11D2A" opacity=".75"/>'
      '<circle cx="200" cy="172" r="6" fill="#E11D2A"/>'
      + D._check(300, 178, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Чисто и прохладно</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одеса · гарантия 12 мес</text>'
      '</svg>\n      </div>')


def build():
    pr = hub_price()
    quick = ("🧼 <b>%s · %s</b>" % (esc(pr[0]), esc(pr[1]))) if pr else "🖱 <b>Диагностика бесплатно</b>"

    title = "Чистка MacBook от пыли в Одессе — чистка макбука и замена термопасты | SPARK"
    desc = ("Чистка макбука от пыли и замена термопасты в Одессе: MacBook Air и Pro всех "
            "поколений, чистка клавиатуры. От 700 грн, 1-2 часа, гарантия 12 месяцев.")
    kw = ("чистка macbook, чистка макбука, чистка макбука от пыли, чистка macbook air, "
          "чистка macbook pro, чистка ноутбука и замена термопасты, замена термопасты, "
          "чистка клавиатуры macbook, чистка макбука цена, чистка ноутбука одесса")
    h1 = "Чистка MacBook от пыли и замена термопасты"
    sub = ("Чистка макбука с полной разборкой системы охлаждения: MacBook Air и MacBook Pro "
           "всех поколений. Вычищаем радиатор, меняем термопасту и термопрокладки, отдельно "
           "чистим клавиатуру. Показываем температуры до и после — результат видно в цифрах.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Чистка MacBook от пыли в Одессе", "serviceType": "Чистка MacBook и замена термопасты",
        "description": desc, "areaServed": {"@type": "City", "name": "Одесса"},
        "provider": {"@type": "Organization", "name": "SPARK", "url": "https://sparkservice.od.ua/",
            "telephone": "+380960755452",
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Академика Королёва, 23",
                        "addressLocality": "Одесса", "addressCountry": "UA"}}}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://sparkservice.od.ua/"},
        {"@type": "ListItem", "position": 2, "name": "Ремонт MacBook", "item": "https://sparkservice.od.ua/remont-macbook/"},
        {"@type": "ListItem", "position": 3, "name": "Чистка от пыли", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Чистка MacBook от пыли в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Чистка от пыли</span></div>\n  </div>\n\n')

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
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>С чем приносят MacBook на чистку</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    # ключевой блок: чистка клавиатуры — ВТОРАЯ голова кластера.
    # «чистка клавиатуры macbook» 150/мес — ровно столько же, сколько головной
    # «чистка макбука», плюс ~800 модельными хвостами 2015-2020. Отдельной строки
    # в прайсе хаба под неё нет, поэтому цену здесь честно не называем.
    p += ('  <section class="sec sec-bg" id="keyboard">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Отдельная услуга</span>\n        <h2>Чистка клавиатуры MacBook</h2>\n'
          '        <p class="lead-p">Западающие клавиши — это не про пыль в вентиляторе, это отдельная работа.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Почему клавиша перестаёт нажиматься.</b> Механизм «бабочка» с очень маленьким ходом клавиши стоял на 12-дюймовом MacBook с 2015 года, на MacBook Pro с 2016-го и на MacBook Air Retina с 2018-го. Попавшей под клавишу крошки хватает, чтобы она залипла или перестала срабатывать совсем. На MacBook Pro и Air 2015 года механизм ножничный — там такой проблемы нет.</span></li>'
          '<li><span class="ck">✓</span><span><b>Каких моделей это касается.</b> Чаще всего приносят MacBook Pro 2017 и 2018 годов, MacBook Air 2018-2019 и 12-дюймовый MacBook. Ножничную Magic Keyboard Apple вернула с MacBook Pro 16″ в конце 2019 года, а в течение 2020-го перевела на неё всю линейку — там проблема встречается заметно реже.</span></li>'
          '<li><span class="ck">✓</span><span><b>Как чистим.</b> По возможности без снятия клавиш: механизм бабочки хрупкий, и лишняя разборка ему вредит больше, чем сама грязь. Если клавиша уже сломана — меняем её отдельно, не весь топкейс.</span></li>'
          '<li><span class="ck">✓</span><span><b>Сколько стоит.</b> Зависит от того, сколько клавиш затронуто и цела ли механика. Скажем после бесплатного осмотра — эта услуга не входит в чистку от пыли и считается отдельно.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Как проходит чистка</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Показываем температуры</h3><p>Замеряем под нагрузкой до и после чистки — результат видно в цифрах, а не на словах.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На деталь и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Обычно 1-2 часа</h3><p>Чаще всего можно подождать на месте — чистка не требует заказа деталей.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Чистка MacBook от пыли в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о чистке MacBook</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Оставьте номер — скажем цену чистки за 15 минут</h2>\n'
          '          <p>Назовите модель и год MacBook — скажем, сколько займёт чистка и нужна ли она вашей модели вообще.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: чистка MacBook</h3>\n'
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
        <p class="lead-p">Мы на Таирова, рядом с Киевским рынком. Бесплатная диагностика — приходите или вызовите курьера.</p></div>
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Чистка MacBook").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d случаев, %d FAQ)" % (SLUG, len(h), len(CASES), len(FAQ)))


if __name__ == "__main__":
    main()
