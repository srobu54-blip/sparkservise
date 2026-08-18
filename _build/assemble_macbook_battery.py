#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Замена аккумулятора MacBook» — вложенный спойк хаба:
/remont-macbook/zamena-akkumulyatora/ (глубина-2). Каркас переиспользуется из
assemble.py (NAV/FOOTER/STYLE/MODAL_JS/helpers), пути деривятся ../ -> ../../.

ПОЧЕМУ ИМЕННО ЭТА СТРАНИЦА. Замер Ahrefs (country=ua, 28.07.2026): кластер замены
аккумулятора MacBook — около 1 900 запросов в месяц, это больше, чем все прочие
сервисные кластеры MacBook вместе. Для сравнения: клавиатура 30, матрица ~90,
тачпад ~240, зарядка ~160. Конкуренция KD 0 почти везде.

ГЛАВНОЕ ОТЛИЧИЕ ОТ iPhone-АНАЛОГА. Спрос идёт с указанием МОДЕЛИ И ГОДА:
«замена аккумулятора macbook pro 15 2017» 80, «…pro 2019» 90, «…air m1» 80,
«…air 2012» 80 и так далее. Поэтому таблица здесь — не прайс по моделям (у
MacBook поматричных цен нет ни в репозитории, ни в CMS: в model_prices лежат
38 моделей iPhone и ни одного MacBook), а перечень поколений с годами. Её задача —
совпасть с формулировкой запроса. Цена берётся из прайса хаба и указывается один
раз, честно, без выдуманных цифр по каждому поколению.

Когда владелец даст цены по поколениям — в GEN добавляется четвёртый элемент
кортежа и колонка в таблице; остальной код не меняется.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/zamena-akkumulyatora"
NAME = "Замена аккумулятора MacBook"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_battery_price():
    """Цена и срок замены АКБ — из прайса хаба MacBook, а не хардкодом.

    Правка прайса в _build/remont-macbook.json автоматически меняет и эту страницу:
    ровно та проблема, из-за которой цены на сайте разъезжались с прайсом.
    """
    default = ("от 1 500 — 3 500 ₴", "1-2 часа", 1500)
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception as e:
        print(f"[macbook_battery] прайс хаба не прочитан ({e}) — беру значения по умолчанию")
        return default
    for r in rows:
        if "аккумулятор" in r.get("service", "").lower():
            price, time_ = r.get("price", default[0]), r.get("time", default[1])
            nums = re.findall(r"\d[\d\s\xa0]*", price)
            lo = int(re.sub(r"\D", "", nums[0])) if nums else default[2]
            return price, time_, lo
    print("[macbook_battery] строки про аккумулятор в прайсе нет — беру значения по умолчанию")
    return default


# ── поколения: подобраны под фактические формулировки запросов ──────────────
# (подпись, годы, чем отличается по работе)
# Годы ПЕРЕЧИСЛЕНЫ, а не заданы диапазоном — и это не косметика.
# Замер GSC 13.08.2026: батарейная подгруппа кластера MacBook даёт ~276 показов,
# и все они висят на позициях 24-31. Запросы идут с конкретным годом: «замена
# аккумулятора macbook pro 15 2018» 16, «...air 2018» 12, «замена батареи macbook
# pro 2018» 12, «...air m1» 8. Год 2018 — самый частый, 48 показов суммарно.
# Диапазон «2016 — 2020» с формулировкой «macbook pro 2018» не совпадает: на
# странице этой строки просто нет. Докстринг файла с самого начала ставил задачу
# «совпасть с формулировкой запроса» — здесь она и выполняется буквально.
# Годы указаны по фактическим релизам, а не сплошным интервалом.
GEN = [
    ("MacBook Air 13″ M1 / M2 / M3 / M4", "2020 · 2022 · 2024 · 2025",
     "Батарея вклеена в корпус, снимаем без нагрева донышка — так не страдает шлейф трекпада. У MacBook Air M1 ресурс чаще всего ещё есть: сначала снимаем циклы и ёмкость, и если батарея живая — честно об этом говорим."),
    ("MacBook Air 13″ Retina", "2018 · 2019 · 2020",
     "У MacBook Air 2018 и 2019 аккумулятор на части ревизий идёт единым блоком с топкейсом — разбираем аккуратно, топкейс сохраняем."),
    ("MacBook Air 13″ и 11″", "2010 · 2011 · 2012 · 2013 · 2014 · 2015 · 2017",
     "Самые частые в ремонте: батарее уже больше восьми лет, ресурс исчерпан почти всегда."),
    ("MacBook Pro 14″ и 16″ M-серии", "2021 · 2023 · 2024 и новее",
     "Плотная компоновка и клеевые язычки — снимаем штатно, без деформации ячеек."),
    ("MacBook Pro 13″ M1 / M2", "2020 · 2022",
     "Батарея в топкейсе. Меняем с проверкой контроллера заряда и портов USB-C."),
    ("MacBook Pro 13″ без Touch Bar", "2016 · 2017",
     "Версия с обычными функциональными клавишами и двумя портами Thunderbolt, корпус A1708. Её часто путают с Touch Bar-моделью тех же лет, а батарея и топкейс там другие — уточняем по номеру на нижней крышке."),
    ("MacBook Pro 13″ с Touch Bar", "2016 · 2017 · 2018 · 2019 · 2020",
     "Частый случай — вздутие под трекпадом: перестаёт нажиматься. На MacBook Pro 2018 и 2019 встречается чаще всего. Меняем батарею и калибруем трекпад."),
    ("MacBook Pro 15″ и 16″ с Touch Bar", "2016 · 2017 · 2018 · 2019",
     "Крупная батарея из шести ячеек, вздутие поднимает корпус. MacBook Pro 15 2018 — один из самых частых у нас в ремонте. Тянуть с заменой опасно."),
    ("MacBook Pro 13″ и 15″ Retina", "2012 · 2013 · 2014 · 2015",
     "Классика на вторичном рынке. Батарея приклеена намертво — снимаем растворителем клея, без изгибов."),
]

