# Urakkaluotsi – julkinen myyntisivu

Reitit: `/esittely`, `/esittely/tietosuoja`, POST `/esittely/api/contact` ja `/urakkaluotsi/*`. Juurireitti, `/ops` ja sisäiset API-reitit säilyvät suojattuina.

Pohja: `feature/urakkaluotsi-pilot-metrics` / c04ccf1, jotta uudempi toimitusportaali säilyy. PR #3 on avoin luonnos; sen jälkeen palvelinlomake on kehitetty haarassa `feature/urakkaluotsi-server-contact` / 31f699b. Lomake integroitiin tähän pohjaan. Main sisältää eri projektin eikä ole tämän sovelluksen julkaisuhaara. AGENTS.md-tiedostoja ei löytynyt. Työpuu oli alussa puhdas.

## Toteutus

- `page.tsx`: suomenkielinen myyntisivu, semanttinen esimerkkikortti ja alkuperäinen PDF.
- `site-config.ts`: 249 € / 30 päivää, lopullinen hinta. Myyjä ei kuulu ALV-rekisteriin (käyttäjän vahvistus 19.10.2026).
- `site.css`: nykyisen CSS-rakenteen rajattu viimeistely. Projektissa ei ole Tailwindia; sitä ei lisätty uutena riippuvuutena.
- `pilot-form.tsx`: yhteinen kenttävalidointi, palvelinvirheet, fokus, lähetyksen tila ja synkroninen kaksoislähetyksen esto.
- `api/contact/route.ts`: nykyinen Resend-käsittelijä, origin-/koko-/tyyppitarkistus ja lähetyspalvelun kuittaus. Ei henkilötietoja localStorageen.
- Logo, OG ja PDF kopioitu liitteistä. PDF SHA-256: `36762a526ae0a7299098c77e8e64a9ca78d15b4a3ac0b9a4624b7b9e4ad1e69b`.

Käyttäjän 19.10.2026 vahvistamat myyjä- ja vastaanottajatiedot: Tmi Jami Harju / 3581581-6 / visualjambo@gmail.com. Myyjä ei kuulu ALV-rekisteriin, joten 249 € / 30 päivää on lopullinen hinta. Tieto perustuu tämän palvelun myyjää koskevaan käyttäjän vahvistukseen.

## Lähetyskanava

Asetukset: `RESEND_API_KEY`, `URAKKALUOTSI_CONTACT_FROM`, `URAKKALUOTSI_CONTACT_TO`. Puuttuva konfiguraatio palauttaa 503: "Lähetys ei ole vielä käytössä." Hyväksytty palveluntarjoajan vastaus palauttaa 202; se osoittaa vastaanoton lähetyspalveluun, ei lopullista inbox-toimitusta. Varmista lähettäjä ja vastaanottava postilaatikko sekä testaa todellinen toimitus ennen tuotantoa.

## Tarkistukset

`npm test`, `npm run lint`, `npm run typecheck`, `npm run build`.
`node tests/auth-http.cjs --missing`, `node tests/auth-http.cjs`.
`node tests/sales-polish-qa.cjs` käyttää QA-ympäristön Playwrightia ja Chromea. `PLAYWRIGHT_MODULE` voi osoittaa valmiiksi asennettuun moduuliin; `CHROME_PATH` selainbinääriin. Ei runtime-riippuvuuksia. Lähetyspalvelun onnistumiset ja virheet simuloidaan, sähköpostia ei lähetetä.
`OPS_BROWSER_QA=true node tests/ops-http.cjs`: sisäisen portaalin työnkulku.

Vercelin tenderpulse-projekti ja nykyinen hosting-osoite tenderpulse-neon.vercel.app varmennettu connectorilla 19.10.2026. MetadataBase käyttää tätä hostia; canonical ja og:url jätetty asettamatta julkaisuosoitteen vahvistamiseen asti. Analytiikkaa ei löytynyt eikä sitä lisätty. Ei Hilma-kutsuja, ei liitteiden lataamista eikä tuotantojulkaisua.

Paikallinen esikatselu: `npm ci && npm run build && npm start`, sitten http://localhost:3000/esittely.

## Esikatselun lähetys varmennettu

19.10.2026: Preview-ympäristön lähettäjä Urakkaluotsi <urakkaluotsi@virellahelsinki.com>, vastaanottaja visualjambo@gmail.com. Virellahelsinki.com on Resendissä varmennettu; avain rajattu tämän domainin sähköpostilähetyksiin. Selaimen oikea lomakelähetys palautti 202 ja viesti löytyi Gmailin Saapuneet-kansiosta. Katso QA-raportin lisätarkistus. Tuotannon asetuksia ei muutettu. API-avainta ei pidä tulostaa tai lisätä tähän dokumenttiin.

## Oman domainin julkaisuvalmistelu

`lib/public-site.ts` rajaa julkisen juurireitin vain urakkaluotsi.fi- ja www.urakkaluotsi.fi-hosteihin. Middleware rewrite `/` → `/esittely`; muiden hostien juurireitti sekä operaattori- ja hankintareitit säilyvät suojattuina. Vercelin www-domain ohjaa 308:lla apex-domainiin.

Canonical ja OG URL aktivoituvat vain erikseen asetettavalla `URAKKALUOTSI_PUBLIC_ORIGIN=https://urakkaluotsi.fi`-muuttujalla. Preview ilman muuttujaa säilyttää aiemman metatietokäytöksen. `tests/domain-http.cjs` testaa aidolla HTTP Host -otsakkeella molemmat domainit, suojatut reitit, väärän hostin ja julkisen PDF:n (11 tarkistusta).

19.10.2026: molemmat domainit lisätty Vercelin tenderpulse-projektiin ja omistajuus hyväksytty (`verified=true`). DNS osoitti edelleen Zonerin IP:hen 84.34.166.69. Zonerin selainhallinta vaatii kirjautumisen; DNS:ää ei muutettu. Nimipalvelimet, MX- ja SPF-tietueet säilytetään. Tuotantodeploymentia tai domainin julkista liikenteensiirtoa ei tehty.
