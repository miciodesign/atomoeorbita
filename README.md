# Atomo e Orbita

Sito atomoeorbita.it: energia e spazio, senza semplificazioni. Analisi su nucleare e spazio per chi lavora, investe o decide.

## Come funziona

- I contenuti stanno in `_src/content` come file Markdown con un piccolo front matter.
- `python3 _src/build.py` genera l'HTML nella radice del repository.
- Hostinger pubblica la radice: ogni push sul ramo principale aggiorna il sito.

## Contenuti

- `_src/content/articoli/AAAA-MM-GG-slug.md` – articoli. Campi: `title`, `slug`, `category` (atomo, orbita, confine), `date`, `description`, `format` (punto, analisi, spiegato, dossier, intervista); opzionali `updated`, `pillar: true`, `draft: true`, `image`.
- `_src/content/numeri/slug.md` – schede dati per la sezione Numeri. Campi: `title`, `slug`, `updated`, `source`, `description`.
- `_src/content/pagine/slug.md` – pagine fisse (manifesto, contatti, privacy, risorse, glossario).

## Requisiti per generare

```
pip install markdown jinja2
python3 _src/build.py
```
