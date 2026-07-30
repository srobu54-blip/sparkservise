#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «Разлочка iPhone от оператора» — спойк услуги разблокировки:
/razblokirovka-iphone/sim-unlock/ (глубина-2). Каркас — из assemble.py,
стили блоков (.legal-box) — из assemble_service.py.

ПОЧЕМУ ЭТА СТРАНИЦА (замер GSC 20-26.07.2026 + Ahrefs country=ua, 30.07.2026).

1) КЛАСТЕР РАЗБЛОКИРОВКИ — ЕДИНСТВЕННЫЙ КОММЕРЧЕСКИЙ КЛАСТЕР САЙТА БЕЗ
   ЛОКАЛЬНОГО ПАКА. В выдаче по «разблокировка icloud» пака нет вообще, а на
   местах 2, 5 и 6 стоят сайты с DR 0 (включая одесский fm-feelmark). Там, где
   пак есть («ремонт айфонов одесса»), позиция 2.9 даёт нам ноль кликов.
   Здесь при DR 0 решает страница, а не GBP. Отсюда 22,6% CTR на
   /razblokirovka-icloud/ при позиции 5,45 — весь кластер даёт 1,7% показов
   сайта и 9% кликов. Узкое место не CTR, а количество показов: 98 в неделю.

2) РАЗЛОЧКА БЫЛА H3 ВНУТРИ ОБЩЕЙ СТРАНИЦЫ. Это самый дорогой чек кластера и
   единственный его подкластер с транзакционным интентом. Запросы (Ahrefs, ua):
   разлочка iphone 70, разлочка айфона 70, iphone разлочка 60, айфон разлочка 60,
   разблокировка iphone от оператора 80, разблокировка оператора iphone 70,
   скільки коштує розблокувати айфон від оператора 50 — ~400/мес плюс уже живые
   показы в GSC по «сколько стоит разблокировать айфон от оператора».

3) СОСЕДНИЙ КЛАСТЕР R-SIM ЗАБИРАЕМ СЮДА. r sim 400, r-sim 250, r sim це 150,
   r sim это 150, r sim iphone 90, стоит ли покупать айфон с r-sim 70 — около
   1000/мес, KD 0. Берём КОММЕРЧЕСКИЙ срез («стоит ли», «r sim iphone»): человек
   выбирает между прокладкой и настоящей разлочкой. Определительный срез
   («r sim це») — это работа для будущей статьи, здесь он не разворачивается.

4) ГРАНИЦА С БУДУЩЕЙ СТАТЬЁЙ ПРО НЕВЕРЛОК (защита от каннибализации). Кластер
   «неверлок» — 8000/мес, но интент информационный и формат там статейный: в
   топ-10 блоги магазинов. Эта страница НЕ оптимизируется под «що таке неверлок»:
   термины lock / neverlock / unlock здесь только разграничиваются в одном
   абзаце, весь разбор уйдёт в /blog/. Ключи в keywords держим транзакционные.

ПРО ЦЕНУ. Услуга для сервиса новая, поэтому НИ ОДНОЙ новой цифры страница не
вводит: обе строки тянутся из прайса родительской страницы
(_build/service/razblokirovka-iphone.json) функцией parent_rows(). Правка
прайса доезжает сюда сама. Всё остальное — «после бесплатной проверки IMEI».

ПРО ФАКТУРУ ПО ОПЕРАТОРАМ. Таблица ORIGIN намеренно не содержит ни цен, ни
сроков, ни обещаний «разлочим любой»: только рынок происхождения и что обычно
за лок. Владельцу стоит вычитать её под свою практику.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D
import assemble_service as SV

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "razblokirovka-iphone/sim-unlock"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
PARENT_JSON = os.path.join(REPO, "_build", "service", "razblokirovka-iphone.json")


def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


# Строки прайса родителя, которые показываем здесь, и под каким именем.
# Ключ — подстрока поля service в _build/service/razblokirovka-iphone.json.
WANT = [
    ("sim-unlock", "Разлочка по оператору (SIM-unlock) по IMEI"),
    ("проверка imei", "Проверка IMEI и статуса блокировки"),
]


