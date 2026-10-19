# P0: lukitun Top 30:n tekoälyavusteinen lähdekatselmointi, 19.10.2026

## Suoritettu, ei vain suunniteltu
Kävin läpi **kaikki 30** aiemman 100 hankinnan ennustejoukon lukitut top-osumat. Arviointisyötteessä käytin todellisen Hilma-haun tallennettua otsikkoa, kuvausta, määräaikaa ja mahdollista metatietoarvoa; en käyttänyt aiempaa malliluokkaa tai sijoitusta perusteluina. Jokainen rivi on tallennettu tiedostoon `data/validation/p0_blind_ai_silver_reviews_2026-10-19.json`. Jokaisella on ilmoitustunnus, lähdetiedoston GitHub-osoite, kuvausote, perustelu, ongelmaluokka ja puuttuvan todistusaineiston luettelo.

## Katselmoinnin alustavat AI-metatietoluokat
- `NOT_RELEVANT`: **20/30**. Lähdekuvauksissa ilmenee useimmiten Uudenmaan ulkopuolinen kohde tai hankintayksikön toiminta-alue, uudisrakennus-/infra-/suunnittelutyö, yksikkökoon ylittävä metatietoarvo, keskeytys tai umpeutunut tarjousaika. Näitä ei ole vielä adjudikoitu täydellisestä alkuperäisestä tarjouspaketista.
- `UNKNOWN`: **10/30**. Työlaji voi olla sopiva mutta kohteen sijainti, yksittäisen urakan koko, liitteet tai yrityskohtaiset ehdot eivät ole riittävästi todennettu.
- `RELEVANT`: **0 vahvistettua**. Puuttuvia asiakirjoja ei saa käsitellä hyväksyntänä.

Erityisen hyödyllinen havainto on peruutetun `59352`-ilmoituksen esiintyminen lukitun mallirankingin kärjessä. Se on selkeä pisteytyksen vanhentuneen ilmoituksen suodatusongelman regressiotapaus, ei näyttö kelpoisesta urakasta.

## Ero varsinaiseen osuvuusmittaukseen
Katselmointi on **AI-silver / metadata-only preliminary screening**. Kaikilta 30 tapaukselta puuttuu vähintään osa täydellisestä alkuperäisen eForms-version, liitepaketin, yksittäisen sopimusosan arvon tai tarjoajakelpoisuuden todistusaineistosta. Siksi *täydellisiä lähdepohjaisia sokkoarvioita on 0/30* ja `AI_SOURCE_REVIEWED_PRECISION_AT_30 = null`; 80 % hyväksymisrajaa ei ole osoitettu eikä siihen verrata alustavien negatiivisten lukumäärää. Tämä on tarkoituksenmukainen laadunvarmistuksen rajaus.

## Tiedostot ja hyväksymisportti
- `data/validation/p0_frozen_ranked_100_2026-10-19.json`: ennen arviointia lukittu ranking.
- `data/validation/p0_top30_ai_metadata_silver_screen_2026-10-19.json`: erillinen lähderiveittäin auditoitava katselmointi.
- `data/validation/p0_blind_ai_silver_reviews_2026-10-19.json`: 30 arviointiriviä varsinaisessa AI-silver-arviointirekisterissä.
- `workers/evaluate_p0_blind_ai_source_review.py`: puuttuvan evidenssin fail-closed-portti.
- `tests/test_p0_actual_30_ai_review.py`: 30/30 kattavuus, AI-luokkajakauma, mittarin pysyminen null-arvossa.

## Seuraava tekninen riippuvuus
Tarvitaan alkuperäisen hankintakohtaisen liiteaineiston ja pakollisten kelpoisuustietojen saatavuus. Tarjouspalvelussa osa on kirjautumisen takana. Tekoälyä voidaan käyttää aineiston arviointiin ilman ulkopuolista arvioijaa, mutta puuttuvien alkuperäislähteiden merkintää ei voi kiertää. Lisäksi alkuperäisen 100-otoksen ja eri hankintaversioiden todelliset virheosumat tulee korjata pisteytyksessä **erillään lukitusta validointijoukosta**.

Ei uusia Hilma API -kutsuja eikä liitelatauksia, ei asiakastoimituksia, ei julkaisuja, ei PR-mergeä.
