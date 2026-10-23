# P0.3d – Deduplikoitu, määräajan perusteella avoin tarkistusjono

Tarkistushetki: **19.10.2026 10:35 Europe/Helsinki**. Lähtöaineisto: 30 todellista Hilman ilmoitustunnusta, joiden ilmoituskuvauksen lähdekatselmointi on tallennettu tiedostoon `p0_3d_30_metadata_review_2026-10-19.json`. Tulostiedosto `p0_3d_dedup_active_review_queue_2026-10-19.json`, generoija `workers/build_p0_3d_dedup_active_queue.py`.

## Tulos
- Lähtöaineisto **30**; saman ilmoitustunnuksen tuplia **0**.
- **9 alustavasti voimassa olevaa tarkistuskohdetta** (7 rakennuksen korjaushankinnan tarkistusvihjettä ja 2 erityisalan hankintaa).
- **9** päättynyttä tarjousaikaa tallennetun määräajan mukaan, **1** otsikon perusteella keskeytetty ilmoitus, **1** Lempäälän Uudenmaan ulkopuolinen ilmoitus, **10** tämän saneeraus-ICP:n ulkopuolista työlajia.
- 9 tarkistusjonon ID:t: `57882`, `59022`, `59139`, `59188`, `59230`, `59375`, `59399`, `59417`, `59464`.
- Aiemmat samaan hankintaan viittaavat `59352` ja `58430` eivät esiinny aktiivisissa tarkistuskohteissa. Myöhemmät `59399` ja `59464` ovat ehdollisia. Virallista keskinäistä korvaus- tai versioviitettä ei ole vahvistettu.
- Kaikissa riveissä säilytetään lähdekuvauksen sanatarkka ote, ilmoitus-ID, lähdekohtainen alue-/sisältöarvio, määräaika, mahdollinen versionippu sekä perusteltu poissulku.

## Varmennuksen rajat

**Kyseessä on tallennetun aidon Hilma-ilmoituskuvauksen lähteeseen sidottu tarkistus, EI täydellisistä tarjousasiakirjoista varmennettu sopivuus.** Sijaintinäyttö tarkoittaa sitä, että alkuperäisessä tallennetussa ilmoituskuvauksessa on yksilöivä maininta kohteesta; alkuperäisen täyden eForms/XML:n eräkohtainen sijainti ja liitteet ovat avoimia. Siten nolla kohdetta on vielä todettu kokonaan tarjouskelpoiseksi.

Tarkistusjonon `REVIEW_*` ei tarkoita asiakkaalle suosittelemista tai aktiivisen kilpailun live-varmennusta. Julkaistua määräaikaa on verrattu tarkistushetkeen, mutta myöhempi keskeytys, korjaus tai uusi määräaika voi muuttaa tilan. Yksittäisen urakan arvoa, erityisehtoja ja kelpoisuutta ei ole vahvistettu. Etenkin kohteet 59139 (turvaluokiteltu), 59375 (pakollinen tutustumiskäynti), 59399 (tutustumiskäynti), 59022 (laaja peruskorjaus) ja 59464 (yhdeksän kohdetta) tarvitsevat rajatun jatkotarkistuksen. Erityisalan kohteet 59417 (hissi) ja 59464 (lämpötekniset työt) eivät muutu yleissaneerausyrityksen sopiviksi ilman erikoispätevyyttä.

Seuraava vaihe: varmista 9 kandidaatin alkuperäisestä eFormsista viimeisin versio, eräkohtainen työkohteen sijainti ja mahdollinen arvon lähde; yhdistä tähän julkisen portaalin näkyvä tarjousaikatieto. Jos hankintailmoitusviitteitä ei voida varmentaa, tila pysyy ehdollisena. P0.4:n riippumaton vertailu on erillinen vaihe.

Ei automaattista goldia (`precision_at_30=null`), ei tuotantojulkaisua, asiakastoimituksia tai PR-mergeä.
