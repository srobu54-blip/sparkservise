#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «iPhone не заряжается» — глубина-2:
/remont-iphone/ne-zaryazhaetsya/. Третья страница волны 1: под тему есть статья
блога «iPhone не заряжается», которая вела человека в общий хаб.

Слаг совпадает с макбучным (/remont-macbook/ne-zaryazhaetsya/) намеренно —
одинаковая проблема, одинаковый URL-паттерн. Каркас — assemble.py."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D
import assemble_model as MOD          # models_for — единственный источник ценовых таблиц

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-iphone/ne-zaryazhaetsya"
NAME = "iPhone не заряжается"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

MODELS = MOD.models_for("Не заряжается (разъём)")
def grn(n): return format(n, ",d").replace(",", " ")

# Вилка для прозы — из прайса. Литерал здесь уже соврал: FAQ обещал потолок
# 2 100 ₴ «на iPhone 17 Pro Max», хотя у 16 Pro Max и 17 Air в прайсе 5 000 ₴.
LO, HI = min(m[2] for m in MODELS), max(m[3] for m in MODELS)
RANGE = "от %s до %s ₴" % (grn(LO), grn(HI))

SIGNS = [
    ("charging", "Не реагирует на кабель совсем",
     "Экран не загорается, значка молнии нет. Прежде чем думать о ремонте, стоит исключить кабель и адаптер — на них приходится заметная доля обращений."),
    ("cleaning", "Заряжается, только если держать под углом",
     "Классический признак забитого порта: спрессованная пыль и ворс из кармана не дают штекеру дойти до контактов. Самый дешёвый из всех сценариев."),
    ("wrench", "«Этот аксессуар не поддерживается»",
     "Телефон видит кабель, но отказывается с ним работать. Причина бывает и в кабеле, и в окисленном разъёме, и в контроллере питания — определяется на диагностике."),
    ("battery", "Заряд стоит на месте или падает при зарядке",
     "Процент не растёт, хотя молния горит. Обычно это изношенный аккумулятор или контроллер, который не пропускает ток."),
    ("water", "Перестал заряжаться после воды",
     "Разъём заливает первым — он снизу. Окисление разъедает контакты и идёт дальше по плате, поэтому тянуть тут дороже всего."),
    ("board", "Греется при зарядке или заряжается очень медленно",
     "Тёплый корпус и часы вместо получаса — признак проблем в цепи питания. Это уже плата, а не разъём."),
]

STEPS = [
    ("Сначала исключаем ерунду", "На диагностике первым делом проверяем ваш кабель и адаптер на заведомо исправном телефоне и осматриваем порт. Если дело в кабеле или забитом разъёме — скажем сразу, это самый дешёвый исход.", ""),
    ("Смотрим, что именно не работает", "Замеряем ток зарядки и проверяем цепь: сам разъём, шлейф, контроллер питания, аккумулятор. Диагностика бесплатная и делается при вас.", ""),
    ("Меняем разъём или чиним цепь", "Если изношен порт — меняем нижний шлейф в сборе. Если проблема глубже, в контроллере питания, — это микропайка, и мы скажем об этом до начала работ.", "30-50 мин"),
    ("Проверка и гарантия", "Проверяем зарядку проводом и беспроводную, замеряем ток. Гарантия 12 месяцев на работу и деталь.", "12 месяцев"),
]

FAQ = [
    ("iPhone не заряжается. С чего начать?",
     "С кабеля и розетки — это звучит банально, но именно кабель отказывает чаще всего. Возьмите другой шнур и другой адаптер, желательно оригинальные. Если не помогло, посмотрите в разъём при свете: часто там спрессованный ворс из кармана, из-за которого штекер не доходит до контактов. Если и это не причина — приходите, диагностика бесплатная."),
    ("Сколько стоит замена разъёма зарядки?",
     "Зависит от модели — %s, цены по каждой в таблице выше. По нескольким моделям цена заметно выше остальных, это не опечатка. Точную стоимость называем после бесплатной диагностики: иногда разъём менять не нужно вовсе." % RANGE),
    ("Правда ли, что часто дело просто в грязи в разъёме?",
     "Да, это одна из самых частых причин. Порт весь день собирает ворс из кармана, тот спрессовывается в плотную пробку, и кабель перестаёт доставать до контактов. Внешне разъём выглядит пустым. Мы смотрим порт на диагностике — если причина в этом, вы узнаете об этом до того, как что-то оплатите."),
    ("Сколько занимает замена разъёма?",
     "Обычно 30-50 минут, при вас. Если выяснится, что проблема в контроллере питания на плате, — это микропайка и работа дольше. Точный срок называем после диагностики, до начала работ."),
    ("iPhone заряжается, только если держать кабель под углом. Что это?",
     "Разболтанный или изношенный разъём: контакты уже не держат штекер плотно. Со временем перестанет заряжаться совсем, а привычка «подпирать» кабель доламывает порт окончательно. Меняется нижний шлейф в сборе."),
    ("Может, дело в аккумуляторе, а не в разъёме?",
     "Бывает и так. Если заряд не растёт, телефон выключается на 30-40% или греется при зарядке, причина чаще в изношенной батарее. На диагностике мы смотрим и то и другое, чтобы не менять исправную деталь — при необходимости предложим замену аккумулятора."),
    ("Телефон перестал заряжаться после воды. Это чинится?",
     "Часто да, но это уже не замена разъёма, а работа с окислением: порт заливает первым, потому что он снизу. Чем раньше принесёте, тем выше шанс обойтись чисткой — окисел продолжает разъедать плату и после высыхания."),
    ("Какая гарантия на замену разъёма зарядки?",
     "12 месяцев на деталь и работу мастера. Оплата по факту, без предоплаты: сначала телефон заряжается у вас на глазах, потом расчёт."),
]

