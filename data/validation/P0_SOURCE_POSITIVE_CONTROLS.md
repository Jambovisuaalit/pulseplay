# Positiiviset ja negatiiviset kontrollit – P0 lähdenäyttö

Tämä ei ole uusi riippumaton holdout eikä lopullinen gold-aineisto.

## Oikeat Hilma-ilmoitukset (vanhoista jäädytetyistä lähdeotoksista)

| Ilmoitus | Otos | AI-silver-luokka | Lähdenäyttö / puuttuva tieto | Tila |
|---|---|---|---|---|
| 59188 | independent_100 | Relevantti (alustava AI-silver) | Espoon Tietotie 1; lähdeotteessa pintaremontti. Urakkakoko, kelpoisuus, liitteet tarkistamatta | POSITIVE_CANDIDATE_UNVERIFIED |
| 58444 | independent_100 | Mahdollinen | Huoneistoremontit; työmaakunta puuttuu | AMBIGUOUS |
| 59230 | independent_100 | Mahdollinen | Työympäristömuutos; urakan koko epäselvä | AMBIGUOUS |
| 160596 | holdout_52 | Epärelevantti (alustava AI-silver) | Kerrostalon purku-urakka Pieksämäellä | NEGATIVE_CANDIDATE |
| 54620 | holdout_52 | Epärelevantti (alustava AI-silver) | Avantosaunan KVR-uudisrakennus Lapualla | NEGATIVE_CANDIDATE |

Lähdepolut: `data/validation/snapshot_2026-10-19/hilma_raw.json`,
`data/validation/holdout_52_2026-10-19/holdout_raw.json`.
AI-silver-lähteet: kummankin otoksen `ai_silver_labels.csv`.

**59188 ei ole vahvistettu kelpoisuudeltaan eikä sopimusarvoltaan.** Sitä ei saa käyttää
todellisena gold-positiivisena tai toimituksen GO-suosituksena. Vanhan 100
ilmoituksen käyttäminen kehityskontrollina ei tee siitä uutta holdoutia.

## Synteettiset, deterministiset testit

`tests/test_eforms_evidence.py` kattaa yhden soveltuvan saneerausesimerkin
(Espoo, 80 000 EUR, yksittäisen urakan arvo testissä eksplisiittisesti
vahvistettu), yhden aluepoissulun (Lohja), arvon vahvistuksen puuttumisen
sekä XML:n ostajan osoitteen ja työmaan erottelun. Nämä ovat ohjelmistotestejä,
eivät oikeiden ilmoitusten osuvuuden validointia.

## Lähde-XML:n poiminta

`workers/extract_eforms_evidence.py` käsittelee **tallennetun** UBL/eForms-XML:n
`ProcurementProjectLot`-rakenteesta projektin kuvauksen, `RealizedLocation`-
osoitteen kunnan ja mahdollisen `EstimatedOverallContractAmount`-arvion.
Puuttuva tai eri rakenteessa sijaitseva kenttä jää UNKNOWN-tilaan.
Puitejärjestelyn arvoa ei hyväksytä yksittäisen työn todistetuksi arvoksi.
XML:n liitteitä tai kelpoisuusehtoja ei tällä työkalulla tarkisteta.

Seuraava välttämätön vaihe: hankkia erilliset **todelliset, alkuperäisestä
hankintailmoituksesta ja tarvittavista asiakirjoista tarkistetut** positiiviset
ja negatiiviset tapaukset, lukita niiden lähdetiedot ennen malliajoa ja
laskea vasta sitten osuvuus. Vähintään yksi vahvistettu positiivinen tarvitaan,
jotta herkkyyttä voidaan edes alustavasti tarkastella.
