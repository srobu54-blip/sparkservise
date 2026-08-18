#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Ремонт Face ID на iPhone» — глубина-2:
/remont-iphone/face-id/. Под неё уже есть статья блога «Не работает Face ID»,
которая до сих пор вела человека в общий хаб: информационный трафик приходил,
а коммерческой страницы под него не было.

Только модели с TrueDepth (31 из 38) — у iPhone 7/8/SE стоит Touch ID, и
models_for() отбрасывает их сам по сентинелу [0,0]. Каркас — assemble.py."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D
import assemble_model as MOD          # models_for — единственный источник ценовых таблиц

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-iphone/face-id"
NAME = "Ремонт Face ID на iPhone"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

# Цены берём из TIERS, а не литералами: помодельный список здесь уже ломался на
# трёх других лендингах — цену правили в админке, страница оставалась со старой.
MODELS = MOD.models_for("Face ID")
def grn(n): return format(n, ",d").replace(",", " ")

# Вилка для ПРОЗЫ считается из прайса, а не пишется литералом. check_prices
# сторожит только ячейки с data-svc — числа в FAQ и SEO проходят мимо гейта и
# тихо расходятся с прайсом при первой же правке в админке.
LO, HI = min(m[2] for m in MODELS), max(m[3] for m in MODELS)
RANGE = "от %s до %s ₴" % (grn(LO), grn(HI))

# ── признаки ──
SIGNS = [
    ("camera", "«Face ID недоступен. Повторите настройку позже»",
     "Самая частая надпись. Появляется, когда система перестала видеть точечный проектор или инфракрасную камеру — обычно из-за повреждённого шлейфа."),
    ("screen", "Перестал работать после замены экрана",
     "Шлейф Face ID проходит под верхним динамиком и легко пережимается при неаккуратной сборке. Если Face ID отвалился сразу после ремонта в другом сервисе — чаще всего дело в этом."),
    ("water", "Пропал после воды",
     "Влага окисляет контакты шлейфа TrueDepth. Чем раньше принесёте, тем больше шансов восстановить — окисление продолжает разъедать дорожки и после высыхания."),
    ("board", "«Не удалось активировать Face ID»",
     "Настройка не проходит до конца, сканирование зависает. Диагностика показывает, какой из трёх модулей TrueDepth не отвечает."),
    ("wrench", "Face ID отвалился после падения",
     "Удар сдвигает или надламывает шлейф внутри корпуса. Внешне телефон целый, а сканирование лица уже не запускается."),
    ("button", "Работает через раз",
     "Разблокировка срабатывает не всегда, чаще в темноте или под углом. Обычно это подсевший инфракрасный модуль, а не настройка — переобучение лица тут не помогает."),
]

STEPS = [
    ("Бесплатная диагностика", "Проверяем все три модуля TrueDepth — точечный проектор, инфракрасную камеру и подсветку — и определяем, какой именно не отвечает.", ""),
    ("Говорим честно: восстановимо или нет", "Если повреждён сам точечный проектор, Face ID не вернуть никакими деталями — скажем это сразу и бесплатно, а не после того, как вы оплатите работу.", ""),
    ("Чиним шлейф или переносим модули", "Если повреждён только шлейф — меняем его, это 30-60 минут. Если задеты сами модули TrueDepth, переносим ваши родные компоненты на исправный шлейф под микроскопом: это дольше, зато сохраняется привязка к плате.", "от 30 минут"),
    ("Проверка и гарантия", "Настраиваем Face ID заново при вас, проверяем разблокировку и Apple Pay. Гарантия 12 месяцев на работу.", "12 месяцев"),
]

FAQ = [
    ("Почему нельзя просто поставить новый модуль Face ID?",
     "Точечный проектор привязан к материнской плате вашего iPhone на уровне Secure Enclave — эта пара формируется на заводе. Модуль, снятый с другого телефона, система не примет: Face ID останется недоступен, даже если деталь полностью исправна. Поэтому Face ID не «меняют», а восстанавливают — переносят ваши родные компоненты на новый шлейф под микроскопом."),
    ("Сколько стоит ремонт Face ID?",
     "Зависит от модели — %s, точные цены по моделям в таблице выше. Диагностика бесплатная, и стоимость мы называем до начала работ. Если восстановить нельзя, вы ничего не платите." % RANGE),
    ("Face ID перестал работать после замены экрана в другом сервисе. Это лечится?",
     "Чаще всего да, и это самый частый случай из всех. Шлейф Face ID проходит под верхним динамиком, его легко пережать или надорвать при снятии дисплея. Если повреждён шлейф, а сами модули целы — восстанавливаем. Приходите на бесплатную диагностику, посмотрим, что именно задели."),
    ("Всегда ли получается восстановить Face ID?",
     "Нет, и мы говорим об этом прямо. Если умер сам точечный проектор — Face ID не вернуть, это ограничение архитектуры Apple, а не нашей мастерской. В таких случаях мы предупреждаем на диагностике, до оплаты. Фронтальная камера при этом обычно продолжает работать, её можно починить отдельно."),
    ("Сколько времени занимает ремонт?",
     "Зависит от того, что повреждено. Самый частый случай — надорванный шлейф после чужой замены экрана: это 30-60 минут при вас. Если задеты сами модули TrueDepth и нужен перенос компонентов под микроскопом, работа занимает дольше — точный срок назовём на диагностике, до того как вы оставите телефон."),
    ("Будет ли работать Apple Pay после ремонта?",
     "Да. Apple Pay использует ту же биометрию, и если Face ID восстановлен корректно, оплата работает как раньше. Мы проверяем это при выдаче телефона вместе с разблокировкой."),
    ("У меня iPhone 8 / SE — почему его нет в таблице?",
     "На iPhone 7, 8 и всех SE стоит не Face ID, а Touch ID — сканер отпечатка в кнопке «Домой». Это другая система и другой ремонт. Напишите нам, что именно не работает, подскажем по вашей модели."),
    ("Какая гарантия на ремонт Face ID?",
     "12 месяцев на работу мастера — как на остальные наши ремонты. Если после ремонта Face ID перестанет работать не по вашей вине, разбираемся бесплатно."),
]

