# Urakkaluotsi – julkinen myyntisivu

- Reitti: `/esittely` (säilyttää nykyisen suojatun dashboardin juurireitillä).
- Copy, tietosisältö ja PDF-linkit: `page.tsx`.
- Pilottihakemuksen esikatselu: `pilot-form.tsx`. Lähetys on tarkoituksella estetty, sillä vastaanottajaa, käsittelyä ja tietosuojaa ei ole vahvistettu. Älä ilmoita onnistumisesta ilman palvelinvahvistusta.
- Visuaalinen toteutus: `site.css`, Urakkaluotsin bränditokenit.
- Logo: `public/urakkaluotsi/logo-primary.svg` ja `logo-white.svg`.
- Nelisivuinen julkinen demo: `public/urakkaluotsi/esimerkkikooste.pdf`.

## Ennen tuotantojulkaisua

1. Vahvista palveluntarjoajan juridinen nimi, yhteystiedot ja tietosuojateksti.
2. Toteuta palvelinpuoleinen hakemuksen vastaanotto, validointi, kaksoislähetysten esto ja virhetilat; poista vasta sitten estetty lähetyspainike.
3. Varmista pilottihinta, toimitusrytmi ja kaupalliset ehdot ennen tilausta.
4. Vahvista domain ennen canonical- ja Open Graph -osoitteita.
5. Mittausvalmius: `pilot_cta_click`, `example_open`, `lead_submit_success` (vasta todellisen onnistumisen jälkeen); älä lähetä henkilötietoja analytiikkaan.

## Tarkistukset

- `npx tsc --noEmit`: PASS 19.10.2026.
- `npm run build`: PASS 19.10.2026, `/esittely` prerenderöity staattisesti.
- PDF: neljä A4-sivua (`pdfinfo`).
- Responsiivinen suunnittelu: 375 / 390 / 768 / 1440 px -breakpointit CSS:ssä; selaimen visuaalinen QA ja näppäimistötestaus vielä tekemättä.
- Repossa ei ole `npm test` -skriptiä, eikä toimivaa `next lint` -skriptiä nykyisellä Next.js-versiolla.

Ei julkaistu tuotantoon.
