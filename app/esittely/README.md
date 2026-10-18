# Urakkaluotsi – julkinen myyntisivu

Nykyinen design säilytetään. Julkiset reitit ovat `/esittely`, `/esittely/tietosuoja` ja `/urakkaluotsi/*`. Juurireitin dashboard säilyy suojattuna.

## Muokkaus

- `page.tsx`: sivun teksti, hero ja nelisivuisen demon linkit.
- `site.css`: nykyinen layout ja rajatut responsiivisuus-/saavutettavuuskorjaukset.
- `contact.ts`: kenttien rajat, validointi ja mailto-luonnoksen muodostus.
- `pilot-form.tsx`: virhetilat, fokus ja kopioitava varaviesti.
- `tietosuoja/page.tsx`: nykyisen yhteydenottotavan tietosuojaseloste; lataa oman tyylitiedostonsa myös suoralla avauksella.
- `JULKAISU-QA.md`: testien tulokset ja jäljellä olevat rajoitteet.

## Palveluntarjoaja ja tietojen käsittely

Tmi Jami Harju, Y-tunnus **3581581-6**, väliaikainen yhteys **visualjambo@gmail.com**. Käyttäjä on antanut nimen, tunnuksen ja osoitteen. YTJ:n yrityshaussa 19.10.2026 tunnus löytyy yksityisenä elinkeinonharjoittajana, Verohallinnon perustiedoissa rekisterissä 24.11.2025 alkaen. Julkinen hakutulos ei näytä henkilön nimeä; sitä ei väitetä rekisteristä varmennetuksi.

Lomake muodostaa luonnoksen käyttäjän omaan sähköpostisovellukseen. Se ei lähetä viestiä palvelimelle, tallenna kenttiä tai vahvista vastaanottoa. Käyttäjä lähettää itse. Puuttuvan sähköpostisovelluksen varalle valmis teksti on kopioitavissa sivulta; suora sähköpostiosoite on aina näkyvissä. JavaScriptin puuttuessa näytetään suora yhteystieto ja piilotetaan toimimaton lomake.

Tietosuojaselosteen säilytysraja ei-asiakkaiden yhteydenotoille on enintään kuusi kuukautta viimeisestä yhteydenotosta, jollei avoin selvitys tai vaade edellytä pidempää. Palveluntarjoajan tulee toteuttaa poistokäytäntö sähköpostissa; sivusto ei voi poistaa Gmail-viestejä. Sähköpostipalvelu on Gmail ja hosting Vercel. Tilikohtaisia sopimus-/siirtojärjestelyjä tai lokisäilytystä ei väitetä tarkastetuiksi. Teksti ei ole oikeudellisen vaatimustenmukaisuuden varmennus.

## Toistettavat tarkistukset

- `npm test`: Node 24, neljä lomakkeen validointi- ja encoding-testiä, ei ulkoisia kutsuja.
- `npm run typecheck`: TypeScript.
- `npm run build`: Next.js production build.
- `node tests/browser-qa.cjs`: Chrome + Node 24, neljä viewportia, virhetilat, mailto-varapolku, näppäimistö, tekstin suurennus, JS pois käytöstä ja julkiset/suojatut HTTP-reitit. Käyttää vain Node- ja Chrome-vakiotyökaluja, ei uusia npm-riippuvuuksia.
- `.github/workflows/urakkaluotsi-sales-qa.yml`: ajaa tarkistukset feature-haaran muutoksista; tulokset ja QA-kuvat ovat Actions-artifaktissa. Testien henkilötiedot ovat synteettisiä, sähköpostia ei lähetetä.

Olemassa oleva `npm run lint` käyttää Next 15:ssä poistunutta `next lint` -komentoa; sitä ei nimetä toimivaksi lint-tarkistukseksi. Runtime-riippuvuuksia ei lisätty. Native iOS Safari ja todellisen sähköpostin vastaanotto eivät sisälly automatisoidun Chromen testiin.

## Julkaisu

Domainit on ostettu; DNS-/tuotantokytkentää ei tehdä tällä PR-korjauksella. Varmista kaupallinen hinta, toimitusrytmi ja ehdot ennen tilausta. Katso hyväksymispäätös QA-raportista. Ei mergeä eikä erillistä tuotantopromootiota tässä työssä.
