"""Cerca su Wikidata e Wikimedia Commons una foto per ogni punto della mappa.

Gira su GitHub Actions (il workflow foto.yml), perché serve accesso a Wikimedia.
Scrive _src/data/foto.json: {nome del sito: {thumb, file, autore, licenza, licenza_url}}.
Le foto vengono solo collegate (hotlink da upload.wikimedia.org), con autore e licenza.
"""
import json, math, re, html, time, pathlib, urllib.parse, urllib.request

SRC = pathlib.Path(__file__).parent
UA = "AtomoEOrbitaBot/1.0 (https://atomoeorbita.it; redazione@atomoeorbita.it)"

# Voci di Wikipedia per i siti spaziali (lingua:titolo). Dove la voce avrebbe solo un logo, niente.
SPAZIO_WIKI = {
    "Centre Spatial Guyanais (Kourou)": "en:Guiana Space Centre",
    "Cape Canaveral e Kennedy Space Center": "en:Kennedy Space Center Launch Complex 39",
    "Vandenberg": "en:Vandenberg Space Force Base",
    "Wallops (MARS)": "en:Mid-Atlantic Regional Spaceport",
    "Starbase (Boca Chica)": "en:Starbase",
    "Pacific Spaceport Complex": "en:Pacific Spaceport Complex – Alaska",
    "Rocket Lab Launch Complex 1": "en:Rocket Lab Launch Complex 1",
    "Baikonur": "en:Baikonur Cosmodrome",
    "Vostochny": "en:Vostochny Cosmodrome",
    "Plesetsk": "en:Plesetsk Cosmodrome",
    "Jiuquan": "en:Jiuquan Satellite Launch Center",
    "Taiyuan": "en:Taiyuan Satellite Launch Center",
    "Xichang": "en:Xichang Satellite Launch Center",
    "Wenchang": "en:Wenchang Space Launch Site",
    "Tanegashima": "en:Tanegashima Space Center",
    "Uchinoura": "en:Uchinoura Space Center",
    "Satish Dhawan (Sriharikota)": "en:Satish Dhawan Space Centre",
    "Naro": "en:Naro Space Center",
    "Imam Khomeini (Semnan)": "en:Imam Khomeini Spaceport",
    "Sohae": "en:Sohae Satellite Launching Station",
    "Palmachim": "en:Palmachim Airbase",
    "Alcântara": "en:Alcântara Space Center",
    "Andøya Spaceport": "en:Andøya Space",
    "SaxaVord": "en:SaxaVord Spaceport",
    "Esrange": "en:Esrange",
    "Centro spaziale Luigi Broglio (Malindi)": "en:Broglio Space Center",
    "Spazioporto di Grottaglie": "en:Taranto-Grottaglie Airport",
    "Centro spaziale del Fucino": "en:Fucino Space Centre",
    "ESA ESRIN, Frascati": "en:ESRIN",
    "Centro di geodesia spaziale, Matera": "it:Centro di geodesia spaziale Giuseppe Colombo",
    "Salto di Quirra (Perdasdefogu)": "it:Poligono sperimentale e di addestramento interforze di Salto di Quirra",
}

# Abbinamenti verificati a mano come sbagliati (la foto mostra un impianto vicino o un modellino).
ESCLUSI = {"Lingao", "Fangjiashan", "Tarapur"}

SCARTA = re.compile(r"(logo|locator|location|map|mappa|karte|flag|emblem|seal|insignia|patch|\.svg$)", re.I)


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print("retry", i, e)
            time.sleep(5 * (i + 1))
    raise RuntimeError(url)


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def centrali_wikidata():
    q = """SELECT ?item ?itemLabel ?coord ?image WHERE {
      ?item wdt:P31/wdt:P279* wd:Q134447; wdt:P625 ?coord; wdt:P18 ?image.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr,de,es,ru,zh,ja". }
    }"""
    data = get("https://query.wikidata.org/sparql", {"query": q, "format": "json"})
    out = []
    for b in data["results"]["bindings"]:
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", b["coord"]["value"])
        if not m:
            continue
        f = urllib.parse.unquote(b["image"]["value"].rsplit("/", 1)[-1])
        out.append({"label": b.get("itemLabel", {}).get("value", ""), "lon": float(m[1]), "lat": float(m[2]), "file": f})
    print("Wikidata: centrali con foto", len(out))
    return out


