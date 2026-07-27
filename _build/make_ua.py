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

# ── Fallback: перевод по ЧИСЛОВОМУ ШАБЛОНУ ────────────────────────────────────
# Зачем: ключи каталога содержат литеральные цены («Замена аккумулятора — 1 300 ₴»).
# Правка цены в админке делает RU-строку НОВЫМ ключом → точного совпадения нет →
# fail-open отдавал РУССКИЙ текст на украинской странице (тихая деградация).
# Решение: если строка отличается от известной ТОЛЬКО числами — берём её UA и
# подставляем фактические числа. Строгие гарантии (иначе отказ и обычный fail-open):
#   1) скелет (текст без чисел) совпадает буква-в-букву;
#   2) количество чисел в RU-ключе == в целевой строке;
#   3) числа в UA-значении идентичны числам RU-ключа и в том же порядке
#      (значит цены копируются в перевод как есть, и подстановка позиционно верна);
#   4) все кандидаты семейства дают один результат — иначе неоднозначность, отказ.
# Подстановка позиционная через re.sub (не str.replace) — не ломает числа-подстроки
# вроде «2 000» внутри «12 000». Ветка js НЕ участвует (там код, а не проза).
_NUM_RE = re.compile(r'\d+(?:[\s  ]\d{3})*')
_NUM_MASK = '\x00'
_tmpl_idx = {}          # id(dict) -> {masked_ru: [(ru, ua), ...]}
tmpl_hits = []          # (sitepath, kind, segment) — что вытянули по шаблону

def _nums(s):
    return _NUM_RE.findall(s)

def _mask(s):
    return _NUM_RE.sub(_NUM_MASK, s)

def _templates(d):
    # кэш держит ССЫЛКУ на сам словарь: иначе id() освобождённого dict мог бы
    # переиспользоваться и отдать чужой индекс (важно для ad-hoc словарей в тестах).
    key = id(d)
    hit = _tmpl_idx.get(key)
    if hit is not None and hit[0] is d:
        return hit[1]
    idx = {}
    for ru, ua in d.items():
        if _NUM_RE.search(ru):
            idx.setdefault(_mask(ru), []).append((ru, ua))
    _tmpl_idx[key] = (d, idx)
    return idx

def tr_by_template(d, s):
    """UA для строки, отличающейся от известной только числами. None, если нельзя надёжно."""
    if not _NUM_RE.search(s):
        return None
    fam = _templates(d).get(_mask(s))
    if not fam:
        return None
    tgt = _nums(s)
    results = set()
    for ru, ua in fam:
        src = _nums(ru)
        if len(src) != len(tgt):
            continue
        if _nums(ua) != src:        # в UA числа не те же / не в том же порядке — не подставляем
            continue
        it = iter(tgt)
        results.add(_NUM_RE.sub(lambda _m: next(it), ua))
    if len(results) == 1:           # ровно один вариант → безопасно
        return results.pop()
    return None

def lookup(d, s, sp=None, kind=None):
    """Точное совпадение → шаблон по числам → None (вызывающий делает fail-open)."""
    v = d.get(s)
    if v is not None:
        return v
    v = tr_by_template(d, s)
    # В отчёт — только РЕАЛЬНЫЕ спасения: если шаблон вернул строку, равную исходной
    # (напр. «1 500 ₴» одинаково в двух языках), перевода не было и хвастаться нечем.
    if v is not None and v != s and sp is not None:
        tmpl_hits.append((sp, kind, s))
    return v
# ─────────────────────────────────────────────────────────────────────────────

def tr_jsonld(obj, sp=None):
    if isinstance(obj, dict):
        return {k: tr_jsonld(v, sp) for k, v in obj.items()}
    if isinstance(obj, list):
        return [tr_jsonld(x, sp) for x in obj]
    if isinstance(obj, str):
        v = lookup(JSONLD, obj, sp, 'jsonld')
        if v is None:
            # JSON-LD молчал при fail-open (в отличие от text/attr/js) — русский
            # текст годами жил в разметке незамеченным. Теперь логируем так же.
            if T.has_cyr(obj):
                untranslated.append((sp, 'jsonld', obj))
            return obj
        return v
    return obj

def fix_inlanguage(obj):
    """RU-исходник может ЯВНО задавать inLanguage ('ru-RU' в блоге, 'ru' в
    o-kompanii). UA-страница — перевод того же контента, значит на ней такое
    значение неверно. Переписываем ru* → 'uk' на любой глубине, включая @graph
    (прежняя проверка ставила язык только когда поля НЕТ, поэтому явное 'ru-RU'
    переживало сборку). Значения других языков не трогаем — они не про перевод.
    'uk' без региона: так же, как <html lang="uk"> и остальные узлы разметки;
    регион живёт в hreflang (uk-UA/ru-UA), где он действительно значим."""
    if isinstance(obj, dict):
        v = obj.get('inLanguage')
        if isinstance(v, str) and (v.lower() == 'ru' or v.lower().startswith('ru-')):
            obj['inLanguage'] = 'uk'
        for x in obj.values():
            fix_inlanguage(x)
    elif isinstance(obj, list):
        for x in obj:
            fix_inlanguage(x)
    return obj

def translate_page(sp, ru_html, existing_ua_tokens):
    toks = T.tokenize(ru_html)
    for i in range(len(toks)):
        tok = toks[i]
        if i % 2 == 0:  # TEXT
            lead, core, trail = T.split_ws(tok)
            if not core:
                continue
            _t = lookup(TEXT, core, sp, 'text')
            if _t is not None:
                toks[i] = lead + _t + trail
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
                obj = tr_jsonld(obj, sp)
                if isinstance(obj, dict) and '@graph' not in obj and 'inLanguage' not in obj and isinstance(obj.get('@type'), str):
                    obj['inLanguage'] = 'uk'
                fix_inlanguage(obj)   # явные ru/ru-RU из RU-исходника → uk
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
                _a = lookup(ATTR, v, sp, 'attr')
                if _a is not None:
                    return _a
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
    if tmpl_hits:
        _tu = {}
        for sp, kind, seg in tmpl_hits:
            _tu.setdefault((kind, seg), set()).add(sp)
        print("Переведено по числовому шаблону: %d уникальных (вхождений: %d) — цены изменились, скелет знаком"
              % (len(_tu), len(tmpl_hits)))
        for (kind, seg), pages in list(_tu.items())[:10]:
            print("  [%s→шаблон] %r  (стр.: %d)" % (kind, seg[:70], len(pages)))
    print("Непереведённых уникальных сегментов: %d (вхождений: %d)" % (len(uniq), len(untranslated)))
    for (kind, seg), pages in list(uniq.items())[:30]:
        print("  [%s] %r  (стр.: %d)" % (kind, seg[:70], len(pages)))
    return 1 if untranslated else 0

if __name__ == '__main__':
    sys.exit(main())
