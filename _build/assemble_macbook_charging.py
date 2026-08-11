#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «MacBook не заряжается» — спойк хаба:
/remont-macbook/ne-zaryazhaetsya/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ИМЕННО ТАКАЯ СТРАНИЦА (замер Ahrefs country=ua, 28.07.2026).

1) ВЫБРАН РЕМОНТНЫЙ КЛАСТЕР, А НЕ ТОРГОВЫЙ. «зарядка для macbook» и соседи
   дают больше (~500/мес), но у них intents = commercial + transactional,
   CPC 15-20 ₴: люди ПОКУПАЮТ зарядку. Там Rozetka и Allo, сервису эти
   запросы не выиграть и не конвертировать. Взят кластер «макбук не
   заряжается» — ~260/мес, KD 0, intent строго informational: человек
   диагностирует поломку. Это наш клиент.

2) ФОРМАТ — ДИАГНОСТИЧЕСКИЙ РАЗБОР, А НЕ ВИТРИНА УСЛУГИ. В выдаче по
   «макбук не заряжается» побеждают статьи «причины и что делать»:
   storepods (DR 25), skeleton.ua (DR 39), jabko.ua (DR 43) и mac.org.ua
   с DR 11 на 8-й позиции — низкий DR тут не приговор. Позицию 1 занимает
   блок «Люди также спрашивают» с четырьмя вопросами; они лежат в основе
   FAQ этой страницы:
     — что делать, если макбук не заряжается;
     — почему не заряжается, хотя подключён к сети;
     — как перезагрузить батарею MacBook;
     — как определить, что батарея неисправна.

3) ТРЕЗВО О ПОТОЛКЕ. Кластер маленький: у лидера выдачи 13 визитов в месяц.
   Страница окупается не объёмом, а качеством интента — человек с неработающей
   зарядкой либо чинит сегодня, либо не чинит вообще.

ГРАНИЦА С ЛЕНДИНГОМ АККУМУЛЯТОРА (защита от каннибализации). Запрос
«аккумулятор не заряжается макбук» пересекается с /zamena-akkumulyatora/.
Разведение по смыслу: ЗДЕСЬ разбираются ВСЕ причины отсутствия заряда —
блок питания, кабель, разъём MagSafe/USB-C, плата зарядки, цепи питания,
SMC; и только КОГДА причина оказывается в батарее, страница уводит на
лендинг аккумулятора. Обратная ссылка уже стоит там. Тот же приём, что
с экраном и стеклом iPhone.

ПРО ЦЕНУ. В отличие от страницы тачпада, цифры выдумывать не нужно: в прайсе
хаба есть «Замена разъёма / платы зарядки MagSafe» и «Ремонт платы / цепей
питания». Обе тянутся из _build/remont-macbook.json функцией hub_rows() —
правка прайса доезжает до страницы сама. Ни одного захардкоженного числа.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/ne-zaryazhaetsya"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")


def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


# Какие строки прайса хаба показываем и под каким именем. Порядок = порядок в
# таблице: от самой частой причины к самой тяжёлой.
WANT = [
    ("разъём", "Замена разъёма / платы зарядки"),
    ("цепей питания", "Ремонт цепей питания на плате"),
    ("аккумулятор", "Замена аккумулятора"),
    ("залити", "Восстановление после залития"),
]


def hub_rows():
    """Строки прайса из JSON хаба. Ни одной цены на странице руками."""
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return []
    out = []
    for needle, label in WANT:
        for r in rows:
            if needle in (r.get("service") or "").lower():
                price = re.sub(r"^\s*от\s+", "", r.get("price") or "")
                out.append((label, price, r.get("time") or ""))
                break
    return out


def hub_diag_time():
    try:
        return json.load(open(HUB_JSON, encoding="utf-8")).get("diagTime") or "15-30 мин"
    except Exception:
        return "15-30 мин"


CASES = [
    ("charging", "Не заряжается вообще, индикатор не горит",
     "Кабель подключён, но ноутбук не реагирует: индикатор на MagSafe не светится, значок в строке меню не меняется. Проверяем по цепочке блок питания, кабель, разъём и плату зарядки."),
    ("wrench", "Заряжается, только если держать кабель под углом",
     "Классический признак разбитого разъёма или надломленного кабеля у основания. Само не пройдёт: контакт постепенно выгорает, а вместе с ним страдает плата зарядки."),
    ("battery", "macOS пишет «Не заряжается» или «Заменить батарею»",
     "Питание доходит, но заряд не растёт. Чаще всего это уже сама батарея или контроллер заряда — здесь решает диагностика, а не замена наугад."),
    ("board", "Работает от сети, но от батареи выключается сразу",
     "Ноутбук живёт только со шнуром. Обычно изношенный аккумулятор или неисправная цепь заряда на плате, реже — сбой контроллера."),
    ("water", "Перестал заряжаться после залития",
     "Жидкость окисляет контакты разъёма и дорожки цепей питания. Сначала чистим плату, иначе новый разъём выйдет из строя по той же причине."),
    ("fan", "Блок питания греется, щёлкает или пахнет",
     "Признак неисправного адаптера. Пользоваться таким опасно — он способен утянуть за собой плату зарядки. Приносите вместе с ноутбуком, проверим оба."),
]

