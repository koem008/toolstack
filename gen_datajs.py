# -*- coding: utf-8 -*-
"""Vygeneruje data.js (offline zálohu) z content/data.json."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(BASE, "content", "data.json"), encoding="utf-8"))

site = json.dumps(d["site"], ensure_ascii=False, indent=2)
cats = json.dumps(d["categories"], ensure_ascii=False, indent=2)

header = """/* ============================================================
   OFFLINE ZÁLOHA OBSAHU (generováno z content/data.json).
   Hlavní obsah je v content/data.json — edituje se přes /admin.
   Tenhle soubor se používá jen při otevření přes file://.
   ============================================================ */

"""
body = (
    "const SITE = " + site + ";\n\n"
    "const CATEGORIES = " + cats + ";\n\n"
    'const INTRO = { type: "intro" };\n'
    'const OUTRO = { type: "outro" };\n'
    "const DATA = [INTRO, ...CATEGORIES, OUTRO];\n"
)
with open(os.path.join(BASE, "data.js"), "w", encoding="utf-8") as f:
    f.write(header + body)
print("data.js regenerated OK")
