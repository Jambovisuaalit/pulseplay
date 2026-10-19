# P0.3b – alkuperäisten eForms-tarjousasiakirjaviitteiden live-varmennus (2026-10-19)

## Rajaus ja ajot

Kaksi kiinteää Hilma-ilmoitusta **59188 ja 59375**, ei uusia muita ilmoituksia. Julkisen rajapinnan alkuperäinen eForms-XML haettu GitHub Actionsissa; avain GitHub-secretistä. Ajo:
- https://github.com/Jambovisuaalit/pulseplay/actions/runs/39212967648 – SUCCESS: 2 API-kutsua, 2 jäsennettyä XML:ää, 2 tarjousasiakirjojen osoitevihjettä, yhteensä 10 XML-URL-kenttää, 0 suoraa liitelinkkiä ja latausta.
- https://github.com/Jambovisuaalit/pulseplay/actions/runs/39213090438 – SUCCESS: sama rajaus, lisäksi lähdepolkujen ja URL-hostien anonymisoitu loki.

## Vahvistetut asiakirjapääsyviitteet

| Notice | Lähdekenttä | Alkuperäisessä XML:ssä esiintyvä osoite | Tulkinta |
|---|---|---|---|
| 59188 | `/ContractNotice[1]/ProcurementProjectLot[1]/TenderingTerms[1]/CallForTendersDocumentReference[1]/Attachment[1]/ExternalReference[1]/URI[1]/text` | `https://tarjouspalvelu.fi/aalto` | `PUBLIC_PORTAL` |
| 59375 | Sama elementtipolku | `https://tarjouspalvelu.fi/espoo` | `PUBLIC_PORTAL` |

Molempien XML:ssä toinen tarjousmenettelyä koskeva URL sijaitsee polussa:
`/ContractNotice[1]/ProcurementProjectLot[1]/TenderingTerms[1]/TenderRecipientParty[1]/EndpointID[1]/text`.
Tämä on **tarjouksen vastaanottokanavan pääteosoite**, ei tarjousasiakirjan liite eikä laskettava toinen tarjousasiakirjaviite. Sen tunnistus lisättiin omaksi `submission_endpoints`-kentäkseen.

Muut kuusi URL-kenttää olivat `EformsExtension/Organizations/Organization/Company/WebsiteURI`-solmuissa: ostajan, yhteysorganisaation ja muiden toimijoiden verkkosivuja. Näitä **ei** saa tulkita tarjousasiakirjojen pääsyosoitteiksi.

## Toteutettu tekninen korjaus

- `workers/extract_eforms_document_links.py` poimii ja luokittelee tarjousasiakirjojen `CallForTendersDocumentReference/Attachment/ExternalReference/URI`-linkit sekä erottaa `TenderRecipientParty/EndpointID`-osoitteet omaksi listakseen.
- Sama moduuli tuottaa tarkistuslokin kaikista XML:n URL-kentistä ilman kyselyparametreja tai URL-salaisuuksia (`audit_url_fields`).
- `workers/pilot_notice_bound_hilma.py` tallentaa dokumenttiviitteet ja rakennetarkistuksen tulokset Actions-artefaktiin.
- `tests/test_eforms_document_links.py` sisältää samanlaista alkuperäistä elementtihierarkiaa vastaavan regressiotestin.

## Lopputulos

**P0.3b:n lähderakenne on näille kahdelle ilmoitukselle varmennettu.**
Tarjousasiakirjojen pääsyosoitteita **2**, molemmat `PUBLIC_PORTAL`; suoria julkisia PDF/ZIP-osoitteita **0**; ladattuja liitteitä **0**; täydellisiä paketteja **0**; riippumattomia positiivisia **0**; Precision@30 **null**.

Portaalin yleinen pääsyosoite `/aalto` tai `/espoo` ei yksilöi yksittäisen hankinnan liitepakettia. Seuraava vaihe P0.3c on selvittää sallittu, julkinen hankintakohtainen asiakirjalista Tarjouspalvelusta tai muusta lähdeportaaliin osoittavasta dokumentoidusta menettelystä. Ei URL-arvailua, kirjautumisen kiertämistä eikä asiakkaalle kelpoisuus-GO:ta.

PR pysyy luonnoksena, ei mergeä, tuotantojulkaisua tai asiakastoimituksia.