# Блок самопроверки. Смысл не в SEO, а в честности: часть обращений —
# не поломка вовсе, и человек должен иметь возможность понять это сам.
SELFCHECK = [
    ("Другая розетка, другой кабель",
     "Половина случаев лечится этим. Попробуйте другую розетку и, если есть, чужой блок питания подходящей мощности — так сразу видно, в ноутбуке дело или в адаптере."),
    ("Осмотрите разъём",
     "Загляните в порт: пыль, мусор, потемневшие или продавленные контакты. На USB-C порт часто просто забит — аккуратно почистите сухой зубочисткой при выключенном ноутбуке."),
    ("«Зарядка приостановлена» — это НЕ поломка",
     "Если macOS пишет «Зарядка приостановлена» или заряд встал около 80% — так работает оптимизированная зарядка, она берегёт батарею. Это штатное поведение, чинить нечего."),
    ("Сброс SMC — только для Intel",
     "На MacBook с процессором Intel сброс SMC иногда возвращает зарядку. На моделях с Apple Silicon (M1, M2, M3 и новее) SMC не сбрасывается — там достаточно полностью выключить ноутбук и подождать 30 секунд."),
    ("Посмотрите состояние аккумулятора",
     "Системные настройки → Аккумулятор → Состояние. Надпись «Требуется обслуживание» или «Заменить» означает, что дело в самой батарее, а не в зарядке."),
]

STEPS = [
    ("Бесплатная диагностика",
     "Проверяем по порядку: блок питания, кабель, разъём, плату зарядки, цепи питания и саму батарею. Так находим настоящую причину, а не первую попавшуюся.", ""),
    ("Называем причину и цену",
     "Говорим прямо, что менять: разъём, плату зарядки, батарею — или ничего, если виноват адаптер. Цену и срок согласуем до начала работ.", ""),
    ("Ремонт",
     "Меняем разъём или плату зарядки, восстанавливаем цепи питания, при залитии сначала чистим плату под микроскопом.", ""),
    ("Проверка и гарантия",
     "Проверяем зарядку под нагрузкой и полный цикл заряда, выдаём гарантию 12 месяцев на деталь и работу.", "12 месяцев"),
]

FAQ = [
    ("Что делать, если MacBook не заряжается?",
     "Начните с простого: другая розетка, другой кабель или блок питания, осмотр разъёма на мусор и окисел. Если индикатор по-прежнему не загорается и заряд не растёт — дело в разъёме, плате зарядки или батарее, и нужна диагностика. У нас она бесплатная и занимает 15-30 минут при вас."),
    ("Почему MacBook не заряжается, хотя подключён к сети?",
     "Питание может доходить до платы, но не идти в батарею. Типичные причины: изношенный аккумулятор, неисправный контроллер заряда, повреждённая цепь питания после скачка напряжения или залития. Отдельный случай — надпись «Зарядка приостановлена»: это не поломка, а штатная оптимизированная зарядка macOS."),
    ("Как понять, что дело в батарее, а не в зарядке?",
     "Откройте Системные настройки → Аккумулятор → Состояние. Если написано «Требуется обслуживание» или «Заменить», проблема в самой батарее. Если состояние в норме, а заряд всё равно не идёт — ищем причину в разъёме, плате зарядки или адаптере. Точный ответ даёт диагностика: мы проверяем обе ветки, чтобы вы не платили за исправную деталь."),
    ("Что означает «Зарядка приостановлена» — это поломка?",
     "Нет. macOS намеренно придерживает заряд около 80%, чтобы продлить срок службы батареи, и продолжает зарядку ближе к моменту, когда ноутбук обычно нужен. Такое поведение нормально и ремонта не требует."),
    ("Нужно ли сбрасывать SMC?",
     "На MacBook с процессором Intel сброс SMC действительно иногда возвращает зарядку — это безопасно и стоит попробовать до визита в сервис. На моделях с Apple Silicon (M1, M2, M3 и новее) отдельного сброса SMC не существует: достаточно полностью выключить ноутбук и подождать около 30 секунд."),
    ("Сколько стоит заменить разъём зарядки MagSafe?",
     "Стоимость зависит от модели и от того, ограничивается ли дело разъёмом или задета плата зарядки. Актуальные цены — в таблице выше на этой странице, они берутся из общего прайса сервиса. Точную сумму назовём после бесплатной диагностики, до начала работ."),
    ("MacBook перестал заряжаться после пролитой жидкости. Что делать?",
     "Не включайте ноутбук и не пытайтесь зарядить — под напряжением окисление идёт быстрее и повреждает цепи питания. Отключите питание и привезите как есть. Сначала чистим плату, а уже потом решаем по разъёму и батарее: иначе новая деталь выйдет из строя по той же причине."),
    ("Сколько занимает ремонт и какая гарантия?",
     "Замена разъёма или платы зарядки обычно занимает 1-2 дня, ремонт цепей питания — дольше, до 2-5 дней, потому что это работа с платой. Гарантия 12 месяцев на деталь и работу мастера, она вписывается в чек."),
]

