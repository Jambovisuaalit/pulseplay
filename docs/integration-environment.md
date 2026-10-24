# Integraatioympäristön asetukset

Sovellus käyttää Node 24:ää ja Python 3.12:ta. Hosted-ajurit tarvitsevat
Node 24.14:n tai uudemman ympäristöproxyn ohjelmalliseen käyttöönottoon.
Asenna Node-riippuvuudet
`npm ci --ignore-scripts` ja Python-testiriippuvuus `python -m pip install
'pypdf>=5,<7'`. Työntekijän valinnaiset PDF/OCR-riippuvuudet ovat erikseen
`requirements-worker.txt`:ssä. Työ tehdään olemassa olevassa checkoutissa;
uutta worktreetä ei tarvita.

## Sovelluspalvelin: Vercel Preview, vain integraatiohaaralle rajattuna

| Nimi | Käyttö | Toimenpide |
| --- | --- | --- |
| `TP_AUTH_USERNAME` | Operaattorin käyttäjätunnus | Varmista Preview-haaran oma arvo |
| `TP_AUTH_PASSWORD_SCRYPT` | Suolan ja salasanatiivisteen yhdistelmä | Aseta turvallisesti muodossa 32 hex-merkkiä, kaksoispiste, 128 hex-merkkiä; ei raakaa salasanaa |
| `TP_SESSION_SECRET` | HMAC-istunnon allekirjoitus | Oma Preview-avain, 64–128 hex-merkkiä; ei tuotantoavainta |
| `TP_OPS_STORE` | Tallennustavan eksplisiittinen valinta | `supabase` |
| `TP_SUPABASE_URL` | Valitun Preview-projektin HTTPS-osoite | Varmista valittu Urakkaluotsi-projekti |
| `TP_SUPABASE_SECRET_KEY` | Palvelinpuolen Data API -avain | Turvallinen palvelinsidonta; ei `NEXT_PUBLIC_`-muuttujaa eikä anon-avainta |
| `TP_OPS_WORKSPACE` | Tämän Previewn erillinen työtila | E2E-ajolle tyhjä `preview-e2e-`-alkuinen työtila, sama nimi kuin ajurin asetuksissa |

Näiden Vercel-arvojen läsnäoloa ei voi päätellä pilvikoneen muuttujista.
GitHubin deployment-metatieto tai kirjautumissivun näkyminen ei todista niitä.
Varmista rajaus juuri integraatiohaaralle ja käynnistä sen Preview uudelleen
asetusten jälkeen. Tuotantoasetuksia ei muuteta.

## Testiajuri: pilvikone tai erillinen turvallinen CI-ympäristö

| Nimi | Käyttö | Toimenpide |
| --- | --- | --- |
| `PREVIEW_E2E_URL` | Täsmällinen valmis Preview-deployment | Aseta integraatiohaaran uusi osoite; vanha PR #12 -deployment ei vastaa uutta sovelluskoodia |
| `PREVIEW_E2E_DEPLOYMENT_ID` | GitHubin deployment-tunniste | Aseta saman deploymentin ID |
| `PREVIEW_E2E_WORKSPACE` | Tyhjä synteettinen työtila | Täsmää Vercelin `TP_OPS_WORKSPACE`-arvoon |
| `PREVIEW_E2E_USERNAME` | Preview-operaattorin tunnus | Täsmää Vercelin `TP_AUTH_USERNAME`-arvoon |
| `PREVIEW_E2E_PASSWORD` | Kirjautumisen raaka testisalasana | Turvallinen sidonta **vain ajuriin**; lähetetään `username/password`-lomakekenttinä `/api/login`-reitille, ei sovelluksen ympäristömuuttujaksi |
| `VERCEL_AUTOMATION_BYPASS_SECRET` | Vercelin Deployment Protection -ohitus automaatiolle | Turvallinen sidonta **vain ajuriin**; HTTP-otsake `x-vercel-protection-bypass`, ei kirjautumissalasana tai session avain |
| `TP_SUPABASE_URL` | Kirjoituksen riippumaton tietokantavarmennus | Sama Preview-projekti kuin palvelimella |
| `TP_SUPABASE_SECRET_KEY` | Rajattu Data API/RPC -testikäyttö | Turvallinen sidonta vain valittuun Supabase-hostiin |
| `PREVIEW_E2E_PERSIST_SYNTHETIC` | Eksplisiittinen testikirjoitusten valinta | `yes`; nykyinen ajuri siivoaa omat tietonsa lopuksi |
| `PREVIEW_E2E_BACKUP_FILE` | Testin itse luoma yksityinen varmuuskopio | Uusi tiedosto ignoratussa `.local/`-hakemistossa |