SIGNS = [
    ("battery", "Надпись «Заменить батарею»",
     "macOS показывает «Требуется обслуживание» или «Заменить батарею» в меню аккумулятора — ресурс исчерпан, система уже просит замену."),
    ("charging", "Держит час-полтора вместо рабочего дня",
     "Ноутбук отключается от розетки и почти сразу садится. Обычно это износ ячеек, а не «неправильные настройки»."),
    ("trackpad", "Вздулась батарея, не кликает трекпад",
     "Корпус качается на столе, крышка не прилегает, трекпад перестал нажиматься — вздутие давит на него снизу. Менять срочно."),
    ("board", "Выключается на 20-30% заряда",
     "Резко гаснет, хотя показывал ещё запас, или не включается без адаптера — просевшая батарея не держит пиковую нагрузку."),
    ("fan", "Греется и шумит вентилятор без нагрузки",
     "Разбухшая или деградировавшая ячейка греется сама и заставляет систему поднимать обороты кулера."),
    ("cleaning", "Более 1000 циклов зарядки",
     "В «Об этом Mac → Отчёт о системе → Электропитание» видно число циклов. Ресурс большинства MacBook — около 1000."),
]

STEPS = [
    ("Бесплатная диагностика",
     "Смотрим число циклов, реальную ёмкость и состояние контроллера заряда — убеждаемся, что дело в батарее, а не в плате или адаптере.", ""),
    ("Согласуем цену и срок",
     "Называем точную стоимость по вашей модели до начала работ. Оплата по факту, без предоплаты.", ""),
    ("Замена в мастерской",
     "Снимаем старую батарею без нагрева и изгибов, ставим новую, прогоняем цикл заряда и проверяем трекпад.", ""),
    ("Проверка и гарантия",
     "Замеряем автономность под нагрузкой и выдаём гарантию 12 месяцев на батарею и работу.", "12 месяцев"),
]

