#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_calc.py — синхронизирует калькулятор на главной (main.js) с ценами хаба.

Источник правды: var TIERS в remont-iphone/index.html.
Вписывает объект IPH_TIERS (модель -> {услуга:[lo,hi]}) в main.js между маркерами
/*TIERS-START*/ ... /*TIERS-END*/. Запускать после любого изменения цен в TIERS.

Так калькулятор показывает ТОЧНЫЕ цены по каждой модели iPhone (как на страницах
моделей и в хабе), без расхождений. Тот же TIERS парсит и assemble_model.py.
"""
import os, re, json
from collections import OrderedDict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_tiers():
    s = open(os.path.join(REPO, "remont-iphone", "index.html"), encoding="utf-8").read()
    body = re.search(r'var TIERS=\[(.*?)\];', s, re.S).group(1)
    rows = re.findall(r"\{id:'([^']+)',label:'([^']+)',prices:\{([^}]*)\},time:'([^']+)'\}", body)
    out = OrderedDict()
    for tid, label, pr, time in rows:
        out[label] = json.loads('{' + pr.replace("'", '"') + '}')
    return out

def main():
    iph = parse_tiers()
    js = json.dumps(iph, ensure_ascii=False, separators=(",", ":"))
    main_path = os.path.join(REPO, "main.js")
    src = open(main_path, encoding="utf-8").read()
    new, n = re.subn(r"/\*TIERS-START\*/.*?/\*TIERS-END\*/",
                     "/*TIERS-START*/" + js.replace("\\", "\\\\") + "/*TIERS-END*/",
                     src, flags=re.S)
    if n != 1:
        raise SystemExit("ERROR: маркеры /*TIERS-START*/.../*TIERS-END*/ не найдены в main.js (n=%d)" % n)
    open(main_path, "w", encoding="utf-8").write(new)
    print("=== sync_calc ===")
    print("  моделей iPhone в калькулятор: %d" % len(iph))
    print("  IPH_TIERS: %d символов вписано в main.js" % len(js))

if __name__ == "__main__":
    main()
