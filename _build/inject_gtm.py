#!/usr/bin/env python3
# inject_gtm.py — вставляет контейнер Google Tag Manager (head-сниппет + noscript
# после <body>) и meta-верификацию Google Search Console. ID берутся из site_ids.json.
# Пустой ID -> шаг пропускается (ничего не грузится). Идемпотентно (маркеры).
# GA4/Pixel НЕ здесь — они настраиваются как теги ВНУТРИ GTM (есть dataLayer).
# Запускать ПОСЛЕ make_ua (на всех RU+UA страницах).
import os, re, json, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(REPO, "_build", "site_ids.json"), encoding="utf-8"))
GTM = (CFG.get("gtm_id") or "").strip()
GSC = (CFG.get("google_site_verification") or "").strip()

M_HEAD0, M_HEAD1 = "<!--gtm-head-->", "<!--/gtm-head-->"
M_BODY0, M_BODY1 = "<!--gtm-body-->", "<!--/gtm-body-->"
M_GSC0, M_GSC1 = "<!--gsc-verify-->", "<!--/gsc-verify-->"

def block(a, b, inner):
    return a + inner + b

def head_snippet():
    if not GTM:
        return ""
    return ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
            "f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','" + GTM + "');</script>")

def body_snippet():
    if not GTM:
        return ""
    return ('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM + '"'
            ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>')

def gsc_snippet():
    if not GSC:
        return ""
    return '<meta name="google-site-verification" content="' + GSC + '">'

def upsert(t, m0, m1, inner):
    """Вставить/заменить блок между маркерами. Пустой inner -> оставить пустые маркеры (для идемпотентности)."""
    b = block(m0, m1, inner)
    if m0 in t:
        return re.sub(re.escape(m0) + ".*?" + re.escape(m1), lambda _: b, t, flags=re.S)
    return None  # маркера ещё нет -> вставит вызывающий код в нужное место

def process(f):
    t = open(f, encoding="utf-8").read()
    orig = t

    # HEAD (GTM + GSC) — сразу после <head> (GTM просит как можно выше)
    head_inner = head_snippet()
    gsc_inner = gsc_snippet()
    for m0, m1, inner in ((M_GSC0, M_GSC1, gsc_inner), (M_HEAD0, M_HEAD1, head_inner)):
        r = upsert(t, m0, m1, inner)
        if r is not None:
            t = r
        elif "<head>" in t:
            t = t.replace("<head>", "<head>\n" + block(m0, m1, inner), 1)

    # BODY noscript — сразу после открывающего <body ...>
    body_inner = body_snippet()
    r = upsert(t, M_BODY0, M_BODY1, body_inner)
    if r is not None:
        t = r
    else:
        t = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + block(M_BODY0, M_BODY1, body_inner), t, count=1)

    if t != orig:
        open(f, "w", encoding="utf-8").write(t)
        return True
    return False

def main():
    if not GTM and not GSC:
        print("inject_gtm: gtm_id и google_site_verification пусты — пропуск (счётчики не подключены)")
        return
    n = tot = 0
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        if "_build" in f or os.sep + "admin" in f:  # админку не трекаем
            continue
        tot += 1
        if process(f):
            n += 1
    print("GTM/GSC инъекция: %d из %d страниц (gtm=%s, gsc=%s)" %
          (n, tot, GTM or "—", "да" if GSC else "—"))

if __name__ == "__main__":
    main()
