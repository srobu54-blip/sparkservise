#!/usr/bin/env python3
# i18n_tok.py — lossless токенайзер HTML + общие хелперы для i18n (bootstrap/make_ua).
# tokenize(s): список, где ЧЁТНЫЕ индексы — TEXT-узлы, НЕЧЁТНЫЕ — TAG/SCRIPT/STYLE/COMMENT.
# Конкатенация ''.join(tokenize(s)) == s БАЙТ-В-БАЙТ (re.split с одной группой захвата).
import re

TOKEN_RE = re.compile(
    r'(<!--.*?-->'                       # комментарии (вкл. <!--lang-redirect-->)
    r'|<script\b[^>]*>.*?</script>'      # script целиком
    r'|<style\b[^>]*>.*?</style>'        # style целиком
    r'|<[^>]+>'                          # любой тег
    r')', re.S | re.I)

def tokenize(s):
    return TOKEN_RE.split(s)

CYR = re.compile(r'[А-Яа-яЁёІіЇїЄєҐґ]')
def has_cyr(s):
    return bool(CYR.search(s))

_WS = re.compile(r'^(\s*)(.*?)(\s*)$', re.S)
def split_ws(t):
    m = _WS.match(t)
    return m.group(1), m.group(2), m.group(3)

def is_translatable_text(core):
    # переводим только сегменты с кириллицей (нейтральные — цены/числа/латиница — пропуск)
    return bool(core) and has_cyr(core)

# ---- атрибуты ----
PLAIN_ATTRS = ('alt', 'aria-label', 'placeholder', 'title')
META_TR = {'description', 'keywords', 'og:title', 'og:description',
           'twitter:title', 'twitter:description'}

def _meta_key(tag):
    m = re.search(r'\b(?:name|property)\s*=\s*"([^"]*)"', tag, re.I)
    return m.group(1).lower() if m else ''

def map_tag_attrs(tag, tr):
    """Применить tr(value)->newvalue|None к переводимым атрибутам тега. Прочее не трогаем."""
    low = tag[:6].lower()
    if low.startswith('<meta'):
        if _meta_key(tag) in META_TR:
            names = ('content',)
        else:
            return tag
    else:
        names = PLAIN_ATTRS
    def repl(m):
        val = m.group(2)
        nv = tr(val)
        return m.group(1) + (nv if nv is not None else val) + m.group(3)
    for a in names:
        tag = re.sub(r'(\b' + re.escape(a) + r'\s*=\s*")([^"]*)(")', repl, tag, flags=re.I)
    return tag

def iter_tag_attr_values(tag):
    """Извлечь значения переводимых атрибутов (для бутстрапа)."""
    out = []
    low = tag[:6].lower()
    if low.startswith('<meta'):
        if _meta_key(tag) in META_TR:
            names = ('content',)
        else:
            return out
    else:
        names = PLAIN_ATTRS
    for a in names:
        for m in re.finditer(r'\b' + re.escape(a) + r'\s*=\s*"([^"]*)"', tag, flags=re.I):
            out.append(m.group(1))
    return out

# ---- script-токены ----
def script_kind(tok):
    head = tok[:120].lower()
    if 'application/ld+json' in head:
        return 'jsonld'
    if 'spark_lang' in tok:        # инжектируемый i18n_wire редирект
        return 'redirect'
    return 'js'

def jsonld_body(tok):
    """Вернуть (prefix, json_text, suffix) для script-токена ld+json."""
    m = re.match(r'(<script\b[^>]*>)(.*)(</script>)', tok, re.S | re.I)
    return m.group(1), m.group(2), m.group(3)

# Переводимые JS-литералы: КИРИЛЛИЦА-ЯКОРЬ + escape-aware + без переноса строки.
# Требование «внутри есть кириллица» защищает от ложного захвата кавычек в regex-литералах
# вроде /[<>&"]/ (там нет кириллицы → нет матча). group(0) = полный литерал С кавычками.
JS_CYR = re.compile(
    r"'(?:\\.|[^'\\\n])*[А-Яа-яЁёІіЇїЄєҐґ](?:\\.|[^'\\\n])*'"
    r"|\"(?:\\.|[^\"\\\n])*[А-Яа-яЁёІіЇїЄєҐґ](?:\\.|[^\"\\\n])*\"")
