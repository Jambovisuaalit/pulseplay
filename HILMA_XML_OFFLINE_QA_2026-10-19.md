# Urakkaluotsi – eForms-määräaikojen offline-varmennus (19.10.2026)

## Päätös

- **Offline XML-regressiotestit:** hyväksytty testatussa laajuudessa.
- **Todellisten Hilma-ilmoitusten määräajat:** EI VAHVISTETTU.
- **Asiakastoimitusportti:** SULJETTU.

## Todisteet

1. EU Publications Officen eForms SDK:n `cn_24_minimal.xml` sisältää
   `ProcurementProjectLot[LOT-0000]/TenderingProcess/TenderSubmissionDeadlinePeriod`:
   `EndDate=2020-02-04+02:00` ja `EndTime=10:00:00+02:00`.
   Lähde: https://github.com/OP-TED/eForms-SDK/blob/develop/examples/notices/cn_24_minimal.xml
2. Hakemistossa `tests/fixtures/ted_cn24_deadline_excerpt.xml` on rakenteellinen
   osapoiminta tästä virallisesta esimerkistä. Osapoiminta ei ole koko alkuperäinen XML.
3. Testi varmentaa indeksin UTC-arvon `2020-02-04T08:00:00Z`, hylkää yhden
   tunnin virheen eikä käytä tarjousten avausajankohtaa tarjousten määräaikana.
4. Erilliset regressiotestit hylkäävät muun muassa puuttuvat aikavyöhykkeet,
   osallistumishakemuksen määräajan väärän käytön, ristiriitaiset osakohteet ja
   yksittäisen osakohteen puuttuvan tarjousajan.

## Live-varmennuksen valmius (EI KÄYNNISTETÄ)

- Aiemman 19.10. testin ajonumero: https://github.com/Jambovisuaalit/pulseplay/actions/runs/39179129255
- Aiemman kiintiön käyttö: 3/3 API-kutsua, 2 XML-noutoa, 0 varmennettua määräaikaa.
- Alkuperäisiä XML-vastauksia ei tallennettu aiempaan testiraporttiin, joten
  ilmoituksia `59709` ja `59708` ei voi tarkistaa uudelleen offline-tilassa.
- Seuraavan live-testin erillinen hyväksyntä edellyttää: uutta nimenomaista
  kutsubudjettia, tarkkaa kohdelistaa, vastauksen rajattua säilytyssuunnitelmaa
  ja työkalun estoa liite- ja asiakastoimitusoperaatioille.
- Julkaisukelpoisuuden portti aukeaa vasta, kun oikeiden Hilma-ilmoitusten
  XML-lähteisiin verratut määräajat ovat oikein, eikä yhtään vahvistamatonta
  tai ristiriitaista ajankohtaa näytetä varmana.

## Toisto ilman verkkoa

`python -m unittest discover -s workers -p 'test_offline_safety.py' -v`

`node tests/offline-deadline.test.cjs`
