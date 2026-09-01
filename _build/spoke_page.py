#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Общий рендер спойк-страницы устройства (глубина-2) — один макет на все семейства.

Появился при добавлении iPad: макет страниц AirPods и iPad совпадал полностью,
и копировать двести строк вёрстки во второй генератор значило заводить второй
источник правды. Впереди ещё iMac и Apple Watch, поэтому вёрстка живёт здесь,
а генераторы семейств держат только данные: прайс-ключи, тексты, FAQ.

Вызывающий передаёт ctx с тем, что различается между семействами:
  hub_slug   — папка хаба, например "remont-airpods"
  hub_name   — как называется хаб в крошке и ссылках
  eyebrow    — надпись над H1
  rows_for   — функция(page) -> список строк прайса хаба
  siblings   — список соседних страниц семейства для блока «смотрите также»
  extra_rel  — дополнительные ссылки в тот же блок
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)


def lo_of(row):
    nums = re.findall(r"\d[\d\s\xa0]*", row.get("price", ""))
    return int(re.sub(r"\D", "", nums[0])) if nums else None


def hero_svg(pref, label, sub):
    grad = D._GRAD % {"p": pref}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % escA(label)
      + grad +
      '<rect x="10" y="10" width="380" height="280" rx="24" fill="url(#%ss)"/>' % pref +
      # кейс
      '<rect x="150" y="150" width="100" height="74" rx="16" fill="none" stroke="#878d99" stroke-width="4"/>'
      '<line x1="150" y1="176" x2="250" y2="176" stroke="#878d99" stroke-width="3"/>'
      # наушники
      '<g fill="none" stroke="#E11D2A" stroke-width="4" stroke-linecap="round">'
      '<path d="M126 74a12 12 0 1 1 24 0v10a12 12 0 1 1-24 0z"/><path d="M138 96v40"/>'
      '<path d="M250 74a12 12 0 1 1 24 0v10a12 12 0 1 1-24 0z"/><path d="M262 96v40"/></g>'
      + D._check(300, 190, 18) +
      '<text x="200" y="258" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">%s</text>' % esc(label) +
      '<text x="200" y="280" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="12">%s</text>' % esc(sub) +
      '</svg>\n      </div>')


