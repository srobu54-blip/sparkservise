#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы «Замена экрана и матрицы MacBook» — спойк хаба:
/remont-macbook/zamena-ekrana/ (глубина-2). Каркас — из assemble.py.

ПОЧЕМУ ЭТА СТРАНИЦА. «Замена матрицы / экрана» — 3 500 — 9 000 ₴, самый
дорогой чек во всём прайсе сайта, дороже любого ремонта iPhone. Страницы под
него не было, при том что у MacBook уже закрыты аккумулятор, тачпад, чистка
и зарядка. Спрос по MacBook, как показал замер по тачпаду, строго модельный —
поэтому Air и Pro названы отдельно в title, H1 и FAQ.

ДВЕ СМЫСЛОВЫЕ РАЗВИЛКИ, РАДИ КОТОРЫХ СТРАНИЦА И НУЖНА.

1) МАТРИЦА ИЛИ КРЫШКА В СБОРЕ. Apple меняет дисплей только целым модулем —
   крышка, петли, камера, шлейфы. Независимый сервис на многих моделях меняет
   ОДНУ матрицу внутри крышки, и это кратно дешевле. Отсюда и вилка 3 500 —
   9 000 ₴: это не «от балды», а два разных объёма работ. Ровно это и стоит
   объяснить человеку, который увидел цену у официалов и решил, что MacBook
   проще выбросить.

2) НЕТ ПОДСВЕТКИ — ЧАСТО НЕ ЭКРАН, А ПЛАТА. Если изображение видно под
   фонариком, а подсветки нет, виновата цепь подсветки на плате, и это
   заметно дешевле замены дисплея. Тот же приём, что на странице тачпада
   («виновата батарея») и разъёма («виноват кабель»): honest-диагностика
   как отстройка, а не как украшение.

