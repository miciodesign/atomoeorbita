import re, markdown, pathlib, subprocess
from bs4 import BeautifulSoup
SRC = pathlib.Path("/home/claude/atomoeorbita/_src/ebook")
OUT = pathlib.Path("/home/claude/ebook")
FIG = {  # capitolo: (sezione dopo cui inserire, didascalia)
 "cap01": ("La reazione a catena", "Fig. 1 — La reazione a catena: ogni nucleo che si spezza libera neutroni che ne spezzano altri."),
 "cap02": ("Dal calore all'elettricità", "Fig. 2 — Il percorso dell'energia in una centrale nucleare."),
 "cap04": ("Dove sono e dove andranno", "Fig. 3 — Che cosa ospiterà il Deposito nazionale."),
 "cap07": ("Le orbite principali", "Fig. 4 — Le tre orbite principali, a confronto."),
}
caps = sorted(SRC.glob("cap*.md"))
body = []
for i, f in enumerate(caps, 1):
    key = f.name[:5]
    html = markdown.markdown(f.read_text(), extensions=["tables"])
    s = BeautifulSoup(html, "html.parser")
    h1 = s.find("h1")
    title = re.sub(r"^\d+\.\s*", "", h1.get_text())
    h1.replace_with(BeautifulSoup(f'<div class="eyebrow">CAPITOLO {i} · NUCLEARE E SPAZIO, SPIEGATI BENE</div><h1><span class="n">{i}.</span> {title}</h1>', "html.parser"))
    for bq in s.find_all("blockquote"):
        t = bq.get_text()
        bq["class"] = "breve" if t.startswith("In breve") else ("numero" if t.startswith("Il numero chiave") else "cita")
    for h2 in s.find_all("h2"):
        if h2.get_text().startswith("Box."):
            box = s.new_tag("div", attrs={"class": "box"})
            h2.string = h2.get_text()[4:].strip()
            sib = list(h2.next_siblings); h2.wrap(box)
            for x in sib:
                if getattr(x, "name", None) == "h2": break
                box.append(x.extract())
        if h2.get_text() == "Collegamenti":
            h2["class"] = "coll"
    if key in FIG:
        sec, cap = FIG[key]
        h = s.find("h2", string=sec)
        # inserisci prima del titolo successivo
        nxt = h.find_next("h2")
        fig = BeautifulSoup(f'<figure>{(OUT/"fig"/(key+".svg")).read_text()}<figcaption>{cap}</figcaption></figure>', "html.parser")
        nxt.insert_before(fig)
    last = s.find_all("p")[-1]
    if last.get_text().startswith("Approfondisci"):
        last["class"] = "appro"
    cls = "cap glossario" if "glossario" in f.name else "cap"
    body.append(f'<section class="{cls}">{s}</section>')

