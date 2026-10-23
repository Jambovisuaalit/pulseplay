# Urakkaluotsi – Style Guide / UI Kit v1.1

19.10.2026. Status: suunnitteluehdotus. Ei julkaistu, ei integroitu repoon.

## Avaa ensin
- ../Urakkaluotsi_Style_Guide_UI_Kit_v1_1.pdf: kuusisivuinen visuaalinen ohje.
- ui-kit.html: paikallinen komponenttiesimerkki. Pidä tokens.css ja assets-kansio vieressä.
- tokens.json / tokens.css: toteutuksen arvot.
- assets/: SVG-logoluonnokset. Sanamerkki on polutettu DejaVu Sans Bold; muokattava tekstilähde ja lisenssitieto ovat logos/-kansiossa.

## Ilme ja käyttösäännöt
Urakkaluotsi. Pääviesti ”Sopivat urakat. Selkeä seuraava askel.” Vaalea dokumenttimainen B2B-ilme; musteensininen teksti ja syaani korostus. Hae pilottiin on myyntisivun pää-CTA. Asiakaskoosteen päätoimi on hankinnan jatkoselvityspäätös. Näitä ei sekoiteta toisiinsa.

Verkkosisältö max 1120 px; marginaalit 20 px mobiili / 32 px desktop. 8 px kortit, 6 px painikkeet. Kortit 1 palsta mobiilissa; ei koko kortin skaalattua kuvaversiota, jos tekstiversio on mahdollinen. Verkkoteksti vähintään 16 px, PDF:n body 10–11 pt ja lähdeviite vähintään 8.5 pt. Ohje-PDF on visuaalinen esitys, ei verkkofontin mittatarkka renderöinti.

Tilat aina tekstillä: vahvistamatta, tarkistus tarvitaan, lähdetieto tarkistettu, määräaika päättynyt. Agentin tarkastus ei ole ihmisen hyväksyntä tai vahvistettu tarjouskelpoisuus. Lähteen fakta, oma tulkinta ja asiakkaalta puuttuva tieto esitetään erikseen. Ikoneihin pieni SVG/viivamuoto, ei emojeja. Ei generatiivisia työmaakuvia referenssinä tai tekaistuja käyttöliittymän tuloksia.

## Faktat ja rajaus seuraavalle mallille
Palvelu seuloo Suomen julkisia Hilma-ilmoituksia rakennus- ja saneerausyrityksen palveluihin ja alueeseen. Tavoite kaksi maksavaa pilottia. Asiakas saa sähköpostikoosteen; portaalia ei ole. Pilotti suunniteltu 30 päiväksi; hinta ja toimitusrytmi auki. Yritysprofiilit eivät ole vielä vahvistettuja. 80 % precision ja alle 10 min aktiivista työtä/päivä ovat mittaamattomia tavoitteita, eivät markkinointiväitteitä. Domain urakkaluotsi.fi suunniteltu, ei ostettu. Yhteystietoja ei ole vahvistettu. Nimen oikeudellista saatavuutta ei ole selvitetty. Urakkaluotsi on valittu nimi; älä jatka TenderPulse-nimen markkinointikäyttöä.

## Integrointikäsky
Toteuta näiden tokenien ja UI-esimerkkien mukaan vain pyydetty materiaali. Repotyössä varmista Jambovisuaalit/pulseplay, tenderpulse-mvp tai sen feature-haara; Vercel-projekti tenderpulse. Lue AGENTS.md ja säilytä nykyiset muutokset. Älä muuta teknisiä repo- tai projektinimiä. Ei uutta authia, laskutusta, dashboardia, riippuvuuksia, palveluita tai maksullisia API-kutsuja. Vain virallinen Hilma API hankintalähteenä, ei scrapingia. Ei API-kutsuja tämän tyylitehtävän vuoksi. Domain ja osoitteet konfiguroitaviksi. Älä näytä lomakkeen onnistumista ilman todellista vastaanottoa. Älä julkaise tai lähetä mitään. Vaihda kuvitteelliset rakenne-esimerkit vain lähteistettyyn aineistoon ja näytä aineistopäivä. Luo valmis toteutus, lähteet ja todelliset tarkistustulokset.

## Inspiraatio
- https://linear.app/ – tuotelähtöinen esittely ja tietohierarkia.
- https://www.vainu.com/fi/ – hyötyviestintä ja tiedon kytkentä toimenpiteeseen.
Nämä ovat sovellettavia periaatteita aiemman rakenne-/viestintätarkastelun perusteella. Verrokeista ei ole tehty kuvakaappauspohjaista visuaalista auditointia eikä kopioitu resursseja.

## Tarkistus
Kontrastit laskettu tokens.json-tiedostoon. Guide-PDF renderöidään ja sivut tarkistetaan ennen toimitusta. HTML sisältää oikeat label/for-, focus- ja aria-invalid/aria-describedby-merkinnät sekä toimivat sisäiset linkit. Ei API:a, analytiikkaa tai vastaanottoa. HTML:n selaintestaus ja lopullinen mobiili-/ruudunlukijavarmennus ovat tekemättä tässä ympäristössä. Tuotantologot on polutettu. Muokattava tekstiversio tarvitsee DejaVu Sans Bold -fontin. Ei näitä testejä väitetä läpäistyiksi.
