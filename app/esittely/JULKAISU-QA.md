# Urakkaluotsi – myyntisivun korjaus ja QA

Päivä: 19.10.2026 (Europe/Helsinki). PR: [#3](https://github.com/Jambovisuaalit/pulseplay/pull/3). Nykyinen design, sisältöjärjestys ja PDF säilytetty. Ei tuotantomergen tai tuotantodomainin hyväksyntää.

## Korjaukset

- Nykyiseen sivuun lisätty näppäimistön ohituslinkki; fokus säilyy näkyvänä myös lomakkeen ja tietosuojalinkin kohdalla.
- Mobiililogo vähintään 140 px, pääpainike vähintään 44 px. Lomakkeen kentät 16 px, jotta pienet fontit eivät aiheuta tarpeetonta iOS-zoomausta. 768 px käyttää nyt yhden palstan pääasettelua.
- Olennaiset korttien tilat eivät katoa pienissä näkymissä. Kapeiden palstojen min-width ja pitkien tekstien rivitys korjattu.
- Pakollisille kentille omat suomenkieliset virheet, `aria-invalid`, kenttäkohtainen `aria-describedby`, virheyhteenveto ja fokus ensimmäiseen virheeseen. Pelkkä välilyönti ei kelpaa sisällöksi.
- Mailto-luonnos muodostetaan vasta kelvollisista arvoista; ääkköset, `&`, `+` ja rivinvaihdot URL-koodataan. Viestiä ei lähetetä testissä tai sivustolta.
- Sähköpostisovelluksen puuttuessa valmis viesti on kopioitavissa; suora osoite näkyy aina. Ei väärää vastaanottokuittausta. JavaScriptin puuttuessa suora osoite korvaa lomakkeen.
- Tietosuojasivu lataa oman CSS:n myös suoraan avattaessa. Seloste kuvaa mailto-polun, kerättävät tiedot, käyttötarkoituksen, Gmailin/Vercelin, kansainvälisen käsittelyn, säilytyksen, pyynnöt ja tekniset lokit. Epäselvä jälkiseuranta korvattu kuuden kuukauden poistokäytännöllä ei-asiakkaiden yhteydenotoille.
- `/favicon.svg` sallitaan julkisesti. Muun sovelluksen kirjautumiskäyttäytymistä ei muutettu.
- Lisätty neljä Node-testiä, TypeScript-komento ja dependency-vapaa Chrome QA GitHub Actionsiin.

## Palveluntarjoajan tarkistus

Käyttäjän ilmoittamat tiedot: **Tmi Jami Harju**, **3581581-6**, **visualjambo@gmail.com**. Nämä näkyvät sivulla.

[YTJ:n yrityshaku](https://tietopalvelu.ytj.fi/yritys/3581581-6) avattu ja luettu 19.10.2026:

- Y-tunnus 3581581-6 löytyy.
- Yritysmuoto: yksityinen elinkeinonharjoittaja.
- Tunnus annettu 23.11.2025.
- Verohallinnon perustiedoissa rekisterissä 24.11.2025 alkaen.
- Julkinen haku ei näytä henkilön nimeä tai osoitetta. Nimen vastaavuutta ei siten väitetä viranomaisrekisteristä varmennetuksi; nimitieto perustuu käyttäjän ilmoitukseen. Kaupparekisterimerkintää tai verorekistereitä ei päätellä pelkästä Y-tunnuksesta.

PRH:n open data -rajapinnan nollatulos ei tarkoita virheellistä tunnusta: palvelu ei sisällä yksityisiä elinkeinonharjoittajia. [YTJ:n rajauksen kuvaus](https://www.ytj.fi/index/avoindata.html).

## Testien käyttäjätarina

Vierailija avaa julkisen esittelyn → tutustuu nelisivuiseen PDF:ään → täyttää pilottiyhteydenoton → korjaa mahdolliset virheet → avaa sähköpostiluonnoksen tai kopioi tekstin → lähettää itse omassa sähköpostissaan. Sivusto ei ole vastaanottava lomakepalvelu eikä väitä hakemusta vastaanotetuksi.

## Tulokset

| Tarkistus | Tulos | Näyttö |
|---|---|---|
| npm test | PASS | 4/4 validointi-/URL-koodauksen testiä, paikallisesti ja CI:ssä |
| npm run typecheck | PASS | Paikallinen ja Actions TypeScript |
| npm run build | PASS | Paikallinen ja Actions Next.js 15.5.28 production build |
| 375 px | PASS | Ei vaakaylivuotoa; logo 140 px; pääpainike 46.5 px; kentät 16 px; kaikki kolme virhe-/hakemustilaa |
| 390 px | PASS | Ei vaakaylivuotoa; logo 140 px; pääpainike 46.5 px; kentät 16 px; kaikki kolme virhe-/hakemustilaa |
| 768 px | PASS | Yksi palsta; logo 155 px; pääpainike 48.5 px; kentät 16 px; virhe-/hakemustilat |
| 1440 px | PASS | Nykyinen kahden palstan hero; logo 194 px; pääpainike 54.5 px; virhe-/hakemustilat |
| Tietosuojasivu, neljä leveyttä | PASS | Suora avaus, tyylit, ei vaakaylivuotoa |
| Lomakkeen tyhjät kentät | PASS | 5 kenttävirhettä; ensimmäinen kenttä fokukseen |
| Virheellinen sähköposti | PASS | Vain sähköpostivirhe, fokus ja ohjelmallinen virhekuvaus |
| Kelvollinen hakemus | PASS | Koodattu mailto ja valmis kopioitava viesti; ei vastaanottoväitettä |
| Näppäimistön ohituslinkki | PASS | Ensimmäinen Tab näyttää ohituksen; Enter siirtää fokuksen mainiin |
| Lomakkeen tabulaattorijärjestys | PASS | Yritys → Nimi → sähköposti → alue → työt → tietosuoja → painike; näkyvä fokus |
| PDF ja julkiset reitit | PASS HTTP | 200 application/pdf; 81 071 tavua; neljä A4-sivua. Esittely, tietosuoja, logo ja favicon 200 |
| Dashboardin suojaus | PASS HTTP | Juurireitti ilman istuntoa: 307 /login |
| Visuaalinen tarkastus | PASS rajatusti | Actionsin neljä sivukuvaa tarkastettu; mobiilin hero ja lomake sekä desktop-hero myös erillisinä rajauksina |
| FAQ Enter | PASS | Natiivi details avautuu Enterillä |
| Tekstin suurennus 200 % | PASS | 1440 px, ei vaakaylivuotoa; tämä on tekstisuurennus, ei natiivin selaimen zoom-sertifiointi |
| JavaScript pois käytöstä | PASS | Toimimaton lomake piiloutuu ja suora sähköpostilinkki näkyy |
| JavaScript-runtime | PASS | Runtime.exceptionThrown: 0 |
| Jäädytetyn PDF:n eheys | PASS paikallisesti ja CI:ssä | SHA-256 36762a526ae0a7299098c77e8e64a9ca78d15b4a3ac0b9a4624b7b9e4ad1e69b; 4 sivudictionaryä; pdfinfo erikseen 4 sivua |

Selaintestit: Chrome headless Linuxissa, viewportit CSS-pikseleinä; tämä ei ole fyysisen iPhone-laitteen Safari-testi. Ensimmäiset kaksi CI-ajoa pysähtyivät natiivin FAQ-kontrollin Enter-simulaatioon: keyDown/keyUp ilman tarvittavaa keypress-tekstiä. Tuotteen lomake-/layout-tarkistukset läpäisivät jo näissä ajoissa. Kolmas ajo läpäisi kaikki 22 selaincheckiä, mutta ajon kokonaisuus jäi punaiseksi runnerin puuttuvan pdfinfo-ohjelman vuoksi. Se korvattiin fixturekohtaisella SHA-256- ja sivumäärätestillä; kyse ei ole yleiskäyttöisestä PDF-parserista. Lopullinen ajotulos kirjataan erikseen alla.

## Tietosuojan ja toimituksen käytännön rajaus

Sähköpostin kuuden kuukauden poistokäytäntö on tässä työssä määritelty toimintatapa. Sitä ei ole automatisoitu Gmailiin eikä käyttäjän postilaatikosta ole poistettu viestejä. Tilikohtainen Google-/Vercel-sopimus, käytännön lokisäilytys, kansainvälisten siirtojen suojatoimet ja rekisterinpitäjän säilytyskäytännön noudattaminen eivät ole tämän ohjelmistotestin todentamia.

Virallista GDPR-tekstiä haettiin EUR-Lexistä, mutta Lakimies AI -ohjeen edellyttämiä artikla- ja ajallisuusvarmennuksen MCP-työkaluja ei ollut tässä sessiossa saatavilla. **Lähdevarmennus epäonnistui – en voi vahvistaa oikeustilaa.** Virhekoodi: `TOOL_UNAVAILABLE`. Selostetta ei ole merkitty juridisesti varmennetuksi tai täydelliseksi vaatimustenmukaisuustodistukseksi. [Tarkastettu EUR-Lex-lähde](https://eur-lex.europa.eu/legal-content/FI/TXT/?uri=CELEX:02016R0679-20160504).

Säilytys-/siirtokäytännön vahvistus on erotettu teknisestä QA:sta. Myös natiivin iOS Safarin, Androidin sähköpostisovelluksen sekä todellisen vastaanottajan inbox-toimituksen testi on erillinen laite-/palvelutesti. Tässä työssä ei lähetetä oikeaa hakemusta.

## Toistaminen ja näyttö

Node 24: `npm test`, `npm run typecheck`, `npm run build`. Chromium: `node tests/browser-qa.cjs`, jonka ajossa Chrome löytyy oletuksena komennolla `google-chrome`; vaihtoehtoinen binääri voidaan antaa `CHROME_PATH`-muuttujalla. Tulokset kirjoitetaan `qa-output/results.json`-tiedostoon; mukana on neljä näkymäkuvaa. QA-tiedot ovat synteettisiä.

Paikallinen production build, TypeScript ja yksikkötestit onnistuivat. Tavallinen `next start` ja paikallisen Chromen käynnistys estyivät ympäristörajoituksiin; Chrome-testit suoritettiin siksi GitHub Actionsissa. HTTP-savutesti suoritettiin production-buildin Next-request handlerilla samassa prosessiympäristössä, ilman runtime-koodin kiertopaikkauksia.

Vanha `npm run lint` viittaa Next 15:ssä poistuneeseen `next lint` -komentoon. Erillistä ESLint-tarkistusta ei väitetä suoritetuksi, eikä tämän työn vuoksi lisätty npm-riippuvuuksia. Juurireitin vanha autentikointitoteutus ei ole kokonaisuutena turvallisuusauditoitu tässä myyntisivun työssä.

## Hyväksymispäätös

**Tekninen QA hyväksytty testatussa laajuudessa.** Julkisen myyntisivun ja mailto-yhteydenottopolun suoritetuissa tarkistuksissa ei löytynyt kriittisiä toiminnallisia, näppäimistökäytön tai responsiivisuuden virheitä. Tämä ei ole koko WCAG-kriteeristön sertifiointi.

Lopullinen [GitHub Actions -ajo 39176008504](https://github.com/Jambovisuaalit/pulseplay/actions/runs/39176008504): **completed / success**, job sales-qa **success**, kaikki pakolliset vaiheet onnistuneet. Testattu commit: `87cc22631184f1519823ff7208d4bae8fec17628`. Neljä yksikkötestiä, TypeScript, build, 22 selaintarkistusta sekä PDF:n eheys/sivumäärä läpäisevät. Ensimmäiset epäonnistuneet ajot eivät ole hyväksynnän peruste.

Lopullinen raporttipäivitys on vain Markdown-muutos; sovelluksen ja testien lähteet vastaavat tätä vihreänä testattua committia. Tuotantomergelle tai domainin käyttöönotolle ei anneta tällä teknisellä testillä erillistä hyväksyntää. Rekisterinpitäjän todellisten käsittely-/säilytys-/siirtokäytäntöjen vahvistus sekä natiivien sähköpostisovellusten ja todellisen vastaanoton testi ovat edellä yksilöidyt rajaukset.
