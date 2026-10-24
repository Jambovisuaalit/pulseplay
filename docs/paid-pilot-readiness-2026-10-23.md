# Urakkaluotsi — maksullisen pilotin toimitusvalmius 23.10.2026

## Päätös: NO-GO maksullisen pilotin aloitukselle ja tähän sidotulle 10 yrityksen lähetyserälle

Myyntisivun tekninen julkaisuvalmius ei osoita hankintaseurannan toimitusvalmiutta. Tavoite säilyy: kaksi maksettua 249 € pilottia (498 €). Tässä ajossa ei lähetetty myyntiviestejä, käynnistetty laskutusta tai kirjattu uusia maksuja.

## Toistettu varmennus

Koodi: d1d16aa0dfe4a8185617a1a3edb3d3fae6278fe9, feature/urakkaluotsi-delivery-readiness.
Ajot:
- python3 workers/evaluate_holdout_v2.py
- python3 -m unittest discover -s tests -v — 130/130 PASS
- python3 workers/evaluate_p0_blind_ai_source_review.py --ranked data/validation/p0_frozen_ranked_100_2026-10-19.json --reviews data/validation/p0_blind_ai_silver_reviews_2026-10-19.json --output <scratch-output>
- python3 workers/simulate_ai_silver_delivery.py

Nämä ovat jäädytettyjen 19.10.2026 aineistojen uusintoja. Ne eivät ole uusi ajallisesti riippumaton testijoukko, uusi 30 päivän seuranta tai oikea asiakastoimitus. Uusia Hilma-kutsuja tässä ajossa: 0.

## 52 ilmoituksen erillinen holdout

| Mittari | Tulos |
|---|---:|
| Ilmoituksia | 52 |
| Päällekkäisyys vanhaan 100 joukkoon (ID, menettely, otsikko) | 0 / 0 / 0 |
| Relevantiksi ennustettu | 0 |
| Pois rajauksesta | 31 |
| Puuttuvan tiedon vuoksi lykätty | 21 |
| AI-vertailun havaitsemat FP | 0 |
| AI-vertailun havaitsemat FN | 0 |
| Mahdollinen FN-väli epäselvät mukana | 0–3 |
| Precision | ei määriteltävissä |
| Täydet tarjousasiakirjat tarkistettu | 0 |

Nolla FP:tä ei tarkoita onnistunutta relevanssia: positiivisia ennusteita ei ollut. FN-luku ei ole varmennettu todellinen herkkyys, koska AI-vertailussa ei ollut vahvistettuja positiivisia ja epäselviä kohteita jäi ratkaisematta.

AI-lähdearvion syykoodit koko 52 joukolle: SCOPE 39, AREA 6, MIXED 4, NO_SOURCE 1, UNRESOLVED 2. Nämä ovat aineiston luokitteluperusteluja, eivät 52 mallivirhettä. Vanhassa versiossa kuusi väärää positiivista liittyivät alueeseen, puitesummaan tai todellisen työn sisällön sekoittumiseen. V2 torjuu myönteiset suositukset puuttuvalla näytöllä, mutta ei vielä osoita löytävänsä sopivia urakoita.

## Ennalta määritelty AI-lähdearvion portti

Mittari: AI_SOURCE_REVIEWED_PRECISION_AT_30 (AI-silver, ei ihmisen gold).
Hyväksyntä: kaikki 30 lukittua kohdetta täydellisesti lähdearvioitu ja vähintään 24/30 relevanttia. Jokaiselta: työmaa, työn sisältö, määräaika, yksittäisen urakan arvo, kelpoisuus, alkuperäislähde ja tarkka ote.

Tulos:
- jätettyjä arvioita 30/30
- täydellisesti dokumentoituja arvioita 0/30
- puutteellisia 30/30
- precision@30 = null
- portti NOT_MEASURED

Arvion olemassaolo ei korvaa sen lähteiden täydellisyyttä. Uutta aineistoa arvioitaessa mallin ennusteet eivät saa muodostaa vertailutotuutta eikä tämä jo nähty joukko saa muuttua uudeksi holdoutiksi.

## Historiallisen 100 ilmoituksen toimitussimulaatio

92 NOT_EVALUATED, 7 EXPIRED, 1 CANCELLED, 0 GO.
Täydellisiä liitesarjoja 0; varmennettuja yrityskohtaisia kelpoisuuksia 0.
Tekniset turvaehdot PASS; maksullisen toimituksen hyöty, kriittiset faktavirheet täydellisiä asiakirjoja vasten ja aktiivinen työaika NOT_MEASURED/NOT_TESTED.

Simulaation kello ja lähdehetki ovat historialliset. Lukuja 93 OPEN / 7 EXPIRED ei pidä tulkita 23.10.2026 ajantasaiseksi hankintatilanteeksi.

## Asiakashankinta ja CRM

Urakkaluotsi-haulla ei löytynyt Drive-tiedostoa. Rakennus- ja CRM-hakujen tulokset eivät yksilöineet Urakkaluotsin hyväksyttyä 10 yrityksen kampanjataulukkoa. Repon aiempi pilot-intake-preparation-2026-10-20.md toteaa myös prospektilistan puuttuvan tarkistetuista haaroista.

Muiden liiketoimintojen CRM-taulukoita ei päivitetty eikä niiden kontakteja merkitty Urakkaluotsin varmennetuiksi prospekteiksi.
Postilaatikon lomakehakemusta ei tulkittu maksetuksi pilotiksi tai kohderyhmän hyväksytyksi yritykseksi.

Tämän toimeksiannon uudet tapahtumat:
- lähetettyjä myyntiviestejä 0
- toimitettuja myyntiviestejä 0
- uusia myönteisiä vastauksia / sovittuja keskusteluja / maksuja ei syntynyt tässä ajossa
Koko aiemman myyntihistorian kokonaismääriä ei varmennettu. Tavoite 498 € ei ole toteutunut kassakertymä.

## Portin avaava työ

1. Kerää uusi, nykyhetken alkuperäisaineisto. Varmista erillisyys aiempiin ilmoituksiin, menettelyihin ja otsikoihin; jäädytä aineisto ennen mallin arviointia.
2. Tee sokkoutetut AI-lähdearviot erillään malliennusteista. Kirjaa puuttuva tieto UNKNOWN-tilaan. Tarvitaan arvioitavia positiivisia ja negatiivisia; älä valitse vain onnistuneita nostoja.
3. Raportoi precision, FP, FN, UNKNOWN ja peitto rehellisine nimittäjineen. Noudata lukittua 30 kohteen porttia; älä laske rajaa jälkikäteen.
4. Aja ajantasaisilla, täydellisillä kohteilla toimitussimulaatio. Kriittiset faktavirheet 0, kaikki väitteet jäljitettäviä, määräajat ja hyväksynnän mitätöinti toimivat; mittaa aktiivinen käsittelyaika.
5. Varmenna 10 kohdeyritystä, vastaanottajat, aiemmat kontaktit ja kiellot sekä lähetyspalvelun soveltuvuus. Määritä Urakkaluotsin CRM:n oikea tallennuspaikka ennen tapahtumakirjauksia.
6. Vapauta maksullisen pilotin myyntierä vasta hyväksyttyjen porttien jälkeen. Mittarijono: toimitetut viestit → myönteiset vastaukset → pilottikeskustelut → varmennetut maksetut pilotit. Avaus tai lomakehakemus ei ole maksu.
