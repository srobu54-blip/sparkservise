#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «Замена клавиатуры MacBook» — спойк хаба:
/remont-macbook/zamena-klaviatury/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ЭТА СТРАНИЦА. «Замена клавиатуры / топкейса» — 1 800 — 4 500 ₴, третья
по чеку строка прайса MacBook, страницы не было. Тема живая из-за механизма
«бабочка»: клавиатуры тех лет ломаются от одной крошки, и такие MacBook ещё
в обороте.

ГЛАВНАЯ РАЗВИЛКА — ОДНА КЛАВИША ИЛИ ТОПКЕЙС ЦЕЛИКОМ. Apple меняет только
топкейс в сборе (корпус, клавиатура, часто и батарея), отсюда суммы, из-за
которых люди списывают рабочие ноутбуки. Если сломана одна-две клавиши,
меняется механизм или колпачок — это в разы дешевле. Тот же приём, что на
странице экрана (матрица против модуля) и тачпада (виновата батарея).

ВТОРАЯ РАЗВИЛКА — ИНОГДА ХВАТАЕТ ЧИСТКИ. На «бабочке» клавиша чаще залипает
от крошки, а не ломается. Страница честно уводит такие случаи на страницу
чистки, вместо того чтобы продавать замену.

ФАКТЫ ПО ПОКОЛЕНИЯМ сверены со страницей чистки, где их уже правили после
фактчека: «бабочка» — 12-дюймовый MacBook с 2015, MacBook Pro с 2016,
MacBook Air Retina с 2018. На Pro и Air 2015 года механизм ножничный.
Magic Keyboard вернулась с MacBook Pro 16″ в конце 2019, вся линейка —
в течение 2020.

ПРО ЦЕНУ. Тянется из прайса хаба через hub_price(), литералов нет.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/zamena-klaviatury"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_price():
    """Цена клавиатуры из прайса хаба: (строка цены, срок, нижняя граница числом)."""
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return None
    for r in rows:
        if "клавиатур" in r.get("service", "").lower():
            price, time_ = r.get("price", ""), r.get("time", "")
            nums = re.findall(r"\d[\d\s\xa0]*", price)
            if not nums:
                return None
            return price, time_, int(re.sub(r"\D", "", nums[0]))
    return None


CASES = [
    ("keyboard", "Не нажимается одна-две клавиши",
     "Самый частый случай на «бабочке». Под клавишу попала крошка — механизм заклинило. Часто это лечится чисткой, а не заменой, и начинаем мы именно с неё."),
    ("wrench", "Клавиша печатает сама или дублируется",
     "Один нажим даёт две буквы или символ идёт сам по себе. Классический признак изношенного механизма бабочки — здесь чисткой уже не обойтись."),
    ("button", "Отвалился колпачок клавиши",
     "Колпачок слетел при чистке или зацепили ногтем. Меняется отдельной клавишей вместе с механизмом — разбирать весь ноутбук не нужно."),
    ("water", "Клавиатура отказала после пролитой жидкости",
     "Здесь сначала плата, а потом клавиатура: под клавишами она первой принимает жидкость на себя. Поставить новую поверх невычищенной платы — значит потерять и её."),
    ("board", "Не работает вся клавиатура сразу",
     "Ни одна клавиша не отвечает, при этом внешняя USB-клавиатура работает. Обычно шлейф или контроллер на плате, а не сама клавиатура — это другой ремонт и другая цена."),
    ("cleaning", "Не горит подсветка клавиш",
     "Подсветка не включается или светится частями. Бывает и шлейф, и настройка, и сама панель подсветки — определяется на диагностике."),
]

STEPS = [
    ("Бесплатная диагностика",
     "Проверяем, сколько клавиш затронуто, отвечает ли клавиатура вообще и не в шлейфе ли дело. Часто выясняется, что менять нечего.", ""),
    ("Пробуем обойтись малым",
     "Если клавиша залипла от крошки — чистим. Если сломан механизм одной-двух клавиш — меняем их отдельно. Топкейс предлагаем только тогда, когда иначе нельзя.", ""),
    ("Согласуем цену и деталь",
     "Называем стоимость и срок до начала работ, показываем, что ставим. Оплата по факту, без предоплаты.", ""),
    ("Замена и проверка",
     "После сборки прогоняем все клавиши, модификаторы и подсветку. Гарантия 12 месяцев на деталь и работу.", "12 месяцев"),
]

