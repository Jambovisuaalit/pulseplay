# Urakkaluotsi – myyntisivun QA 19.10.2026

## Päätös

Muutos valmis tarkistettavaksi. Ei tuotantojulkaisua. Myyjä, vastaanottaja ja ALV-rekisteriin kuulumattomuus vahvistettu käyttäjältä 19.10.2026. Lopullinen julkaisuosoite ja todellinen sähköpostitoimitus vahvistetaan ennen tuotantoa.

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

- Vahvistettu 19.10.2026: 249 € / 30 päivää on lopullinen hinta. Myyjä ei kuulu ALV-rekisteriin. Konfiguraatio käyttää arvoa `SELLER_NOT_VAT_REGISTERED`, ei nollaverokantaa.
- Käyttäjä vahvisti myyjän ja vastaanottajan: Tmi Jami Harju / 3581581-6 / visualjambo@gmail.com.
- `RESEND_API_KEY`, `URAKKALUOTSI_CONTACT_FROM`, `URAKKALUOTSI_CONTACT_TO`, lähettäjän varmennus ja todellinen inbox-vastaanotto testattava tuotantoympäristöön erikseen.
- Tietosuojakäytännön käytännön toteutus palveluntarjoajilla vahvistettava; tämä QA ei ole oikeudellinen arvio.
- MetadataBase käyttää Vercelistä varmennettua tenderpulse-neon.vercel.app-hostia. Canonical ja og:url odottavat julkaisuosoitteen päätöstä.
- Maksullinen pilotti aloitetaan vasta erillisen toimitusvalmiuden varmistamisen jälkeen.

GitHub Actionsin tarkistus ei korvaa tässä dokumentoitua paikallista näyttöä: ensimmäinen ajo oli raportin kirjoitushetkellä jonossa. Vanha `tests/browser-qa.cjs` kuvaa aiempaa mailto-toteutusta; uusi workflow käyttää `sales-polish-qa.cjs`-tiedostoa.

## Todellinen esikatselun vastaanottotesti 19.10.2026

Tämä lisätarkistus sulkee esikatselun todellista sähköpostivastaanottoa koskevan avoimen kohdan. Aiemmat simuloidut testitulokset yllä säilyvät erillisinä.

- Esikatselu: https://tenderpulse-n9trl4boh-info-32533854s-projects.vercel.app/esittely
- Deployment: `dpl_EhiaqYnywHykdRyGCDnkRv7h9DvC`; sovelluskoodi `7b8c6dadcb8b8fc29b936d41a7c3814b44f0c3c2`.
- Verceliin tallennettu vain Preview-ympäristöön `RESEND_API_KEY`, `URAKKALUOTSI_CONTACT_FROM` ja `URAKKALUOTSI_CONTACT_TO`. Avain on lähetyskohtainen ja rajattu varmennettuun virellahelsinki.com-domainiin. Salaista arvoa ei tallennettu lähdekoodiin tai raporttiin.
- Tekninen lähettäjä: Urakkaluotsi <urakkaluotsi@virellahelsinki.com>. Vastaanottaja: käyttäjän vahvistama visualjambo@gmail.com.
- Suora lomake-API-testi `UL-20261019-1941`: HTTP 202; Resend `delivered`; Gmailissa Saapuneet-kansiossa klo 19.45.57 Suomen aikaa.
- Selaimen lomaketesti `UL-20261019-1948`: kenttien täyttö → Lähetä pilottihakemus → HTTP 202 → pyydetty kiitosviesti. Resend `delivered`; viesti Gmailin Saapuneet-kansiossa klo 19.46.43 Suomen aikaa. [Selainnäyttö](../../docs/sales-qa/live-contact-browser.json), [HTTP-näyttö](../../docs/sales-qa/live-contact-http.json).
- Lähetettiin yhteensä kaksi selvästi teknisiksi testeiksi merkittyä viestiä, molemmat vahvistettuun vastaanottajaosoitteeseen. Ei asiakashakemuksia tai tilauksia.
- Alkuperäinen selainyritys estyi automaattisessa tarkistuksessa Vercel-kirjautumissivun ulkopuolisen Sentry-telemetrian vuoksi. Onnistunut testi salli vain täsmälleen tämän esikatselun originin ja esti muut verkko-osoitteet. Paikallisen testiproxyn vuoksi QA-selaimen sertifikaattivirheet ohitettiin; sovelluksen TLS-asetuksia ei muutettu.
- Vercelin Deployment Protection säilyi käytössä. Testin tilapäinen, deployment-kohtainen jakolinkki peruttiin testin jälkeen. Tuotantoympäristön asetuksia ei muutettu eikä tuotantojulkaisua tehty.

**Jäljellä ennen tuotantoa:** lopullinen julkaisuosoite, tuotannon erilliset lähetysasetukset ja tietosuojakäytäntöjen operatiivinen vahvistus. Sisäisen portaalin tuotannon tunnistautumis- ja tallennusasetukset käsitellään erikseen. Maksullisen asiakaspilotin toimitusvalmius on erillinen portti.
