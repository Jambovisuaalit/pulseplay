# Urakkaluotsi – AI-uusintasimulaation QA ja hyväksymispäätös

**SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS**

Testi 19.10.2026, 100 ainutkertaista Hilma-hakutulosta;
lähdeaineiston aikaleima `2026-10-19T00:12:27.163249+00:00`.
Yksi offline-ajo, ei 30 päivän seurantaa eikä oikean asiakkaan toimitusta.

## Kriittiset hyväksymistarkistukset

| Tarkistus | Tulos | Todiste / rajoitus |
| --- | --- | --- |
| Automaattinen määräaikaraja käsittelee vanhentuneet, aikavyöhykkeet ja päivämäärän tarkkuuden | **PASS** | Python- ja TypeScript-regressiot; 7 EXPIRED, 0 GO |
| Todellinen tarjous- ja kysymysmääräaika tarkistettu tarjousasiakirjoista | **NOT TESTED** | Hakumetadata ei sisällä luotettavasti alkuperäisten liitteiden kaikkia määräaikoja |
| Lähteen keskeytysmerkintä estää GO:n | **PASS** | Otsikko `KESKEYTETTY`, ID 59352; regressiot ja 1 CANCELLED |
| Kelpoisuusvaatimuksia tai yrityksen pätevyyksiä ei keksitä toimitukseen | **PASS** | Kelpoisuus ja liitteet tuntemattomia, vahvistettuja GO:ta 0 |
| Kaikki hankintakohtaiset kelpoisuusvaatimukset tunnistettu | **NOT TESTED** | Täysiä tarjousliitteitä ei tarkistettu |
| Kaikki toimituksen hankintaväitteet jäljitettävissä lähde-ID:hen | **PASS** | 100 yksilöllistä tunnistetta, `classified_notices.csv`, AI-sitaatit ja SHA-256 |
| Kohteiden toteutusalue ja urakkakoko varmennettu | **NOT TESTED** | Hakumetadata ei yksilöi täydellisiä työmaita eikä kaikkia urakkahintoja |
| Tekoälyvertailua ei esitetä riippumattomana gold-totuutena | **PASS** | 100 AI-silver-riviä, 0 ulkoista gold-riviä, official precision NOT MEASURED |
| PDF yhtenäinen hyväksyttyjen brändivärien kanssa, kahdella A4-sivulla, testimerkintä | **PASS** | ReportLab-pohjan uudelleenkäyttö, PNG-renderöinti molemmille sivuille |
| PDF:n ja sähköpostiluonnoksen lukujen vastaavuus | **PASS** | Molemmissa 100 / 93 / 7 / 0 ja sama lähteeseen viittaava mahdollinen kohde 59188 |
| Asiakasviesti lähetetty tai tuotantojulkaisu tehty | **NOT TESTED** | Ei toteutettu; erikseen kielletty tässä testissä |
| 30 päivän aktiivinen työaika, kustannus ja jatkuva toimivuus mitattu | **NOT TESTED** | Vain kertaluonteinen offline-testi |
| Python-regressiot | **PASS** | 21/21 (`unittest discover`) |
| TypeScript/Node-regressiot | **PASS** | 6/6 (`node --test`) |
| TypeScript-tyyppitarkistus ja Next.js-build | **PASS** | `npm run typecheck`, `npm run build` paikallisesti; ei deployta |

## Jäädytetyn AI-kierroksen osuvuus

AI-silver: **1 relevantti, 7 ehdollista, 91 epärelevanttia, 1 arvioimatta**.
Automaattisen seulonnan 15 positiivisesta yksi oli AI:n mielestä relevantti,
10 epärelevanttia ja 4 epäselvää. Selvästi luokiteltujen 92 rivin joukossa
alustava TP 1, FP 10, FN 0 ja TN 81. Epäselvyys mukaan lukien FP 10–14,
FN 0–4, precision 6,7–33,3 %. **Virallinen precision: NOT MEASURED.**
Mallin omia ennusteita ei käytetty AI-vertailuluokkien muodostamiseen;
AI-arvio ei silti ole riippumattomasti vahvistettua totuutta.

## Uusi toimitussimulaatio

- **100/100** lähde-ID:tä mukana; yhtään lähde-ID-duplikaattia ei löydy.
- Lähdehetkellä **93 OPEN**, **7 EXPIRED**; yksi OPEN-määräajalla
  olevan keskeytetty-ilmoituksen turvatila `CANCELLED`.
- Lopulliset turvatilat: **92 NOT_EVALUATED**, **7 EXPIRED**, **1 CANCELLED**.
- **0 vahvistettua GO-suositusta** ja 0 valmiiksi tarkistettua tarjousliitesarjaa.
- AI:n yksi alustavasti relevantti työ (Hilma 59188) jää **jatkoselvityksen
  ehdokkaaksi**, ei tarjous- tai soveltuvuussuositukseksi.
- 7 ehdollista AI-osumaa ja 1 arvioimaton rivi tarvitsevat lähdetarkistuksen.

## KPI-portit

| KPI | Tavoite | Tulos |
| --- | --- | --- |
| Relevanssin virallinen precision | ≥ 80 % | **NOT MEASURED** |
| Kriittiset faktavirheet | 0 | **NOT TESTED** täydellisiä asiakirjoja vasten |
| Keksityt kelpoisuustiedot toimituksessa | 0 | **PASS** tässä simulaatiossa |
| Jäljitettävyys rivitasolla | 100 % | **PASS** 100/100 hakumetadata-ID:tä |
| Koko kaupallisen toimituksen QA | 100 % | **NOT TESTED** |
| Aktiivinen työ / päivä / asiakas | alle 10 min | **NOT MEASURED** |
| Toistettavuus ilman uusia pohjia | ei uusia pohjia | **PASS** PDF-pohjan osalta; koko prosessi **NOT TESTED** |

## Lopullinen päätös

**CONDITIONAL PASS ainoastaan tekniselle turvaportille.**

**EI HYVÄKSYTTY ensimmäisen maksavan asiakkaan toimitukseen.** Alustavan
AI-precisionin alaraja on kaukana 80 %:sta, riippumaton totuus puuttuu,
liitteet ja yrityksen kelpoisuus ovat tuntemattomia ja todellinen työaika
mittaamatta. Täydellisten tarjousasiakirjojen puuttuessa ei ole todistettu,
ettei kriittisiä faktavirheitä olisi.