SEO = [
    "«iPhone не заряжается» — формулировка, за которой прячутся минимум пять разных причин, и стоят они очень по-разному. Самая частая и самая дешёвая — забитый разъём: карманный ворс спрессовывается в плотную пробку, и кабель просто не доходит до контактов. Дальше по частоте идут сам кабель и адаптер, изношенный порт, посаженный аккумулятор и, реже всего, контроллер питания на плате. Поэтому первое, что делает нормальный сервис, — не меняет разъём, а выясняет, нужен ли он вообще.",
    "Разъём меняется нижним шлейфом в сборе: на iPhone это единый модуль с портом, микрофоном и антенной. Работа занимает 30-50 минут и делается при вас. Признак, по которому порт пора менять, знают все, кто с этим сталкивался: телефон заряжается, только если держать кабель под определённым углом или подпирать его чем-нибудь. Так ходить не стоит — расшатанный разъём доламывается быстро, а вместе с ним страдают контакты на плате.",
    "В SPARK диагностика бесплатная, и мы сначала исключаем кабель и загрязнение — это честнее и дешевле для вас, чем сразу продавать замену детали. Если разъём действительно изношен, меняем его с гарантией 12 месяцев, оплата по факту. Если телефон перестал заряжаться после воды, приезжайте в тот же день: порт заливает первым, и окисление идёт дальше по плате. Мы в Одессе на улице Академика Королёва, 23, ежедневно с 10:00 до 19:00.",
]

RELATED = [
    ("../../remont-iphone/", "Ремонт iPhone — все услуги"),
    ("../../blog/iphone-ne-zaryazhaetsya/", "Статья: почему iPhone не заряжается"),
    ("../zamena-akkumulyatora/", "Замена аккумулятора iPhone"),
    ("../posle-vody/", "Ремонт iPhone после воды"),
]

FORM_OPTS = ["iPhone не заряжается", "Заряжается только под углом", "«Аксессуар не поддерживается»",
             "Не заряжается после воды", "Греется при зарядке", "Другое (опишу в разговоре)"]

def hero_svg():
    grad = D._GRAD % {"p": "chg"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ремонт разъёма зарядки iPhone">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#chgf)"/>'
      '<rect x="40" y="40" width="220" height="280" rx="18" fill="#12151b"/>'
      '<rect x="86" y="96" width="128" height="66" rx="12" fill="none" stroke="#878d99" stroke-width="2.6"/>'
      '<rect x="214" y="118" width="9" height="22" rx="3" fill="#878d99"/>'
      '<rect x="94" y="104" width="86" height="50" rx="7" fill="#1FAE5A" opacity=".22"/>'
      '<path d="M152 176l-22 42h20l-6 34 30-46h-21z" fill="#E11D2A"/>'
      '<rect x="126" y="252" width="48" height="13" rx="6" fill="none" stroke="#878d99" stroke-width="2.4"/>'
      '<line x1="150" y1="252" x2="150" y2="238" stroke="#878d99" stroke-width="2.4" stroke-linecap="round"/>'
      + D._check(214, 250, 20) +
      '<text x="150" y="296" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Зарядка работает</text>'
      '<text x="150" y="318" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')

