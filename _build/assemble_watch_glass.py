#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Замена стекла Apple Watch» — вложенный спойк хаба часов:
/remont-apple-watch/zamena-stekla/ (глубина-2). Каркас — как у assemble_battery.py
(NAV/FOOTER/STYLE/MODAL_JS из assemble.py, depth-2 пути ../ -> ../../).

Зачем страница: кластер ~290 запросов/мес («полировка apple watch» 80, «замена стекла
apple watch» 40, «заміна скла apple watch» 30 и др.) без своей посадочной. Старая
Tilda-страница /zamena_stekla_apple_watch давала CTR 6.1% на поз. 7.23, но теперь
301-редиректится на общий хаб часов — специфика потеряна. Возвращаем клики.

Контент (признаки/шаги/FAQ/SEO/мета) — в _build/watch_glass_content.json, RU+UA.
Нет файла → страница НЕ собирается (exit 0), пайплайн не падает.
Скрипты/фавикон/og-хост/UA — навешивает пайплайн после генерации."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-apple-watch/zamena-stekla"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"
CONTENT_PATH = os.path.join(REPO, "_build", "watch_glass_content.json")

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

# Ключи иконок из контента → реально существующие в assemble.ICONS
ICON_MAP = {"screen": "screen", "search": "glass", "wrench": "wrench",
            "water": "water", "shield": "case", "clock": "battery",
            "glass": "glass", "battery": "battery", "case": "case"}

# ── Прайс: услуги по стеклу/экрану часов (цены из прайса хаба Apple Watch) ──
PRICES = [
    ("Диагностика", "Бесплатно", "при вас", True),
    ("Полировка стекла (царапины)", "1 500 ₴", "1-2 часа", False),
    ("Замена защитного стекла", "800 – 1 600 ₴", "1-2 часа", False),
    ("Замена стекла Apple Watch Ultra", "2 500 – 5 000 ₴", "1-2 дня", False),
    ("Замена тачскрина (сенсора)", "1 500 – 3 200 ₴", "1-2 дня", False),
    ("Замена дисплейного модуля", "1 800 – 4 500 ₴", "1-3 дня", False),
    ("Замена аккумулятора", "1 200 – 2 400 ₴", "1-2 часа", False),
    ("Восстановление после воды", "1 000 – 2 500 ₴", "1-3 дня", False),
    ("Чистка от окислов и пыли", "800 – 1 500 ₴", "1-2 часа", False),
]

RELATED = [
    ("../../remont-apple-watch/", "Ремонт Apple Watch — все услуги"),
    ("../../remont-apple-watch/apple-watch-ultra/", "Ремонт Apple Watch Ultra"),
    ("../../diagnostika/", "Бесплатная диагностика"),
    ("../../kontakty/", "Контакты и адрес сервиса"),
]

FORM_OPTS = ["Замена стекла Apple Watch", "Полировка стекла (царапины)",
             "Разбит дисплей Apple Watch", "Часы были в воде",
             "Другое (опишу в разговоре)"]


def hero_svg():
    """SVG-герой: часы с трещиной на стекле + искра."""
    grad = D._GRAD % {"p": "wg"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена стекла Apple Watch">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#wgs)"/>'
      # ремешок
      '<rect x="120" y="42" width="60" height="52" rx="16" fill="#2a2f3a"/>'
      '<rect x="120" y="266" width="60" height="52" rx="16" fill="#2a2f3a"/>'
      # корпус часов
      '<rect x="92" y="92" width="116" height="176" rx="34" fill="none" stroke="#E11D2A" stroke-width="6"/>'
      # экран
      '<rect x="106" y="106" width="88" height="148" rx="24" fill="rgba(225,29,42,.18)"/>'
      # Digital Crown
      '<rect x="206" y="146" width="10" height="26" rx="4" fill="#E11D2A"/>'
      # трещина
      '<polyline points="128,132 152,168 134,182 166,228" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
      + D._check(202, 250, 20) +
      '<text x="150" y="306" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="18" font-weight="700">Новое стекло</text>'
      '<text x="150" y="330" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · гарантия до 12 мес</text>'
      '</svg>\n      </div>')


