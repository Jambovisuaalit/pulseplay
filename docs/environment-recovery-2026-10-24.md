# Urakkaluotsin ympäristön palautus ja QA – 24.10.2026

Tekninen hosted-Preview-hyväksyntä ja maksullisen pilotin hyväksyntä ovat edelleen
**BLOCKED / EI VALMIS**. Tässä työssä korjattiin kolme paikallisesti toistettua
ajurivirhettä ja suoritettiin riippumattomat tarkistukset loppuun. Ulkoisia
käyttöoikeuksia ei kierretty.

## Toteutetut korjaukset

1. Hosted- ja varmuuskopioajurit ottavat Node 24.14+:ssa käyttöön olemassa olevan
   ympäristöproxyn ennen verkkopyyntöjä. Ilman tätä Node-fetch aikakatkaistiin,
   vaikka sama GitHub-pyyntö onnistui Pythonilla. Korjattu pyyntö palauttaa 200:n.
   `NO_PROXY`, kohderajatut salaisuudet ja TLS-varmennus säilyvät. Regressio käyttää
   paikallista CONNECT-proxyä ja todentaa myös paikallisen kohteen ohituksen.
2. Varmuuskopioajuri tallentaa ennen etäkirjoitusta yksityisen, tarkistussummatun
   omistajuusmanifestin. Sitoutuneen INSERTin kuittauksen katoaminen ei enää jätä
   syntynyttä riviä ilman paikallista siivoustietoa. `cleanup-recovery` lukee tämän
   tiedoston uudessa prosessissa ja poistaa vain täsmälleen odotetut omat rivit.
   Palautus hylkää tämän keskeneräisen manifestin varmuuskopiona. Testi toistettiin
   ensin vanhalla koodilla: manifesti puuttui, vaikka INSERT oli sitoutunut.
3. Portaalin selainajuri käyttää ajokohtaista väliaikaista Chrome-profiilia ja
   vapaata CDP-porttia. Palautettuun QA-profiiliin jäänyt toisen koneen
   `SingletonLock` esti aiemmin Chromen käynnistyksen (exit 21). Vanhaa profiilia
   ei poistettu; korjattu testi läpäisee sen ollessa edelleen olemassa.

Tietokanta- ja siivouskuljetuksen sekä paikallisen palautustiedoston parse-virheet
eivät tulosta vastauksen runkoa tai alkuperäisen poikkeuksen yksityisiä tietoja.

## Paikallinen todentaminen

| Tarkistus | Tulos |
| --- | --- |
| npm test | PASS: 46 Node-testiä ja 155 Python-testiä |
| lint, typecheck, tuotantokäännös | PASS |
| Selainpaketin palvelinavaintunnisteiden tarkistus | PASS |
| PostgreSQL-oikeudet, RLS, rajoitteet ja CAS | PASS: 26 tarkistusta, vain paikallinen PGlite |
| SQL-siivous sekä tavallinen ja keskeytyneen ajon palautus/siivous | PASS: 3 prosessi-/SQL-testiä, vain paikallinen PGlite |
| Next-tuotanto-HTTP + PostgreSQL-testikuljetus | PASS: 46 tarkistusta |
| Domain-HTTP ja tunnistautuminen | PASS: 11 + 3 puuttuvan asetuksen + 17 auth-tarkistusta |
| Julkinen sivusto ja yhteydenottopolku | PASS: 23 selainryhmää, 375/390/768/1440 px; viestipalvelu simuloitu |
| Julkinen PDF | PASS: neljä sivua, alkuperäinen SHA-256 säilyy |
| Portaali mobiilissa/desktopilla | PASS: 7 selainryhmää ja 5 muokkaus-/virhetilaregressiota |

PGlite- ja selainraportit ovat `qa-output/`-hakemistossa. Paikalliset fixturet ja
niiden tietokannat poistetaan testien lopuksi. Niitä ei esitetä hosted-näyttönä.

## Oikeat verkkohavainnot

Tarkistettu lähtötilan integraatio-Preview:
`https://tenderpulse-khfh9zta8-info-32533854s-projects.vercel.app`, GitHub deployment
`7290228474`, SHA `5c9a8b1e547d502fa87d8ab769a4b2878d49b76d`. Mahdollisen uuden
deploymentin tunniste ja SHA tarkistetaan erikseen PR:n loppuraportissa.

