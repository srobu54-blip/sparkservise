#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Ремонт iPhone после воды» — глубина-2:
/remont-iphone/posle-vody/. Под тему уже есть статья блога «iPhone упал в воду»,
которая вела человека в общий хаб — информационный трафик приходил, коммерческой
страницы под него не было.

Цены по всем 38 моделям. Каркас — assemble.py."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D
import assemble_model as MOD          # models_for — единственный источник ценовых таблиц

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-iphone/posle-vody"
NAME = "Ремонт iPhone после воды"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

MODELS = MOD.models_for("После воды")
def grn(n): return format(n, ",d").replace(",", " ")

# Вилка для прозы — из прайса, не литералом (см. комментарий в assemble_faceid.py).
LO, HI = min(m[2] for m in MODELS), max(m[3] for m in MODELS)
RANGE = "от %s до %s ₴" % (grn(LO), grn(HI))

# ── признаки ──
SIGNS = [
    ("water", "Упал в воду и не включается",
     "Раковина, унитаз, море, бассейн. Не включайте и не ставьте на зарядку — ток через мокрую плату дожигает то, что ещё живо."),
    ("board", "Включился, но ведёт себя странно",
     "Сам перезагружается, глючит сенсор, пропадает сеть. Значит, вода уже внутри и окисление пошло — телефон работает на остатках."),
    ("battery", "Быстро садится или греется после залития",
     "Влага замыкает цепи питания. Аккумулятор разряжается за пару часов, корпус тёплый даже в покое."),
    ("mic", "Пропал звук, микрофон или динамик",
     "Вода чаще всего добирается до нижних шлейфов первой. Собеседник вас не слышит, динамик хрипит или молчит."),
    ("camera", "Запотела камера или экран",
     "Конденсат под стеклом — верный признак, что герметичность нарушена. Даже если телефон работает, влага внутри осталась."),
    ("cleaning", "Пролили чай, кофе, сладкую газировку",
     "Хуже чистой воды: сахар и кислота разъедают дорожки быстрее и оставляют липкий налёт, который сам не высохнет."),
]

STEPS = [
    ("Привозите как есть — не включая", "Чем раньше, тем дешевле ремонт. Не сушите феном, не грейте на батарее и не ставьте на зарядку: это самые частые причины, по которым телефон становится неремонтопригодным.", ""),
    ("Разбираем и смотрим плату под микроскопом", "Снимаем аккумулятор, чтобы обесточить схему, и оцениваем, куда дошла влага и насколько разъело контакты. Диагностика бесплатная.", ""),
    ("Ультразвуковая чистка платы", "Плата отмывается в ультразвуковой ванне — так удаляется окисел из-под чипов и разъёмов, куда не добраться кистью. Затем сушим и проверяем цепи.", "от 2 часов"),
    ("Восстанавливаем то, что пострадало", "Меняем сгоревшие элементы, восстанавливаем дорожки, при необходимости — шлейфы и модули. Называем цену до работ, платите по факту.", "1-3 дня"),
]

FAQ = [
    ("Айфон упал в воду. Что делать прямо сейчас?",
     "Выключите телефон и больше не включайте. Не ставьте на зарядку, не сушите феном и не кладите на батарею — от нагрева хуже. Достаньте сим-лоток, чтобы вода вышла, и везите в сервис как есть. Каждый час работает против вас: окисление продолжается, пока плата мокрая."),
    ("Правда, что нужно положить в рис?",
     "Нет, это самый живучий и самый вредный совет. Рис не вытягивает влагу из-под чипов — она остаётся внутри и продолжает разъедать плату, а рисовая пыль забивается в разъёмы. Пока телефон лежит в рисе, вы просто теряете время, за которое ремонт из чистки превращается в замену элементов."),
    ("Сколько стоит ремонт iPhone после воды?",
     "Зависит от модели и от того, куда дошла вода: %s, цены по моделям в таблице выше. Разброс большой, потому что случаи разные: одному телефону хватит промывки платы, другому нужна замена сгоревших элементов. Точную сумму называем после бесплатной диагностики, до начала работ." % RANGE),
    ("Мой iPhone влагозащищённый, ему же ничего не будет?",
     "Влагозащита — не гидроизоляция. Заводские уплотнители стареют, а после любой разборки герметичность уже не та, что с завода. Apple прямо указывает, что повреждения от жидкости не покрываются гарантией. На практике мы регулярно видим утопленные iPhone 14 и 15 — влагозащита снижает риск, но не отменяет его."),
    ("Телефон высох и работает. Всё в порядке?",
     "Не обязательно. Вода уходит, а окисел остаётся и продолжает разъедать дорожки — телефон может отработать неделю или месяц, а потом отказать уже насовсем. Если он побывал в воде, плату лучше промыть, пока это ещё чистка, а не восстановление."),
    ("Морская вода опаснее обычной?",
     "Да, заметно. Соль проводит ток лучше пресной воды и разъедает контакты быстрее. То же с чаем, кофе и сладкой газировкой: сахар и кислота оставляют налёт, который не высыхает. Такие случаи стоит везти в сервис в тот же день."),
    ("Данные сохранятся?",
     "Мы работаем с телефоном так, чтобы сохранить данные, и это одна из причин везти его сразу. Если плата уже не запускается, есть отдельная услуга — восстановление данных. Гарантировать сохранность на утопленном аппарате заранее не может никто, и обещать этого мы не будем."),
    ("Какая гарантия на ремонт после воды?",
     "12 месяцев на выполненные работы. Оговорка тут честная и важная: гарантия распространяется на то, что мы сделали, — заменённые элементы и восстановленные цепи. Отвечать за всю плату, по которой прошла вода, не может ни один сервис: окисел иногда проявляет себя там, где при ремонте всё было чисто. Об этом мы предупреждаем сразу, а не постфактум."),
]

