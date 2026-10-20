# Portaalin pysyvän tallennuksen toteutus – 20.10.2026

Tila: adapteri ja paikalliset testit valmiit; ei kytketty eikä julkaistu.
Pohja: myynti- ja portaalihaara `feature/urakkaluotsi-sales-polish`, `1a2a10d`.

## Toteutus

`lib/server/ops-database.ts` käyttää Supabasen HTTPS Data API:a palvelimelta ilman uutta sovellusriippuvuutta. `ops-store.ts` valitsee tietokannan vain asetuksella `TP_OPS_STORE=supabase`. Nykyinen palvelimen allekirjoitettu operaattori-istunto ja saman originin tarkistus säilyvät API-reitillä. Tämä on yhden sisäisen operaattorin malli, ei asiakasportaali tai Supabase Auth -käyttäjähallinta.

Ensimmäinen tallennus käyttää INSERTiä; myöhemmät käyttävät atomista workspace_id + storage_version -ehtoa. Kilpaileva muutos palauttaa 409. Komentoa ei ajeta automaattisesti uudelleen. Aikakatkaisu tai epäselvä tallennuskuittaus palauttaa 503; lataamalla tilan uudelleen operaattori selvittää, tallentuiko muutos. Ei paikallista varatallennusta tuotannossa. JSONB:n avainten järjestys ei vaikuta kuittauksen tarkistukseen.

Koko nykyinen versioitu työnkulku säilytetään yhdessä enintään 5 MB:n JSONB-snapshotissa. Tämä on tarkoituksellinen rajattu ensimmäinen toteutus: profiilit, ilmoitukset, arviot, hyväksytyt snapshotit, tapahtumat ja mittaukset säilyvät yhtenä atomisena kokonaisuutena. Se ei ole relaatiotauluihin normalisoitu moniasiakasjärjestelmä. Kokorajan lähestyessä tallennus pysäytetään; tietoja ei poisteta automaattisesti.

`docs/ops-database-schema.sql` on valmisteltu skeema, ei vielä ajettu migraatio. Taulussa on RLS eikä anon-/authenticated-oikeuksia tai julkisia käytäntöjä. Vain service_role saa SELECT/INSERT/UPDATE-oikeudet. Secret key ohittaa RLS:n palvelimella, joten API:n istuntotarkistus on varsinainen operaattorin käyttöoikeusraja. Avainta ei toimiteta selaimeen. Sovellusmalli säilyy SIMULATION-tilassa; pysyvä tallennus ei hyväksy oikeita asiakastoimituksia.

## Asetukset vasta valitulle projektille

- `TP_OPS_STORE=supabase`
- `TP_SUPABASE_URL=https://<valitun projektin ref>.supabase.co`
- `TP_SUPABASE_SECRET_KEY`: uudenmuotoinen `sb_secret_...`, vain palvelinympäristöön
- `TP_OPS_WORKSPACE=urakkaluotsi-pilot-simulation` (Previewlle eri workspace)
- Nykyiset TP_AUTH_USERNAME, TP_AUTH_PASSWORD_SCRYPT ja TP_SESSION_SECRET säilyvät; arvoja ei kirjata dokumentteihin.

Ei automaattista vanhojen paikallisten tietojen tuontia. Ei oikeita asiakastietoja ennen lähteiden ja toimitusvalmiuden hyväksyntää.

## Todennettu tässä työssä

- 29 Node + 18 Python-testiä PASS; kuusi uutta adapteritestiä sisältää uuden palvelininstanssin, hyväksynnän mitätöinnin historiatietoja muuttamatta, kilpailevan INSERT/PATCHin, virhetilat ja paikallisen varatallennuksen eston.
- Lint, tyyppitarkistus ja tuotantobuild PASS.
- 19 PostgreSQL-tarkistusta PASS paikallisella PGlite 0.5.10 -testimoottorilla: skeema, oikeudet, RLS:n estämä rivinäkyvyys myös erikseen annetulla SELECT-oikeudella, rajoitteet ja versioehdollinen päivitys. PGlite on erillinen tilapäinen QA-asennus; sitä ei lisätty sovelluksen riippuvuuksiin.
- Domainreititys 11 ja tunnistautuminen 3 + 17 HTTP-tarkistusta PASS.
- Hosted Supabase Data API, todellinen palvelinavain, uudelleenkäynnistyksen yli säilyminen, varmuuskopion palautus ja Vercelin Previewn päästä päähän -ajo: EI VIELÄ TESTATTU.

## Käyttöönoton järjestys

1. Valitse tietokantaprojekti ja tiliyhteys. Kahdesta luetusta Supabase-yhteydestä ei löytynyt Urakkaluotsille nimettyä projektia. Muiden hankkeiden tietokantoihin ei kirjoitettu.
2. Tarkista valitun projektin nykyinen skeema ja Data API -asetukset. Sovella valmisteltu SQL vain tähän kohteeseen. Aja advisor-tarkistus, generoi CLI:llä migraatio ja varmista historia.
3. Kytke rajatut palvelinympäristön asetukset ensin Previewhin. Älä muuta julkista myyntisivua tai DNS:ää.
4. Testaa synteettinen profiili → arvio → kooste → hyväksyntä → vienti, palvelininstanssin vaihto, samanaikainen muutos ja istunnoton API-pyyntö. Varmista anon-/authenticated-käytön esto oikeassa Data API:ssa.
5. Todista palautus yksityisestä varmuuskopiosta testityötilaan. Varmista käytettävän palvelutason varmistukset; älä oleta maksullisia ominaisuuksia.
6. Tuotantokytkentä ja oikeat tiedot vasta erikseen hyväksyttävän käyttöönoton ja toimitusvalmiuden jälkeen.

Viralliset toteutusohjeet tarkistettu 20.10.2026:
- https://supabase.com/docs/guides/api/securing-your-api
- https://supabase.com/docs/guides/getting-started/api-keys
- https://supabase.com/changelog/cbc-tls-ciphers-deprecated
