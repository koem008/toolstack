# -*- coding: utf-8 -*-
"""Generuje SEO/GEO soubory z content/data.json:
   - sitemap.xml (vč. 70 stránek nástrojů)
   - llms.txt (GEO — odkazy na interní stránky)
   - nastroje.html (crawlable výpis, ItemList JSON-LD)
   - nastroje/<slug>.html (samostatná stránka každého nástroje)
   - og-image.png
"""
import json
import html
import re
import os
import datetime
import unicodedata
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://tvujweb.cz"  # TODO: nahraď svou skutečnou doménou

d = json.load(open(os.path.join(BASE, "content", "data.json"), encoding="utf-8"))
site = d["site"]
cats = d["categories"]
today = datetime.date.today().isoformat()

name = site["name"]
tagline = site["tagline"]


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "nastroj"


def domain_of(url):
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


# Sestav seznam všech nástrojů s kategorií a slugem (unikátní)
tools_flat = []
seen = {}
for c in cats:
    for t in c["tools"]:
        slug = slugify(t["name"])
        if slug in seen:
            seen[slug] += 1
            slug = slug + "-" + str(seen[slug])
        else:
            seen[slug] = 1
        tools_flat.append({"cat": c, "tool": t, "slug": slug})

# ---------- Samostatné stránky nástrojů ----------
os.makedirs(os.path.join(BASE, "nastroje"), exist_ok=True)

for entry in tools_flat:
    t = entry["tool"]
    c = entry["cat"]
    slug = entry["slug"]
    t_name = html.escape(t["name"])
    t_desc = html.escape(t["desc"])
    t_long = html.escape(t.get("longdesc", t["desc"]))
    t_cat = html.escape(c["name"])
    t_url = html.escape(t["url"])
    logo = html.escape("https://www.google.com/s2/favicons?domain=%s&sz=128" % domain_of(t["url"]))
    page_url = "%s/nastroje/%s.html" % (SITE_URL, slug)

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Domů", "item": SITE_URL + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Nástroje", "item": SITE_URL + "/nastroje.html"},
                    {"@type": "ListItem", "position": 3, "name": t["name"]},
                ],
            },
            {
                "@type": "SoftwareApplication",
                "name": t["name"],
                "description": t.get("longdesc", t["desc"]),
                "applicationCategory": c["name"],
                "url": t["url"],
            },
        ],
    }
    jsonld = json.dumps(graph, ensure_ascii=False)

    page = (
        "<!DOCTYPE html>\n<html lang=\"cs\">\n<head>\n"
        '  <meta charset="UTF-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        "  <title>%s — %s | %s</title>\n" % (t_name, t_cat, html.escape(name))
        + '  <meta name="description" content="%s" />\n' % t_desc
        + '  <link rel="canonical" href="%s" />\n' % page_url
        + '  <meta name="robots" content="index, follow" />\n'
        + '  <meta property="og:type" content="article" />\n'
        + '  <meta property="og:title" content="%s — recenze a informace | %s" />\n' % (t_name, html.escape(name))
        + '  <meta property="og:description" content="%s" />\n' % t_desc
        + '  <meta property="og:url" content="%s" />\n' % page_url
        + '  <meta property="og:image" content="%s/og-image.png" />\n' % SITE_URL
        + '  <link rel="stylesheet" href="../pages.css" />\n'
        + '  <script src="../config.js"></script>\n'
        + '  <script src="../analytics.js"></script>\n'
        + '  <script type="application/ld+json">%s</script>\n' % jsonld
        + "</head>\n<body>\n"
        + '  <header class="pg-header">\n'
        + '    <a class="pg-brand" href="../index.html"><span class="brand-mark"></span> %s</a>\n' % html.escape(name)
        + "  </header>\n"
        + '  <main class="pg">\n'
        + '    <nav class="crumb"><a href="../index.html">Domů</a> › <a href="../nastroje.html">Nástroje</a> › %s</nav>\n' % t_name
        + '    <div class="tool-hero">\n'
        + '      <img class="tool-logo-big" src="%s" alt="%s" onerror="this.style.display=\'none\'" />\n' % (logo, t_name)
        + '      <div>\n'
        + '        <h1>%s</h1>\n' % t_name
        + '        <p class="lead">%s</p>\n' % t_cat
        + "      </div>\n"
        + "    </div>\n"
        + '    <h2>O nástroji</h2>\n'
        + '    <p>%s</p>\n' % t_long
        + '    <a class="cta" href="%s" target="_blank" rel="noopener">Vyzkoušet %s →</a>\n' % (t_url, t_name)
        + '    <p class="pg-note">Odkaz vede na oficiální web nástroje.</p>\n'
        + "  </main>\n"
        + '  <footer class="pg-footer">\n'
        + '    <a class="back" href="../nastroje.html">← Všechny nástroje</a>\n'
        + '    <a href="../podminky.html">Obchodní podmínky</a>\n'
        + '    <a href="../soukromi.html">Ochrana soukromí</a>\n'
        + '    <a href="../faq.html">FAQ</a>\n'
        + '    <a href="../kontakt.html">Kontakt</a>\n'
        + "  </footer>\n</body>\n</html>\n"
    )
    open(os.path.join(BASE, "nastroje", slug + ".html"), "w", encoding="utf-8").write(page)

