# Urakkaluotsi – uusi sisäinen toimitussimulaatio

SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS

Testiyritys: Uudenmaan Korjausrakentajat Oy, kuvitteellinen. Aikaleima:
2026-10-19T00:12:27.163249+00:00 (UTC). Tämä ei ole 30 päivän toteutunut seuranta.

## Tulos

- Aidot, uniikit hakumetadatan ilmoitukset: **100**.
- Avoin määräaika snapshot-hetkellä: **93**.
- Päättynyt määräaika snapshot-hetkellä: **7**.
- Automaattisen saneerauspainotuksen alustavat osumat: **15**.
- Automaattisesti ehdolliset osumat: **19**.
- **Vahvistettuja asiakasnostoja: 0**.
- Riippumattomia arviointiluokkia: **0/100**; precision, FP ja FN: **NOT MEASURED**.

Kaikkien 100 rivin tunniste ja alkuperäistä hakutietoa vastaava viite ovat
`classified_notices.csv`-taulukossa. Automatiikan luokat eivät ole vertailutotuus.

## Estävät avoimet asiat

1. Täyttä tarjousasiakirja- ja liiteaineistoa ei ole haettu eikä tarkistettu.
2. Kuvitteellisen yrityksen referenssejä, taloutta, pätevyyksiä eikä kapasiteettia ole vahvistettu.
3. 100 riippumatonta lähdetarkistukseen perustuvaa luokittelua puuttuu.
4. Ilmoituksen hakumetadata ei yksin osoita hankkeen toteutusaluetta, kokoa,
   kelpoisuutta, kysymysten määräaikaa tai mahdollisia keskeytyksiä.

## QA ja hyväksyntä

- Päättyneiden ilmoitusten positiivisen noston esto: **PASS**.
- Tarkistamattomien liitteiden positiivisen noston esto: **PASS**.
- Ilmoitustunnisteiden jäljitettävyys: **PASS**.
- Riippumaton relevanssimittaus: **NOT TESTED**.
- Oikean asiakkaan toimituskelpoisuus: **NOT TESTED**.

**CONDITIONAL PASS vain tekniselle turvaportille.** Ensimmäisen maksavan asiakkaan
toimitusvalmius **EI HYVÄKSYTTY** ennen 100 riippumatonta luokkaa,
tarjousliitteiden tarkistuksia ja yritystietojen vahvistusta. Sähköpostia ei lähetetty.