toc = "".join(f'<li><span>{i}</span>{re.sub(r"^# \d+\.\s*","",f.read_text().splitlines()[0])}</li>' for i, f in enumerate(caps, 1))
cover = (SRC/"copertina.html").read_text()
cover_inner = re.search(r'<div class="p">.*</div></body>', cover, re.S).group(0)[:-7]
cover_css = re.search(r"<style>(.*?)</style>", cover, re.S).group(1)
cover_css = cover_css.replace("url(fr.woff2)", "url(fraunces.woff2)").replace("url(fri.woff2)", "url(fraunces-italic.woff2)").replace("url(mono.woff2)", "url(ibm-plex-mono-latin-500-normal.woff2)").replace("url(nr.woff2)", "url(newsreader.woff2)")
cover_css = cover_css.replace("body{margin:0}", "")
cover_css = re.sub(r"(^|\})\s*(h1|\.)", lambda m: m.group(0), cover_css)
# scala la copertina (1240x1754) su A4 (794x1123 px)
html = f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Nucleare e spazio, spiegati bene</title><style>
{cover_css.replace('h1{', '.cov h1{').replace('.p{', '.cov .p{')}
@page{{size:A4;margin:18mm 20mm 20mm}}
@page:first{{margin:0}}
@font-face{{font-family:N;font-style:italic;src:url(newsreader-italic.woff2)}}
html{{background:#FBF8F2}}
body{{margin:0;font-family:N;font-size:10.9pt;line-height:1.5;color:#1C1B18}}
.cov{{width:210mm;height:297mm;overflow:hidden;break-after:page}}
.cov .p{{transform:scale(.6403);transform-origin:0 0}}
.eyebrow{{font:500 8pt M;letter-spacing:.16em;color:#B4321C;margin-bottom:6mm}}
section.cap{{break-before:page}}
h1{{font:600 30pt/1.05 F;letter-spacing:-.01em;margin:0 0 7mm}}
h1 .n{{color:#B4321C}}
h2{{font:600 15pt/1.2 F;margin:7mm 0 2.5mm;break-after:avoid}}
p,li{{orphans:3;widows:3}}
ul,ol{{padding-left:5mm}}
strong{{font-weight:700}}
blockquote{{margin:4mm 0;padding:3.5mm 5mm;break-inside:avoid}}
blockquote p{{margin:0}}
blockquote.breve{{background:#EFE9DC;border-left:3px solid #1C1B18;font-size:11.8pt}}
blockquote.numero{{border:1.5px solid #B4321C;background:#FBF8F2}}
blockquote.numero strong:first-child{{font:600 8pt M;letter-spacing:.14em;text-transform:uppercase;color:#B4321C;display:block;margin-bottom:1.5mm}}
blockquote.cita{{border-left:3px solid #A39A89;font-size:10.5pt}}
table{{width:100%;border-collapse:collapse;margin:3mm 0 4mm;font-size:9.8pt;break-inside:avoid}}
th{{font:500 7.5pt M;letter-spacing:.1em;text-transform:uppercase;color:#6B655A;text-align:left;border-bottom:1.5px solid #1C1B18;padding:1.5mm 2mm}}
td{{border-bottom:1px solid #DDD5C5;padding:1.8mm 2mm;vertical-align:top}}
.box{{background:#1C1B18;color:#F3EFE6;padding:5mm 6mm;margin:5mm 0}}
.box h2{{color:#E4A08F;margin-top:0;font-size:13pt}}
.box strong{{color:#fff}}
h2.coll{{font:600 8.5pt M;letter-spacing:.16em;text-transform:uppercase;border-top:1.5px solid #1C1B18;padding-top:3mm}}
p.appro{{break-before:avoid;font-size:10pt;color:#6B655A;border-top:1px solid #DDD5C5;padding-top:2mm}}
figure{{margin:5mm 0;break-inside:avoid;background:#F3EFE6;padding:4mm 5mm}}
figure svg{{width:100%;height:auto;display:block}}
figcaption{{font:500 7.5pt M;letter-spacing:.06em;color:#6B655A;margin-top:2mm}}
.glossario p{{margin:0 0 1.6mm;font-size:10pt;line-height:1.45}}
.glossario{{column-count:1}}
.pag{{break-before:page}}
.toc ol{{list-style:none;padding:0;margin:6mm 0}}
.toc li{{display:flex;gap:6mm;font:500 13pt F;padding:2.6mm 0;border-bottom:1px solid #DDD5C5}}
.toc li span{{font:500 9pt M;color:#B4321C;width:8mm;padding-top:1.2mm}}
.fine{{text-align:left}}
.fine .big{{font:600 22pt/1.15 F;margin:20mm 0 6mm}}
.mono{{font:500 8pt M;letter-spacing:.12em;color:#6B655A;line-height:1.8}}
a{{color:#B4321C}}
</style></head><body>
<div class="cov">{cover_inner}</div>
<section class="pag toc"><div class="eyebrow">INDICE</div><h1>Che cosa trovi</h1><ol>{toc}</ol>
<h2>Come usare questa guida</h2>
<p>Questa guida è pensata per gli ultimi anni delle superiori e il primo anno di università. Ogni capitolo si apre con un riquadro <strong>In breve</strong>, che riassume l'essenziale in tre righe, e contiene un <strong>numero chiave</strong> da ricordare. Alla fine trovi i <strong>Collegamenti</strong> con le materie scolastiche e i rimandi agli approfondimenti su <a href="https://atomoeorbita.it">atomoeorbita.it</a>.</p>
<p>Il capitolo 10 propone otto percorsi per la tesina e il colloquio di maturità. I numeri sono aggiornati all'autunno 2026 e ognuno viene da una fonte ufficiale, citata nel testo o nel capitolo 12.</p>
<p class="mono">ATOMO E ORBITA · EDIZIONE 2026–2027 · LICENZA CC BY-NC 4.0: PUOI STAMPARLA E CONDIVIDERLA CITANDO LA FONTE, NON VENDERLA.</p></section>
{''.join(body)}
<section class="pag fine"><div class="eyebrow">FINE</div><p class="big">Restiamo in contatto.</p>
<p>Ogni lunedì <strong>Il Punto</strong>, la newsletter gratuita di Atomo e Orbita, racconta in cinque minuti le notizie della settimana su nucleare e spazio, con i numeri e le fonti. Ci si iscrive da <a href="https://atomoeorbita.it">atomoeorbita.it</a>.</p>
<p>Hai trovato un errore o un dato da aggiornare? Scrivici a <a href="mailto:redazione@atomoeorbita.it">redazione@atomoeorbita.it</a>: correggiamo e ringraziamo nella prossima edizione.</p>
<p class="mono" style="margin-top:20mm">NUCLEARE E SPAZIO, SPIEGATI BENE · GUIDA PER STUDENTI<br>ATOMO E ORBITA · EDIZIONE 2026–2027 · NOVEMBRE 2026<br>CC BY-NC 4.0 · ATOMOEORBITA.IT</p></section>
</body></html>"""
(OUT/"guida.html").write_text(html)
print("html ok")