| Pyyntö / vaihe | Havainto ja rajaus |
| --- | --- |
| GitHub-pyyntö korjatulla Node-proxyllä | PASS: HTTP 200 |
| Preview `/login` ilman tunnuksia | PASS suojauskerrokselle: 302 Vercelin kirjautumiseen; ei sovellus-authin näyttö |
| Supabase GET satunnaiseen olemattomaan testityötilaan | FAIL tunnistautumisessa: HTTP 401; vastausrunko ja avain jätetty pois |
| Vercelin projektinhallinta ilman hallintasidontaa | BLOCKED: HTTP 403 |
| Supabasen projektinhallinta ilman hallintasidontaa | BLOCKED: HTTP 401 |
| Hosted-ajurin esitarkistus kirjoitukset estettyinä | FAIL: työtila ei kuulu testinimiavaruuteen; ei hosted-pyyntöjä |
| Autentikoitu työnkulku, HTTP-kilpailu ja riippumaton tallennusvarmennus | BLOCKED, ei ajettu |
| Hosted-varmuuskopiointi, palautus ja Previewn todellinen uudelleenkäynnistys | BLOCKED, ei ajettu |
| Hosted-testidatan siivous | Ei tarvittu: etärivejä luotu 0 |

Kokoonpanon lukutulos on nyt julkaistu versio, jonka tunniste päättyy
`cecfgver_6adbfb5eb4cc81a1b948158b1110e5b5`. Ajonaikaisen koneen aktiivisen
kokoonpanoversion ja tähän julkaisuun kytkennän tilakysely ei ole saatavilla.

## Täsmälliset hallintatoimet ja hyväksymisesteet

- **Codex Cloud → pulseplay → Edit → Network secrets → Manage:** muokkaa
  olemassa olevien `PREVIEW_E2E_PASSWORD`- ja `VERCEL_AUTOMATION_BYPASS_SECRET`-
  vaatimusten **Allowed domains** valitun onnistuneen Preview-deploymentin
  täsmälliseksi hostiksi. Luettu kohde on edelleen vanha `tenderpulse-fch3db8x2-…`.
  Nykyinen luonnoksen päivitysrajapinta ei tue tämän ristiriitaisen kohteen muutosta.
- **Environment variables → Manage:** `PREVIEW_E2E_WORKSPACE` pitää kohdistaa
  todelliseen tyhjään `preview-e2e-`-alkuiseen työtilaan. Sama arvo tarvitaan
  **Vercel → tenderpulse → Preview → integraatiohaara → TP_OPS_WORKSPACE**.
  Myös käyttäjän ja muiden palvelinasetusten täsmäys on varmennettava. Vercelin
  hallintatokenia, CLI-istuntoa tai hallintatyökalua ei ole käytettävissä.
- **Supabase-testiprojektin turvallinen TP_SUPABASE_SECRET_KEY-sidonta:** korjaa
  HTTP 401:een johtava tunnistautuminen ja varmista projektin testikäyttö sekä
  erillisyys tuotannosta. Anon/publishable-avaimia ei käytetä palvelinavaimena.
  Hallintatokenia tai suoraa SQL-yhteyssidontaa ei ole käytettävissä. Keskustelussa
  paljastuneiden tunnusten kierrätystä ei voida tällä pääsyllä tehdä tai todentaa.
- Sovella `docs/ops-test-cleanup.sql` vasta erikseen varmennettuun testiprojektiin.
  Tätä SQL:ää ei sovellettu etänä. Varsinaiset hosted-kirjoitukset ja palautus
  pysyvät estettyinä tähän asti. Todellinen Preview-uudelleenkäynnistys vaatii
  lisäksi Vercelin Preview-hallintatoiminnon ja ennen/jälkeen-lukunäytön.
- Relevanssin uusinta on sama 52 ilmoituksen AI-silver-regressio: 32 poissulkua,
  20 lykkäystä, 0 positiivista ennustetta. Riippumatonta ihmis-goldia ja uusia
  riippumattomia holdout-tapauksia ei ole; precision/recall eivät ole virallisesti
  mitattavissa. Aiemman top30-portin täydellisiä asiakirja-arvioita on 0/30.

Tuotantoasetuksia tai -dataa ei muutettu, viestejä ei lähetetty eikä PR:iä yhdistetty.
