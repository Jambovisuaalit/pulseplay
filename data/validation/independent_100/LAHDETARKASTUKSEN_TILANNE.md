# Urakkaluotsi – 100 ilmoituksen riippumattoman tarkastuksen tilanne

SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS

Aineisto: 100 jäädytettyä Hilma-hakutulosta, haettu 2026-10-19T00:12:27.163249+00:00.
Lähteen SHA-256: `99f386d49a7996594ee3f4d856c707bea209e51742cec32e707e6c3bbf9ca074`. **Hakumetadata ei sisällä tarjousliitteitä.**

## Valmiit tarkastukset

- 100/100 uniikkia ilmoitustunnistetta. Määräaika 100/100, julkaisuaika 100/100.
- Kuvaus 99/100; arvioitu arvo 35/100.
- Omaa työmaakohteen sijaintikenttää 0/100, kysymysten määräaikakenttää 0/100.
- Mahdolliset samannimiset / keskeytyksellä merkityt ilmoitukset: 58430/59464, 59352/59399.
- Otsikossa keskeytetyksi ilmoitetut: 59352.
- `source_evidence_queue.csv` sisältää kaikki 100 ilmoitusta sekä lähdetekstin sanatarkat
  poiminnat **ilman automaattisen ennusteen sarakkeita ja ilman lopullisia luokkia**.

## Hyväksynnän estävä vaihe

**Riippumaton lähdetarkistus: 0/100.** Tämä agentti voi poimia näyttövihjeet, mutta se
ei ole riippumaton tuomari oman koodinsa luokittelulle. Tarkastaja tarvitsee vähintään
alkuperäisen ilmoituksen ja hankinnan alue-/kokotiedot. Ratkaisevat liitteet ja
yrityksen referenssit/pätevyydet puuttuvat. Vasta todellisen, sokkoutetun tarkastajan
perustelemat ja allekirjoittamat luokat syötetään `gold_labels.csv`-tiedostoon.

**Precision, FP ja FN: NOT MEASURED. Arvioimatta 100/100.** Tekninen CI-testi ei
korvaa riippumatonta arviointia. Uusi *arviointiin perustuva* toimitussimulaatio
ja kaupallinen hyväksyntä ovat odotustilassa, kunnes tämä portti täyttyy.
