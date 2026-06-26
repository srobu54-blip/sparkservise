#!/usr/bin/env python3
# i18n_bootstrap.py — разовый: извлекает каталог переводов из существующих 62 RU/UA пар
# в _build/i18n_ua.json. Структура RU и UA идентична (только текст отличается) → парный обход
# токенов по индексу. В каталог идут только сегменты с кириллицей и ru != ua.
import os, re, json, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_tok as T

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = {"text": {}, "attr": {}, "jsonld": {}, "js": {}}
conflicts = []

def put(branch, k, v, where):
    if not k or k == v or not T.has_cyr(k):
        return
    old = CAT[branch].get(k)
    if old is not None and old != v:
        conflicts.append((branch, where, k, old, v))
        return
    CAT[branch][k] = v

def walk_json(ru, ua, where):
    if isinstance(ru, dict) and isinstance(ua, dict):
        for kk in ru:
            if kk in ua:
                walk_json(ru[kk], ua[kk], where)
    elif isinstance(ru, list) and isinstance(ua, list):
        for a, b in zip(ru, ua):
            walk_json(a, b, where)
    elif isinstance(ru, str) and isinstance(ua, str):
        put("jsonld", ru, ua, where)

def ua_sitepaths():
    out = []
    for f in glob.glob(os.path.join(REPO, 'ua', '**', 'index.html'), recursive=True):
        rel = os.path.relpath(os.path.dirname(f), os.path.join(REPO, 'ua')).replace(os.sep, '/')
        out.append('' if rel == '.' else rel)
    return sorted(out)

def process(sp):
    ru_path = os.path.join(REPO, sp, 'index.html') if sp else os.path.join(REPO, 'index.html')
    ua_path = os.path.join(REPO, 'ua', sp, 'index.html') if sp else os.path.join(REPO, 'ua', 'index.html')
    ru = T.tokenize(open(ru_path, encoding='utf-8').read())
    ua = T.tokenize(open(ua_path, encoding='utf-8').read())
    where = sp or '(root)'
    if len(ru) != len(ua):
        conflicts.append(('LEN', where, '', len(ru), len(ua)))
        return
    for i in range(len(ru)):
        if i % 2 == 0:  # TEXT
            rc = T.split_ws(ru[i])[1]
            uc = T.split_ws(ua[i])[1]
            put("text", rc, uc, where)
        else:           # TAG / SCRIPT / STYLE / COMMENT
            rt, ut = ru[i], ua[i]
            if rt.lower().startswith('<script'):
                kind = T.script_kind(rt)
                if kind == 'jsonld':
                    try:
                        rj = json.loads(T.jsonld_body(rt)[1])
                        uj = json.loads(T.jsonld_body(ut)[1])
                        walk_json(rj, uj, where)
                    except Exception as e:
                        conflicts.append(('JSONLD', where, str(e), '', ''))
                elif kind == 'js':
                    rl = [m.group(0) for m in T.JS_CYR.finditer(rt)]   # полные литералы с кавычками
                    ul = [m.group(0) for m in T.JS_CYR.finditer(ut)]
                    if len(rl) == len(ul):
                        for a, b in zip(rl, ul):
                            put("js", a, b, where)
                    else:
                        conflicts.append(('JS-LEN', where, '', len(rl), len(ul)))
            elif rt.startswith('<') and not rt.startswith('<!--'):
                rv = T.iter_tag_attr_values(rt)
                uv = T.iter_tag_attr_values(ut)
                if len(rv) == len(uv):
                    for a, b in zip(rv, uv):
                        put("attr", a, b, where)

def main():
    sps = ua_sitepaths()
    for sp in sps:
        process(sp)
    out = os.path.join(REPO, '_build', 'i18n_ua.json')
    # стабильный порядок для читаемого diff
    ordered = {b: dict(sorted(CAT[b].items())) for b in CAT}
    json.dump(ordered, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=False)
    print("Каталог: text=%d attr=%d jsonld=%d js=%d  (страниц=%d)" % (
        len(CAT['text']), len(CAT['attr']), len(CAT['jsonld']), len(CAT['js']), len(sps)))
    if conflicts:
        print("\nКОНФЛИКТЫ/предупреждения: %d" % len(conflicts))
        for c in conflicts[:25]:
            print("  ", c[0], c[1], '|', repr(c[2])[:60], '->', repr(c[3])[:40], 'vs', repr(c[4])[:40])
    print("\nЗаписано:", out)

if __name__ == '__main__':
    main()
