# P0 – julkisten tarjouspyyntöjen gold-aineiston esikarsinta 19.10.2026

Tavoite: löytää **todellisia** korjausrakentamisen hankintoja, joiden tarjouspyyntö, kelpoisuusehdot, arvo ja tarvittavat liitteet ovat julkisesti kokonaisuudessaan luettavissa ilman tunnistautumista. Aineisto on **tarkoituksella etsitty esikarsinta**, ei riippumaton satunnaisotos eikä Precision@30:n perusta.

## Toteutettu haku ja lähteiden saavutettavuus

| Kohde | Lähde | Tarkistettu havainto | Este positiiviselle gold-luokalle |
|---|---|---|---|
| Sankariniemi, Iisalmi | https://ysao.fi/2026/10/01/tarjouspyynto-sankariniemen-a-siiven-saneerauksen-ja-auditorion-muutoshankkeen-valvontatyosta/ | Hakukoneen indeksoima laaja liiteluettelo, valvontapalveluhankinta. Suora verkkohaku palautti ei löydy -sivun. | Väärä alue, valvontapalvelu eikä rakennusurakka; täysi lähde ei saatavilla |
| Sydänpuunpuisto, Helsinki | https://paatokset.hel.fi/fi/asia/hel-2026-010970?paatos=3b32626d-de09-c458-875e-a014ebf00000 | Kaupungin hankintapäätös kertoo tukimuurin kuorielementtien asennusurakasta. Tarjouspyyntö, urakkaohjelma ja sopimusmalli on nimenomaisesti merkitty internetissä julkaisemattomiksi. | ICP:n ulkopuolinen infra, täydet tarjousasiakirjat puuttuvat |
| Tuomarilan päiväkoti, Espoo | https://viranhaltija.fi/haku/?page=2&q=tilapalvelut&sort=newest | Hakutuloksen päätöstiivistelmä ilmoittaa voittaneeksi urakkahinnaksi 379 000 € | Voittaneen tarjouksen hinta ei ole sama kuin tarjouspyynnön ennakoitu arvo; ei täydellisiä tarjouspyyntöliitteitä |
| Mankkaan päiväkoti, Espoo | https://viranhaltija.fi/haku/?page=2&q=tilapalvelut&sort=newest | Hakutuloksen päätöstiivistelmä ilmoittaa 687 000 € sopimuksen | Vastaava arvo- ja asiakirjaeste |

Tarkat koneelliset esikarsintatiedot: `data/validation/public_tender_candidates_2026-10-19.json`.

## Automaattinen hyväksyntäportti

`workers/public_source_gold_gate.py` vaatii samanaikaisesti:
- Vahvistetun täydellisen tarjouspyynnön tekstin, kelpoisuusehdot, urakan hinnan/laajuuden lähteen ja liiteindeksin. Kullakin URL, SHA-256 ja noutoaika.
- ICP:n mukaisen sijainnin ja päätyön.
- Yksittäisen sopimuksen 10 000–250 000 € arvon lähdepohjaisen todentamisen.
- Tarjoajakelpoisuuden ehtojen läpikäynnin.

Hyväksyntäportin läpäisy antaa vain **SOURCE_REVIEW_READY**, ei automaattista gold-positiivista. Riippumaton sokkoarvio vaaditaan edelleen. Hakutulos, julkinen hankintapäätös tai liiteluettelo ei riitä.

## Tulos

- Esikarsintaan kirjattu **4** todellista julkista hankintakohdetta.
- Täydellisen lähdeaineiston tarkistukseen hyväksytty **0**.
- Vahvistetut positiiviset **0**.
- Tarkastellut kohteet ovat pääosin historiallisia; niitä ei saa käsitellä asiakkaan nykyisin avoimina tarjousmahdollisuuksina.
- Precision@30, recall ja malliversioiden osuvuusero **NOT MEASURED**.

Seuraava automatisoitava vaihe: etsi suoraan julkaistuja hankintayksikön tarjouspyyntö-PDF:iä ja liitteitä, vahvista lataus ja sisältö, tallenna tarkistussummat, ja tee riippumaton lähdearvio. Jos täydellistä pakettia ei ole julkisesti, kohde jää `PARTIAL_OR_MISSING`-tilaan. Ei keinotekoisia positiivisia, ei asiakastoimituksia eikä tuotantojulkaisua.