SEO = [
    "MacBook перестаёт заряжаться по нескольким разным причинам, и они требуют разного ремонта. Самые частые — неисправный блок питания или кабель, разбитый разъём MagSafe либо загрязнённый порт USB-C, повреждённая плата зарядки, выгоревшие цепи питания на материнской плате и, наконец, изношенный аккумулятор. Сервисный центр SPARK в Одессе находит причину на бесплатной диагностике и называет цену до начала работ.",
    "Важно, что часть обращений оказывается не поломкой. Если macOS пишет «Зарядка приостановлена» или заряд останавливается около 80% — так работает оптимизированная зарядка, которая продлевает жизнь батарее. Мы говорим об этом прямо: если ремонт не нужен, вы услышите это на диагностике и ничего не заплатите.",
    "Отдельного внимания заслуживает залитие. Если ноутбук перестал заряжаться после пролитой жидкости, включать и заряжать его нельзя — под напряжением окисление распространяется по цепям питания. Работаем в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком. Оплата по факту, без предоплаты. Назовите модель и год MacBook — подскажем, есть ли нужная деталь в наличии.",
]

RELATED = [
    ("../../remont-macbook/zamena-akkumulyatora/", "Замена аккумулятора MacBook"),
    ("../../remont-macbook/zamena-tachpada/", "Замена тачпада MacBook"),
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/macbook-pro/", "Ремонт MacBook Pro"),
    ("../../remont-macbook/macbook-air/", "Ремонт MacBook Air"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["MacBook не заряжается", "Разбит разъём зарядки", "Не держит заряд",
             "Не заряжается после залития", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "ch"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="MacBook не заряжается — ремонт">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#chs)"/>'
      '<rect x="70" y="52" width="260" height="158" rx="10" fill="none" stroke="#E11D2A" stroke-width="5"/>'
      '<path d="M50 216 H350 L364 240 H36 Z" fill="#E11D2A" opacity=".92"/>'
      # батарея на экране
      '<rect x="140" y="96" width="112" height="58" rx="9" fill="none" stroke="#fff" stroke-width="5"/>'
      '<rect x="256" y="114" width="12" height="22" rx="3" fill="#fff"/>'
      '<rect x="150" y="106" width="34" height="38" rx="4" fill="#E11D2A"/>'
      # молния
      '<path d="M206 92 L188 126 H202 L196 160 L216 122 H202 Z" fill="#fff"/>'
      + D._check(300, 178, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Зарядка восстановлена</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одеса · гарантия 12 мес</text>'
      '</svg>\n      </div>')


def build():
    rows = hub_rows()
    quick = ("🔌 <b>%s · %s</b>" % (esc(rows[0][1]), esc(rows[0][2]))) if rows else "🔌 <b>Диагностика бесплатно</b>"

    title = "MacBook не заряжается в Одессе — причины и ремонт Air и Pro | SPARK"
    desc = ("MacBook не заряжается: разбираем причины — блок питания, разъём MagSafe, плата "
            "зарядки, батарея. Ремонт в Одессе, бесплатная диагностика, гарантия 12 месяцев.")
    kw = ("macbook не заряжается, макбук не заряжается, почему макбук не заряжается, "
          "что делать если макбук не заряжается, батарея не заряжается macbook, "
          "замена разъёма зарядки macbook, ремонт платы зарядки macbook одесса")
    h1 = "MacBook не заряжается — находим причину и чиним"
    sub = ("Разбираем по порядку все причины: блок питания и кабель, разъём MagSafe или порт "
           "USB-C, плата зарядки, цепи питания и сам аккумулятор. Диагностика бесплатная — "
           "если ремонт не нужен, скажем об этом прямо.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Ремонт зарядки MacBook в Одессе", "serviceType": "Ремонт цепи зарядки MacBook",
        "description": desc, "areaServed": {"@type": "City", "name": "Одесса"},
        "provider": {"@type": "Organization", "name": "SPARK", "url": "https://sparkservice.od.ua/",
            "telephone": "+380960755452",
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Академика Королёва, 23",
                        "addressLocality": "Одесса", "addressCountry": "UA"}}}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://sparkservice.od.ua/"},
        {"@type": "ListItem", "position": 2, "name": "Ремонт MacBook", "item": "https://sparkservice.od.ua/remont-macbook/"},
        {"@type": "ListItem", "position": 3, "name": "Не заряжается", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("MacBook не заряжается — ремонт в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Не заряжается</span></div>\n  </div>\n\n')

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт MacBook в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += ('        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n'
          '          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>%s</span>\n        </div>\n' % quick)
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic, t, d in CASES)
    p += ('  <section class="sec" id="cases">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>Как проявляется проблема с зарядкой</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    # Блок самопроверки: часть обращений — не поломка. Честность важнее лишнего визита.
    sc = "".join('<li><span class="ck">✓</span><span><b>%s.</b> %s</span></li>' % (esc(t), esc(d))
                 for t, d in SELFCHECK)
    p += ('  <section class="sec sec-bg" id="selfcheck">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">До визита в сервис</span>\n        <h2>Что проверить самому за 5 минут</h2>\n'
          '        <p class="lead-p">Часть случаев вообще не требует ремонта. Пройдитесь по списку — возможно, везти ноутбук не придётся.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>%s</ul></div>\n'
          '    </div>\n  </section>\n\n' % sc)

    # Цены: только из прайса хаба, ни одного числа руками.
    if rows:
        trs = "\n            ".join(
            '<tr><td class="svc-name">%s</td><td class="pr">%s</td><td class="time">%s</td></tr>' % (
                esc(lbl), esc(pr), esc(tm)) for lbl, pr, tm in rows)
        p += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
              '        <span class="sec-tag">Цены</span>\n        <h2>Сколько стоит вернуть зарядку</h2>\n'
              '        <p class="lead-p">Цены ориентировочные и зависят от модели. Точную стоимость мастер назовёт после бесплатной диагностики, до начала работ.</p>\n      </div>\n'
              '      <div class="ptable-wrap reveal">\n        <table class="price-table">\n'
              '          <thead><tr><th>Услуга</th><th>Цена</th><th>Срок</th></tr></thead>\n          <tbody>\n'
              '            <tr><td class="svc-name free">Диагностика</td><td class="pr free">Бесплатно</td><td class="time">%s</td></tr>\n'
              '            %s\n          </tbody>\n        </table>\n      </div>\n    </div>\n  </section>\n\n'
              % (esc(hub_diag_time()), trs))

    # Смысловая развилка: когда виновата батарея — уводим на её лендинг.
    p += ('  <section class="sec sec-bg" id="battery">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Важно знать</span>\n        <h2>Когда дело всё-таки в батарее</h2>\n'
          '        <p class="lead-p">Зарядка и аккумулятор — разные неисправности, и лечатся они по-разному.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Питание доходит, заряд не растёт.</b> Если индикатор горит и система видит адаптер, но процент стоит на месте — вопрос к аккумулятору и контроллеру заряда, а не к разъёму.</span></li>'
          '<li><span class="ck">✓</span><span><b>Система прямо говорит об этом.</b> Надпись «Требуется обслуживание» или «Заменить батарею» в состоянии аккумулятора — однозначный признак. В этом случае нужна <a href="../zamena-akkumulyatora/">замена аккумулятора MacBook</a>.</span></li>'
          '<li><span class="ck">✓</span><span><b>Батарея вздулась.</b> Перестал нажиматься трекпад, крышка неплотно прилегает — аккумулятор разбух. Пользоваться ноутбуком в таком виде опасно, подробности на странице <a href="../zamena-tachpada/">ремонта тачпада</a>.</span></li>'
          '<li><span class="ck">✓</span><span><b>Почему мы проверяем обе ветки.</b> Разъём и батарея выходят из строя независимо. Диагностика бесплатная — вы не платите за деталь, которая исправна.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Ремонт зарядки за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Проверяем всю цепь</h3><p>Блок питания, кабель, разъём, плату и батарею — чтобы не менять исправную деталь.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На деталь и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Скажем, если ремонт не нужен</h3><p>Если виноват адаптер или сработала оптимизированная зарядка — вы об этом услышите.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Почему MacBook не заряжается — разбор причин</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о зарядке MacBook</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Оставьте номер — скажем причину и цену за 15 минут</h2>\n'
          '          <p>Назовите модель и год MacBook и что показывает индикатор — подскажем, в разъёме дело, в плате или в батарее.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: MacBook не заряжается</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт зарядки MacBook").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d случаев, %d цен из прайса, %d FAQ)"
          % (SLUG, len(h), len(CASES), len(hub_rows()), len(FAQ)))


if __name__ == "__main__":
    main()