FAQ = [
    ("Сколько стоит замена клавиатуры на MacBook?",
     "Разброс большой, потому что это не одна работа, а три разные: замена колпачка с механизмом одной клавиши, замена самой клавиатуры и замена топкейса в сборе. Точную цену называем после бесплатной диагностики, до начала работ."),
    ("Можно ли поменять одну клавишу, а не всю клавиатуру?",
     "Часто да, и с этого мы начинаем. Если сломан механизм одной-двух клавиш, меняются колпачок и сама «бабочка» или ножницы под ним — работа быстрая и в разы дешевле. Всю клавиатуру или топкейс есть смысл менять, когда отказала часть ряда, залита жидкость или механизмы изношены по всей панели."),
    ("Почему в официальном сервисе меняют топкейс целиком?",
     "Потому что на большинстве MacBook клавиатура закреплена в верхней части корпуса заклёпками и отдельной деталью не поставляется. Официальный сервис меняет узел в сборе — корпус, клавиатуру, а на ряде моделей и аккумулятор. Мы работаем и точечно там, где это возможно, а если на вашей модели иначе нельзя, скажем об этом прямо."),
    ("Что такое клавиатура «бабочка» и на каких MacBook она стоит?",
     "Это механизм с очень маленьким ходом клавиши. Apple ставила его на 12-дюймовый MacBook с 2015 года, на MacBook Pro с 2016-го и на MacBook Air Retina с 2018-го. Попавшей под клавишу крошки хватает, чтобы она залипла или перестала срабатывать. На MacBook Pro и Air 2015 года механизм ножничный, там такой проблемы нет. Ножничную Magic Keyboard Apple вернула с MacBook Pro 16″ в конце 2019 года и в течение 2020-го перевела на неё всю линейку."),
    ("Клавиша залипает. Это уже замена?",
     "Не обязательно. На «бабочке» клавиша чаще именно залипает от крошки, а не ломается, и помогает аккуратная чистка — это отдельная и заметно более дешёвая работа. Мы всегда проверяем этот вариант первым, чтобы вы не платили за деталь, которая цела."),
    ("Пролил жидкость на клавиатуру. Менять клавиатуру?",
     "Сначала плату, а клавиатуру потом. Под клавишами она принимает жидкость на себя первой, и если поставить новую клавиатуру поверх невычищенной платы, окисление доберётся и до неё. Не включайте ноутбук и везите как есть — чем раньше, тем дешевле."),
    ("Сколько времени занимает замена клавиатуры?",
     "Отдельная клавиша — обычно в день обращения. Замена клавиатуры или топкейса дольше: узел разбирается полностью, и срок зависит от модели и наличия детали. Точно скажем после диагностики."),
    ("Какая гарантия на замену клавиатуры?",
     "12 месяцев на деталь и работу мастера. Гарантия вписывается в чек, который выдаём вместе с ноутбуком."),
]

SEO = [
    "Клавиатура — самая частая механическая поломка MacBook, и виноват в этом механизм «бабочка». Apple ставила его на 12-дюймовый MacBook с 2015 года, на MacBook Pro с 2016-го и на MacBook Air Retina с 2018-го: ход клавиши там настолько мал, что попавшей крошки хватает, чтобы кнопка залипла или перестала срабатывать совсем. Такие ноутбуки до сих пор в работе, поэтому обращений с ними много. На MacBook Pro и Air 2015 года механизм ножничный, а ножничную Magic Keyboard Apple вернула с MacBook Pro 16″ в конце 2019 года и в течение 2020-го перевела на неё всю линейку.",
    "Главное, из-за чего люди списывают рабочие ноутбуки: в официальном сервисе клавиатуру меняют только топкейсом в сборе. На большинстве MacBook она действительно закреплена в верхней части корпуса заклёпками и отдельной деталью не поставляется, а вместе с топкейсом на ряде моделей меняется и аккумулятор — отсюда и сумма. Но если сломаны одна-две клавиши, менять весь узел не нужно: колпачок и механизм под ним меняются точечно, и это в разы дешевле.",
    "Ещё чаще выясняется, что менять вообще нечего. На «бабочке» клавиша обычно залипает от крошки, а не ломается, и помогает аккуратная чистка — отдельная и куда более дешёвая работа. Поэтому диагностику мы начинаем с неё. Отдельный случай — когда не отвечает вся клавиатура сразу: тогда дело обычно в шлейфе или контроллере на плате, а не в самой панели. Сервисный центр SPARK работает в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком. Оплата по факту, без предоплаты — назовите модель и год MacBook, подскажем, есть ли деталь в наличии.",
]