def build():
    lo_min = min(m[2] for m in MODELS)
    # Заголовок ведём от коммерческой формулировки, а не от «iPhone не заряжается»:
    # этой фразой открывается статья blog/iphone-ne-zaryazhaetsya/, у неё больше
    # входящих ссылок и истории, и в лобовом столкновении Google выберет её.
    # Статье остаётся информационный интент, лендингу — транзакционный.
    title = "Ремонт разъёма зарядки iPhone в Одессе от %s ₴ | SPARK" % grn(lo_min)
    desc = ("iPhone не заряжается или заряжается под углом? SPARK в Одессе: проверим кабель "
            "и порт бесплатно, заменим разъём за 30-50 минут. Гарантия 12 месяцев.")
    kw = ("iphone не заряжается, замена разъёма зарядки iphone, не заряжается айфон одесса, "
          "ремонт разъёма зарядки iphone, айфон не видит зарядку, аксессуар не поддерживается, "
          "замена нижнего шлейфа iphone, чистка разъёма зарядки iphone")
    h1 = "Ремонт разъёма зарядки iPhone в Одессе — если не заряжается"
    sub = ("Меняем изношенный разъём зарядки нижним шлейфом в сборе за 30-50 минут при вас. "
           "Но сначала бесплатно исключаем кабель и загрязнение порта: очень часто телефон исправен, "
           "и менять в нём нечего.")

    service = {"@context":"https://schema.org","@type":"Service","@id":CANON+"#service",
        "name":"Ремонт разъёма зарядки iPhone в Одессе","serviceType":"Ремонт разъёма зарядки iPhone",
        "description":desc,"areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "offers":{"@type":"Offer","priceCurrency":"UAH","price":str(lo_min),"priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo_min),"priceCurrency":"UAH"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
        {"@type":"ListItem","position":3,"name":"Не заряжается","item":CANON}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Ремонт разъёма зарядки iPhone в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n<script defer src="/price-live.js"></script>\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>Не заряжается</span></div>\n  </div>\n\n'

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>8 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>🔌 <b>от %s ₴ · 30-50 минут</b></span>\n        </div>\n' % grn(lo_min)
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic,t,d in SIGNS)
    p += '  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">С чем приходят</span>\n        <h2>Как проявляется проблема с зарядкой</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards

    p += ('  <section class="sec sec-bg" id="how">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Прежде чем платить</span>\n        <h2>Что проверить дома за пять минут</h2>\n'
          '        <p class="lead-p">Часть обращений заканчивается тем, что менять в телефоне нечего. Пройдите этот список до визита — возможно, ремонт вам не нужен.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Другой кабель и другой адаптер.</b> Кабель — самая частая причина из всех. Проверьте заведомо рабочим, а не запасным из ящика: он мог отказать так же.</span></li>'
          '<li><span class="ck">✓</span><span><b>Посветите в разъём.</b> Спрессованный карманный ворс выглядит как «пусто», а на деле не даёт штекеру дойти до контактов. Если телефон заряжается, когда кабель прижимаешь, — почти наверняка это.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не ковыряйте порт железом.</b> Иголка и скрепка гнут и рвут контакты — после такого дешёвая чистка превращается в замену шлейфа.</span></li>'
          '<li><span class="ck">✓</span><span><b>Заряд не растёт, хотя молния горит?</b> Тогда дело, скорее всего, не в разъёме, а в <a href="../zamena-akkumulyatora/">аккумуляторе</a> или контроллере питания.</span></li>'
          '<li><span class="ck">✓</span><span><b>Перестал заряжаться после воды?</b> Это отдельный случай и другая срочность — смотрите <a href="../posle-vody/">ремонт после воды</a>, там счёт идёт на часы.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    rows = "\n            ".join(
        '<tr><td class="svc-name"><a href="../../remont-iphone/%s/">%s не заряжается</a></td><td class="pr" data-price-label="%s" data-price-dash="en" data-svc="Не заряжается (разъём)">%s ₴</td><td class="time">30-50 мин</td></tr>' % (
            slug, esc(label), esc(label), (grn(lo) if lo==hi else grn(lo)+" – "+grn(hi))) for label,slug,lo,hi in MODELS)
    p += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость замены разъёма зарядки по моделям</h2>\n'
          '        <p class="lead-p">В таблице — замена разъёма нижним шлейфом в сборе. Если причина окажется в кабеле, загрязнении порта или аккумуляторе, стоимость будет другой, и мы назовём её на бесплатной диагностике. По нескольким моделям цена заметно выше остальных — это не опечатка, а особенность конкретных аппаратов; на диагностике объясним, из чего складывается сумма именно в вашем случае. Нажмите на модель — там все виды ремонта.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Модель</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in STEPS)
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Ремонт зарядки за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Сначала исключаем лишнее</h3><p>Проверяем кабель и порт до того, как предлагать замену детали. Часто менять нечего.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На деталь и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>30-50 минут при вас</h3><p>Разъём меняется нижним шлейфом в сборе — уходите с работающей зарядкой.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in RELATED)
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">Ремонт разъёма зарядки iPhone в Одессе — сервис SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel)

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(FAQ))
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о ремонте зарядки</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Оставьте номер — подскажем, нужен ли вообще ремонт</h2>\n          <p>Опишите, как ведёт себя зарядка. Часто причину видно уже по разговору, и ехать никуда не придётся.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: ремонт зарядки</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт разъёма зарядки iPhone").replace("{{MODALOPTIONS}}", opts)
    return p

def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d моделей, %d FAQ)" % (SLUG, len(h), len(MODELS), len(FAQ)))

if __name__ == "__main__":
    main()
