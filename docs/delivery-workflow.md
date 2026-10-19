# Urakkaluotsi: tietomalli ja kokonainen toimitustyönkulku

Toteutus on tarkasteltava paikallinen sisäinen simulaatio, ei tuotannossa oleva asiakasportaali. Suojattu `/ops` ja `/api/ops` käyttävät M0:n operaattori-istuntoa. Erillistä Supabase-projektia, hallittua kirjautumista tai tuotantotallennusta ei ole vielä kytketty. Tuotantoympäristössä API palauttaa 503:n. Todellisia asiakastietoja ei käytetä tässä vaiheessa.

## Käyttö paikallisesti

1. Konfiguroi operaattorin ympäristö M0-ohjeella (`scripts/configure_auth.py`).
2. Käynnistä `TP_OPS_LOCAL_ENABLED=true npm run dev` ja kirjaudu `/login`-sivulla.
3. Avaa `/ops`. Luo kuvitteellinen asiakas ja testivastaanottaja, esim. `test@example.invalid`.
4. Tallenna profiiliversio: palvelut, alueet, vahvistettavat tiedot. UNKNOWN käyttää arvoa null, ei false/0; CONFIRMED vaatii lähteen ja aikavyöhykkeellisen vahvistusajan.
5. Lisää synteettinen ilmoitus numeroineen, lähde-URL, lähdeote, tuleva määräaika ja todellinen tarkistusaika. Merkitse peruutustilan tarkistuksen tulos.
6. Kirjaa arvio, puuttuvat tiedot ja seuraava toimi. Osittaisen tarkistuksen rajaus on näytettävä.
7. Valitse enintään 10 nostoa ja luo kooste. Nolla nostoa on sallittu.
8. Avaa esikatselu ja tarkista QA. Hyväksy näkyvä sisältöversio.
9. Lataa PDF, HTML, TXT, EML tai JSON. EML ei sisällä To/From/Date-kenttiä eikä mitään lähetetä. Kaikki viennit on merkitty simulaatioksi.
10. Muuta profiilia, arviota, vastaanottajaa tai lähdettä. Hyväksyntä poistuu ja vienti estyy. Historiallinen hyväksyntäsnapshot ja vientitapahtumat säilyvät.

Tiedosto `.local/ops-state.json` on yksityinen paikallinen simulaatiotallennus, Gitin ulkopuolella. Vaihtoehtoinen testihakemisto määritetään `TP_OPS_LOCAL_DIRECTORY`:lla. Kirjoitukset käyttävät tiedostolukkoa, odotettua revisionumeroa, fsync- ja atomic rename -tallennusta. Prosessin kaatumisesta jäänyt lukko estää uudet kirjoitukset; poista vain varmistettu vanha lukko pysäytetyssä kehitysympäristössä. Tämä ei ole pilviadapteri tai hajautettu tuotantotallennus.

## QA ja hyväksynnän sitovuus

Palvelin tarkistaa kaikki säännöt myös suoralla API-kutsulla. Käyttöliittymän disabled-painike ei ole turvaraja.

- Asiakkaan nykyinen profiiliversio ja arvioiden asiakas/versioviitteet täsmäävät.
- Uusin ilmoitusversio on tarkistettu; lähde ja lähdeote löytyvät.
- Tarkistusaika on enintään 24 h vanha eikä tulevaisuudessa. Alle vuorokausi määräaikaan vaatii alle tunnin lähdetarkistuksen.
- Määräaika on aikavyöhykkeellinen, tunnettu ja tulevaisuudessa. Peruutustila on tarkistettu kielteiseksi.
- Jokaisella nostolla on ihmisen kirjaama arvio ja seuraava toimi. Tuntemattomat profiilifaktat ja puuttuvat lähdetiedot näkyvät koosteessa.
- Osittainen kattavuus sallitaan vain näkyvin rajauksin. CHECKS_PASS ei ole lupaus tarjouskelpoisuudesta; vanhaa GO-moottoria ei tässä muuteta eikä käytetä hyväksyntään.
- Hyväksyntä jäädyttää syväkopion ja kanonisen SHA-256-sisältötunnisteen. Vienti vertaa nykyistä sisältöä sekä jäädytettyä snapshotia tähän tunnisteeseen ja laskee QA:n uudelleen.
- Profiilin, vastaanottajan, arvioiden tai lähdeversion muutos mitätöi aktiivisen hyväksynnän. Ajan kuluminen voi estää viennin ilman mitään käyttäjän muokkausta.
- Vienti kirjataan EXPORTED-tapahtumana, ei lähetyksenä. Oikean lähetyksen kirjaus on simulaatiossa estetty. Uusintavienti samassa formaatissa ja samasta hyväksynnästä ei luo uutta tapahtumaa.

