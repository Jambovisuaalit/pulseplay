# Urakkaluotsi – 100 ilmoituksen alustava AI-osuvuusanalyysi

SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS

**Vertailu on AI-silver, ei riippumaton ihmisen gold.** Automaattinen algoritmi
ei kirjoittanut vertailuluokkia. AI-arviointi tehtiin jäädytetyn lähdemetadatan
perusteella sokkona ennen mallin pisteiden avaamista. Arkistosta ei tarkistettu
tarjousliitteitä, eikä todellista yrityskelpoisuutta ole osoitettu.

## Otos ja alustavat luokat

- 100 yksilöityä Hilma-hakutulosta.
- AI:n selvästi relevantiksi merkitsemiä: 1.
- AI:n poissulkemia: 91.
- AI:n ehdollisesti epäselviä: 7.
- Lähdesisällön puuttuessa arvioimatta: 1.

## Virheanalyysi (alustava AI-vertailu)

- Mallin positiiviset nostot: 15.
- Positiivinen ja AI:n perusteella relevantti: 1.
- Väärä positiivinen AI-arvion perusteella: 10.
- Väärä negatiivinen AI-arvion perusteella: 0.
- Oikea negatiivinen AI-arvion perusteella: 81.
- Epäselviä tai arvioimattomia otoksen rivejä: 8.
- AI-pohjainen precision arvioitavissa oleville positiivisille: 0.0909.
- Koko 100 rivin AI-pohjainen precision-raja: 0.0667–0.3333.
- FP:n AI-pohjainen vaihteluväli: [10, 14].
- FN:n AI-pohjainen vaihteluväli: [0, 4].
- Top-30 AI-pohjainen precision-väli: 0.0333–0.2.

## Päätös

**Virallinen 80 % precision -portti: NOT MEASURED.** AI-silver luokat eivät ole
riippumaton hyväksytty totuus. Tiedot ovat käyttökelpoisia algoritmin virheiden
diagnosointiin ja seuraavan sisäisen simulaation priorisointiin, eivät kaupalliseen
lupaukseen tai vahvistettuun asiakasnostoon. Ehdollisia rivejä ei poistettu
nimittäjistä: mahdolliset vaikutukset näkyvät vaihteluväleissä.

Lukitut lähteet: `ai_silver_manifest.json`, `ai_silver_labels.csv`,
`predictions.csv`; kohdekohtaiset vertailut: `ai_silver_error_analysis.csv`.
