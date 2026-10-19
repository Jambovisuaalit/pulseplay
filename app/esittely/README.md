# Urakkaluotsi – julkinen myyntisivu

Reitit: `/esittely`, `/esittely/tietosuoja`, POST `/esittely/api/contact` ja `/urakkaluotsi/*`. Juurireitti, `/ops` ja sisäiset API-reitit säilyvät suojattuina.

Pohja: `feature/urakkaluotsi-pilot-metrics` / c04ccf1, jotta uudempi toimitusportaali säilyy. PR #3 on avoin luonnos; sen jälkeen palvelinlomake on kehitetty haarassa `feature/urakkaluotsi-server-contact` / 31f699b. Lomake integroitiin tähän pohjaan. Main sisältää eri projektin eikä ole tämän sovelluksen julkaisuhaara. AGENTS.md-tiedostoja ei löytynyt. Työpuu oli alussa puhdas.

## Toteutus

- `page.tsx`: suomenkielinen myyntisivu, semanttinen esimerkkikortti ja alkuperäinen PDF.
- `site-config.ts`: 249 € / 30 päivää, verokohtelu `null`. Vahvistettava ennen julkaisua.
- `site.css`: nykyisen CSS-rakenteen rajattu viimeistely. Projektissa ei ole Tailwindia; sitä ei lisätty uutena riippuvuutena.
- `pilot-form.tsx`: yhteinen kenttävalidointi, palvelinvirheet, fokus, lähetyksen tila ja synkroninen kaksoislähetyksen esto.
- `api/contact/route.ts`: nykyinen Resend-käsittelijä, origin-/koko-/tyyppitarkistus ja lähetyspalvelun kuittaus. Ei henkilötietoja localStorageen.
- Logo, OG ja PDF kopioitu liitteistä. PDF SHA-256: `36762a526ae0a7299098c77e8e64a9ca78d15b4a3ac0b9a4624b7b9e4ad1e69b`.

Aiemmassa repossa dokumentoidut yhteystiedot säilytetty: Tmi Jami Harju / 3581581-6 / visualjambo@gmail.com. Uusin materiaalipaketti pitää juridisen myyjän ja verokohtelun vahvistamista avoimina; julkaisija vahvistaa nämä ennen tuotantoa. Muihin yrityksiin liittyvistä ALV-tiedoista ei tehdä päätelmiä.

## Lähetyskanava

Asetukset: `RESEND_API_KEY`, `URAKKALUOTSI_CONTACT_FROM`, `URAKKALUOTSI_CONTACT_TO`. Puuttuva konfiguraatio palauttaa 503: "Lähetys ei ole vielä käytössä." Hyväksytty palveluntarjoajan vastaus palauttaa 202; se osoittaa vastaanoton lähetyspalveluun, ei lopullista inbox-toimitusta. Varmista lähettäjä ja vastaanottava postilaatikko sekä testaa todellinen toimitus ennen tuotantoa.

## Tarkistukset

`npm test`, `npm run lint`, `npm run typecheck`, `npm run build`.
`node tests/auth-http.cjs --missing`, `node tests/auth-http.cjs`.
`node tests/sales-polish-qa.cjs` käyttää QA-ympäristön Playwrightia ja Chromea. `PLAYWRIGHT_MODULE` voi osoittaa valmiiksi asennettuun moduuliin; `CHROME_PATH` selainbinääriin. Ei runtime-riippuvuuksia. Lähetyspalvelun onnistumiset ja virheet simuloidaan, sähköpostia ei lähetetä.
`OPS_BROWSER_QA=true node tests/ops-http.cjs`: sisäisen portaalin työnkulku.

Vercelin tenderpulse-projekti ja nykyinen hosting-osoite tenderpulse-neon.vercel.app varmennettu connectorilla 19.10.2026. MetadataBase käyttää tätä hostia; canonical ja og:url jätetty asettamatta julkaisuosoitteen vahvistamiseen asti. Analytiikkaa ei löytynyt eikä sitä lisätty. Ei Hilma-kutsuja, ei liitteiden lataamista eikä tuotantojulkaisua.

Paikallinen esikatselu: `npm ci && npm run build && npm start`, sitten http://localhost:3000/esittely.
