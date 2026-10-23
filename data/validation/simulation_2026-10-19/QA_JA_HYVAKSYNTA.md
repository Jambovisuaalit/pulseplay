# Urakkaluotsi – kriittisten korjausten QA ja hyväksyntä

**SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS**

Tarkistusajankohta: 19.10.2026. Korjaushaara: `fix/urakkaluotsi-p0-validation`.
Ei tuotantojulkaisua, sähköpostin lähetystä eikä uutta Hilma-API-kutsua.

## Automaattinen regressiotestaus

| Tarkistus | Tulos | Näyttö |
| --- | --- | --- |
| Määräajat: ohitetut, aikavyöhykkeelliset, vain päivämäärä sekä virheelliset | **PASS** | Python + Node testit, sekä 8 historiallisen ilmoituksen integraatio |
| Kelpoisuusehto: lähde-evidenssi ja erillinen yrityksen vahvistus vaaditaan | **PASS** | Molempien toteutusten regressiotestit |
| Tarjousliitteet: oletus tuntematon, COMPLETE tarvitsee auditoinnin | **PASS** | Python + Node testit |
| Saneerauspainotteinen pisteytys ja rakennus-CPV-siemenet | **PASS** | Pythonin pisteytys- ja AST-testit |
| Precision, FP, FN sekä puuttuvan vertailuluokan fail-closed-portti | **PASS** | Synteettinen testi: TP 24, FP 6, FN 10, precision 0.80; ei oikea KPI |
| 100 autenttista lähdetunnistetta ilman duplikaatteja | **PASS** | 100/100 yksilöllistä ID:tä, 100/100 määräaikakenttää |
| Python-regressiotestit | **PASS** | 14/14 paikallisesti |
| TypeScript/Node-regressiotestit | **PASS** | 5/5 paikallisesti |
| TypeScript-tyyppitarkistus | **PASS** | `npm run typecheck` |
| Next.js-tuotantobuild | **PASS** | `npm run build`, ei deployta |
| PDF:n ulkoasu | **PASS** | 2 A4-sivua, PNG-renderöinti tarkistettu, Urakkaluotsi-värit ja merkintä |
| XLSX:n eheys | **PASS** | 3 välilehteä; sokkotiedot 101 riviä (otsikko + 100), vertailuluokat 101 riviä |
| GitHub CI korjaushaaralle | **NOT TESTED** | Workflow on lisätty, mutta haaraa ei ole julkaistu |

## Todellisen 100 ilmoituksen arvioinnin tilanne

| Mittari | Mittaus |
| --- | --- |
| Alkuperäisiä hakutulosilmoituksia | 100 |
| Sokkoutetun vertailun näyttöä / ihmisen luokituksia | **0/100** |
| Arvioimatta jääneet | **100** |
| Automaattisesti alustavasti relevantit | 15 (ei vertailutotuus) |
| Automaattisesti ehdolliset | 19 (ei vertailutotuus) |
| Precision | **NOT MEASURED** |
| Väärät positiiviset | **NOT MEASURED** (mahdollinen väli 0–15) |
| Väärät negatiiviset | **NOT MEASURED** (mahdollinen väli 0–85) |
| Top-30-precision | **NOT MEASURED** (0/30 riippumatonta luokkaa) |
| Virhetyyppien jakauma | **NOT MEASURED** |

Yllä mainitut 80 prosentin raja-arvon synteettiset regressionumeroarvot ovat vain
laskennan yksikkötestejä. Niitä **ei** saa esittää toteutuneena relevanssina.

Alkuperäisessä GitHub Actions -arkistossa on myös vanha
`hilma_100_luokiteltavaksi.csv`, jonka CPV-kentät voivat olla merkkitasolle
pilkottuja. Sitä säilytetään keruun alkuperäisenä jälkenä, mutta riippumattoman
arvioinnin syötteenä käytetään tästä syystä vain alkuperäistä JSONia ja siitä
regeneroitua `blind_review.csv`-aineistoa.

## Uusi offline-toimitussimulaatio

100/100 jäädytettyä riviä käsitelty; lähteestä oli 93 avointa ja seitsemän
päättynyttä määräaikaa snapshot-hetkellä. Kaikkien tarjousliitteiden tarkistus
ja kuvitteellisen yrityksen kelpoisuus ovat vahvistamatta. Turvaportti tuotti
**0 vahvistettua jatkonostoa**, 93 soveltuvuudeltaan arvioimatonta (määräaika
auki) ja seitsemän päättynyttä.

Tämä on tarkoituksellinen fail-closed-toimitustulos, ei todistus siitä, ettei
markkinassa olisi asiakkaalle sopivia avoimia urakoita. Määriä ei saa yleistää
255 ilmoituksen aiemmin raportoidun aineiston kattavuudeksi.

## Korjauslista

| Prioriteetti | Jäljellä oleva työ |
| --- | --- |
| **P0** | Riippumaton arvioija(t) tarkistaa 100 alkuperäistä ilmoitusta ja täyttää todelliset, auditoitavat gold-luokat. |
| **P0** | Tarkista alustavien kohteiden tarjousasiakirjat, liitteet, voimassaolo sekä asiakkaan referenssi-/kelpoisuustiedot ennen asiakasnostoa. |
| **P1** | Varmenna rakennus-CPV-hakukattavuus tulevassa erikseen hyväksytyssä API-ajossa; tämän snapshotin yksi hakukutsu ei osoita recallia. |
| **P1** | Aja riippumattomalla aineistolla precision/FP/FN/top-30 ja virhetyyppianalyysi; todista vähintään 80 % ennen kaupallista hyväksyntää. |
| **P2** | Aja uusi toimituksen ajoaikamittaus aidossa toistuvassa prosessissa ja tee käyttäjäpalaute. |

## Hyväksyntäpäätös

**CONDITIONAL PASS – tekninen fail-closed-toimitus onnistui. Ensimmäisen
maksavan pilottiasiakkaan toimitusvalmiutta EI HYVÄKSYTÄ.** Riippumaton
relevanssimittaus ja lähdedokumenttien täydellisyys puuttuvat. Ennen näiden
vahvistamista vahvaa PASS-päätöstä ei voi tehdä.