FAQ = [
    ("Сколько стоит замена аккумулятора MacBook?",
     "Стоимость зависит от модели и поколения: у MacBook Air она ниже, у MacBook Pro 15″ и 16″ с крупной батареей выше. Диагностика бесплатная, точную цену по вашей модели мастер называет до начала работ — без предоплаты."),
    ("Сколько времени занимает замена батареи MacBook?",
     "Обычно работу выполняем в день обращения. На моделях, где батарея вклеена, разборка занимает больше времени, поэтому точный срок называем после диагностики."),
    ("Как узнать, какая у меня модель MacBook?",
     "Проще всего по номеру модели на нижней крышке — строка вида A1466, A1502, A1708, A1990. Ещё вариант: меню Apple → «Об этом Mac», там указаны модель и год. Назовите номер или год по телефону — сразу скажем, есть ли батарея в наличии."),
    ("Как посмотреть число циклов и износ батареи?",
     "Меню Apple → «Об этом Mac» → «Отчёт о системе» → раздел «Электропитание». Там видно количество циклов перезарядки и состояние. Ресурс большинства MacBook — около 1000 циклов; после этого ёмкость заметно падает."),
    ("Вздулась батарея — можно ли пользоваться ноутбуком?",
     "Лучше не стоит. Вздутая ячейка давит на трекпад и корпус, крышка перестаёт прилегать, а при сильном вздутии есть риск повреждения корпуса и платы. Выключите ноутбук, не заряжайте и привезите на замену."),
    ("Вы ставите оригинальную батарею или аналог?",
     "Используем качественные сервисные аккумуляторы с проверенной ёмкостью, на популярные модели бывают и оригинальные. Разницу в ресурсе и цене объясняем до замены — выбираете вы."),
    ("Какая гарантия на замену аккумулятора MacBook?",
     "12 месяцев на батарею и на работу мастера. Гарантия вписывается в чек, который выдаём вместе с ноутбуком."),
    ("Меняете батарею, если MacBook заливали или он падал?",
     "Да, но сначала бесплатная диагностика. После залития быстрый разряд часто вызывает не батарея, а окисленная плата или контроллер питания — проверим и честно скажем, поможет ли замена."),
]

SEO = [
    "Аккумулятор MacBook — расходник: ресурс большинства моделей около 1000 циклов зарядки, после чего ёмкость заметно падает, ноутбук перестаёт держать заряд и может выключаться при остатке 20-30%. Сервисный центр SPARK в Одессе меняет батареи на всех поколениях MacBook Air и MacBook Pro — от классических моделей 2012-2015 годов до актуальных на чипах M-серии.",
    "Отдельный и самый неприятный случай — вздутие. Разбухшая ячейка поднимает корпус, крышка перестаёт прилегать, а трекпад просто перестаёт нажиматься, потому что батарея давит на него снизу. Пользоваться таким ноутбуком не стоит: выключите его, не ставьте на зарядку и привезите на замену. На большинстве моделей батарея вклеена, поэтому снимаем её без нагрева и изгибов — так не страдают ни шлейфы, ни корпус.",
    "Перед заменой всегда проверяем, действительно ли дело в батарее: иногда быстрый разряд вызывает контроллер заряда, порт или последствия залития. Диагностика бесплатная и ни к чему не обязывает. Работаем в центре Одессы на ул. Академика Королёва, 23 — рядом с Киевским рынком, оплата по факту.",
]

