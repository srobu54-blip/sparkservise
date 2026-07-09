#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерит favicon-набор из фирменной искры SPARK (красная плитка #E11D2A + белая молния).
Пишет в корень репо: favicon.svg (мастер), favicon.ico (16/32/48), apple-touch-icon.png (180),
web-app-manifest-192x192.png / -512x512.png (maskable), site.webmanifest.
Идемпотентно — просто перезаписывает файлы. Вектор рисуется на супер-сэмпле ×8 → LANCZOS (чёткие края)."""
import os, json
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RED = (225, 29, 42, 255)          # #E11D2A — взят пипеткой из logo.png
WHITE = (255, 255, 255, 255)
SS = 8
BOLT = [(57,13),(31,53),(48,53),(40,89),(73,45),(54,45),(64,13)]   # молния на 100×100

def render(size, full_bleed=False, radius_frac=0.22):
    S = size * SS
    img = Image.new("RGBA", (S, S), (0,0,0,0))
    d = ImageDraw.Draw(img)
    if full_bleed:
        d.rectangle([0,0,S,S], fill=RED)
    else:
        d.rounded_rectangle([0,0,S-1,S-1], radius=int(S*radius_frac), fill=RED)
    d.polygon([(x/100*S, y/100*S) for (x,y) in BOLT], fill=WHITE)
    return img.resize((size,size), Image.LANCZOS)

def p(name): return os.path.join(REPO, name)

# SVG-мастер (та же геометрия — чёткий на любом размере, любимый браузерами)
pts = " ".join("%g,%g" % (x,y) for (x,y) in BOLT)
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
       '<rect width="100" height="100" rx="22" fill="#E11D2A"/>'
       '<polygon points="' + pts + '" fill="#fff"/></svg>\n')
open(p("favicon.svg"), "w", encoding="utf-8").write(svg)

# favicon.ico — многоразмерный (браузерный таб + фавикон в Google-выдаче)
render(48).save(p("favicon.ico"), sizes=[(16,16),(32,32),(48,48)])

# apple-touch — 180×180 full-bleed (iOS сам скругляет, прозрачность/скругление не нужны)
render(180, full_bleed=True).convert("RGB").save(p("apple-touch-icon.png"))

# PWA-манифест иконки — maskable (плитка красная до краёв, молния в safe-зоне центра)
render(192, full_bleed=True).save(p("web-app-manifest-192x192.png"))
render(512, full_bleed=True).save(p("web-app-manifest-512x512.png"))

manifest = {
    "name": "SPARK — сервисный центр Apple в Одессе",
    "short_name": "SPARK",
    "icons": [
        {"src": "/web-app-manifest-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "/web-app-manifest-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        {"src": "/favicon.svg", "type": "image/svg+xml", "sizes": "any"},
    ],
    "theme_color": "#ffffff",
    "background_color": "#ffffff",
    "display": "standalone",
    "lang": "ru",
    "start_url": "/",
}
open(p("site.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print("favicon: svg, ico, apple-touch-icon, 192, 512, site.webmanifest -> repo root")
