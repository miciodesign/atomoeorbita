# Redazione di Atomo e Orbita

Manuale operativo per chi scrive e pubblica, compreso Claude in una conversazione nuova. Leggere tutto prima di scrivere il primo pezzo.

## Identità

- **Nome**: Atomo e Orbita. Nel logo si scrive "Atomo & Orbita"; ovunque sia testo (titoli, email, social, firme) si scrive con la "e".
- **Sito**: https://atomoeorbita.it (il .com rimanda al .it). Email: redazione@atomoeorbita.it.
- **Payoff**: Energia e spazio, senza semplificazioni.
- **Claim**: Le tecnologie che decideranno i prossimi trent'anni, spiegate a chi deve capirle.
- **Missione**: spiegare in modo chiaro e verificabile nucleare e spazio a chi lavora, investe o decide. Analisi, non notizie.
- **Visione**: il punto di riferimento in italiano che un ingegnere, un analista e un decisore pubblico possono citare insieme.
- **Palette**: grafite #121417, testo #E8ECEF, accento verde reattore #3DDCC8. Titoli Space Grotesk maiuscolo spaziato, testo Source Serif 4.

## Regole di scrittura

1. **Fonti primarie prima di tutto**: documenti ufficiali, atti parlamentari, bilanci, dati di agenzie (IAEA, ESA, ASI, ISIN, Eurostat). La stampa si linka solo quando aggiunge qualcosa. Ogni numero ha fonte e data.
2. **Cercare sempre prima di scrivere**: niente dati a memoria su fatti recenti. Verificare con ricerca web e, quando possibile, leggere il documento originale.
3. **Né pro né contro**: niente tifo per o contro nucleare, spazio pubblico o privato. Si descrive cosa funziona, cosa costa, chi decide, cosa manca.
4. **Dire quando non si sa**: l'incertezza fa parte dell'analisi.
5. **Niente numeri inventati, niente placeholder nei pezzi pubblicati**: se un dato non si trova, si scrive che non è pubblico.
6. **Tono**: diretto, sobrio, concreto. Frasi corte. Niente "rivoluzione", "svolta epocale", "game changer". Spiegare le sigle alla prima occorrenza. Dare sempre un ordine di grandezza per i numeri grandi.
7. **Struttura tipo**: apertura con il fatto e perché conta; sezioni con titoli H2; dove serve una tabella; chiusura "Cosa guardare" o "In sintesi" con 3 punti concreti; riga finale in corsivo con le fonti principali linkate.
8. **Link interni**: ogni articolo linka almeno un altro articolo del sito quando pertinente.
9. **Lunghezze**: Il Punto 600-800 parole; analisi e Spiegato bene 1.200-1.600; Dossier 3.000+.
10. **Rileggere**: prima di pubblicare, controllare date, cifre e nomi contro la fonte.

## Formati (campo `format` nel front matter)

- `punto` – Il Punto, settimanale, categoria `confine`. È anche la newsletter.
- `analisi` – analisi su un tema di attualità con dati.
- `spiegato` – Spiegato bene: pezzo didattico senza scadenza.
- `dossier` – approfondimento mensile con tabelle e dati scaricabili.
- `intervista` – una al mese, dal quarto mese.

## Sezioni (campo `category`)

- `atomo` – fissione, SMR, fusione, ciclo del combustibile, scorie, politica energetica.
- `orbita` – lanciatori, satelliti, esplorazione, difesa, economia spaziale, Italia ed ESA.
- `confine` – dove i due mondi si toccano: propulsione nucleare spaziale, reattori per lo spazio, materiali critici, geopolitica delle infrastrutture. Qui esce Il Punto.

## Calendario

- **Lunedì**: Il Punto (confine, 600-800 parole). Dopo la pubblicazione, inviarlo come newsletter da Brevo (lista "Atomo e Orbita", mittente redazione@atomoeorbita.it, nome mittente "Atomo e Orbita").
- **Mercoledì**: Atomo. **Venerdì**: Orbita. Ogni due settimane uno dei due è uno Spiegato bene.
- **Ultimo venerdì del mese**: Dossier.
- **Schede Numeri**: quando c'è un dato nuovo dalla fonte.
- La **Rassegna** si aggiorna da sola ogni mattina (GitHub Actions, `_src/rassegna.py`).

Primo Punto: lunedì 26 ottobre 2026. Primo Dossier: fine ottobre 2026.

## Scaletta prossimi pezzi

**Dossier 1 – Nucleare in Italia: la mappa completa** (fine ottobre): legge 169/2026, decreti attuativi attesi, attori (MASE, ISIN, Sogin, Nuclitalia, Edison/EDF/Nuward, Newcleo, Ansaldo), siti e Deposito nazionale, aziende quotate, tempi. Tabelle: attori e ruoli; calendario; aziende e capitalizzazione.

