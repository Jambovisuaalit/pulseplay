# P0.3 – lähdekeruun ja arvioinnin jatkosuunnitelma, 19.10.2026

## Varmennettu lähtötila
- PR #8 on luonnos. Viimeisen live-testin 39211257253: 2 API-kutsua, 2 jäsennettyä XML-ilmoitusta, 0 suoraa julkista PDF/ZIP-linkkiä, 0 latausta ja 0 täydellistä tarjouspakettia. Precision@30 ei ole mitattu.
- Hilman virallinen [AVP-Read-dokumentaatio](https://github.com/Hankintailmoitukset/hilma-api/blob/master/endpoints/avpendpoints.md) kertoo, että ilmoitushaku palauttaa indeksoituja metatietoja eikä koko ilmoitusta; täydet eForms-ilmoitukset noudetaan erikseen. Rajapinnan lukutoiminnoilla on käyttörajoja.
- Hankintamenettelyssä tarjousasiakirjat voivat olla Hilmassa tai erillisessä sähköisessä kilpailutusjärjestelmässä. Tästä ei seuraa, että erillinen avoin liiterajapinta olisi yleisesti käytettävissä.

## Tehtävät

1. **P0.3a (toteutettu)**: pakastetun 100 ilmoituksen läpinäkyvä seulontajono. `workers/build_p0_uusimaa_discovery_queue.py` käsittelee koko tallennetun otoksen ilman valikoivaa poistamista, järjestää alustavat tarkistusvihjeet ja säilyttää alkuperäisen ilmoitustunnuksen. Kaupungin nimen esiintyminen tekstissä **ei ole todiste työkohteen sijainnista**. Metatiedoissa ilmoitettu arvo **ei ole varmistettu yksittäinen urakkahinta**. Gold jää `UNREVIEWED`, Precision@30 = null.
2. **P0.3b (seuraava)**: eForms-ilmoitusten alkuperäiset `NoticeResult`/UBL-XML:n viitteet tarjousasiakirjojen verkko-osoitteisiin, markkina-alustoihin ja tarjouspyynnön asiakirjaosoitteeseen tulee poimia **erillisinä kenttinä**, säilyttäen elementin XPath ja lähteen SHA-256. Luokittele `DIRECT_PUBLIC_DOCUMENT`, `PUBLIC_PORTAL`, `ACCESS_RESTRICTED_OR_UNKNOWN` ilman URL-arvailua.
3. **P0.3c**: poimi tarjousasiakirjoja todistettavasti tarjolla olevista lähteistä vain jos pääsy ja käyttöehdot sallivat sen; erillinen portaali ei ole sama asia kuin Hilman AVP-liiterajapinta. Osoita asiakirjan ilmoitus-/menettelytunnus, versio, liiteluettelo ja tavujen SHA-256.
4. **P0.3d**: laajenna 30–50 todellisen vuoden 2026 Uudenmaan **työkohteen** otokseen. Älä väitä pakastetun 100 ilmoituksen sisältävän tätä määrää ilman lähdenäyttöä. Rakennetaan tarvittaessa erillinen satunnaistettu ennaltamääritelty otanta; dokumentoidaan hakupäivä, kaikki osumat, puutteet ja hakurajat.
5. **P0.4–P0.5**: tarkistuta erikseen alue, saneerauslaajuus, arvo, tarjousajan voimassaolo ja kelpoisuus. Vasta lukittu riippumaton 30 kappaleen ranked holdout saa Precision@30:n ja 80 % rajan mittauksen.

## Stop-gates
- Ei automaattisia lisää Hilma-API-kutsuja, ellei seuraavaa live-ajoa rajata erikseen.
- Ei liitteiden latausta portaalin kirjautumisen tai käyttörajoitusten ohittaen.
- Ei `GO`-päätöstä vain metatiedoista.
- Ei PR-mergeä, tuotantojulkaisua tai asiakastoimituksia.
