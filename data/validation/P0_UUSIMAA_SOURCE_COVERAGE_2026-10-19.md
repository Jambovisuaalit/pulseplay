# Uudenmaan saneerausurakoiden lähdepakettien saatavuus – P0

Päiväys: 2026-10-19. Työhaara: `fix/urakkaluotsi-p0-validation`. Tämä on **saatavuuskartoitus**, ei gold-aineisto eikä tarjouskelpoisuuden vahvistus.

## Esikarsinta

| Ilmoitus | Lähteen kautta vahvistettu | Puuttuu |
|---|---|---|
| Hilma 59188, Tietotie 1, Espoo | Sijainti ja saneeraussisältö alkuperäisen eForms-XML:n perusteella | Alkuperäisen tarjouspyynnön koko teksti, kelpoisuusehdot, hinnoitteluliitteet, urakkarajat, kohdekäyntiehdot ja yksittäisen urakan arvo |
| Hilma 59375, Kastevuoren päiväkoti, Espoo | Sijainti, saneeraussisältö ja pakollinen kohdekäynti | Tarjouspyynnön ja liitteiden täydet ehdot, kelpoisuustiedot, urakan arvo, kohdekäynnin toteutumistodiste |

Portaalilinkit:
- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=631619
- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=611165

Hakukoneen ja julkisten päätösten avulla ei tässä vaiheessa saatu kummallekaan täydellistä alkuperäistä tarjouspyyntöpakettia. Muut löytyneet Helsingin kaupungin päätökset koskevat pääosin ICP:n ulkopuolisia infraurakoita tai asiakirjoja, jotka on toimitettu rajatulle tarjoajajoukolle. Päätös ei korvaa tarjouspyyntöä liitteineen.

## Toteutettu

- `data/validation/uusimaa_document_coverage_queue_2026-10-19.json`: puuttuvien asiakirjatyyppien rekisteri ja lähdestatus.
- `workers/evaluate_uusimaa_document_coverage.py`: tarkistaa SHA-256:n, URL:n ja noutoajan jokaiselta hyväksyttävältä lähdeasiakirjalta, raportoi puuttuvat asiakirjatyypit sekä estää positiivisen gold-luokan automaattisen luomisen.
- `tests/test_uusimaa_document_coverage.py`: kolme fail-closed-regressiotestiä.
- CI suorittaa puuttuvan lähdeaineiston tarkistuksen; nykyinen odotettu tila on **0 täydellistä pakettia**.

## Mittaus ja seuraava riippuvuus

**Kaksi esikarsittua Espoon ehdokasta, nolla täydellistä lähdepakettia, nolla vahvistettua positiivista ja Precision@30 = null.**

Lähdepakettien saatavuus ja osuvuuden mittaus ovat eri tehtäviä. Vasta kun tarvittavat alkuperäiset asiakirjat ovat kokonaan käytettävissä ja niiden ehdot sekä tarjoajaprofiilin tosiasiat on varmennettu, ehdokas voi siirtyä riippumattomaan arvioon. Ei saa päätellä, että pelkkä saneerausaihe ja oikea kaupunki todistaisivat tarjoajalle sopivuuden.

Jatko: priorisoi **Uudenmaan korjausrakennushankintojen alkuperäiset avoimet liitepaketit**, joista löytyvät tarjouspyyntö, kelpoisuus, työselostus, urakkarajat ja arvo. Käytä vain julkista pääsyä; jos tarjousasiakirjat edellyttävät kirjautumista, merkitse `ACCESS_RESTRICTED` ja jätä gold `UNREVIEWED`. Älä kierrä käyttöoikeuksia. Ei asiakastoimituksia, PR-mergeä eikä tuotantojulkaisua.