Salaisia arvoja, cookieita tai prosessin koko ympäristöä ei tulosteta.
Ajuri hyväksyy turvallisen proxyn salaisuussidonnat paljastamatta raaka-arvoja.
Vercelin suojausta ei poisteta. Julkisen yhteydenottolomakkeen sähköpostipalvelu
simuloidaan QA:ssa; `RESEND_API_KEY` ei ole näiden testien edellytys.

24.10.2026 uudessa tarkistuksessa kaikki viisi tavallista asetusta ja kolme
verkkosalaisuussidontaa ovat saatavilla. Kokoonpanon lukutulos palauttaa nyt
julkaistun version (ei luonnosrevisiota), jonka tunniste päättyy
`cecfgver_6adbfb5eb4cc81a1b948158b1110e5b5`. Tämä ei yksin todista koneen
aktiivista kokoonpanoversiota; ajonaikaista versiotilakyselyä ei ole käytettävissä.

Julkaistusta kokoonpanosta luetuissa vaatimuksissa kahden Preview-salaisuuden
sallittu host on edelleen vanha
`tenderpulse-fch3db8x2-info-32533854s-projects.vercel.app`. Se ei vastaa nykyistä
integraatio-Previewta. Muutos on tehtävä **Network secrets → Manage → olemassa
oleva salaisuus → Allowed domains** -kenttään. Yleisen Internet-sallintalistan
muutos ei muuta salaisuuden kohderajausta. Päivitystyökalu ei tue olemassa olevan
vaatimuksen ristiriitaisen kohteen muuttamista eikä vaatimuksia monisteta.

`PREVIEW_E2E_WORKSPACE` on asetettu, mutta se ei täytä erillisen testityötilan
`preview-e2e-`/`pr12-e2e-`-nimiavaruutta. Arvoa ei arvata tai muuteta vain ajurissa:
sen pitää vastata integraatiohaaran Preview-palvelimen erillistä työtilaa.

Hosted-ajurit ottavat nyt Node-prosessissa käyttöön `http.setGlobalProxyFromEnv`-
tuen ennen verkkopyyntöjä. Ympäristön `HTTPS_PROXY` ja `NO_PROXY` säilyvät käytössä,
TLS-varmennusta ei poisteta. Ilman tätä Node-fetch aikakatkaistiin, vaikka Pythonin
ja GitHub CLI:n HTTPS-yhteydet toimivat. Korjauksen jälkeen oikea, satunnaiseen
olemattomaan testityötilaan rajattu Supabase GET palautti HTTP 401:n: sidonnan
saatavuus ei vielä osoita kelvollista tietokantatunnistautumista. Vastauksen runkoa
tai avainta ei kirjattu. Erillistä testiprojektia ei ole tämän perusteella varmennettu.

Vercelin hallintarajapinta palauttaa ilman hallintasidontaa 403:n, Supabasen
hallintarajapinta 401:n. Hallintatokenia, suoraa SQL-yhteyssidontaa tai kirjautunutta
CLI-istuntoa ei löytynyt. Integraatiohaaran Vercel-palvelinasetukset ovat siten
**varmentamatta**, eivät todistetusti tyhjät. Tarvitaan palvelinasetusten ja
testiprojektin erillisyyden varmennus hallintapääsyllä. Arvoja ei pyydetä keskusteluun.

## Testidatan siivous

Sovella `docs/ops-test-cleanup.sql` erikseen vain hyväksyttyyn Preview-testiprojektiin.
Se ei muuta sovelluksen taulun SELECT/INSERT/UPDATE-oikeuksia eikä myönnä DELETEä.
Rajattu RPC vaatii E2E-nimiavaruuden, tämän ajon UUID:n jokaisen asiakkaan
synteettisessä nimessä, `example.invalid`-vastaanottajat, synteettiset lähteet ja
täsmäävän tallennusversion. Anon- ja authenticated-roolit eivät saa kutsua sitä.
Muuttunutta tai toiselle ajolle kuuluvaa työtilaa ei poisteta.

Preview-ajuri tarkistaa siivouksen saatavuuden ennen ensimmäistä testikirjoitusta
ja kieltäytyy koskemasta olemassa olevaan työtilaan. Jos siivous epäonnistuu,
testi epäonnistuu eikä virhettä peitetä. Varmuuskopioajon jälkeen käytetään sen
omaa `cleanup`-vaihetta. Koko taulua tai muiden ajojen rivejä ei poisteta.