SEO = [
    "Вода — самая коварная поломка iPhone, потому что она не заканчивается в момент падения. Жидкость попадает под экранирующие крышки и микросхемы, и там начинается окисление, которое продолжается и после того, как телефон внешне высох. Поэтому аппарат нередко работает день, неделю или месяц, а потом отказывает окончательно — и ремонт, который стоил бы промывки платы, превращается в замену элементов или в замену платы целиком.",
    "Два действия делают ремонт дороже почти всегда: включить телефон и поставить его на зарядку. Ток через влажную плату замыкает соседние цепи и выжигает то, что залитие ещё не тронуло. Третье — сушка феном или на батарее: горячий воздух гонит влагу глубже под чипы и деформирует проклейку. Рис не работает совсем: он не вытягивает воду из-под микросхем, зато забивает разъёмы пылью. Правильный порядок простой — выключить, достать сим-лоток, не включать и везти в сервис как есть.",
    "В SPARK утопленный iPhone разбирают, обесточивают и промывают плату в ультразвуковой ванне — так окисел уходит из-под чипов и разъёмов, куда не добраться иначе. Дальше под микроскопом восстанавливают то, что пострадало: дорожки, элементы питания, шлейфы. Диагностика бесплатная, цену называем до работ. Мы в Одессе на улице Академика Королёва, 23, рядом с Киевским рынком, ежедневно с 10:00 до 19:00 — если телефон побывал в воде сегодня, приезжайте сегодня.",
]

RELATED = [
    ("../../remont-iphone/", "Ремонт iPhone — все услуги"),
    ("../../blog/iphone-upal-v-vodu-chto-delat/", "Статья: iPhone упал в воду — что делать"),
    ("../../vosstanovlenie-dannyh/", "Восстановление данных"),
    ("../../diagnostika/", "Бесплатная диагностика"),
]

FORM_OPTS = ["iPhone упал в воду", "Залил чаем / кофе / газировкой", "После воды не включается",
             "Работает, но глючит после залития", "Пропал звук или микрофон", "Другое (опишу в разговоре)"]

