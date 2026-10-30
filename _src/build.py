#!/usr/bin/env python3
"""Generatore del sito atomoeorbita.it.

Legge i file Markdown in _src/content, applica i template in _src/templates
e scrive l'HTML statico nella radice del repository (che Hostinger pubblica).

Uso:  python3 _src/build.py

Contenuti:
  _src/content/articoli/AAAA-MM-GG-slug.md   articoli (front matter: title, slug,
                                              category, date, description, format,
                                              [updated], [draft], [pillar], [image])
  _src/content/numeri/*.md                   schede dati (title, slug, source, updated)
  _src/content/pagine/*.md                   pagine fisse (title, slug, [description])
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
CONTENT = SRC / "content"
TEMPLATES = SRC / "templates"
STATIC = SRC / "static"

CONFIG = json.loads((SRC / "config.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(SRC))
try:
    from rassegna import FEEDS as FEEDS_FOR_PAGE  # solo per elencare le fonti
except Exception:  # feedparser assente in locale: la pagina elenca comunque le fonti
    FEEDS_FOR_PAGE = []
SITE_URL = CONFIG["site_url"].rstrip("/")
FORMATS = CONFIG.get("formats", {})

MD = markdown.Markdown(
    extensions=["tables", "toc", "attr_list", "sane_lists", "md_in_html", "footnotes"],
    extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}},
    output_format="html5",
)

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


# ---------------------------------------------------------------- utilities
def parse_front_matter(text: str) -> tuple[dict, str]:
    """Front matter minimale: righe `chiave: valore` fra due `---`."""
    if not text.startswith("---"):
        return {}, text
    _, fm, body = text.split("---", 2)
    meta: dict = {}
    for line in fm.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, body.lstrip("\n")


def render_markdown(body: str) -> tuple[str, str]:
    MD.reset()
    html_out = MD.convert(body)
    toc = MD.toc if getattr(MD, "toc_tokens", None) else ""
    return html_out, toc


def mark_external_links(html_out: str) -> str:
    """I link esterni si aprono in una nuova scheda. Le fonti restano `follow`:
    una testata di analisi linka le fonti primarie e vuole che Google lo veda."""
    return re.sub(
        r'<a href="(https?://(?!atomoeorbita\.it)[^"]+)"',
        r'<a href="\1" rel="noopener" target="_blank"',
        html_out,
    )


def reading_time(body: str) -> int:
    words = len(re.findall(r"\w+", body))
    return max(1, round(words / 200))


def iso(d: str) -> str:
    return dt.date.fromisoformat(d).isoformat()


def human_date(d: str) -> str:
    months = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
              "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    date = dt.date.fromisoformat(d)
    return f"{date.day} {months[date.month - 1]} {date.year}"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clean_output() -> None:
    """Rimuove l'HTML generato in precedenza, lasciando sorgenti e git."""
    keep = {"_src", ".git", ".github", ".gitignore", "README.md", ".htaccess", "CNAME"}
    for item in ROOT.iterdir():
        if item.name in keep or item.name.startswith("google") and item.suffix == ".html":
            continue  # file di verifica Google Search Console
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


# ---------------------------------------------------------------- content
def load_foto() -> dict:
    p = SRC / "data" / "foto.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def thumb(url: str, width: int) -> str:
    """Le miniature di Commons hanno la larghezza nel nome: /1200px-File.jpg."""
    url = url.split("?", 1)[0]
    return re.sub(r"/\d+px-", f"/{width}px-", url, count=1)


def anteprima_mappa(centrali: list, spazio: list) -> str:
    """Anteprima SVG della mappa: i punti veri in proiezione equirettangolare (lat 75..-50)."""
    col = {"lancio": "#F2A33A", "sviluppo": "#E8653A", "italia": "#4FB3E8"}
    out = ['<svg class="map-preview" viewBox="0 0 360 125" role="img" aria-label="Anteprima della mappa: centrali nucleari e basi spaziali nel mondo">',
           '<rect width="360" height="125" fill="#0D0F12"/>']
    for lon in range(-150, 181, 30):
        out.append(f'<line x1="{lon+180}" y1="0" x2="{lon+180}" y2="125" stroke="#1E2329" stroke-width=".3"/>')
    for lat in (60, 30, 0, -30):
        out.append(f'<line x1="0" y1="{75-lat}" x2="360" y2="{75-lat}" stroke="#1E2329" stroke-width=".3"/>')
    for c in sorted(centrali, key=lambda c: -c["mw"]):
        r = max(0.9, min(3.2, (c["mw"] ** 0.5) / 28))
        out.append(f'<circle cx="{c["lon"]+180:.1f}" cy="{75-c["lat"]:.1f}" r="{r:.1f}" fill="#3DDCC8" fill-opacity=".55"/>')
    for p in spazio:
        out.append(f'<circle cx="{p["lon"]+180:.1f}" cy="{75-p["lat"]:.1f}" r="1.5" fill="{col[p["k"]]}" stroke="#0D0F12" stroke-width=".4"/>')
    out.append("</svg>")
    return "".join(out)