def build(C):
    m = C["meta"]
    title, desc, h1, sub = m["title_ru"], m["desc_ru"], m["h1_ru"], m["lead_ru"]
    kw = ("замена стекла apple watch, замена стекла на эпл вотч, полировка apple watch, "
          "замена стекла apple watch одесса, замена экрана apple watch, поменять стекло на часах apple")

    SIGNS = [(ICON_MAP.get(s["icon"], "glass"), s["t_ru"], s["d_ru"]) for s in C["signs"]]
    STEPS = [(s["t_ru"], s["d_ru"], s["badge_ru"]) for s in C["steps"]]
    FAQ = [(f["q_ru"], f["a_ru"]) for f in C["faq"]]
    SEO = [x["ru"] for x in C["seo"]]

    # ── JSON-LD ──
    service = {"@context": "https://schema.org", "@type": "Service", "@id": CANON + "#service",
        "name": "Замена стекла Apple Watch в Одессе", "serviceType": "Замена стекла Apple Watch",
        "description": desc, "areaServed": {"@type": "City", "name": "Одесса"},
        "provider": {"@type": "Organization", "name": "SPARK", "url": "https://sparkservice.od.ua/",
            "telephone": "+380960755452",
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Академика Королёва, 23",
                        "addressLocality": "Одесса", "addressCountry": "UA"}},
        "offers": {"@type": "Offer", "priceCurrency": "UAH", "price": "800",
            "priceSpecification": {"@type": "PriceSpecification", "minPrice": "800", "priceCurrency": "UAH"}}}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://sparkservice.od.ua/"},
        {"@type": "ListItem", "position": 2, "name": "Ремонт Apple Watch", "item": "https://sparkservice.od.ua/remont-apple-watch/"},
        {"@type": "ListItem", "position": 3, "name": "Замена стекла", "item": CANON}]}
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False) + '\n</script>'
                            for x in (service, crumb, faqpage))

    # ── head ──
    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Замена стекла Apple Watch в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    # ── breadcrumb ──
    p += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../remont-apple-watch/">Ремонт Apple Watch</a>'
          '<span>›</span><span>Замена стекла</span></div>\n  </div>\n\n')

    # ── hero ──
    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт Apple Watch в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>\n          <span>⌚ <b>от 800 ₴ · 1-2 часа</b></span>\n        </div>\n'
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    # ── признаки / ситуации ──
    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic, t, d in SIGNS)
    p += ('  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Что случилось</span>\n        <h2>Полировка или замена: как понять, что нужно вам</h2>\n'
          '        <p class="lead-p">Выбор зависит не от серии часов, а от характера повреждения. Разбираем шесть типичных ситуаций.</p>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n') % cards

    # ── прайс ──
    rows = "\n            ".join(
        '<tr><td class="svc-name%s">%s</td><td class="pr%s">%s</td><td class="time">%s</td></tr>' % (
            " free" if free else "", esc(n), " free" if free else "", esc(pr), esc(t))
        for n, pr, t, free in PRICES)
    p += ('  <section class="sec sec-bg" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость замены стекла Apple Watch</h2>\n'
          '        <p class="lead-p">Цена внутри вилки зависит от серии, размера корпуса и типа стекла. Точную сумму называем после бесплатной диагностики, до начала работ.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Услуга</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n'
          '      <p class="lead-p" style="margin-top:18px;font-size:.88rem">Полировка не дешевле замены стекла. Её смысл в другом: часы не вскрывают, заводская влагозащита остаётся нетронутой, стекло остаётся родным.</p>\n'
          '    </div>\n  </section>\n\n') % rows

    # ── процесс ──
    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "мес" in b.lower() else "badge", esc(b)) if b else ""))
        for t, d, b in STEPS)
    p += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Замена стекла за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n') % steps

    # ── почему мы ──
    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Скажем, хватит ли полировки или нужна замена — до начала работ и без обязательств.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия до 12 месяцев</h3><p>На стекло и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Восстанавливаем герметизацию</h3><p>После вскрытия проклеиваем корпус заново — влагозащита не остаётся «на честном слове».</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    # ── SEO + related ──
    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href, t in RELATED)
    p += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена стекла Apple Watch в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n') % (seops, rel)

    # ── FAQ ──
    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i == 0 else ""), esc(q), esc(a)) for i, (q, a) in enumerate(FAQ))
    p += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о замене стекла Apple Watch</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n') % fqs

    # ── форма ──
    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n'
          '          <span class="sec-tag">Заявка</span>\n          <h2>Оставьте номер — назовём цену за 15 минут</h2>\n'
          '          <p>Подскажем, хватит ли полировки или нужна замена, и сколько это будет стоить для вашей модели. Или просто позвоните — мастер на связи.</p>\n        </div>\n')
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: стекло Apple Watch</h3>\n'
    p += '''            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
            <div class="mf-field"><label>Телефон</label>
              <div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
              <div class="mf-dots js-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
              <div class="mf-hint js-hint">Введите номер мобильного оператора Украины</div>
            </div>
            <div class="mf-field"><label>Что случилось</label><div class="mf-input"><select class="js-device" aria-label="Что случилось">''' + opts + '''</select></div></div>
            <button class="btn btn-spark mf-submit js-submit" type="button" disabled>Отправить заявку</button>
            <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных.</p>
            <div class="mf-trust"><span><b>✓</b> Бесплатная диагностика</span><span><b>✓</b> Гарантия до 12 мес</span><span><b>✓</b> Оплата по факту</span></div>
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
        <p class="lead-p">Мы в центре Одессы, рядом с Киевским рынком. Диагностика бесплатная — приходите без записи.</p></div>
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Замена стекла Apple Watch").replace("{{MODALOPTIONS}}", opts)
    return p


def main():
    if not os.path.exists(CONTENT_PATH):
        print("[assemble_watch_glass] нет watch_glass_content.json — страница пропущена")
        return 0
    C = json.load(open(CONTENT_PATH, encoding="utf-8"))
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build(C)
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d ситуаций, %d FAQ)" % (SLUG, len(h), len(C["signs"]), len(C["faq"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
