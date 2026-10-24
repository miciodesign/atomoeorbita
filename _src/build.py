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
def load_articles() -> list[dict]:
    articles = []
    for path in sorted((CONTENT / "articoli").glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("draft") == "true":
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
        articles.append(article)
    articles.sort(key=lambda a: a["date_iso"], reverse=True)
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
    write(ROOT / "mappa" / "index.html", env.get_template("mappa.html").render(
        **base_ctx, centrali=centrali, spazio=spazio, c_sites=len(centrali),
        c_reactors=sum(c["r"] for c in centrali), page_url="/mappa/",
        title=f"Mappa delle centrali nucleari e delle basi spaziali · {CONFIG['name']}",
        description="Mappa interattiva delle centrali nucleari operabili nel mondo, degli spazioporti e dei siti spaziali italiani, con fonti e limiti dei dati."))

    # numeri
    write(ROOT / "numeri" / "index.html", env.get_template("numeri.html").render(
        **base_ctx, numeri=numeri, page_url="/numeri/",
        title=f"Numeri · {CONFIG['name']}",
        description="Schede dati aggiornate su nucleare e spazio: reattori, lanci, progetti, aziende. Sempre con la fonte."))
    for n in numeri:
        write(ROOT / "numeri" / n["slug"] / "index.html", env.get_template("numero.html").render(
            **base_ctx, n=n, page_url=n["url"],
            title=f"{n['title']} · Numeri · {CONFIG['name']}", description=n.get("description", "")))

    # articoli
    for a in articles:
        related = [x for x in articles if x["category"] == a["category"] and x is not a][:4]
        write(ROOT / a["category"] / a["slug"] / "index.html", env.get_template("article.html").render(
            **base_ctx, a=a, related=related, page_url=a["url"],
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
        "  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml",
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
