# Integraatioympäristön asetukset

Sovellus käyttää Node 24:ää ja Python 3.12:ta. Asenna Node-riippuvuudet
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

24.10.2026 tässä koneessa kaikki yllä mainitut E2E-sidonnat puuttuvat.
Pilviympäristön luonnoksessa kolmen salaisuuden `has_saved_binding` on false.
GitHub-integraation Preview-salaisuuksien nimien listaus palauttaa HTTP 403.
Vercelin palvelinasetukset ovat siten **varmentamatta**, eivät todistetusti tyhjät.
Tarvitaan sidontojen turvallinen syöttö ja integraatiohaaran Preview-asetusten
varmennus. Arvoja ei pyydetä keskusteluun.

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
