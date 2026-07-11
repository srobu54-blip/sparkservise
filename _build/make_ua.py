#!/usr/bin/env python3
# make_ua.py — собирает UA-страницы из RU по каталогу _build/i18n_ua.json, затем зовёт
# i18n_wire.main() для всей детерминированной обвязки (lang/пути/canonical/hreflang/
# переключатель/редирект/фото/ссылки). RU — источник; UA — генерируемый артефакт.
# Непереведённые сегменты остаются RU (fail-open) и логируются. Запуск:
#   python3 _build/make_ua.py            # пишет в /ua/, в конце wire
#   python3 _build/make_ua.py --dry DIR  # пишет во временную папку DIR (без wire) для diff
import os, re, json, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_tok as T
import i18n_wire

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(REPO, '_build', 'i18n_ua.json'), encoding='utf-8'))
TEXT, ATTR, JSONLD, JS = CAT['text'], CAT['attr'], CAT['jsonld'], CAT['js']
untranslated = []   # (sitepath, kind, segment)

def tr_jsonld(obj):
    if isinstance(obj, dict):
        return {k: tr_jsonld(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [tr_jsonld(x) for x in obj]
    if isinstance(obj, str):
        return JSONLD.get(obj, obj)
    return obj

def translate_page(sp, ru_html, existing_ua_tokens):
    toks = T.tokenize(ru_html)
    for i in range(len(toks)):
        tok = toks[i]
        if i % 2 == 0:  # TEXT
            lead, core, trail = T.split_ws(tok)
            if not core:
                continue
            if core in TEXT:
                toks[i] = lead + TEXT[core] + trail
            elif T.has_cyr(core):
                untranslated.append((sp, 'text', core))
            continue
        # odd: TAG / SCRIPT / STYLE / COMMENT
        low = tok[:8].lower()
        if low.startswith('<script'):
            kind = T.script_kind(tok)
            if kind == 'jsonld':
                pre, body, suf = T.jsonld_body(tok)
                try:
                    obj = json.loads(body)
                except Exception:
                    # fail-safe: взять валидный JSON-LD из существующей UA-страницы
                    if existing_ua_tokens and i < len(existing_ua_tokens) and existing_ua_tokens[i].lower().startswith('<script'):
                        toks[i] = existing_ua_tokens[i]
                    untranslated.append((sp, 'jsonld-unparsed', body[:60]))
                    continue
                obj = tr_jsonld(obj)
                if isinstance(obj, dict) and '@graph' not in obj and 'inLanguage' not in obj and isinstance(obj.get('@type'), str):
                    obj['inLanguage'] = 'uk'
                toks[i] = pre + json.dumps(obj, ensure_ascii=False) + suf
            elif kind == 'js':
                new = tok
                for ru_lit in sorted(JS, key=len, reverse=True):  # длинные первыми
                    if ru_lit in new:
                        new = new.replace(ru_lit, JS[ru_lit])
                for m in T.JS_CYR.finditer(tok):
                    if m.group(0) not in JS:
                        untranslated.append((sp, 'js', m.group(0)))
                toks[i] = new
            # redirect: не трогаем
            continue
        if low.startswith('<') and not low.startswith('<!--') and not low.startswith('<style'):
            # og:locale ru_RU -> uk_UA (часть языкового слоя)
            if tok[:6].lower().startswith('<meta') and 'og:locale' in tok:
                tok = tok.replace('content="ru_RU"', 'content="uk_UA"')
            def attr_tr(v):
                if v in ATTR:
                    return ATTR[v]
                if T.has_cyr(v):
                    untranslated.append((sp, 'attr', v))
                return None
            toks[i] = T.map_tag_attrs(tok, attr_tr)
    return ''.join(toks)

def ru_sitepaths():
    # Все RU-страницы (корень), КРОМЕ /ua/ (это выход) и служебных (admin/_*).
    # Так новые RU-страницы автоматически получают UA-зеркало + hreflang-обвязку.
    out = set()
    for f in glob.glob(os.path.join(REPO, '**', 'index.html'), recursive=True):
        rel = os.path.relpath(os.path.dirname(f), REPO).replace(os.sep, '/')
        if rel == '.':
            out.add(''); continue
        top = rel.split('/', 1)[0]
        if top in ('ua', 'admin') or top.startswith('_') or top.startswith('.'):
            continue
        out.add(rel)
    return sorted(out)

def main():
    dry = None
    if len(sys.argv) >= 3 and sys.argv[1] == '--dry':
        dry = sys.argv[2]
    sps = ru_sitepaths()
    for sp in sps:
        ru_path = os.path.join(REPO, sp, 'index.html') if sp else os.path.join(REPO, 'index.html')
        ua_path = os.path.join(REPO, 'ua', sp, 'index.html') if sp else os.path.join(REPO, 'ua', 'index.html')
        ru_html = open(ru_path, encoding='utf-8').read()
        existing = T.tokenize(open(ua_path, encoding='utf-8').read()) if os.path.isfile(ua_path) else None
        out_html = translate_page(sp, ru_html, existing)
        dest = os.path.join(dry, 'ua', sp, 'index.html') if dry else ua_path
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'w', encoding='utf-8').write(out_html)
    print("Собрано UA-страниц: %d%s" % (len(sps), (" (DRY -> %s)" % dry) if dry else ""))
    if not dry:
        i18n_wire.main()
    # отчёт по непереведённому
    from collections import Counter
    uniq = {}
    for sp, kind, seg in untranslated:
        uniq.setdefault((kind, seg), set()).add(sp)
    print("Непереведённых уникальных сегментов: %d (вхождений: %d)" % (len(uniq), len(untranslated)))
    for (kind, seg), pages in list(uniq.items())[:30]:
        print("  [%s] %r  (стр.: %d)" % (kind, seg[:70], len(pages)))
    return 1 if untranslated else 0

if __name__ == '__main__':
    sys.exit(main())