def scegli_centrale(s, cand):
    best, bd = None, 1e9
    tok = norm(s["n"].split("(")[0])[:6]
    for c in cand:
        if SCARTA.search(c["file"]):
            continue
        d = km(s["lat"], s["lon"], c["lat"], c["lon"])
        if tok and tok in norm(c["label"]):
            d -= 6  # il nome coincide: preferiscilo
        if d < bd:
            best, bd = c, d
    return best if best and bd < 6 else None


def pageimage(spec):
    lang, title = spec.split(":", 1)
    d = get(f"https://{lang}.wikipedia.org/w/api.php", {
        "action": "query", "titles": title, "prop": "pageimages", "piprop": "name",
        "redirects": 1, "format": "json", "formatversion": 2})
    pages = d.get("query", {}).get("pages", [])
    if pages and pages[0].get("pageimage"):
        return pages[0]["pageimage"]
    return None


def pulisci(t):
    t = re.sub(r"<[^>]+>", "", html.unescape(t or "")).strip()
    return re.sub(r"\s+", " ", t)[:80]


def info_commons(files):
    res = {}
    files = list(dict.fromkeys(files))
    for i in range(0, len(files), 40):
        chunk = files[i:i + 40]
        d = get("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "titles": "|".join("File:" + f for f in chunk),
            "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1200,
            "format": "json", "formatversion": 2})
        norm_map = {n["to"]: n["from"] for n in d.get("query", {}).get("normalized", [])}
        for p in d.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                continue
            md = ii.get("extmetadata", {})
            lic = pulisci(md.get("LicenseShortName", {}).get("value"))
            if not lic:
                continue
            key = p["title"][5:]
            res[key] = {
                "thumb": ii.get("thumburl") or ii["url"],
                "file": ii.get("descriptionurl"),
                "autore": pulisci(md.get("Artist", {}).get("value")) or "autore su Commons",
                "licenza": lic,
                "licenza_url": md.get("LicenseUrl", {}).get("value", ""),
            }
        time.sleep(1)
    return res


def main():
    centrali = json.loads((SRC / "data/centrali.json").read_text(encoding="utf-8"))["sites"]
    spazio = json.loads((SRC / "data/spazio.json").read_text(encoding="utf-8"))["sites"]
    scelte = {}
    cand = centrali_wikidata()
    for s in centrali:
        c = None if s["n"] in ESCLUSI else scegli_centrale(s, cand)
        if c:
            scelte[s["n"]] = (c["file"], c["label"])
    for s in spazio:
        spec = SPAZIO_WIKI.get(s["n"])
        if spec:
            f = pageimage(spec)
            if f and not SCARTA.search(f):
                scelte[s["n"]] = (f, spec)
            time.sleep(0.5)
    # articoli: riga "foto: en:Titolo voce" oppure "foto: File:Nome.jpg" nel front matter
    for art in sorted((SRC / "content/articoli").glob("*.md")):
        t = art.read_text(encoding="utf-8")
        m, sl = re.search(r"^foto:\s*(.+)$", t, re.M), re.search(r"^slug:\s*(.+)$", t, re.M)
        if not (m and sl):
            continue
        spec = m[1].strip().strip('"')
        f = spec[5:] if spec.startswith("File:") else pageimage(spec)
        if f:
            scelte["articolo:" + sl[1].strip()] = (f, spec)
        time.sleep(0.5)
    info = info_commons([f for f, _ in scelte.values()])
    out = {}
    for n, (f, origine) in scelte.items():
        k = f.replace("_", " ")
        k = k[0].upper() + k[1:]
        if k in info:
            out[n] = dict(info[k], origine=origine)
    print("Foto trovate:", len(out), "su", len(centrali) + len(spazio))
    (SRC / "data/foto.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