**Idee per Il Punto** (una a settimana, scegliere in base all'attualità):
- La scelta di Nuclitalia sul design SMR (attesa novembre 2026)
- Fusione Airbus-Leonardo-Thales: cosa resta a Torino
- Themis: il primo salto del dimostratore riutilizzabile europeo
- La costellazione nazionale annunciata da Urso: cosa si sa
- HALEU: perché l'Europa non ha un piano
- IRIS²: dal contratto al primo lancio

**Atomo in coda**: fusione (ITER, progetti privati, Eni-CFS); il Deposito nazionale regione per regione; costo del kWh nucleare, cosa dicono i contratti veri (Hinkley, Dukovany); Italia e il PNIEC.

**Orbita in coda**: **costellazioni satellitari: quanto costano, a cosa servono, chi le fa in Italia** (priorità: Search Console mostra già ricerche su costi, casi d'uso e osservazione della Terra); Vega E e il motore M10; COSMO-SkyMed terza generazione; Space Rider; l'astronauta italiano su Artemis; i dati satellitari come servizio.

**Search Console (25 ottobre 2026)**: le pagine con più impressioni e zero clic erano SMR (60), Italia nello spazio (55) e satelliti militari (48). Il 25 ottobre ho ritoccato i titoli sulle ricerche reali: "cosa significa SMR", "Agenzia Spaziale Italiana" e "NASA italiana", "satellite militare", "centrali nucleari nel mondo". Ricontrollare a metà novembre.

**Schede Numeri da fare**: inventario rifiuti radioattivi per regione (ISIN); reattori nel mondo (fatta, aggiornare a ogni revisione WNA); lanci orbitali dell'anno; SMR in Europa per stato di avanzamento; satelliti italiani in orbita; contributi ESA per paese.

## Come si pubblica

1. Scrivere il file in `_src/content/articoli/AAAA-MM-GG-slug.md` con front matter: `title`, `slug`, `category`, `date`, `description`, `format`; opzionali `pillar: true`, `updated`, `draft: true`, `foto`. La `foto` è la foto d'apertura da Wikimedia Commons: `foto: File:Nome_esatto.jpg` oppure `foto: en:Titolo voce Wikipedia` (prende la foto principale della voce), più alternative separate da `|` (anche `cerca:parole chiave`). Il workflow `foto.yml` parte da solo al push dell'articolo, salva autore e licenza in `_src/data/foto.json` e ricostruisce il sito: dopo il push aspettare un minuto, fare pull e controllare in `foto.json` che la foto mostri davvero il soggetto (niente loghi, schemi, impianti vicini o omonimi). Se è sbagliata, indicare un `File:` preciso. Le foto della mappa si correggono con `ESCLUSI` e `SPAZIO_CERCA` in `_src/foto_mappa.py`.
2. `python3 _src/build.py` (serve `pip install markdown jinja2`).
3. Prima del commit: `git pull --rebase origin main`, perché la Rassegna fa un commit automatico ogni mattina. Se ci sono conflitti sui file HTML generati, rilanciare `python3 _src/build.py`, `git add -A` e continuare. Poi commit e push su `main` del repository `miciodesign/atomoeorbita`. Hostinger pubblica da solo.
4. Verificare la pagina online. Per Il Punto, inviare la newsletter da Brevo con lo stesso testo e il link all'articolo.

Le pagine fisse stanno in `_src/content/pagine/`, le schede Numeri in `_src/content/numeri/` (campi `title`, `slug`, `updated`, `source`, `headline`, `description`).

## Cosa non si fa

- Nessun banner, ticker o pubblicità. Nessun contenuto sponsorizzato né guest post.
- Nessun piano a pagamento finché la testata non ha costruito autorevolezza e una lista email: quando sarà il momento, piano "Analista" intorno ai 9 €/mese e piano Team da 5 licenze.
- Affiliazioni (Amazon per i libri, corsi) solo nella pagina Risorse, dichiarate, e solo quando c'è traffico.
- Nessun tracciamento con cookie: se servono statistiche, Search Console o uno strumento senza cookie.

## Decisioni rinviate

- **Versione inglese**: no per ora. Il vantaggio della testata è l'italiano; in inglese concorrono testate con redazioni vere. Da riconsiderare se Search Console mostra lettori dall'estero: in quel caso tradurre solo Dossier e schede Numeri, non tutto il sito.
- **Abbonamento a pagamento**: quando c'è autorevolezza e una lista email di qualche migliaio di iscritti.
- **Affiliazioni**: Amazon per i libri nella pagina Risorse, quando c'è traffico (Amazon chiude l'account senza 3 vendite in 180 giorni).
- **Instagram**: no per ora (niente link nei post, serve materiale visivo dedicato, il nostro lettore è su LinkedIn). Registrare solo il nome @atomoeorbita con logo e link al sito, senza pubblicare.
- **Banner o ticker di notizie**: no. La Rassegna quotidiana è la risposta a quel bisogno.

## Strumenti e accessi

- Hosting: Hostinger, deploy da GitHub (`miciodesign/atomoeorbita`, ramo `main`).
- Email: Hostinger, `redazione@atomoeorbita.it`, con inoltro alla casella personale del direttore.
- Newsletter: Brevo, lista "Atomo e Orbita", modulo con doppia conferma; pagine `/grazie/` e `/benvenuto/`.
- Google Search Console: proprietà verificata con file HTML nella radice (non cancellarlo); sitemap inviata.
- Social: Pagina Facebook e Pagina LinkedIn `atomoeorbita`, linkate nel footer.
- Rassegna: GitHub Actions `.github/workflows/rassegna.yml`, ogni giorno alle 04:40 UTC; fonti in `_src/rassegna.py`.

## Per Claude, in una conversazione nuova

Leggere questo file, poi `_src/config.json` e gli ultimi articoli in `_src/content/articoli/` per il tono. Prima di scrivere, cercare le fonti. Prima di pubblicare, dire al direttore cosa si sta per pubblicare in una riga; se ha detto "procedi", pubblicare e riassumere. Rispondere sempre in italiano.
