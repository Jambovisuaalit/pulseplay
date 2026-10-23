# PR #12 — teknisen loppuhyväksynnän valmistelu

Käyttäjä hyväksyi automaattisen QA:n GitHub Actions -ajosta
[39879845550](https://github.com/Jambovisuaalit/pulseplay/actions/runs/39879845550).
GitHubin rajapinnasta varmennettu tulos: `completed / success`, commit
`f6577d5ed4f8cb2c1e73c5f027f1cc4bb1a0232e`. Tämä hyväksyntä koskee kyseistä
committia; myöhemmät testimuutokset tarvitsevat oman CI-tuloksensa.

## Hyväksymisportit

| Portti | Tila | Tarvittava näyttö |
| --- | --- | --- |
| Alkuperäinen automaattinen QA | Käyttäjän hyväksymä | Yllä linkitetty onnistunut ajo ja täsmäävä SHA |
| Autentikoitu Vercel Preview → Supabase | AVOIN | Aidot kirjautumiset, suojatut istunnot, HTTP-luku ja kirjoituksen löytyminen oikeasta Supabase-työtilasta |
| Samanaikainen HTTP-tallennus | AVOIN | Kaksi erillistä istuntoa, 200/409, yksi voittanut kirjoitus, yksi versioaskel ja muuttumattomat aiemmat asiakkaat |
| Erillisen varmuuskopion palautus | AVOIN | Riippumaton tiedosto, erillinen sitoutunut palautus ja täsmäävä uudelleenluku uudessa prosessissa oikeasta Supabasesta |
| Preview-uudelleenkäynnistyksen yli säilyminen | AVOIN | Erillinen oikean Preview-palvelimen uudelleenkäynnistys ja tallennetun tilan uudelleenluku |
| PR:n tila | Draft | Ei yhdistämistä eikä tuotantoon julkaisua |

## Testimuutokset

- `tests/preview-hosted-e2e.mjs` käyttää kahta aidosti eri istuntoa, eri
  kirjoitusmerkkejä ja lukee Supabasen rivin suoraan vertailuksi. Vanhentuneen
  komennon uusinta ja CSRF-esto eivät saa muuttaa tallennusversiota.
- `tests/preview-backup-restore.mjs` suorittaa varmuuskopioinnin, palautuksen ja
  varmennuksen erillisinä prosesseina. Palautus ei ylikirjoita aiempaa työtilaa.
  Varmennus vertaa myös hyväksyntähistoriaa ja mittauksia sekä käyttää uutta
  sovellusadapteria.
- Paikallinen PostgreSQL-testiajo tarkistaa palautusohjelman toiminnan ilman
  hosted-tunnuksia. Se ei korvaa oikeaa Vercel/Supabase-ajoa.
- Sovelluslogiikkaa, riippuvuusmäärityksiä tai tuotantoasetuksia ei muuteta
  näiden testien vuoksi. PR12 CI saa palautusohjelman paikallisen regressioajon
  ja uuden hosted-ohjelman syntaksitarkistuksen.

## Varmennettu Preview-kohde ja pääsyeste

GitHubin deployment `7267251281` on `success`, ympäristö `Preview – tenderpulse`,
commit `b4b5d9a1f9b0806d16b5f9cb6bdecf1d66ff2565`, osoite
`https://tenderpulse-fch3db8x2-info-32533854s-projects.vercel.app`.
Sovellushakemistojen `app/`, `lib/`, middlewaren, Next-konfiguraation sekä
pakettimääritysten ja lukitustiedoston diffi tämän version ja hyväksytyn
`f6577d5`-version välillä on tyhjä. Mahdolliseen testiraporttiin merkitään silti
todellinen deployment-versio; nykyisen PR-HEADin deploymentia ei oleteta samaksi.

Kirjautumaton `/api/ops` palauttaa HTTP 302 -ohjauksen Vercel SSO:hon. Tämä
todistaa suojauskerroksen, ei sovelluksen autentikoinnin tai tietokannan toimintaa.
Tässä pilvikoneessa tarvittavia Preview-tunnuksia ei ole. GitHub-integraatio saa
lukea PR:n ja Actions-tulokset, mutta Actions-salaisuuksien ja muuttujien
listaus estyy HTTP 403:lla. Se ei todista, ettei GitHubissa olisi jo tunnuksia.

Tarvittavat turvalliset sidonnat: `PREVIEW_E2E_PASSWORD`,
`VERCEL_AUTOMATION_BYPASS_SECRET`, `TP_SUPABASE_SECRET_KEY`. Ei-salaiset
kohdeasetukset: `PREVIEW_E2E_URL`, `PREVIEW_E2E_DEPLOYMENT_ID`, `PREVIEW_E2E_USERNAME`,
`PREVIEW_E2E_WORKSPACE` ja `TP_SUPABASE_URL`. Työtilan nimen on täsmättävä
Vercelin haararajattuun Preview-asetukseen. Supabase-kohde on aiemmassa PR-työssä
valittu `kzcmzelxydrhxxhcmmua`; muita projekteja ei käytetä.

Vaatimukset on tallennettu pilviympäristön asetusten luonnokseen arvojen
turvallista syöttöä varten. Tallennus ei aseta tunnuksia tähän prosessiin.
Jos tunnukset ovat jo olemassa GitHub-ympäristössä, käytetään olemassa olevia
sidontoja ja niiden täsmällisiä nimiä; arvoja ei tuoda keskusteluun tai lokiin.

## Jatko

Paikallisesti todennettu testivalmistelu: kaikki 34 Node- ja 18 Python-testiä;
lint, typecheck ja tuotantokäännös; 26 PostgreSQL-oikeus-/RLS-/versiotarkistusta;
20 autentikoinnin HTTP-tarkistusta; erillinen PGlite-palautusohjelman
prosessi-integraatiotesti. Nämä ovat paikallista regressiotodistetta, eivät
hyväksyntä avoimille hosted-porteille. Haaran vaihdon jälkeen poistettiin vain
edellisen haaran vanhentuneet generoidut Next-tyypit ja rakennettiin oikeat
tyypit uudelleen; lähdekoodikorjausta ei tarvittu.

Suoritusohjeet ja raporttien rajaukset:
[preview-hosted-e2e.md](preview-hosted-e2e.md). Kolmea avointa testiä ei merkitä
hyväksytyiksi ennen niiden todellista suoritusta ja näyttöjen tarkastusta.
Testiraportit tarvitsevat ajankohdan, deployment-version, kohteen ja testin
rajauksen. Tuotanto edellyttää myöhemmin omaa erillistä päätöstä.
