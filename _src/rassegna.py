#!/usr/bin/env python3
"""Rassegna quotidiana: legge i feed delle fonti specialistiche e scrive
_src/content/rassegna.json con le notizie delle ultime 48 ore.

Eseguito ogni mattina da GitHub Actions (.github/workflows/rassegna.yml),
che poi rigenera il sito e fa il push. Non sceglie e non commenta: elenca.

Uso:  python3 _src/rassegna.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_src" / "content" / "rassegna.json"

# (sezione, nome fonte, url feed, lingua)
FEEDS = [
    ("atomo", "World Nuclear News", "https://www.world-nuclear-news.org/rss", "en"),
    ("atomo", "POWER Magazine", "https://www.powermag.com/category/nuclear/feed/", "en"),
    ("atomo", "IAEA", "https://www.iaea.org/feeds/topnews", "en"),
    ("atomo", "NucNet", "https://www.nucnet.org/feed", "en"),
    ("atomo", "Qualenergia", "https://www.qualenergia.it/feed/", "it"),
    ("orbita", "SpaceNews", "https://spacenews.com/feed/", "en"),
    ("orbita", "ESA", "https://www.esa.int/rssfeed/TopNews", "en"),
    ("orbita", "ASI", "https://www.asi.it/feed/", "it"),
    ("orbita", "AstronautiNEWS", "https://www.astronautinews.it/feed/", "it"),
    ("orbita", "European Spaceflight", "https://europeanspaceflight.com/feed/", "en"),
]

# Per le fonti generaliste di energia tengo solo i pezzi sul nucleare.
KEYWORD_FILTER = {
    "Qualenergia": re.compile(r"nuclear|nuclea|smr|reattor|fusion|uranio|scorie|atomo", re.I),
}

WINDOW_HOURS = 48
MAX_PER_SECTION = 12


def entry_time(e) -> dt.datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        t = e.get(key)
        if t:
            return dt.datetime(*t[:6], tzinfo=dt.timezone.utc)
    return None


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    import feedparser  # installato dal workflow; non serve per generare il sito

    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(hours=WINDOW_HOURS)
    items = []
    errors = []
    for section, source, url, lang in FEEDS:
        try:
            feed = feedparser.parse(url, agent="AtomoEOrbita-Rassegna/1.0 (+https://atomoeorbita.it)")
        except Exception as exc:  # pragma: no cover
            errors.append(f"{source}: {exc}")
            continue
        if feed.bozo and not feed.entries:
            errors.append(f"{source}: feed non leggibile")
            continue
        flt = KEYWORD_FILTER.get(source)
        for e in feed.entries:
            when = entry_time(e)
            if not when or when < since:
                continue
            title = clean(e.get("title", ""))
            link = e.get("link", "")
            if not title or not link:
                continue
            summary = clean(e.get("summary", ""))[:220]
            if flt and not flt.search(title + " " + summary):
                continue
            items.append({
                "section": section,
                "source": source,
                "lang": lang,
                "title": title,
                "url": link,
                "summary": summary,
                "time": when.isoformat(),
            })

    # dedup per url, ordina per data, taglia per sezione
    seen = set()
    uniq = []
    for it in sorted(items, key=lambda x: x["time"], reverse=True):
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        uniq.append(it)
    out = {"atomo": [], "orbita": []}
    for it in uniq:
        if len(out[it["section"]]) < MAX_PER_SECTION:
            out[it["section"]].append(it)

    payload = {
        "updated": now.isoformat(),
        "window_hours": WINDOW_HOURS,
        "sources": [{"name": s, "url": u, "section": sec} for sec, s, u, _ in FEEDS],
        "errors": errors,
        "atomo": out["atomo"],
        "orbita": out["orbita"],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rassegna: {len(out['atomo'])} Atomo, {len(out['orbita'])} Orbita; errori: {len(errors)}")
    for err in errors:
        print("  -", err, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