def build(p, ctx):
    rows = ctx["rows_for"](p)
    # Цена в title и в Offer — от ПРОФИЛЬНОЙ услуги страницы, то есть первой
    # строки списка, а не минимум по таблице. Минимум давал ложное обещание:
    # страница чистки писала «от 250 ₴» (цена амбушюр), а страница аккумулятора
    # «от 500 ₴» (цена чистки контактов) при батарее от 700 ₴.
    lo = lo_of(rows[0]) if rows else None
    canon = "https://sparkservice.od.ua/%s/%s/" % (ctx["hub_slug"], p["slug"])
    price_short = ("от %s ₴" % format(lo, ",d").replace(",", " ")) if lo else None
    title = (p["title"] % price_short) if "%s" in p["title"] and price_short else p["title"].replace(" — %s", "")
    desc = (p["desc"] % price_short.capitalize()) if "%s" in p["desc"] and price_short else p["desc"].replace(" %s.", ".").replace("%s", "")
    quick = ("%s <b>%s · %s</b>" % (p["quick_icon"], esc(rows[0]["price"]), esc(rows[0].get("time","")))) if rows \
            else "%s <b>Диагностика бесплатно</b>" % p["quick_icon"]

    service = {"@context":"https://schema.org","@type":"Service","@id":canon+"#service",
        "name": p["service_name"] + " в Одессе", "serviceType": p["service_type"],
        "description": desc, "areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}}}
    if lo:
        service["offers"] = {"@type":"Offer","priceCurrency":"UAH","price":str(lo),
            "priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo),"priceCurrency":"UAH"}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":ctx["hub_name"],"item":"https://sparkservice.od.ua/%s/" % ctx["hub_slug"]},
        {"@type":"ListItem","position":3,"name":p["crumb"],"item":canon}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in p["faq"]]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>'
                            for x in (service, crumb, faqpage))

    h = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    h += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(p["kw"]))
    h += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % canon
    h += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    h += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA(p["ogtitle"]), escA(desc))
    h += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % canon
    h += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    h += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    h += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    h += ('<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки">'
          '<a href="../../">Главная</a><span>›</span><a href="../../%s/">%s</a>'
          '<span>›</span><span>%s</span></div>\n  </div>\n\n' % (ctx["hub_slug"], esc(ctx["hub_name"]), esc(p["crumb"])))

    h += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    h += '        <span class="eyebrow">%s</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(ctx["eyebrow"]), esc(p["h1"]), esc(p["sub"]))
    h += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    h += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    h += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>8 лет</div>\n'
    h += ('        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n'
          '          <span>🕐 <b>Ежедневно 10:00-19:00</b></span>\n          <span>%s</span>\n        </div>\n' % quick)
    h += '      </div>\n      ' + ctx["hero"](p) + '\n    </div>\n  </section>\n\n'

    # Описание карточки НЕ экранируем: страницам нужны инлайновые ссылки на
    # соседние спойки (стекло Apple Watch, аккумулятор), а заголовок — да,
    # в нём разметки не бывает. Проверено: в текстах AirPods и iPad символов
    # & < > нет, поэтому вывод этих семейств не изменился ни на байт.
    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), d) for ic,t,d in p["cases"])
    h += ('  <section class="sec" id="cases">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">С чем приходят</span>\n        <h2>%s</h2>\n      </div>\n'
          '      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n'
          % (esc(ctx["cases_h2"]), cards))

    bullets = "".join('<li><span class="ck">✓</span><span><b>%s</b> %s</span></li>' % (esc(b), t) for b,t in p["insight"])
    h += ('  <section class="sec sec-bg" id="insight">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">%s</span>\n        <h2>%s</h2>\n        <p class="lead-p">%s</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>%s</ul></div>\n    </div>\n  </section>\n\n'
          % (esc(p["insight_tag"]), esc(p["insight_h2"]), esc(p["insight_lead"]), bullets))

    prows = "\n            ".join(
        '<tr><td class="svc-name">%s</td><td class="pr">%s</td><td class="time">%s</td></tr>' % (
            esc(r["service"]), esc(D.normprice(r.get("price",""))), esc(r.get("time",""))) for r in rows)
    h += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Сколько это стоит</h2>\n'
          '        <p class="lead-p">Цены ориентировочные — точную назовём после бесплатной диагностики, до начала работ. Полный прайс%s — на <a href="../../%s/">%s</a>.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Услуга</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n'
          % (ctx.get("price_lead_suffix", ""), ctx["hub_slug"], esc(ctx["hub_price_anchor"]), prows))

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in p["steps"])
    h += ('  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">%s за 4 шага</h2>\n      </div>\n'
          '      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % (esc(p["service_name"]), steps))

    h += ('''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Сначала исключаем дешёвое</h3><p>Чистка и сброс проверяются раньше замены — часто менять ничего не приходится.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На работу мастера и установленную деталь. Оплата по факту.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>%s</h3><p>%s</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>8 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n''' % (esc(ctx["why3_title"]), esc(ctx["why3_text"])))

    others = [x for x in ctx["siblings"] if x["slug"] != p["slug"]]
    rel = [("../../%s/" % ctx["hub_slug"], ctx["hub_all_anchor"])]
    rel += [("../%s/" % o["slug"], o["service_name"]) for o in others]
    rel += ctx["extra_rel"]
    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in p["seo"])
    rell = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in rel)
    h += ('  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n'
          '        <h2 style="font-size:1.3rem;margin-bottom:14px">%s в Одессе — сервис SPARK</h2>\n        %s\n'
          '        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n'
          '        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n'
          % (esc(p["service_name"]), seops, rell))

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(p["faq"]))
    h += ('  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Частые вопросы</span>\n        <h2>%s</h2>\n      </div>\n'
          '      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % (esc(ctx["faq_h2"]), fqs))

    opts = "".join('<option>%s</option>' % esc(o) for o in p["form"])
    h += ('  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n'
          '        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n'
          '          <h2>%s</h2>\n          <p>%s</p>\n        </div>\n' % (esc(p["book_h2"]), esc(p["book_p"])))
    h += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    h += '            <h3 class="sf-title">Заявка: %s</h3>\n' % esc(p["service_name"])
    h += '''            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
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

    h += '''  <section class="sec sec-bg" id="contacts">
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

    h += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", p["service_name"]).replace("{{MODALOPTIONS}}", opts)
    return h


def write(page, ctx):
    outd = os.path.join(REPO, ctx["hub_slug"], page["slug"])
    os.makedirs(outd, exist_ok=True)
    html = build(page, ctx)
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(html)
    return html