FUTURE_URLS: set = set()


def unlink_future(html_body: str) -> str:
    """Toglie i link verso articoli programmati ma non ancora usciti (restano come testo)."""
    if not FUTURE_URLS:
        return html_body
    def repl(m):
        return m.group(2) if m.group(1) in FUTURE_URLS else m.group(0)
    return re.sub(r'<a href="(/[^"#]+/)"[^>]*>(.*?)</a>', repl, html_body)


def load_articles() -> list[dict]:
    foto = load_foto()
    articles = []
    for path in sorted((CONTENT / "articoli").glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("draft") == "true":
            FUTURE_URLS.add(f"/{meta.get('category', '')}/{meta.get('slug', '')}/")
            continue
        if dt.date.fromisoformat(meta["date"]) > dt.date.today():
            # programmato: esce da solo con la ricostruzione quotidiana del sito
            cat_slug = meta.get("category", "")
            FUTURE_URLS.add(f"/{cat_slug}/{meta['slug']}/")
            continue
        html_body, toc = render_markdown(body)
        html_body = mark_external_links(html_body)
        cat = next(c for c in CONFIG["categories"] if c["slug"] == meta["category"])
        fmt = meta.get("format", "analisi")
        article = {
            **meta,
            "format": fmt,
            "format_name": FORMATS.get(fmt, fmt.capitalize()),
            "body": html_body,
            "toc": toc,
            "category_obj": cat,
            "url": f"/{cat['slug']}/{meta['slug']}/",
            "date_iso": iso(meta["date"]),
            "date_human": human_date(meta["date"]),
            "updated_iso": iso(meta.get("updated", meta["date"])),
            "updated_human": human_date(meta.get("updated", meta["date"])),
            "minutes": reading_time(body),
            "pillar": meta.get("pillar") == "true",
        }
        f = foto.get("articolo:" + meta["slug"])
        if f and "locale" in f:
            article["image"] = f["locale"]["1280"]
            article["image_small"] = f["locale"]["640"]
            article["credit"] = f
        articles.append(article)
    articles.sort(key=lambda a: a["date_iso"], reverse=True)
    published = {a["url"] for a in articles}
    sections = tuple(f"/{c['slug']}/" for c in CONFIG["categories"])
    def repl(m):
        url = m.group(1)
        if url.startswith(sections) and url.count("/") == 3 and url not in published:
            return m.group(2)  # articolo non (ancora) pubblicato: resta il testo, senza link
        return m.group(0)
    for a in articles:
        a["body"] = re.sub(r'<a href="(/[^"#]+/)"[^>]*>(.*?)</a>', repl, a["body"])
    return articles


def load_numeri() -> list[dict]:
    """Schede dati: ogni file è una scheda con tabella e fonte."""
    items = []
    folder = CONTENT / "numeri"
    if not folder.exists():
        return items
    for path in sorted(folder.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("draft") == "true":
            continue
        html_body, _ = render_markdown(body)
        items.append({**meta, "body": mark_external_links(html_body),
                      "url": f"/numeri/{meta['slug']}/",
                      "updated_human": human_date(meta["updated"]),
                      "updated_iso": iso(meta["updated"])})
    items.sort(key=lambda n: n["updated_iso"], reverse=True)
    return items


def load_rassegna() -> dict | None:
    """Rassegna quotidiana scritta da _src/rassegna.py (via GitHub Actions)."""
    path = CONTENT / "rassegna.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    months = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

    def human(ts: str) -> str:
        t = dt.datetime.fromisoformat(ts).astimezone(dt.timezone(dt.timedelta(hours=2)))
        return f"{t.day} {months[t.month - 1]}, {t:%H:%M}"

    for sec in ("atomo", "orbita"):
        for it in data.get(sec, []):
            it["time_human"] = human(it["time"])
    data["updated_human"] = human(data["updated"])
    return data


def load_pages() -> list[dict]:
    pages = []
    for path in sorted((CONTENT / "pagine").glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        html_body, _ = render_markdown(body)
        pages.append({**meta, "body": mark_external_links(html_body), "url": f"/{meta['slug']}/"})
    return pages


# ---------------------------------------------------------------- build
def build() -> None:
    clean_output()
    articles = load_articles()
    numeri = load_numeri()
    pages = load_pages()
    rassegna = load_rassegna()

    categories = []
    for c in CONFIG["categories"]:
        items = [a for a in articles if a["category"] == c["slug"]]
        categories.append({**c, "url": f"/{c['slug']}/", "articles": items,
                           "pillar": next((a for a in items if a["pillar"]), None)})

    punti = [a for a in articles if a["format"] == "punto"]
    dossier = [a for a in articles if a["format"] == "dossier"]
    spiegati = [a for a in articles if a["format"] == "spiegato"]

    base_ctx = {
        "site": CONFIG,
        "site_url": SITE_URL,
        "categories": categories,
        "year": dt.date.today().year,
        "build_date": dt.date.today().isoformat(),
    }

    # assets
    shutil.copytree(STATIC, ROOT / "assets")
    shutil.copytree(SRC / "data", ROOT / "assets" / "dati")

    # home
    write(ROOT / "index.html", env.get_template("home.html").render(
        **base_ctx, articles=articles, punto=punti[0] if punti else None,
        dossier=dossier[:2], spiegati=spiegati[:4], numeri=numeri[:4], rassegna=rassegna,
        page_url="/", title=CONFIG["title"], description=CONFIG["description"]))

    # categorie
    for c in categories:
        write(ROOT / c["slug"] / "index.html", env.get_template("category.html").render(
            **base_ctx, cat=c, page_url=c["url"],
            title=f"{c['name']} · {CONFIG['name']}", description=c["description"]))

    # raccolte per formato: /dossier/ e /il-punto/
    write(ROOT / "dossier" / "index.html", env.get_template("list.html").render(
        **base_ctx, items=dossier, page_url="/dossier/", heading="Dossier",
        lead="Un approfondimento al mese: chi, dove, quando e quanto costa. Fonti primarie, tabelle e grafici che puoi scaricare, non solo le conclusioni.",
        empty="Il primo Dossier è in lavorazione. Iscriviti alla newsletter per riceverlo appena esce.",
        title=f"Dossier · {CONFIG['name']}",
        description="I Dossier di Atomo e Orbita: approfondimenti mensili su nucleare e spazio con dati scaricabili."))
    write(ROOT / "il-punto" / "index.html", env.get_template("list.html").render(
        **base_ctx, items=punti, page_url="/il-punto/", heading="Il Punto",
        lead="L'analisi breve di ogni settimana: un tema di confine tra nucleare e spazio, la tesi in poche righe, i documenti per approfondire. È anche la nostra newsletter.",
        empty="Il primo Punto esce con il lancio del sito.",
        title=f"Il Punto · {CONFIG['name']}",
        description="Il Punto: l'analisi settimanale di Atomo e Orbita su nucleare e spazio."))

    # rassegna
    from urllib.parse import urlsplit
    raw = rassegna["sources"] if rassegna else [{"name": s, "url": u} for _, s, u, _ in FEEDS_FOR_PAGE]
    srcs = [{"name": r["name"], "url": f"{urlsplit(r['url']).scheme}://{urlsplit(r['url']).netloc}/"} for r in raw]
    write(ROOT / "rassegna" / "index.html", env.get_template("rassegna.html").render(
        **base_ctx, rassegna=rassegna, sources=srcs, page_url="/rassegna/",
        title=f"Rassegna · {CONFIG['name']}",
        description="Le notizie delle ultime 48 ore dalle fonti specialistiche su nucleare e spazio, aggiornate ogni mattina."))

    # mappa
    data_dir = SRC / "data"
    centrali = json.loads((data_dir / "centrali.json").read_text(encoding="utf-8"))["sites"]
    spazio = json.loads((data_dir / "spazio.json").read_text(encoding="utf-8"))["sites"]
    foto = load_foto()
    for s in centrali + spazio:
        f = foto.get(s["n"])
        if f and "locale" in f:
            s["f"] = {"u": f["locale"]["480"], "p": f["file"], "a": f["autore"], "l": f["licenza"]}
    write(ROOT / "mappa" / "index.html", env.get_template("mappa.html").render(
        **base_ctx, centrali=centrali, spazio=spazio, n_foto=sum(1 for s in centrali + spazio if 'f' in s), c_sites=len(centrali),
        c_reactors=sum(c["r"] for c in centrali), page_url="/mappa/",
        title=f"Centrali nucleari nel mondo e basi spaziali: la mappa · {CONFIG['name']}",
        description="Mappa interattiva di tutte le centrali e i reattori nucleari in funzione nel mondo, degli spazioporti e dei siti spaziali italiani, con fonti e limiti dei dati."))

    # numeri
    write(ROOT / "numeri" / "index.html", env.get_template("numeri.html").render(
        **base_ctx, numeri=numeri, anteprima=anteprima_mappa(centrali, spazio), page_url="/numeri/",
        title=f"Numeri · {CONFIG['name']}",
        description="Schede dati aggiornate su nucleare e spazio: reattori, lanci, progetti, aziende. Sempre con la fonte."))
    for n in numeri:
        write(ROOT / "numeri" / n["slug"] / "index.html", env.get_template("numero.html").render(
            **base_ctx, n=n, page_url=n["url"],
            title=f"{n['title']} · Numeri · {CONFIG['name']}", description=n.get("description", "")))

    # articoli
    for a in articles:
        serie = []
        if a.get("serie"):
            serie = sorted([x for x in articles if x.get("serie") == a["serie"]], key=lambda x: int(x.get("ordine", 99)))
        related = [x for x in articles if x["category"] == a["category"] and x is not a and x not in serie][:4]
        write(ROOT / a["category"] / a["slug"] / "index.html", env.get_template("article.html").render(
            **base_ctx, a=a, related=related, serie=serie, page_url=a["url"],
            title=f"{a['title']} · {CONFIG['name']}", description=a["description"]))

    # pagine fisse
    for p in pages:
        write(ROOT / p["slug"] / "index.html", env.get_template("page.html").render(
            **base_ctx, p=p, page_url=p["url"],
            title=f"{p['title']} · {CONFIG['name']}", description=p.get("description", "")))

    # 404
    write(ROOT / "404.html", env.get_template("404.html").render(
        **base_ctx, page_url="/404.html", title=f"Pagina non trovata · {CONFIG['name']}",
        description=""))

    # sitemap, robots, feed
    urls = (["/", "/dossier/", "/il-punto/", "/numeri/", "/rassegna/", "/mappa/"] + [c["url"] for c in categories]
            + [a["url"] for a in articles] + [n["url"] for n in numeri] + [p["url"] for p in pages])
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        last = next((a["updated_iso"] for a in articles if a["url"] == u), base_ctx["build_date"])
        sitemap.append(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{last}</lastmod></url>")
    sitemap.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sitemap))
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nDisallow: /_src/\nSitemap: {SITE_URL}/sitemap.xml\n")

    feed = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0"><channel>',
            f"<title>{html.escape(CONFIG['name'])}</title>",
            f"<link>{SITE_URL}/</link>",
            f"<description>{html.escape(CONFIG['description'])}</description>",
            "<language>it-it</language>"]
    for a in articles[:20]:
        feed.append("<item>"
                    f"<title>{html.escape(a['title'])}</title>"
                    f"<link>{SITE_URL}{a['url']}</link>"
                    f"<guid>{SITE_URL}{a['url']}</guid>"
                    f"<pubDate>{dt.datetime.fromisoformat(a['date_iso']).strftime('%a, %d %b %Y 08:00:00 +0100')}</pubDate>"
                    f"<description>{html.escape(a['description'])}</description>"
                    "</item>")
    feed.append("</channel></rss>")
    write(ROOT / "feed.xml", "\n".join(feed))

    # .htaccess: protegge i sorgenti, pagina 404, compressione e cache
    write(ROOT / ".htaccess", "\n".join([
        "RedirectMatch 404 ^/_src/",
        "ErrorDocument 404 /404.html",
        "AddDefaultCharset UTF-8",
        "<IfModule mod_deflate.c>",
        "  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml application/xml",
        "</IfModule>",
        "<IfModule mod_expires.c>",
        "  ExpiresActive On",
        "  ExpiresByType text/css \"access plus 7 days\"",
        "  ExpiresByType image/svg+xml \"access plus 30 days\"",
        "  ExpiresByType image/png \"access plus 30 days\"",
        "  ExpiresByType image/webp \"access plus 30 days\"",
        "</IfModule>",
        "",
    ]))

    print(f"Sito generato: {len(articles)} articoli, {len(numeri)} schede Numeri, {len(pages)} pagine.")


if __name__ == "__main__":
    build()