RELATED = [
    ("../zamena-tachpada/", "Ремонт тачпада MacBook"),
    ("../zamena-ekrana/", "Замена экрана MacBook"),
    ("../zalitie/", "MacBook после залития"),
    ("../ne-zaryazhaetsya/", "MacBook не заряжается"),
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/macbook-pro/", "Ремонт MacBook Pro"),
    ("../../remont-macbook/macbook-air/", "Ремонт MacBook Air"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["Замена аккумулятора MacBook", "MacBook быстро разряжается", "Вздулась батарея MacBook",
             "MacBook не включается без зарядки", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "mb"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена аккумулятора MacBook">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#mbs)"/>'
      # корпус ноутбука
      '<rect x="86" y="62" width="228" height="146" rx="10" fill="none" stroke="#E11D2A" stroke-width="5"/>'
      '<path d="M64 214 H336 L350 236 H50 Z" fill="#E11D2A" opacity=".92"/>'
      # батарея внутри экрана
      '<rect x="132" y="96" width="112" height="62" rx="8" fill="none" stroke="#fff" stroke-width="4"/>'
      '<rect x="244" y="112" width="10" height="30" rx="3" fill="#fff"/>'
      '<rect x="140" y="104" width="60" height="46" rx="4" fill="rgba(255,255,255,.9)"/>'
      + D._check(286, 176, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Новая батарея MacBook</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одеса · гарантия 12 мес</text>'
      '</svg>\n      </div>')


def build():
    price, time_, lo = hub_battery_price()
    price_short = "от %s ₴" % format(lo, ",d").replace(",", " ")

    title = "Замена аккумулятора MacBook в Одессе — %s | SPARK" % price_short
    desc = ("Замена аккумулятора MacBook Air и Pro в Одессе: %s, гарантия 12 месяцев, "
            "бесплатная диагностика. Все поколения — от 2012 года до M-серии." % price_short)
    kw = ("замена аккумулятора macbook, замена батареи macbook, замена аккумулятора macbook pro, "
          "замена батареи macbook air, замена аккумулятора macbook одесса, вздулась батарея macbook")
    h1 = "Замена аккумулятора MacBook в Одессе"
    sub = ("Меняем батарею на MacBook Air и MacBook Pro всех поколений — от моделей 2012 года "
           "до актуальных на чипах M-серии. Бесплатная диагностика, гарантия 12 месяцев, оплата по факту.")

    # ── JSON-LD ──
    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Замена аккумулятора MacBook в Одессе", "serviceType": "Замена аккумулятора MacBook",
        "description": desc, "areaServed": {"@type": "City", "name": "Одесса"},
        "provider": {"@type": "Organization", "name": "SPARK", "url": "https://sparkservice.od.ua/",
            "telephone": "+380960755452",
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Академика Королёва, 23",
                        "addressLocality": "Одесса", "addressCountry": "UA"}},
        "offers": {"@type": "Offer", "priceCurrency": "UAH", "price": str(lo),
                   "priceSpecification": {"@type": "PriceSpecification", "minPrice": str(lo), "priceCurrency": "UAH"}}}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://sparkservice.od.ua/"},
        {"@type": "ListItem", "position": 2, "name": "Ремонт MacBook", "item": "https://sparkservice.od.ua/remont-macbook/"},
        {"@type": "ListItem", "position": 3, "name": "Замена аккумулятора", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    # ── head ──
    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Замена аккумулятора MacBook в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Замена аккумулятора</span></div>\n  </div>\n\n')

    # ── hero ──
    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт MacBook в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>8 лет</div>\n'
    p += ('        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n'
          '          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>🔋 <b>%s · %s</b></span>\n        </div>\n' % (esc(price_short), esc(time_)))
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    # ── признаки ──
    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic, t, d in SIGNS)
    p += ('  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Когда менять</span>\n        <h2>Признаки, что пора менять батарею</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    # ── поколения ──
    rows = "\n            ".join(
        '<tr><td class="svc-name">%s</td><td class="time">%s</td><td>%s</td></tr>' % (
            esc(g), esc(y), esc(note)) for g, y, note in GEN)
    p += ('  <section class="sec sec-bg" id="models">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Модели</span>\n        <h2>Какие MacBook меняем</h2>\n'
          '        <p class="lead-p">Работаем со всеми поколениями MacBook Air и MacBook Pro. Цена зависит от модели: '
          'у Air она ниже, у Pro 15″ и 16″ с крупной батареей выше. Точную стоимость называем после бесплатной диагностики — '
          'назовите год или номер модели вида A1466 с нижней крышки.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Поколение</th><th>Годы</th>'
          '<th>Особенности замены</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    # ── важно знать ──
    p += ('  <section class="sec" id="info">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Важно знать</span>\n        <h2>Вздутие батареи — почему нельзя тянуть</h2>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Трекпад перестал нажиматься</b> — самый частый первый признак. Батарея разбухла и давит на него снизу.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не заряжайте вздутый ноутбук.</b> Выключите его и привезите — так безопаснее и дешевле, пока не деформирован корпус.</span></li>'
          '<li><span class="ck">✓</span><span><b>Снимаем без нагрева и изгибов.</b> На большинстве моделей батарея вклеена; мы используем растворитель клея, а не «отдираем».</span></li>'
          '<li><span class="ck">✓</span><span><b>Гарантия 12 месяцев</b> на батарею и работу, с записью в чеке.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    # ── процесс ──
    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Замена батареи за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    # ── почему мы ──
    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Проверим циклы, ёмкость и контроллер заряда до начала работ.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На батарею и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Чаще всего в день обращения</h3><p>Держим ходовые батареи в наличии — не нужно ждать заказа неделями.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    # ── SEO + related ──
    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена аккумулятора MacBook в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    # ── FAQ ──
    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о замене батареи MacBook</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    # ── форма ──
    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Оставьте номер — назовём цену замены за 15 минут</h2>\n'
          '          <p>Подскажем стоимость батареи под вашу модель и срок. Или просто позвоните — мастер на связи.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: замена аккумулятора MacBook</h3>\n'
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

    # ── контакты ──
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Замена аккумулятора MacBook").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d поколений, %d FAQ)" % (SLUG, len(h), len(GEN), len(FAQ)))


if __name__ == "__main__":
    main()