RELATED = [
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/chistka/", "Чистка MacBook и клавиатуры"),
    ("../../remont-macbook/zalitie/", "MacBook после залития"),
    ("../../remont-macbook/zamena-ekrana/", "Замена экрана MacBook"),
    ("../../remont-macbook/macbook-pro/", "Ремонт MacBook Pro"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["Замена клавиатуры MacBook", "Не нажимается клавиша", "Клавиша печатает сама",
             "Отвалился колпачок", "Не работает вся клавиатура", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "mkb"}
    keys = "".join(
        '<rect x="%g" y="%g" width="26" height="20" rx="4" fill="%s"/>' % (
            96 + (i % 7) * 30, 96 + (i // 7) * 26,
            "#E11D2A" if i == 9 else "rgba(255,255,255,.16)")
        for i in range(21))
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена клавиатуры MacBook">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#mkbs)"/>'
      '<rect x="70" y="52" width="260" height="158" rx="10" fill="none" stroke="#878d99" stroke-width="5"/>'
      + keys +
      '<rect x="152" y="176" width="96" height="26" rx="6" fill="rgba(255,255,255,.10)"/>'
      '<path d="M50 216 H350 L364 240 H36 Z" fill="#E11D2A" opacity=".92"/>'
      + D._check(300, 178, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Клавиша работает</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')


def build():
    pr = hub_price()
    quick = ("⌨ <b>%s · %s</b>" % (esc(pr[0]), esc(pr[1]))) if pr else "⌨ <b>Диагностика бесплатно</b>"

    price_short = ("от %s ₴" % format(pr[2], ",d").replace(",", " ")) if pr else None
    title = ("Замена клавиатуры MacBook в Одессе — %s | SPARK" % price_short) if price_short \
            else "Замена клавиатуры MacBook в Одессе | SPARK"
    desc = ("Замена клавиатуры MacBook Air и Pro в Одессе: залипают клавиши, печатают сами. "
            "Меняем отдельную клавишу, а не топкейс. %s, гарантия 12 месяцев."
            % (price_short.capitalize() if price_short else "Цена после диагностики"))
    kw = ("замена клавиатуры macbook, ремонт клавиатуры macbook, замена клавиатуры macbook air, "
          "замена клавиатуры macbook pro, не работает клавиша macbook, клавиатура бабочка macbook, "
          "замена топкейса macbook, замена клавиатуры макбук одесса")
    h1 = "Замена и ремонт клавиатуры MacBook в Одессе"
    sub = ("Чиним клавиатуру MacBook Air и MacBook Pro: залипают клавиши, печатают сами, отвалился колпачок. "
           "Меняем отдельную клавишу там, где официальный сервис меняет топкейс целиком — "
           "и сначала проверяем, не хватит ли просто чистки.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Замена клавиатуры MacBook в Одессе", "serviceType": "Замена и ремонт клавиатуры MacBook",
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
        {"@type": "ListItem", "position": 3, "name": "Замена клавиатуры", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Замена клавиатуры MacBook в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Замена клавиатуры</span></div>\n  </div>\n\n')

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
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>Что случилось с клавиатурой</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    p += ('  <section class="sec sec-bg" id="butterfly">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Важно знать</span>\n        <h2>Одна клавиша или топкейс целиком — от чего зависит цена</h2>\n'
          '        <p class="lead-p">Именно из-за этой разницы люди списывают рабочие MacBook, услышав цену у официалов.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Чаще всего хватает чистки.</b> На механизме «бабочка» клавиша обычно залипает от крошки, а не ломается. Это отдельная и куда более дешёвая работа — смотрите <a href="../chistka/">чистку MacBook и клавиатуры</a>. С неё мы и начинаем.</span></li>'
          '<li><span class="ck">✓</span><span><b>Сломана одна-две клавиши — меняем их.</b> Колпачок и механизм под ним ставятся точечно, весь узел разбирать не нужно. В разы дешевле замены топкейса.</span></li>'
          '<li><span class="ck">✓</span><span><b>Топкейс в сборе — когда иначе нельзя.</b> На большинстве MacBook клавиатура закреплена в корпусе заклёпками и отдельной деталью не поставляется. Официальный сервис меняет только так, а на ряде моделей вместе с аккумулятором — отсюда и сумма.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не отвечает вся клавиатура сразу?</b> Тогда дело обычно в шлейфе или контроллере на плате, а не в панели. Это другой ремонт и другая цена — проверяем на <a href="../../diagnostika/">бесплатной диагностике</a>.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Ремонт клавиатуры за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Начинаем с чистки</h3><p>На «бабочке» клавиша чаще залипает, чем ломается — и менять её не приходится.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На деталь и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Меняем клавишу, а не топкейс</h3><p>Там, где модель это позволяет — в разы дешевле замены узла в сборе.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена клавиатуры MacBook в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о ремонте клавиатуры</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Оставьте номер — скажем, менять клавишу или чистить</h2>\n'
          '          <p>Назовите модель и год MacBook и какие клавиши не работают. Подскажем, во что это обойдётся, ещё по телефону.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: ремонт клавиатуры MacBook</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт клавиатуры MacBook").replace("{{MODALOPTIONS}}", opts)
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