PDF on deterministinen tekstikooste, A4, upotettu lisensoitu DejaVu Sans, suomen merkit ja sivutus. Se ei vielä vastaa julkisen nelisivuisen esimerkin kaikkia taittoratkaisuja. WinAnsi-merkistön ulkopuoliset merkit korvautuvat kysymysmerkillä PDF:ssä; HTML/TXT/EML/JSON säilyttävät UTF-8:n. PDF:n visuaalinen renderöinti tarkistetaan synteettisellä aineistolla. Tämä rajoite on korjattava ennen täyttä Unicodea edellyttävää asiakastoimitusta.

## Tietokantasopimus

`database/01-tables.sql` … `04-source-checks.sql` ovat skeeman lähdetiedostoja tyhjää PostgreSQL/Supabase-tietokantaa varten. Niitä ei ole ajettu olemassa olevaan pilviprojektiin eikä merkitty migraatiohistoriaan. M2:ssa todellinen Supabase-migraatio luodaan CLI:llä, tarkastetaan ja kytketään sovellusadapteriin.

| Kokonaisuus | Taulut ja rajoitteet |
|---|---|
| Operaattorit | organizations, operator_memberships; vain ylläpidon ennalta lisäämät käyttäjät, ADMIN/EDITOR/VIEWER, aktiivisuus tarkistetaan tietokannasta |
| Asiakkaat | clients; organisaatio, yhteystiedot, tila ja optimistinen row_version |
| Profiilihistoria | client_profile_versions; asiakaskohtainen versionumero, palvelut/CPV/alueet/poissulut ja vahvistustilat |
| Lähteet | notices + notice_versions; Hilma-tunniste, muuttumaton raakasisältö, hash ja määräaika |
| Evidenssi | source_evidence + source_checks; ote, asiakirjakohta, tarkistusaika ja muuttumattoman lähteen uusintatarkistukset |
| Tarkistukset | assessments + assessment_evidence; tarkka asiakas-, profiili- ja lähdeversio, fakta/arvio/puuttuva/seuraava toimi, kattavuus |
| Toimitukset | digests + digest_versions + digest_items; simulaatio erotettu oikeasta, jäädytetty snapshot, hyväksynnän metatiedot ja versionumero |
| Historia | delivery_events; vienti/lähetyskirjaus/korjaus erillään, idempotenssiavain ja todisteviite |

RLS on kaikissa 14 taulussa. Anonyymeillä ei ole tauluoikeuksia. Organisaatiorajat ovat myös yhdistelmäviiteavaimissa: pelkkä ID ei riitä vaihtamaan asiakkaan profiilia tai evidenssin lähdeversiota. Käyttäjä ei voi lisätä omaa jäsenyyttään tai vaihtaa rooliaan. Ei SECURITY DEFINER -funktioita, ei service_role-avainta selaimeen. M0-eväste ei ole Supabase-JWT eikä anna tietokantaoikeuksia.

Historiariveille ei myönnetä tavallista UPDATE/DELETE-oikeutta, ja trigger estää muutokset myös omistajan normaalissa DML-ajossa. Hallittu poistaminen/anonymisointi vaatii erillisen ylläpitomenettelyn ja varmistusten elinkaaren ennen oikeita tietoja; muuttumattomuus ei tarkoita ikuista henkilötietojen säilyttämistä.

Skeema estää viite-, käyttöoikeus- ja perusversiovirheet. Se ei yksin todista lähteiden tuoreutta, sisällön hashia tai kaikkien QA-sääntöjen toteutumista: nämä ovat testatussa domain-palvelussa. Tietokanta-adapterin on tehtävä niiden tarkistus ja snapshotin/historian tallennus yhdessä transaktiossa. Paikallisen API:n DTO:t ovat sovellussopimus, eivät suoraan SQL-rivien muodossa; esimerkiksi checked_at koostetaan source_checks-riveistä.

## Testit

- `npm test`: vanhat 26 testiä ja 7 työnkulun regressiotestiä.
- `npm run lint`, `npm run typecheck`, `npm run build`.
- Tuotantobuildin kirjautumisen HTTP- ja julkisen sivun 22 Chromium-tarkistusta.
- `node tests/ops-http.cjs`: koko paikallinen kehityspolku, viisi tiedostovientiä, mitätöinti ja fail-closed-kytkin; käyttää väliaikaista hakemistoa ja vain synteettisiä tunnuksia.
- `OPS_BROWSER_QA=true node tests/ops-http.cjs`: lisäksi /ops 375/390/768/1440, lomaketallennus, kenttien labelit, fokus ja hyväksynnän mitätöinnin vientipainikkeet.
- CI `Urakkaluotsi data model`: tyhjä PostgreSQL 16 + synteettiset auth-roolit; skeeman ajo ja oikeat SQL-kyselyt RLS-, viite-, versiovirhe- ja historiarajoitteille.

Supabasen changelog ja RLS/tauluohjeet tarkistettu 19.10.2026. Marraskuun TLS-muutos koskee myöhempää verkkokytkentää, ei paikallista SQL-skeemaa. Lähteet: https://supabase.com/docs/guides/database/tables ja https://supabase.com/docs/guides/database/postgres/row-level-security.