SEO = [
    "Face ID — система распознавания лица, которая работает на iPhone начиная с iPhone X. За неё отвечает блок TrueDepth в верхней части экрана: точечный проектор рисует на лице сетку из тридцати тысяч невидимых точек, инфракрасная камера считывает её, а подсветка позволяет всему этому работать в темноте. Если хотя бы один из трёх модулей перестаёт отвечать, iPhone пишет «Face ID недоступен» и предлагает повторить настройку позже — но настройка не помогает, потому что проблема не в ней.",
    "Главное, что нужно знать про этот ремонт: Face ID нельзя починить заменой детали. Точечный проектор привязан к материнской плате на уровне Secure Enclave, и модуль с другого iPhone система не примет — это защита от подмены биометрии, и обойти её нельзя. Поэтому Face ID восстанавливают на микропайке: ваши родные компоненты переносят на исправный шлейф под микроскопом. Если сервис говорит, что «поставит новый Face ID», — это либо замена фронтальной камеры под видом Face ID, либо непонимание того, как устроена привязка. Ни то ни другое разблокировку лицом не вернёт.",
    "В SPARK диагностику Face ID делают бесплатно и до оплаты говорят, восстановимо ли именно ваше повреждение. Самый частый случай — Face ID пропал после замены экрана в другом сервисе: шлейф проходит под верхним динамиком и легко травмируется при разборке, а сами модули при этом целы. Такое чинится. Если же умер сам точечный проектор, мы скажем об этом прямо, а не возьмём деньги за заведомо безнадёжную работу. Приходите на улицу Академика Королёва, 23 в Одессе — ежедневно с 10:00 до 19:00.",
]

RELATED = [
    ("../../remont-iphone/", "Ремонт iPhone — все услуги"),
    ("../zamena-ekrana/", "Замена экрана iPhone"),
    ("../../diagnostika/", "Бесплатная диагностика"),
    ("../../blog/ne-rabotaet-face-id-iphone/", "Статья: почему не работает Face ID"),
]

FORM_OPTS = ["Не работает Face ID", "«Face ID недоступен»", "Пропал после замены экрана",
             "Пропал после воды", "Работает через раз", "Другое (опишу в разговоре)"]

