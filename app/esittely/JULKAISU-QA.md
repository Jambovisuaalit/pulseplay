# Urakkaluotsi – myyntisivun QA 19.10.2026

## Päätös

Muutos valmis tarkistettavaksi. Ei tuotantojulkaisua. Verokohtelu, juridinen myyjä, lopullinen julkaisuosoite ja todellinen sähköpostitoimitus vahvistetaan ennen tuotantoa.

## Suoritetut tarkistukset

| Tarkistus | Tulos |
|---|---|
| `npm test` | PASS: 20 Node- ja 18 Python-testiä |
| `npm run lint` | PASS: projektin nykyinen TypeScript/noUnused-tarkistus, ei ESLint |
| `npm run typecheck` | PASS |
| `npm run build` | PASS: Next 15.5.28, kaikki julkiset ja sisäiset reitit mukana |
| `node tests/auth-http.cjs --missing` ja ilman lippua | PASS: 3 + 17 tarkistusta |
| `node tests/sales-polish-qa.cjs` | PASS: 19 tarkistusryhmää; [tulokset](../../docs/sales-qa/browser-results.json) |
| PDF:n SHA-256, sivumäärä ja HTTP | PASS: alkuperäinen 81 071 tavua, 4 sivua; [tulokset](../../docs/sales-qa/pdf-verification.json) |
| `OPS_BROWSER_QA=true node tests/ops-http.cjs` | PASS: 39 HTTP- ja 7 selaintarkistusta; [selain](../../docs/sales-qa/ops-browser-results.json) |
| `git diff --check` | PASS |

Selain: Chrome Headless Shell 131, Playwright QA-ympäristöstä. Ei uusia sovellusriippuvuuksia.

Testattu 375 / 390 / 768 / 1440 CSS-pikselin leveydet; ei vaakaylivuotoa normaalisti eikä 200 % tekstisuurennuksella. Lisäksi 1440 → 720 CSS-pikselin näkymä vastaa 200 % zoomin aiheuttamaa uudelleenrivitystä. Fyysistä iOS-laitetta tai selaimen natiivia zoom-valikkoa ei testattu.

CTA-ankkurit, yksi H1, labelit, virhekentän fokus, näppäimistön siirtymisjärjestys, skip-linkki, FAQ, prefers-reduced-motion, no-JavaScript-varapolku ja tietosuojan suora avaus läpäisivät. PDF palauttaa 200/application/pdf julkisesta polusta myös mobiilinäkymässä; natiivia iOS PDF -katselinta ei testattu.

Palvelinvalidointi ja API:n origin-, tyyppi- ja kokorajat testattu. Puuttuva konfiguraatio antaa 503. Honeypot ei väitä vastaanottoa. Lähetyspalvelun hylkäys, virheellinen kuittaus ja verkkovirhe palauttavat 502. Hyväksytty kuittaus antaa 202. Nämä ovat simuloituja lähetyspalvelun vastauksia; oikeaa sähköpostia ei lähetetty. Selaimessa testattiin onnistuminen, ei-JSON-virhe, lomaketietojen säilyminen virheessä, lataustila ja synkronisen kaksoislähetyksen esto. localStorageen ei tallennettu tietoja.

React-tarkistus: sivu säilyy palvelinkomponenttina; vain lomake on asiakaskomponentti. Yhteinen validointi, ref-pohjainen lähetyslukko, vakaat listojen avaimet, ei tarpeettomia efektejä tai uusia UI-kirjastoja. Analytiikkaa ei löytynyt eikä lisätty.

## Korjattu testihavainto

200 % tekstisuurennus paljasti pitkien suomenkielisten sanojen venyttävän mobiiligridiä. Korjattu sarakkeiden vähimmäisleveydet ja pitkien sanojen rivittyminen; koko selainajo uusittiin onnistuneesti.

## Julkaisua edeltävät avoimet asiat

- 249 € / 30 päivää on vahvistettu hintapäätös. Verokohtelu on tarkoituksella `null` konfiguraatiossa.
- Aiemman repon Tmi Jami Harju / 3581581-6 / visualjambo@gmail.com säilytetty; uusin materiaalipaketti edellyttää myyjän ja rekisterinpitäjän lopullista vahvistusta.
- `RESEND_API_KEY`, `URAKKALUOTSI_CONTACT_FROM`, `URAKKALUOTSI_CONTACT_TO`, lähettäjän varmennus ja todellinen inbox-vastaanotto testattava tuotantoympäristöön erikseen.
- Tietosuojakäytännön käytännön toteutus palveluntarjoajilla vahvistettava; tämä QA ei ole oikeudellinen arvio.
- MetadataBase käyttää Vercelistä varmennettua tenderpulse-neon.vercel.app-hostia. Canonical ja og:url odottavat julkaisuosoitteen päätöstä.
- Maksullinen pilotti aloitetaan vasta erillisen toimitusvalmiuden varmistamisen jälkeen.

GitHub Actionsin tarkistus ei korvaa tässä dokumentoitua paikallista näyttöä: ensimmäinen ajo oli raportin kirjoitushetkellä jonossa. Vanha `tests/browser-qa.cjs` kuvaa aiempaa mailto-toteutusta; uusi workflow käyttää `sales-polish-qa.cjs`-tiedostoa.