# ---------- sitemap.xml ----------
urls = [("", "1.0"), ("nastroje.html", "0.8"), ("faq.html", "0.6")]
for e in tools_flat:
    urls.append(("nastroje/%s.html" % e["slug"], "0.7"))
urls += [
    ("podminky.html", "0.4"),
    ("soukromi.html", "0.4"),
    ("cookies.html", "0.4"),
    ("kontakt.html", "0.4"),
]
entries = []
for p, prio in urls:
    url = (SITE_URL + "/") if not p else (SITE_URL + "/" + p)
    entries.append(
        "  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>%s</priority></url>"
        % (html.escape(url), today, prio)
    )
sitemap = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(entries)
    + "\n</urlset>\n"
)
open(os.path.join(BASE, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

# ---------- llms.txt (GEO — odkazy na interní stránky) ----------
lines = []
lines.append("# " + name)
lines.append("")
lines.append("> " + tagline + ". " + site["introSub"])
lines.append("")
lines.append(site["introTitle"].replace("\n", " "))
lines.append("")
lines.append("## Kategorie a nástroje")
lines.append("")
for c in cats:
    lines.append("### " + c["name"])
    for t in c["tools"]:
        slug = None
        for e in tools_flat:
            if e["tool"] is t:
                slug = e["slug"]
                break
        lines.append("- [%s](%s/nastroje/%s.html) — %s" % (t["name"], SITE_URL, slug, t["desc"]))
    lines.append("")
lines.append("## Klíčové stránky")
lines.append("")
for label, p in [
    ("Domů", ""),
    ("Všechny nástroje", "nastroje.html"),
    ("Časté dotazy", "faq.html"),
    ("Kontakt", "kontakt.html"),
]:
    lines.append("- [%s](%s/%s)" % (label, SITE_URL, p))
lines.append("")
open(os.path.join(BASE, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))

# ---------- nastroje.html (crawlable, ItemList JSON-LD) ----------
items = []
pos = 1
for c in cats:
    for t in c["tools"]:
        slug = None
        for e in tools_flat:
            if e["tool"] is t:
                slug = e["slug"]
                break
        items.append({
            "@type": "ListItem",
            "position": pos,
            "url": "%s/nastroje/%s.html" % (SITE_URL, slug),
            "item": {
                "@type": "SoftwareApplication",
                "name": t["name"],
                "description": t["desc"],
                "url": t["url"],
                "applicationCategory": c["name"],
            },
        })
        pos += 1
jsonld = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "numberOfItems": pos - 1,
    "itemListElement": items,
}
jsonld_str = json.dumps(jsonld, ensure_ascii=False)

body_cats = []
for c in cats:
    lis = []
    for t in c["tools"]:
        slug = None
        for e in tools_flat:
            if e["tool"] is t:
                slug = e["slug"]
                break
        lis.append(
            '        <li><a href="nastroje/%s.html">%s</a> — %s</li>'
            % (slug, html.escape(t["name"]), html.escape(t["desc"]))
        )
    body_cats.append("    <h2>%s</h2>\n    <ul>\n%s\n    </ul>" % (html.escape(c["name"]), "\n".join(lis)))

page = (
    "<!DOCTYPE html>\n<html lang=\"cs\">\n<head>\n"
    '  <meta charset="UTF-8" />\n'
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
    "  <title>Všechny nástroje — %s</title>\n" % html.escape(name)
    + '  <meta name="description" content="Kompletní přehled všech nástrojů v katalogu %s." />\n' % html.escape(name)
    + '  <link rel="canonical" href="%s/nastroje.html" />\n' % SITE_URL
    + '  <meta name="robots" content="index, follow" />\n'
    + '  <link rel="stylesheet" href="pages.css" />\n'
    + '  <script src="config.js"></script>\n'
    + '  <script src="analytics.js"></script>\n'
    + '  <script type="application/ld+json">%s</script>\n' % jsonld_str
    + "</head>\n<body>\n"
    + '  <header class="pg-header">\n'
    + '    <a class="pg-brand" href="index.html"><span class="brand-mark"></span> %s</a>\n' % html.escape(name)
    + "  </header>\n"
    + '  <main class="pg">\n'
    + "    <h1>Všechny nástroje</h1>\n"
    + '    <p class="lead">Kompletní přehled nástrojů v katalogu.</p>\n'
    + "\n".join(body_cats)
    + "\n  </main>\n"
    + '  <footer class="pg-footer">\n'
    + '    <a class="back" href="index.html">← Zpět na katalog</a>\n'
    + '    <a href="podminky.html">Obchodní podmínky</a>\n'
    + '    <a href="soukromi.html">Ochrana soukromí</a>\n'
    + '    <a href="faq.html">FAQ</a>\n'
    + '    <a href="kontakt.html">Kontakt</a>\n'
    + "  </footer>\n</body>\n</html>\n"
)
open(os.path.join(BASE, "nastroje.html"), "w", encoding="utf-8").write(page)

print("OK: %d stránek nástrojů, sitemap.xml (%d URL), llms.txt, nastroje.html" % (len(tools_flat), len(urls)))