def hero_svg():
    grad = D._GRAD % {"p": "fid"}
    dots = "".join(
        '<circle cx="%g" cy="%g" r="1.7" fill="#E11D2A" opacity="%.2f"/>' % (
            96 + (i % 7) * 18, 96 + (i // 7) * 18, 0.30 + 0.09 * ((i * 5) % 8))
        for i in range(35))
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ремонт Face ID на iPhone">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#fidf)"/>'
      '<rect x="40" y="40" width="220" height="280" rx="18" fill="#12151b"/>'
      '<rect x="112" y="46" width="76" height="15" rx="8" fill="#0b0d11"/>'
      + dots +
      '<path d="M108 118v-14a8 8 0 018-8h14" fill="none" stroke="#878d99" stroke-width="2.6" stroke-linecap="round"/>'
      '<path d="M192 118v-14a8 8 0 00-8-8h-14" fill="none" stroke="#878d99" stroke-width="2.6" stroke-linecap="round"/>'
      '<path d="M108 214v14a8 8 0 008 8h14" fill="none" stroke="#878d99" stroke-width="2.6" stroke-linecap="round"/>'
      '<path d="M192 214v14a8 8 0 01-8 8h-14" fill="none" stroke="#878d99" stroke-width="2.6" stroke-linecap="round"/>'
      + D._check(214, 250, 20) +
      '<text x="150" y="290" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Face ID восстановлен</text>'
      '<text x="150" y="312" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · микропайка</text>'
      '</svg>\n      </div>')

def build():
    lo_min = min(m[2] for m in MODELS)
    title = "Ремонт Face ID на iPhone в Одессе от %s ₴ | SPARK" % grn(lo_min)
    desc = ("Не работает Face ID на iPhone? SPARK в Одессе восстанавливает TrueDepth "
            "с сохранением привязки к плате. Бесплатная диагностика, честный ответ до оплаты.")
    kw = ("не работает face id, ремонт face id, face id недоступен, восстановление face id, "
          "face id не работает после замены экрана, ремонт face id одесса, face id iphone одесса, "
          "не удалось активировать face id, ремонт truedepth")
    h1 = "Ремонт Face ID на iPhone в Одессе"
    sub = ("Восстанавливаем распознавание лица на iPhone X — iPhone 17: переносим ваши родные модули "
           "TrueDepth на исправный шлейф под микроскопом, с сохранением привязки к плате. "
           "Диагностика бесплатная — до оплаты честно говорим, восстановимо ваше повреждение или нет.")

    service = {"@context":"https://schema.org","@type":"Service","@id":CANON+"#service",
        "name":"Ремонт Face ID на iPhone в Одессе","serviceType":"Ремонт Face ID на iPhone",
        "description":desc,"areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "offers":{"@type":"Offer","priceCurrency":"UAH","price":str(lo_min),"priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo_min),"priceCurrency":"UAH"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
        {"@type":"ListItem","position":3,"name":"Ремонт Face ID","item":CANON}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Ремонт Face ID на iPhone в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n<script defer src="/price-live.js"></script>\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>Ремонт Face ID</span></div>\n  </div>\n\n'

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>8 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>🔬 <b>от %s ₴ · микропайка</b></span>\n        </div>\n' % grn(lo_min)
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic,t,d in SIGNS)
    p += '  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">С чем приходят</span>\n        <h2>Как проявляется поломка Face ID</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards

    p += ('  <section class="sec sec-bg" id="how">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как это устроено</span>\n        <h2>Почему Face ID нельзя просто заменить</h2>\n'
          '        <p class="lead-p">Это главное, что стоит понимать до того, как выбирать сервис. Face ID защищён от подмены на уровне железа, и обойти эту защиту нельзя ни в одной мастерской мира.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Точечный проектор привязан к вашей плате.</b> Пара «модуль — Secure Enclave» формируется на заводе. Деталь с другого iPhone система не примет, даже полностью исправную: для неё это попытка подменить биометрию.</span></li>'
          '<li><span class="ck">✓</span><span><b>Поэтому Face ID восстанавливают, а не меняют.</b> Ваши родные компоненты переносим на исправный шлейф под микроскопом — привязка сохраняется, потому что физически это те же чипы.</span></li>'
          '<li><span class="ck">✓</span><span><b>«Поставим новый Face ID» — так не бывает.</b> Под этим обычно имеют в виду замену фронтальной камеры: она действительно меняется, но к распознаванию лица отношения не имеет. Разблокировка после такого не заработает.</span></li>'
          '<li><span class="ck">✓</span><span><b>Иногда восстановить нельзя.</b> Если умер сам точечный проектор — Face ID не вернуть. Мы говорим это на бесплатной диагностике, до оплаты, а не после.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    rows = "\n            ".join(
        '<tr><td class="svc-name"><a href="../../remont-iphone/%s/">Face ID %s</a></td><td class="pr" data-price-label="%s" data-price-dash="en" data-svc="Face ID">%s ₴</td><td class="time">30-60 мин</td></tr>' % (
            slug, esc(label), esc(label), (grn(lo) if lo==hi else grn(lo)+" – "+grn(hi))) for label,slug,lo,hi in MODELS)
    p += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость ремонта Face ID по моделям</h2>\n'
          '        <p class="lead-p">Цены ориентировочные, точную назовём после бесплатной диагностики — до неё никто не скажет, какой из модулей повреждён. Нижняя граница вилки — замена повреждённого шлейфа, она укладывается в 30-60 минут; верхняя — перенос модулей под микроскопом, это дольше. Нажмите на модель: там все виды ремонта. В таблице только iPhone с Face ID — на iPhone 7, 8 и SE стоит Touch ID, это другая система.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Модель</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in STEPS)
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Ремонт Face ID за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Честный ответ до оплаты</h3><p>Если Face ID не восстановить, говорим это на бесплатной диагностике — вы ничего не платите.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Привязка сохраняется</h3><p>Переносим ваши родные модули, а не ставим чужие — иначе Face ID не заработает в принципе.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Своя микропайка</h3><p>Работа под микроскопом в мастерской, без отправки телефона на сторону.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in RELATED)
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">Ремонт Face ID на iPhone в Одессе — сервис SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel)

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(FAQ))
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о ремонте Face ID</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Оставьте номер — скажем, восстановим ли ваш Face ID</h2>\n          <p>Опишите, что случилось и после чего пропало распознавание. Перезвоним за 15 минут и подскажем, стоит ли везти телефон.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: ремонт Face ID</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт Face ID на iPhone").replace("{{MODALOPTIONS}}", opts)
    return p

def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d моделей, %d FAQ)" % (SLUG, len(h), len(MODELS), len(FAQ)))

if __name__ == "__main__":
    main()
