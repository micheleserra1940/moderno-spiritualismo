# Moderno Spiritualismo

Biblioteca statica per GitHub Pages. Prima pubblicazione: **Hydesville, l’inizio**, E. E. Lewis, traduzione e commenti di Michele Serra.

## Struttura

- `site/`: sito completo, senza compilazione e senza dipendenze esterne.
- `site/leggi.html`: testo integrale disponibile, indice dei capitoli e preferenze di lettura salvate solo nel browser.
- `site/assets/`: PDF con caratteri incorporati, copertina PNG e copertina vettoriale SVG.
- `scripts/build_book.py`: ricostruisce PDF e lettura online dal Word originale.
- `templates/reader.html`: struttura della pagina di lettura.

## Anteprima locale

Avviare un server statico dalla cartella `site`, per esempio `python -m http.server 4173 --directory site`, e aprire `http://localhost:4173`.

## Rigenerazione del libro

Installare `requirements.txt`, poi eseguire `python scripts/build_book.py` dalla radice. Il generatore usa Georgia e Arial della cartella Fonts di Windows. I Word di partenza rimangono invariati. L’indice cartaceo originario viene sostituito da un indice coerente con la nuova impaginazione, con collegamenti interni nel PDF.

## Nota sul manoscritto

Il Word non contiene i due documenti inglesi citati nell’indice. Questi sono stati aggiunti all’appendice a partire dal PDF fornito successivamente: rapporto di E. E. Lewis (34 pagine) e confessione di Margaret Fox Kane (3 pagine). Le trascrizioni revisionate sono conservate in `sources/appendici/`; le riproduzioni delle pagine, ottimizzate per il web e con testo selezionabile, sono in `site/assets/appendice-lewis-en.pdf` e `site/assets/appendice-fox-en.pdf`. Il generatore le unisce al libro e inserisce le trascrizioni nella lettura online. La confessione proviene da una stampa web che riporta il testo del 1888. Le grafie e i refusi della copia sono conservati; menu e pubblicità non sono inclusi nella trascrizione online.

`scripts/prepare_appendix.py` prepara i due PDF ottimizzati e copia le trascrizioni dagli elaborati locali in `output/appendici-inglesi/`. Non è necessario rieseguirlo per rigenerare il libro: i documenti preparati e le trascrizioni sono già versionati. Gli elaborati di revisione e i registri delle correzioni rimangono in `output/`, esclusa dal repository.

La presentazione di Michele Serra e il suo recapito email sono stati forniti per la pubblicazione.

## Pubblicazione

Il workflow `.github/workflows/pages.yml` pubblica la cartella `site/` su GitHub Pages a ogni aggiornamento di `main`. Nelle impostazioni Pages del repository la sorgente deve essere **GitHub Actions**. Word e strumenti rimangono nei sorgenti del repository. Nessun tracciamento, nessuna richiesta di registrazione, nessuna risorsa caricata da servizi esterni.

Indirizzo del sito: https://micheleserra1940.github.io/moderno-spiritualismo/

Per verificare contenuti e collegamenti locali: `python scripts/verify.py` (richiede anche `pypdf`).
