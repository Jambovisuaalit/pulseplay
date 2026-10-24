# P0 – Uudenmaan alkuperäisten tarjousasiakirjojen löytö ja varmennus (19.10.2026)

## Löydös

Hilman julkisesta liitearkistosta löytyi **neljä** Helsingissä sijaitseviin saneeraus- tai korjaushankkeisiin liittyvää alkuperäistä PDF-asiakirjaa. Ne on lisätty ennalta määritettyyn, julkisiin URL-osoitteisiin rajattuun PDF-manifestiin. GitHub Actions -ajo https://github.com/Jambovisuaalit/pulseplay/actions/runs/39197752379 **PASS**: 7 PDF-yritystä yhteensä (mukaan lukien kolme vanhaa kontrollia), **6 onnistunutta**, **1 URLError**, **0 täydellistä tarjousasiakirjapakettia**. Kaikki neljä uutta Helsinki-PDF:ää ladattiin ja tekstipoimittiin.

| Kohde | Lähdeasiakirja | PDF:n sivut | SHA-256 | Arvion status |
|---|---|---:|---|---|
| Musiikkitalo IV-puhaltimien saneeraus, **2025** | [Alkuperäinen tarjouspyyntö](https://cdn.hankintailmoitukset.fi/public-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff) | 5 | `86663197595eff9ad318ab6acd1aa41d9391f410fc57639192b8dc386f8c0eda` | Erikois-IV, ei yleisen saneeraus-ICP:n positiivinen |
| Pohjola Sairaala Helsinki 4. krs, **2020** | [Alkuperäinen tarjouspyyntö](https://cdn.hankintailmoitukset.fi/public-attachments/42f2a55c-dc72-4832-4445-08d8241b96e8) | 3 | `c57e670f5909ed2837ebcbafeea8fff7bb521ab7e8708533ec2ed5c778e36187` | Sisätilojen muutostyöt, mahdollinen ICP, ei gold |
| Uspenskin katedraali, Helsinki | [Alkuperäinen rakennustyöselostus](https://cdn.hankintailmoitukset.fi/public-attachments/4efc21a0-a41e-4fb0-6f5d-08d813538d7d) | 9 | `3fed9b93014f66005668f16b819c75222a138e7d008bc6d3034d3932d1a8384d` | Piikkaus-, paikkaus- ja maalaustyöt, mahdollinen ICP, ei gold |
| Musiikkitalo IV-puhaltimien saneeraus, **2026** | [Urakkaohjelma 17.3.2026](https://cdn.hankintailmoitukset.fi/public-attachments/680a9605-60c3-4165-b0ae-08de83eb31df) | 14 | `cff504c30bdaf4dd07786dd7460623393e66f766364e8826b0d333ec3d317374` | Erillinen lähdevuosikerta; ei yhdistetä vuoden 2025 tarjouspyyntöön |

## Lähteistä tarkistetut olennaiset ehdot

**Pohjola Sairaala, 2020.** Alkuperäinen tarjouspyyntö koskee kolmen potilashuoneen muuttamista kuudeksi ja erikseen hinnoiteltavia rakennus-, LVIA- ja sähköurakoita. Siinä vaaditaan tarjoajalta vähintään **500 000 € toiminnan vastuuvakuutusta**, kolmen tilikauden liikevaihtotiedot, luottoluokitustieto ja vähintään **kolme soveltuvaa referenssiä**. Tarjouspyynnön lopussa nimetään `Liite 1 Rakennusurakka.zip`, `Liite 2 LVIA urakka.zip` ja `Liite 3 Sähköurakka.zip`, mutta näitä liitepaketteja ei ole vielä ladattu tai tarkastettu. **Yksittäisen urakan ennakoitu arvo puuttuu.** Tarjousten määräaika 10.8.2020, joten historiallinen.

**Musiikkitalo, 2025.** Alkuperäinen tarjouspyyntö käsittelee kuuden ilmanvaihtokoneen AC-puhaltimien korvaamista EC-puhallinseinillä. Tarjouspyyntö edellyttää rakennuspaikkaan tutustumista 14.3. tai 20.3.2025. Työaika 2.6.–29.8.2025. Urakka on erikoistunut IV-työ, ei automaattinen yleissaneeraus-ICP:n osuma.

**Uspenski.** Työselostus koskee sähkötöihin liittyviä piikkaus-, paikkaus- ja maalaustöitä Helsingin Kanavakadulla. Se ei ole itsessään täydellinen tarjouspyyntö: hinnan, tarjoajan kelpoisuusehtojen ja muun liitekokonaisuuden arviointi puuttuu.

**Musiikkitalo, 2026.** Erillinen 17.3.2026 päivätty urakkaohjelma. Vaikka projektinimi muistuttaa 2025 tarjouspyyntöä, **näitä ei yhdistetä** ilman tarjouspyyntöön sidottua asiakirjaversiota ja lähdeviitettä.

## Toteutetut muutokset

- `workers/collect_public_tender_pdfs.py`: rajattu pääsy alkuperäisiin `cdn.hankintailmoitukset.fi/public-attachments/<uuid>`-liitteisiin, 12 asiakirjan katto, SHA-256, noutoaika, tekstinpoiminta, alkuperäisen PDF:n tallennus artefaktiin.
- `data/validation/public_pdf_manifest_2026-10-19.json`: neljä uutta alkuperäistä Helsinki-asiakirjaa, lähdevuosikerrat erillään.
- `data/validation/helsinki_original_tender_discovery_2026-10-19.json`: alustava riippumaton lähdearvio, tiedossa olevat ehdot, puuttuvat liitteet, ei gold-positiivisia.
- `tests/test_public_pdf_collector.py`: julkinen Hilma-liite hyväksytään, yksityisen liitepolun nouto estetään.
- `workers/extract_public_pdf_requirements.py`: laajennettu `kohteen esittely` -ilmaisun tunnistus.

## Tulos ja päätös

**Uudenmaan alkuperäisten tarjous- tai työselostusasiakirjojen löytyminen ja lataaminen on nyt teknisesti todistettu.** Täydellisen tarjousasiakirjapaketin löytymistä **ei ole todistettu**. Nämä ovat tarkoituksella haettuja historiallisia esimerkkejä, eivät riippumaton 30 osuman holdout.

- Alkuperäisiä Helsinki-PDF:iä varmennettu: **4**.
- Täydellisiä tarjouspyyntöpaketteja: **0**.
- Gold-positiivisia: **0**.
- Precision@30: **null**.
- 80 %:n hyväksymisraja: **todentamatta**.

**Seuraava tarkka riippuvuus:** etsi alkuperäisen tarjouspyynnön ilmoitukseen kuuluvat **kaikki** julkiset liitteet, erityisesti Pohjolan rakennusurakan ZIP ja Uspenskin tarjouspyyntö, ja yhdistä ne ilmoitustunnuksen ja lähdeasiakirjojen perusteella, ei pelkällä nimiosumalla. Julkisissa liitteissä mahdollisesti olevat henkilötiedot pidetään vain sisäisessä lyhytikäisessä artefaktissa. Ei asiakastoimituksia, tuotantojulkaisua eikä PR:n yhdistämistä.