def parent_rows():
    """Цены только из прайса родительской страницы. Своих чисел не заводим."""
    try:
        rows = json.load(open(PARENT_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return []
    out = []
    for needle, label in WANT:
        for r in rows:
            if needle in (r.get("service") or "").lower():
                out.append((label, D.normprice(r.get("price") or ""), r.get("time") or ""))
                break
    return out


def unlock_time():
    """Срок разлочки — из той же строки прайса, чтобы FAQ не расходился с таблицей."""
    for lbl, pr, tm in parent_rows():
        if "SIM-unlock" in lbl:
            return tm
    return "от 1 до 7 дней"


CASES = [
    ("sim", "iPhone не видит украинскую SIM-карту",
     "Вставили Киевстар, Vodafone или lifecell, а телефон пишет «SIM не поддерживается», «Недопустимая SIM» или просит карту другого оператора. Это и есть лок: аппарат привязан к сети, в которой его продали."),
    ("board", "Телефон привезли из-за границы",
     "Аппараты из США, Японии, Канады и Европы часто продаются в связке с контрактом оператора. Пока лок не снят, в Украине такой iPhone остаётся дорогим плеером."),
    ("wrench", "Стоит R-SIM и постоянно отваливается",
     "Прокладка под SIM-карту обходит лок, а не снимает его: слетает после обновления iOS, теряет сеть, ломает VoLTE. Официальная разлочка убирает саму причину, а не симптом."),
    ("speaker", "Связь работает через раз",
     "Звонки срываются, интернет держится только в 3G, VoLTE недоступен. Так ведёт себя аппарат под прокладкой — и так же выглядит неисправность модема, поэтому сначала проверяем, что именно у вас."),
    ("case", "Покупаете б/у и не знаете, lock или neverlock",
     "Проверим по IMEI до сделки: оператор, страна, статус блокировки и Lost Mode. Проверка стоит несопоставимо меньше, чем залоченный аппарат по цене чистого."),
    ("button", "Продаёте iPhone и хотите поднять цену",
     "Неверлок на вторичном рынке стоит заметно дороже залоченного. Официальная разлочка остаётся в базе Apple навсегда и переходит к новому владельцу вместе с телефоном."),
]

# Самопроверка: часть обращений вообще не про лок. Отсекать это до визита
# честнее и дешевле для обеих сторон.
SELFCHECK = [
    ("Настройки → Основные → Об этом устройстве",
     "Пролистайте до строки «Блокировка оператора». Надпись «Нет ограничений SIM» означает, что аппарат неверлок и разлочка ему не нужна. Строка есть в iOS 14 и новее."),
    ("Вставьте SIM другого оператора",
     "Самый быстрый тест. Если чужая карта ловит сеть и звонит — лока нет. Если появляется «Недопустимая SIM» или требование карты конкретного оператора — есть."),
    ("Загляните под SIM-лоток",
     "Слово «неверлок» в объявлении ничего не доказывает. Достаньте лоток: если под картой лежит тонкая пластина-прокладка, перед вами R-SIM — обход лока, а не разлочка."),
    ("Наберите *#06# — это IMEI",
     "По IMEI видно оператора, страну продажи и статус блокировки. Это единственный точный способ: продавец может не знать историю аппарата, а база знает."),
    ("Украинский аппарат не видит SIM — это не лок",
     "В Украине iPhone продаются без привязки к оператору. Если карту не видит телефон, купленный здесь, дело в модеме, лотке или контактах — нужна диагностика, а не разлочка."),
]

# Ни цен, ни сроков, ни обещаний «разлочим любой» — только рынок и характер лока.
ORIGIN = [
    ("США — AT&T, T-Mobile, Verizon",
     "Контрактные аппараты. Часть оператор разблокирует сам после выполнения условий договора, часть остаётся в локе.",
     "IMEI и, если сохранились, документы о покупке."),
    ("Япония — Softbank, docomo, au",
     "Ввозных аппаратов много, лок бывает жёстче: у части моделей официальная разлочка недоступна в принципе.",
     "IMEI — статус проверим до того, как вы что-то заплатите."),
    ("Европа — Великобритания, Польша, Германия",
     "Обычно тот же контракт с оператором связи; после закрытия договора лок чаще снимается штатно.",
     "IMEI и страна покупки."),
    ("Украина — Киевстар, Vodafone, lifecell",
     "iPhone здесь продаются без привязки к оператору. Если украинский аппарат не видит SIM, разлочка ни при чём.",
     "Приносите на бесплатную диагностику — ищем причину в железе."),
]

STEPS = [
    ("Проверка по IMEI",
     "Пробиваем аппарат: оператор, страна продажи, статус блокировки, Lost Mode и розыск. Проверка бесплатная, результат говорим как есть — в том числе если разлочка невозможна.", "Шаг 1"),
    ("Цена и срок до начала работ",
     "Стоимость зависит от оператора и страны, поэтому называем её после проверки, а не по телефону наугад. Согласовываем — и только потом начинаем.", "Шаг 2"),
    ("Разлочка",
     "Официальная отвязка по IMEI. Данные на телефоне не трогаем: это не сброс и не перепрошивка, содержимое аппарата остаётся на месте.", "Шаг 3"),
    ("Проверка с украинской SIM",
     "Убеждаемся при вас, что аппарат видит сеть, звонит и держит мобильный интернет. Оплата по факту результата — если разлочить не вышло, платить не за что.", "Оплата по факту"),
]

FAQ = [
    ("Что такое разлочка iPhone от оператора?",
     "Это снятие привязки аппарата к сети конкретного оператора. Контрактные iPhone из США, Японии и Европы продаются дешевле именно потому, что работают только с SIM продавца. Официальная разлочка меняет статус аппарата по IMEI, после чего он принимает любую SIM-карту, в том числе украинскую."),
    ("Как проверить, залочен ли мой iPhone?",
     "Откройте Настройки → Основные → Об этом устройстве и найдите строку «Блокировка оператора». «Нет ограничений SIM» означает неверлок. Второй способ — вставить SIM другого оператора: если появляется «Недопустимая SIM», лок есть. Точный ответ даёт проверка по IMEI, её мы делаем бесплатно."),
    ("Сколько стоит разлочить айфон?",
     "Цена зависит от оператора и страны, в которой аппарат продали: разные операторы отвязываются по-разному. Ориентир — в таблице выше на этой странице, он берётся из общего прайса сервиса. Точную сумму называем после бесплатной проверки по IMEI и до начала работ."),
    ("Чем R-SIM отличается от официальной разлочки?",
     "R-SIM — это тонкая прокладка под SIM-карту, которая подменяет данные оператора и обманывает телефон. Лок при этом остаётся на месте. Официальная разлочка меняет статус аппарата в базе по IMEI: прокладка больше не нужна, а телефон ведёт себя как обычный неверлок."),
    ("Слетит ли разлочка после обновления iOS?",
     "Официальная — нет: статус привязан к аппарату по IMEI и переживает и обновления, и полный сброс. Слетает как раз R-SIM: после очередного обновления прокладка перестаёт работать, и всё начинается сначала."),
    ("Любой ли iPhone можно разлочить?",
     "Нет, и мы говорим об этом сразу. Часть аппаратов — например, отдельные японские модели или телефоны с незакрытым контрактом — официально не отвязываются. Поэтому сначала проверка по IMEI, и только потом разговор о цене: браться за заведомо безнадёжный случай мы не будем."),
    ("Данные на телефоне сохранятся?",
     "Да. Разлочка от оператора — это не сброс и не перепрошивка: фотографии, переписки и приложения остаются на месте. Сброс данных может потребоваться в другом случае — когда снимают забытый пароль экрана."),
    ("Сколько времени занимает разлочка?",
     "Срок зависит от оператора: у одних статус меняется быстро, у других процедура растянута. Ориентир — в таблице выше, точный срок называем вместе с ценой после проверки IMEI, до начала работ."),
]

SEO = [
    "Разлочка iPhone от оператора — это снятие привязки аппарата к сети, в которой его продали. В Украине телефоны официально продаются без такой привязки, поэтому с локом почти всегда сталкиваются владельцы ввозных аппаратов: контрактных из США, японских, европейских. Внешне всё выглядит как поломка связи — «Недопустимая SIM», «SIM не поддерживается», требование карты чужого оператора, — но чинить тут нечего, аппарат исправен.",
    "Обходное решение в виде R-SIM популярно потому, что стоит дёшево и работает сразу. Плата за это — нестабильная связь, отсутствие VoLTE и регулярно слетающая после обновления iOS сеть. Официальная разлочка снимает лок по IMEI: после неё прокладка не нужна, статус остаётся за аппаратом навсегда и переходит к новому владельцу при продаже. Разница видна и в цене на вторичном рынке — неверлок стоит дороже.",
    "Сервисный центр SPARK работает в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком. Проверку по IMEI делаем бесплатно и до оплаты: смотрим оператора, страну и статус блокировки, а если разлочка для конкретного аппарата невозможна — говорим об этом прямо, а не берём деньги за попытку. Оплата по факту результата.",
]

RELATED = [
    ("../", "Разблокировка iPhone — все виды"),
    ("../../razblokirovka-icloud/", "Разблокировка iCloud и Activation Lock"),
    ("../../blog/iphone-nedostupen-zabyl-parol/", "«iPhone недоступен»: что делать"),
    ("../../diagnostika/", "Бесплатная диагностика"),
    ("../../remont-iphone/", "Ремонт iPhone — цены по моделям"),
    ("../../vosstanovlenie-dannyh/", "Восстановление данных"),
]

FORM_OPTS = ["Разлочка от оператора (SIM-unlock)", "iPhone не видит украинскую SIM",
             "Стоит R-SIM — хочу официальную разлочку", "Проверить IMEI перед покупкой",
             "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "su"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Разлочка iPhone от оператора">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#sus)"/>'
      # SIM-карта со срезанным углом
      '<path d="M96 96 h78 l30 30 v104 a10 10 0 01-10 10 H96 a10 10 0 01-10-10 V106 a10 10 0 0110-10 z" '
      'fill="none" stroke="#E11D2A" stroke-width="5" stroke-linejoin="round"/>'
      '<rect x="112" y="150" width="76" height="52" rx="7" fill="#E11D2A" opacity=".9"/>'
      '<path d="M112 176 h76 M138 150 v52 M162 150 v52" stroke="#fff" stroke-width="4"/>'
      + D._check(196, 214, 18) +
      '<text x="150" y="272" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="18" font-weight="700">Работает с любой SIM</text>'
      '<text x="150" y="298" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · оплата по факту</text>'
      '</svg>\n      </div>')


def build():
    rows = parent_rows()
    quick = "🔓 <b>Проверка IMEI бесплатно</b>"

    title = "Разлочка iPhone от оператора в Одессе: SIM-unlock по IMEI | SPARK"
    desc = ("Разлочка iPhone от оператора в Одессе: официальная отвязка по IMEI вместо R-SIM. "
            "Проверим статус бесплатно, цену и срок назовём до начала работ.")
    kw = ("разлочка iphone, разлочка айфона, айфон разлочка, iphone разлочка, "
          "sim-unlock iphone, разблокировка iphone от оператора, разблокировка оператора iphone, "
          "сколько стоит разблокировать айфон от оператора, r-sim iphone, официальный анлок iphone одесса")
    h1 = "Разлочка iPhone от оператора"
    sub = ("Официальная отвязка по IMEI: телефон начинает работать с любой SIM-картой — без "
           "прокладок R-SIM, которые слетают после обновления iOS. Статус проверяем бесплатно, "
           "цену и срок называем до начала работ.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Разлочка iPhone от оператора в Одессе",
        "serviceType": "Разлочка iPhone от оператора (SIM-unlock)",
        "description": desc, "areaServed": {"@type": "City", "name": "Одесса"},
        "provider": {"@type": "Organization", "name": "SPARK", "url": "https://sparkservice.od.ua/",
            "telephone": "+380960755452",
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Академика Королёва, 23",
                        "addressLocality": "Одесса", "addressCountry": "UA"}}}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://sparkservice.od.ua/"},
        {"@type": "ListItem", "position": 2, "name": "Разблокировка iPhone", "item": "https://sparkservice.od.ua/razblokirovka-iphone/"},
        {"@type": "ListItem", "position": 3, "name": "Разлочка от оператора", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Разлочка iPhone от оператора в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    # Таблица рынков — не прайс: у неё три СМЫСЛОВЫЕ колонки. На мобильном
    # .price-table схлопывается в карточку и прячет thead за экран, поэтому
    # второй и третий столбцы надо развести визуально, иначе они слипаются
    # в один абзац без подписей.
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + SV.SERVICE_STYLE + '''
<style>
  #origin .price-table td+td{color:var(--muted);font-size:.9rem;line-height:1.5}
  @media(max-width:560px){#origin .price-table td+td{margin-top:7px}}
</style>
''' + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../">Разблокировка iPhone</a>'
          '<span>›</span><span>Разлочка от оператора</span></div>\n  </div>\n\n')

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Разблокировка iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · проверка IMEI бесплатно</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += ('        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n'
          '          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>\n          <span>%s</span>\n        </div>\n' % quick)
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(dsc)) for ic, t, dsc in CASES)
    p += ('  <section class="sec" id="cases">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>Когда нужна разлочка</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    sc = "".join('<li><span class="ck">✓</span><span><b>%s.</b> %s</span></li>' % (esc(t), esc(dsc))
                 for t, dsc in SELFCHECK)
    p += ('  <section class="sec sec-bg" id="selfcheck">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">До визита в сервис</span>\n        <h2>Как проверить лок самому за 2 минуты</h2>\n'
          '        <p class="lead-p">Часть обращений оказывается вообще не про лок. Пройдитесь по списку — возможно, разлочка вам не нужна.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>%s</ul></div>\n'
          '    </div>\n  </section>\n\n' % sc)

    # Откуда приезжают залоченные аппараты. Ни цен, ни сроков — только характер лока.
    trs = "\n            ".join(
        '<tr><td class="svc-name">%s</td><td>%s</td><td>%s</td></tr>' % (esc(a), esc(b), esc(c))
        for a, b, c in ORIGIN)
    p += ('  <section class="sec" id="origin">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Откуда лок</span>\n        <h2>Аппараты каких рынков приносят чаще всего</h2>\n'
          '        <p class="lead-p">Характер блокировки зависит от оператора и страны продажи. Что именно у вас — видно по IMEI.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal">\n        <table class="price-table">\n'
          '          <thead><tr><th>Рынок и оператор</th><th>Что обычно за лок</th><th>Что нужно от вас</th></tr></thead>\n'
          '          <tbody>\n            %s\n          </tbody>\n        </table>\n      </div>\n    </div>\n  </section>\n\n' % trs)

    # Цены: только строки родительской страницы, своих чисел не заводим.
    if rows:
        prs = "\n            ".join(
            '<tr><td class="svc-name">%s</td><td class="pr">%s</td><td class="time">%s</td></tr>' % (
                esc(lbl), esc(pr), esc(tm)) for lbl, pr, tm in rows)
        p += ('  <section class="sec sec-bg" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
              '        <span class="sec-tag">Цены</span>\n        <h2>Сколько стоит разлочка</h2>\n'
              '        <p class="lead-p">Цены ориентировочные: стоимость зависит от оператора и страны аппарата. Точную сумму и срок назовём после бесплатной проверки по IMEI, до начала работ.</p>\n      </div>\n'
              '      <div class="ptable-wrap reveal">\n        <table class="price-table">\n'
              '          <thead><tr><th>Услуга</th><th>Цена</th><th>Срок</th></tr></thead>\n          <tbody>\n'
              '            <tr><td class="svc-name free">Проверка статуса перед работой</td><td class="pr free">Бесплатно</td><td class="time">10-20 минут</td></tr>\n'
              '            %s\n          </tbody>\n        </table>\n      </div>\n    </div>\n  </section>\n\n' % prs)

    # Смысловая развилка кластера: прокладка против настоящей разлочки.
    p += ('  <section class="sec" id="rsim">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Важно знать</span>\n        <h2>R-SIM или официальная разлочка</h2>\n'
          '        <p class="lead-p">Оба способа заставляют залоченный iPhone принять украинскую SIM, но это разные вещи.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>R-SIM обходит лок, а не снимает его.</b> Тонкая пластина под SIM-картой подменяет данные оператора и обманывает телефон. Сама блокировка остаётся на аппарате.</span></li>'
          '<li><span class="ck">✓</span><span><b>Прокладка слетает после обновления iOS.</b> Apple закрывает лазейку — сеть пропадает, и всё начинается сначала. Официальная разлочка переживает и обновления, и полный сброс.</span></li>'
          '<li><span class="ck">✓</span><span><b>Связь под R-SIM хуже.</b> Типичные спутники — недоступный VoLTE, срывающиеся звонки, интернет, застрявший в 3G. Это плата за обход, а не поломка телефона.</span></li>'
          '<li><span class="ck">✓</span><span><b>Разлочка остаётся с аппаратом.</b> Статус меняется по IMEI и переходит к новому владельцу при продаже. Неверлок на вторичном рынке стоит дороже залоченного телефона с прокладкой.</span></li>'
          '<li><span class="ck">✓</span><span><b>Термины, которые путают.</b> <b>Lock</b> — привязка к оператору, <b>unlock</b> — снятая привязка, <b>neverlock</b> — аппарат, который никогда не был залочен. К <a href="../../razblokirovka-icloud/">блокировке iCloud</a> всё это отношения не имеет: там привязка не к оператору, а к Apple ID.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(dsc), ('<span class="%s">%s</span>' % ("badge w" if "факт" in b.lower() else "badge", esc(b)) if b else "")) for t, dsc, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Разлочка за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Проверка IMEI бесплатно</h3><p>Оператор, страна, статус блокировки и Lost Mode — до того, как вы что-то заплатите.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Скажем, если нельзя</h3><p>Часть аппаратов официально не отвязывается. За безнадёжный случай не беремся и денег не берём.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Оплата по факту</h3><p>Платите за результат, а не за попытку. Цену и срок согласуем до начала работ.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Разлочка iPhone от оператора в Одессе — сервисный центр SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о разлочке</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Пришлите IMEI — скажем, снимается лок или нет</h2>\n'
          '          <p>Наберите на телефоне *#06# и продиктуйте номер мастеру: проверим оператора, страну и статус блокировки бесплатно, назовём цену и срок. Или просто позвоните — мастер на связи.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: разлочка iPhone</h3>\n'
    p += '''            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
            <div class="mf-field"><label>Телефон</label>
              <div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
              <div class="mf-dots js-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
              <div class="mf-hint js-hint">Введите номер мобильного оператора Украины</div>
            </div>
            <div class="mf-field"><label>Что нужно</label><div class="mf-input"><select class="js-device" aria-label="Что случилось">''' + opts + '''</select></div></div>
            <button class="btn btn-spark mf-submit js-submit" type="button" disabled>Отправить заявку</button>
            <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных.</p>
            <div class="mf-trust"><span><b>✓</b> Проверка IMEI бесплатно</span><span><b>✓</b> Оплата по факту</span><span><b>✓</b> Только легально</span></div>
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
        <p class="lead-p">Мы в центре Одессы, рядом с Киевским рынком. Проверка по IMEI бесплатная — приходите или позвоните.</p></div>
      <div class="loc-grid reveal">
        <div class="loc-card">
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/><circle cx="12" cy="11" r="2"/></svg></span><div><b>Адрес</b><span>ул. Академика Королёва, 23, Одесса</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span><div><b>Часы работы</b><span>Пн-Сб: 10:00-19:00 · Вс: выходной</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 4h4l1.5 5-2 1.2a12 12 0 005.3 5.3l1.2-2 5 1.5v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/></svg></span><div><b>Телефон</b><a href="tel:+380960755452">+38 (096) 075-54-52</a></div></div>
          <a class="btn btn-spark" href="https://www.google.com/maps/dir/?api=1&destination=46.4035605,30.7226524" target="_blank" rel="noopener">Проложить маршрут</a>
        </div>
        <div class="loc-map"><iframe loading="lazy" title="SPARK на карте Одессы" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2751.2871721068323!2d30.720994715589114!3d46.40336147912331!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40c6335e75e1ea93%3A0x24bdf429024f4684!2z0YPQuy4g0JDQutCw0LTQtdC80LjQutCwINCa0L7RgNC-0LvRkdCy0LAsIDIzLA!5e0!3m2!1sru!2sua!4v1667565183335!5m2!1sru!2sua"></iframe></div>
      </div>
    </div>
  </section>
</main>\n\n'''

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Разлочка iPhone").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    unknown = [ic for ic, _, _ in CASES if ic not in D.ICONS]
    if unknown:
        # ICONS молча падает в 'wrench' — на лендинге АКБ MacBook так вышло
        # 5 одинаковых значков из 6. Лучше упасть на сборке.
        raise SystemExit("✖ неизвестные иконки: %s (есть: %s)" % (unknown, sorted(D.ICONS)))
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d случаев, %d цен из прайса родителя, %d FAQ)"
          % (SLUG, len(h), len(CASES), len(parent_rows()), len(FAQ)))


if __name__ == "__main__":
    main()
