# Urakkaluotsi – julkinen myyntisivu

- Reitti: `/esittely` (säilyttää nykyisen suojatun dashboardin juurireitillä).
- Copy, tietosisältö ja PDF-linkit: `page.tsx`.
- Pilottihakemuksen väliaikainen yhteydenotto: `pilot-form.tsx` avaa täytetyn viestin käyttäjän sähköpostisovellukseen osoitteella `visualjambo@gmail.com`. Käyttäjän pitää lähettää se itse; selaimesta ei voida vahvistaa vastaanottoa eikä tietoja tallenneta sivustolle. Ei serveripuolen vastaanottoa.
- Visuaalinen toteutus: `site.css`, Urakkaluotsin bränditokenit.
- Logo: `public/urakkaluotsi/logo-primary.svg` ja `logo-white.svg`.
- Nelisivuinen julkinen demo: `public/urakkaluotsi/esimerkkikooste.pdf`.

## Ennen tuotantojulkaisua

1. Palveluntarjoaja on Tmi Jami Harju, **Y-tunnus 3581581-6** (käyttäjän ilmoittama 19.10.2026; muodollinen tarkistusnumero täsmää). Rekisteritietojen vastaavuus YTJ:ssä ja mahdolliset muut yritystiedot tulee vielä tarkistaa ennen julkaisua.
2. `tietosuoja/page.tsx` kuvaa nykyistä mailto-yhteydenottoa, ei tulevaa API-lomaketta. Rekisterinpitäjän tulee vahvistaa rekisteritiedot, säilytyksen kriteerit ja tosiasialliset sähköposti-/hosting-palveluntarjoajat sekä mahdolliset kansainväliset siirrot. Jos käsittelytapa muuttuu, päivitä teksti ennen käyttöönottoa.
3. Väliaikainen yhteysosoite on `visualjambo@gmail.com` (vahvista vielä Urakkaluotsin käyttöön). Varsinaista suoraa verkkolomakelähetystä varten toteuta palvelinpuoleinen vastaanotto, validointi, kaksoislähetysten esto ja virhetilat. Älä rinnasta `mailto`-avausta onnistuneeseen lähetykseen.
4. Varmista pilottihinta, toimitusrytmi ja kaupalliset ehdot ennen tilausta.
5. Domainit `urakkaluotsi.fi` ja `urakkaluotsi.online` on ostettu, mutta yhteyttä sivustoon ei ole asetettu. Vahvista varsinainen käyttödomen ennen canonical- ja Open Graph -osoitteita.
6. Mittausvalmius: `pilot_cta_click`, `example_open`, `lead_submit_success` (vasta todellisen onnistumisen jälkeen); älä lähetä henkilötietoja analytiikkaan.

## Tarkistukset

- `npx tsc --noEmit`: PASS 19.10.2026.
- `npm run build`: PASS 19.10.2026, `/esittely` prerenderöity staattisesti.
- Päivitetyn sähköpostiluonnoksen jälkeen `npm run build`: PASS 19.10.2026.
- HTTP-savutestiä ei voitu suorittaa tässä ympäristössä: Next.js käynnistys pysähtyi `uv_interface_addresses`-järjestelmävirheeseen. Tämä ei ole osoitus reitin toimivuudesta tai viasta palvelimella.
- PDF: neljä A4-sivua (`pdfinfo`).
- Responsiivinen suunnittelu: 375 / 390 / 768 / 1440 px -breakpointit CSS:ssä; selaimen visuaalinen QA ja näppäimistötestaus vielä tekemättä.
- 19.10.2026: uusi julkinen `/esittely/tietosuoja`-reitti, tietosuojalinkit lomakkeessa ja footerissa, `middleware.ts`-poikkeus. `npm run build`: PASS; molemmat sivut staattisesti prerenderöity; `git diff --check`: PASS.
- Paikallinen Next.js HTTP-testi pysähtyi edelleen `uv_interface_addresses`-järjestelmävirheeseen. **Mobiili-/desktop-selaimessa ei ole vielä todennettua läpikäyntiä**, eikä PDF-linkin toimintaa vahvistettu toimivalla selaimella; pelkkä CSS-breakpointtien olemassaolo ei ole QA-hyväksyntä.
- Repossa ei ole `npm test` -skriptiä, eikä toimivaa `next lint` -skriptiä nykyisellä Next.js-versiolla.

Ei julkaistu tuotantoon.