def hero_svg():
    grad = D._GRAD % {"p": "wtr"}
    drops = "".join(
        '<circle cx="%g" cy="%g" r="%g" fill="#4aa3ff" opacity="%.2f"/>' % (
            78 + (i % 5) * 26, 84 + (i // 5) * 22, 2.2 + (i % 3) * 0.9, 0.22 + 0.07 * (i % 5))
        for i in range(20))
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ремонт iPhone после воды">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#wtrf)"/>'
      '<rect x="40" y="40" width="220" height="280" rx="18" fill="#12151b"/>'
      + drops +
      '<path d="M150 168c0 0-26 28-26 44a26 26 0 0052 0c0-16-26-44-26-44z" fill="none" stroke="#4aa3ff" stroke-width="3" stroke-linejoin="round"/>'
      '<path d="M138 214a12 12 0 0010 10" fill="none" stroke="#4aa3ff" stroke-width="2.2" stroke-linecap="round"/>'
      + D._check(214, 250, 20) +
      '<text x="150" y="290" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Плата отмыта и жива</text>'
      '<text x="150" y="312" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · ультразвук</text>'
      '</svg>\n      </div>')

def build():
    lo_min = min(m[2] for m in MODELS)
    title = "Ремонт iPhone после воды в Одессе от %s ₴ | SPARK" % grn(lo_min)
    desc = ("Утопили iPhone? SPARK в Одессе: ультразвуковая чистка платы, восстановление под "
            "микроскопом. Не включайте и не сушите феном. Бесплатная диагностика.")
    kw = ("iphone упал в воду, ремонт iphone после воды, айфон утонул, залил айфон, "
          "чистка платы iphone, айфон после воды не включается одесса, ремонт после залития iphone, "
          "утопил айфон что делать, ультразвуковая чистка платы iphone")
    h1 = "Ремонт iPhone после воды в Одессе"
    sub = ("Промываем плату в ультразвуковой ванне и восстанавливаем повреждённые цепи под микроскопом — "
           "от лёгкого залития до аппарата, который уже не включается. "
           "Не включайте телефон и не сушите феном: этим ремонт дорожает сильнее всего.")

    service = {"@context":"https://schema.org","@type":"Service","@id":CANON+"#service",
        "name":"Ремонт iPhone после воды в Одессе","serviceType":"Ремонт iPhone после попадания влаги",
        "description":desc,"areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "offers":{"@type":"Offer","priceCurrency":"UAH","price":str(lo_min),"priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo_min),"priceCurrency":"UAH"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
        {"@type":"ListItem","position":3,"name":"Ремонт после воды","item":CANON}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Ремонт iPhone после воды в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n<script defer src="/price-live.js"></script>\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>После воды</span></div>\n  </div>\n\n'

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>8 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>💧 <b>от %s ₴ · ультразвук</b></span>\n        </div>\n' % grn(lo_min)
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic,t,d in SIGNS)
    p += '  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">С чем приходят</span>\n        <h2>Как проявляется залитие</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards

    p += ('  <section class="sec sec-bg" id="how">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Первая помощь</span>\n        <h2>Что сделать до сервиса — и чего не делать никогда</h2>\n'
          '        <p class="lead-p">Стоимость ремонта после воды почти целиком определяется первым часом. Вот что реально важно.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Выключите и не включайте.</b> Проверять «а работает ли ещё» — самое дорогое любопытство: ток через мокрую плату замыкает соседние цепи и выжигает то, что вода ещё не тронула.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не ставьте на зарядку.</b> По той же причине, только хуже: на разъём подаётся напряжение, а он залит.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не сушите феном и не грейте.</b> Горячий воздух загоняет влагу глубже под микросхемы и ведёт проклейку.</span></li>'
          '<li><span class="ck">✓</span><span><b>Рис не помогает.</b> Он не вытягивает воду из-под чипов, зато засоряет разъёмы пылью. Пока телефон лежит в крупе, окисление идёт своим ходом.</span></li>'
          '<li><span class="ck">✓</span><span><b>Достаньте сим-лоток и везите как есть.</b> Через открытый слот часть воды выйдет. Подробнее — в статье <a href="../../blog/iphone-upal-v-vodu-chto-delat/">«iPhone упал в воду»</a>.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    rows = "\n            ".join(
        '<tr><td class="svc-name"><a href="../../remont-iphone/%s/">%s после воды</a></td><td class="pr" data-price-label="%s" data-price-dash="en" data-svc="После воды">%s ₴</td><td class="time">от 2 часов</td></tr>' % (
            slug, esc(label), esc(label), (grn(lo) if lo==hi else grn(lo)+" – "+grn(hi))) for label,slug,lo,hi in MODELS)
    p += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость ремонта после воды по моделям</h2>\n'
          '        <p class="lead-p">Вилка широкая не просто так: одному телефону хватает промывки платы, другому нужна замена выгоревших элементов — до вскрытия этого не видно никому. Нижняя граница — чистка, верхняя — восстановление платы. Точную цену называем после бесплатной диагностики.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Модель</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in STEPS)
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Ремонт после воды за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Вскрываем и показываем, куда дошла вода, до того как вы за что-то заплатите.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Ультразвуковая ванна</h3><p>Окисел уходит из-под чипов и разъёмов — там, где кистью не достать.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Берём в день обращения</h3><p>После залития счёт идёт на часы, поэтому такие аппараты пускаем без очереди.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in RELATED)
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">Ремонт iPhone после воды в Одессе — сервис SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel)

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(FAQ))
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о ремонте после воды</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Телефон побывал в воде? Позвоните сейчас</h2>\n          <p>После залития счёт идёт на часы. Оставьте номер — перезвоним за 15 минут и скажем, что делать до того, как вы доедете.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: ремонт после воды</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Ремонт iPhone после воды").replace("{{MODALOPTIONS}}", opts)
    return p

def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d моделей, %d FAQ)" % (SLUG, len(h), len(MODELS), len(FAQ)))

if __name__ == "__main__":
    main()
