# TOOLSTACK — katalog špičkových nástrojů

Profesionální web s 3D efektem „letu vpřed": kategorie se přibližují, otevírají a ukazují nástroje. Obsah se edituje **bez znalosti kódu** přes webový editor (Decap CMS) na adrese `/admin`.

## Struktura

```
superweb/
├── index.html            # 3D katalog (hlavní stránka)
├── styles.css            # design 3D katalogu
├── pages.css             # design informačních stránek
├── app.js                # logika (3D let, hledání, načtení obsahu)
├── config.js             # ★ měření: Google Analytics + Search Console
├── analytics.js          # načítá nastavení z config.js
├── content/
│   └── data.json         # ★ OBSAH — texty, kategorie, nástroje, odkazy
├── data.js               # offline záloha obsahu (generovaná)
├── nastroje/             # 70 stránek jednotlivých nástrojů (generované)
├── nastroje.html         # crawlable výpis všech nástrojů (generovaný)
├── sitemap.xml           # (generovaný)
├── llms.txt              # GEO — pro AI vyhledávače (generovaný)
├── robots.txt
├── og-image.png          # náhled pro sdílení (generovaný)
├── podminky.html · soukromi.html · cookies.html · faq.html · kontakt.html
├── gen_seo.py            # generátor SEO souborů (běží na Netlify)
├── gen_datajs.py         # generátor data.js (běží na Netlify)
├── gen_og_image.py       # generátor og-image (jen lokálně, Python+numpy+PIL)
└── netlify.toml          # konfigurace Netlify (build příkaz)
```

## Jak upravovat obsah

Obsah je v **`content/data.json`**. Dvě možnosti:

1. **Webový editor (doporučeno):** po nasazení otevři `https://tvujweb/admin` → přihlas se → upravuješ texty, přidáváš nástroje a měníš odkazy. Uložení = commit → web i SEO soubory se samy přegenerují.
2. **Ručně:** uprav `content/data.json` v textovém editoru.

> **Nástroj = 1 záznam:** `{ "name": "Canva", "desc": "Grafika pro každého…", "url": "https://tvuj-affiliate-link" }`
>
> ⚠️ **Provize a délky provizí NEJSOU na webu** — jsou jen ve tvé soukromé tabulce `affiliate-programy-prehled.xlsx`.

## Před nasazením (jednou)

1. **Doména:** nahraď `https://tvujweb.cz` svou doménou — v `index.html`, info stránkách, `robots.txt` a v `gen_seo.py` (proměnná `SITE_URL`).
2. **Měření:** do `config.js` vyplň `GA_MEASUREMENT_ID` (Google Analytics 4, např. `G-ABC123`) a `GSC_VERIFICATION` (token z Google Search Console). Prázdné hodnoty = funkce vypnutá.
3. **Kontakt:** doplň reálný e-mail v `kontakt.html` a identifikaci provozovatele v `podminky.html` / `soukromi.html`.

## Nasazení na Netlify (zdarma, ~10 minut)

1. **Založ účty:** [github.com](https://github.com) a [netlify.com](https://netlify.com) (přihlášení přes GitHub).
2. **Nahraj na GitHub:** vytvoř repozitář a nahraj **celý obsah složky `superweb/`**.
3. **Připoj Netlify:** *Add new site → Import an existing project* → vyber repozitář → **Deploy**. Build příkaz se načte automaticky z `netlify.toml` (přegeneruje SEO soubory). Za ~30 s je web online.
4. **Zapni editor (Decap CMS):** Netlify → *Site settings → Identity → Enable Identity* → *Git Gateway → Enable* → pozvi svůj e-mail → otevři `https://tvujweb.netlify.app/admin/`.

## Lokální náhled

Spusť z této složky `python -m http.server 8642` a otevři `http://127.0.0.1:8642/`.

## Poznámky

- **Affiliate odkazy** jsou v poli `url` u každého nástroje — nahraď je svými affiliate linky.
- **Právní texty** (podmínky, soukromí, cookies) jsou šablony — doporučuji nechat je zkontrolovat právníkem.
- SEO soubory (sitemap, stránky nástrojů, llms.txt) se **automaticky přegenerují** při každém Netlify buildu; lokálně je spustíš: `python gen_seo.py` a `python gen_datajs.py`.