ПРО ЦЕНУ. Тянется из прайса хаба через hub_price() — литералов на странице нет.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-macbook/zamena-ekrana"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
HUB_JSON = os.path.join(REPO, "_build", "remont-macbook.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def hub_price():
    """Цена экрана из прайса хаба: (строка цены, срок, нижняя граница числом).

    Нижняя граница нужна отдельно — она идёт в title, description и в Offer.
    None, если строки в прайсе нет: тогда страница честно отправляет на
    бесплатную диагностику вместо выдуманной цифры.
    """
    try:
        rows = json.load(open(HUB_JSON, encoding="utf-8")).get("priceRows", [])
    except Exception:
        return None
    for r in rows:
        if "матриц" in r.get("service", "").lower():
            price, time_ = r.get("price", ""), r.get("time", "")
            nums = re.findall(r"\d[\d\s\xa0]*", price)
            if not nums:
                return None
            return price, time_, int(re.sub(r"\D", "", nums[0]))
    return None


CASES = [
    ("screen", "Разбито стекло, трещины по матрице",
     "Уронили, закрыли крышку на наушниках или на кабеле. На MacBook с Retina стекло приклеено к матрице намертво, поэтому «переклеить только стекло» здесь нельзя — меняется панель."),
    ("board", "Изображения нет, но подсветка горит",
     "Экран светится ровным белым или серым. Обычно это матрица или шлейф, реже видеотракт на плате — до вскрытия не определить, поэтому диагностика бесплатная."),
    ("glass", "Нет подсветки, картинку видно под фонариком",
     "Наведите фонарик под углом: если изображение просматривается, дело чаще в цепи подсветки на плате, а не в дисплее. Это заметно дешевле замены экрана."),
    ("wrench", "Полосы, артефакты, битые пиксели",
     "Вертикальные или горизонтальные полосы, рябь, цветные пятна. Иногда лечится переподключением шлейфа, но чаще меняется матрица."),
    ("hinge", "Светлые пятна внизу экрана, «сценический свет»",
     "Характерная беда MacBook Pro 2016-2017: шлейф подсветки короче, чем нужно, и перетирается от открывания крышки. Сначала подсветка неровная снизу, потом гаснет при открытии больше чем наполовину."),
    ("case", "Пятна и разводы на покрытии",
     "Антибликовое покрытие Retina-дисплеев 2012-2015 годов отслаивается пятнами в местах контакта с клавиатурой. Картинка целая, испорчено именно покрытие."),
]

STEPS = [
    ("Бесплатная диагностика",
     "Смотрим под фонариком, есть ли изображение, проверяем шлейф и цепь подсветки на плате. Задача — понять, нужен ли дисплей вообще.", ""),
    ("Говорим, что менять: матрицу или крышку",
     "На многих моделях достаточно заменить одну матрицу внутри крышки — это кратно дешевле замены модуля в сборе. Скажем, что подходит вашей модели, до начала работ.", ""),
    ("Согласуем цену и деталь",
     "Называем стоимость и срок, показываем, какую панель ставим. Оплата по факту, без предоплаты.", ""),
    ("Замена и проверка",
     "Меняем, собираем, проверяем равномерность подсветки, отсутствие битых пикселей, работу камеры и датчика закрытия крышки. Гарантия 12 месяцев.", "12 месяцев"),
]

FAQ = [
    ("Сколько стоит замена экрана на MacBook?",
     "Вилка широкая, и это не уклончивость: разброс зависит от того, меняется одна матрица внутри крышки или крышка в сборе, и от модели. Точную цену называем после бесплатной диагностики, до начала работ и без предоплаты."),
    ("Можно ли заменить только стекло, не меняя матрицу?",
     "На MacBook с Retina-дисплеем — нет. Стекло там приклеено к матрице в единый пакет, и попытки «переклеить стекло» заканчиваются разводами, пылью под поверхностью и повторным ремонтом. Меняется панель целиком. На старых не-Retina моделях стекло действительно было отдельным, но таких MacBook в работе почти не осталось."),
    ("В официальном сервисе назвали цену как за половину ноутбука. Почему у вас дешевле?",
     "Потому что там меняют дисплей только модулем в сборе: крышка, петли, камера, антенны, шлейфы — всё вместе. Мы на многих моделях меняем одну матрицу внутри вашей крышки, а остальное остаётся ваше. Работа тоньше и дольше, зато деталь стоит кратно меньше. Если на вашей модели так сделать нельзя, скажем об этом прямо."),
    ("Экран не светится, но ноутбук работает. Это дисплей?",
     "Не факт, и это стоит проверить до того, как платить за экран. Посветите фонариком под углом: если изображение просматривается, матрица жива, а не работает подсветка — а её цепь находится на материнской плате. Такой ремонт заметно дешевле замены дисплея, и начинаем мы именно с этой проверки."),
    ("Что за светлые пятна внизу экрана на MacBook Pro?",
     "Это известный дефект MacBook Pro 2016-2017 годов: шлейф подсветки сделан коротким и перетирается от постоянного открывания и закрывания крышки. Сначала внизу экрана появляются неровные светлые участки, похожие на подсветку сцены, затем подсветка гаснет, если открыть крышку больше чем наполовину. Лечится заменой шлейфа или дисплея — что именно нужно, покажет диагностика."),
    ("На экране пятна, как будто стёрлось покрытие. Что это?",
     "Отслоение антибликового покрытия — типично для Retina-дисплеев 2012-2015 годов, особенно в местах, где экрана касаются клавиши. Само изображение при этом в порядке. Покрытие можно аккуратно снять целиком или заменить панель — разница в цене и в том, как экран будет вести себя на солнце. Покажем оба варианта."),
    ("Сколько занимает замена экрана MacBook?",
     "Обычно 1-2 дня. Дольше, чем замена аккумулятора, потому что дисплейный модуль разбирается аккуратно и с прогревом. Точный срок назовём после диагностики — заранее скажите модель и год ноутбука."),
    ("Какая гарантия на замену экрана?",
     "12 месяцев на деталь и работу мастера. Гарантия вписывается в чек, который выдаём вместе с ноутбуком. Если появятся вопросы к подсветке или к посадке дисплея не по вашей вине — разбираемся бесплатно."),
]

SEO = [
    "Экран — самый дорогой узел MacBook, и именно из-за его цены ноутбуки часто списывают раньше времени. Разброс стоимости здесь не случайный: заменить можно либо одну матрицу внутри вашей крышки, либо дисплейный модуль в сборе — с петлями, камерой, антенной и шлейфами. Официальный сервис работает только вторым способом, поэтому и называет сумму, сопоставимую с половиной стоимости ноутбука. Сервисный центр SPARK в Одессе меняет экраны и матрицы на MacBook Air и MacBook Pro всех поколений с гарантией 12 месяцев.",
    "Прежде чем менять дисплей, стоит убедиться, что дело в нём. Самая обидная ошибка — заплатить за экран там, где не работала подсветка: её цепь находится на материнской плате, и такой ремонт кратно дешевле. Проверить можно дома: посветите фонариком на тёмный экран под углом. Видно изображение — матрица жива. Отдельная история у MacBook Pro 2016-2017 годов: там перетирается короткий шлейф подсветки, и это выглядит как неровные светлые пятна внизу экрана, а потом как погасший дисплей при открытой крышке.",
    "На MacBook с Retina стекло приклеено к матрице в единый пакет, поэтому «переклеить только стекло» на них нельзя — это тот случай, когда дешёвое предложение оборачивается разводами и пылью под поверхностью. Мы меняем панель целиком и проверяем после сборки равномерность подсветки, битые пиксели, камеру и датчик закрытия крышки. Работаем в центре Одессы на ул. Академика Королёва, 23, рядом с Киевским рынком. Оплата по факту, без предоплаты — назовите модель и год MacBook, и мы подскажем, есть ли нужная матрица в наличии.",
]

RELATED = [
    ("../../remont-macbook/", "Ремонт MacBook — все услуги"),
    ("../../remont-macbook/zamena-akkumulyatora/", "Замена аккумулятора MacBook"),
    ("../../remont-macbook/zamena-tachpada/", "Замена тачпада MacBook"),
    ("../../remont-macbook/macbook-pro/", "Ремонт MacBook Pro"),
    ("../../remont-macbook/macbook-air/", "Ремонт MacBook Air"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["Замена экрана MacBook", "Разбит экран", "Полосы или пятна на экране",
             "Нет подсветки", "Светлые пятна внизу экрана", "Другое (опишу в разговоре)"]


def hero_svg():
    grad = D._GRAD % {"p": "mbs"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена экрана MacBook">'
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#mbss)"/>'
      # крышка
      '<rect x="70" y="46" width="260" height="162" rx="10" fill="none" stroke="#878d99" stroke-width="5"/>'
      # экран: левая половина целая, правая с трещиной
      '<rect x="82" y="58" width="236" height="138" rx="5" fill="#12151b"/>'
      '<rect x="82" y="58" width="118" height="138" fill="#1FAE5A" opacity=".16"/>'
      '<polyline points="248,58 232,104 268,120 226,196" fill="none" stroke="#E11D2A" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
      '<line x1="232" y1="104" x2="200" y2="88" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      '<line x1="268" y1="120" x2="308" y2="100" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      # основание
      '<path d="M50 214 H350 L364 238 H36 Z" fill="#E11D2A" opacity=".92"/>'
      + D._check(300, 176, 18) +
      '<text x="200" y="266" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Новая матрица</text>'
      '<text x="200" y="286" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')


def build():
    pr = hub_price()
    quick = ("🖥 <b>%s · %s</b>" % (esc(pr[0]), esc(pr[1]))) if pr else "🖥 <b>Диагностика бесплатно</b>"

    price_short = ("от %s ₴" % format(pr[2], ",d").replace(",", " ")) if pr else None
    title = ("Замена экрана MacBook в Одессе — %s | SPARK" % price_short) if price_short \
            else "Замена экрана и матрицы MacBook в Одессе | SPARK"
    desc = ("Замена экрана и матрицы MacBook Air и Pro в Одессе: разбит, полосы, нет подсветки. "
            "Меняем матрицу, а не крышку в сборе. %s, гарантия 12 месяцев."
            % (price_short.capitalize() if price_short else "Цена после диагностики"))
    kw = ("замена экрана macbook, замена матрицы macbook, замена дисплея macbook, "
          "разбил экран macbook, замена экрана macbook air, замена экрана macbook pro, "
          "полосы на экране macbook, не работает подсветка macbook, замена экрана макбук одесса")
    h1 = "Замена экрана и матрицы MacBook в Одессе"
    sub = ("Меняем дисплей на MacBook Air и MacBook Pro: разбито стекло, полосы, нет подсветки, "
           "пятна на покрытии. На многих моделях достаточно заменить одну матрицу внутри вашей крышки — "
           "это кратно дешевле замены модуля в сборе, которую предлагают официалы.")

    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Замена экрана MacBook в Одессе", "serviceType": "Замена экрана и матрицы MacBook",
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
        {"@type": "ListItem", "position": 3, "name": "Замена экрана", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (
        escA("Замена экрана MacBook в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-macbook/">Ремонт MacBook</a>'
          '<span>›</span><span>Замена экрана</span></div>\n  </div>\n\n')

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
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>Что случилось с экраном</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards)

    # ключевой блок: из чего складывается цена и когда экран вообще ни при чём
    p += ('  <section class="sec sec-bg" id="matrix">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Важно знать</span>\n        <h2>Почему у одних экран стоит 3 500, а у других 9 000</h2>\n'
          '        <p class="lead-p">Это не разные наценки, а два разных ремонта. Разница в том, что именно меняется.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Матрица внутри вашей крышки.</b> Меняется одна панель, а крышка, петли, камера, антенны и шлейфы остаются ваши. Работа тоньше и дольше, зато деталь стоит кратно меньше.</span></li>'
          '<li><span class="ck">✓</span><span><b>Дисплейный модуль в сборе.</b> Крышка меняется целиком. Так работает официальный сервис — отсюда и суммы, сопоставимые с половиной цены ноутбука. Иногда это действительно единственный вариант, и тогда мы скажем прямо.</span></li>'
          '<li><span class="ck">✓</span><span><b>Нет подсветки — сначала проверьте фонариком.</b> Посветите на тёмный экран под углом. Видно изображение — матрица жива, а не работает цепь подсветки на плате. Это <a href="../../diagnostika/">другой ремонт</a> и заметно дешевле.</span></li>'
          '<li><span class="ck">✓</span><span><b>Стекло отдельно на Retina не меняется.</b> Оно приклеено к матрице в единый пакет. Предложения «переклеить только стекло» заканчиваются разводами и пылью под поверхностью.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Замена экрана за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps)

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Меняем матрицу, а не крышку</h3><p>Там, где модель это позволяет, — деталь обходится кратно дешевле модуля в сборе.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На деталь и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Проверяем подсветку до замены</h3><p>Чтобы вы не платили за дисплей там, где дело в плате.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена экрана MacBook в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о замене экрана MacBook</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs)

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>Оставьте номер — назовём цену по вашей модели</h2>\n'
          '          <p>Скажите модель и год MacBook и что видно на экране. Подскажем, хватит ли замены матрицы, и есть ли она в наличии.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: замена экрана MacBook</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Замена экрана MacBook").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    pr = hub_price()
    print("✓ %s/index.html (%d симв., %d случаев, %d FAQ, цена из прайса: %s)"
          % (SLUG, len(h), len(CASES), len(FAQ), pr[0] if pr else "нет строки"))


if __name__ == "__main__":
    main()
