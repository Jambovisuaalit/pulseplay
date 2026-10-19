# P0.3b – eForms-asiakirjaviitteet (19.10.2026)

Toteutus: `workers/extract_eforms_document_links.py`.

**Tavoite:** tarkastaa alkuperäisen Hilma-eForms-XML:n tarjousasiakirjaviitteet säilyttäen ilmoitustunnuksen, lähde-XML:n SHA-256:n ja elementtipolun. Tulos on lähdevihje, ei todettu julkinen tiedosto tai hyväksytty hankinta.

Luokat:
- `DIRECT_PUBLIC_DOCUMENT`: vain suora HTTPS-osoite Hilman sallittuun `/public-attachments/<uuid>`-polkuun. Tämä on **osoitemuodon tunnistus**, ei onnistunut lataus.
- `PUBLIC_PORTAL`: tarjousportaalin HTTPS-osoite, esimerkiksi Tarjouspalvelu tai Hilma. Se ei todista liitteiden julkista tai esteetöntä latausta.
- `ACCESS_RESTRICTED_OR_UNKNOWN`: muu yhteys, tuntematon tai estetty pääsy. Ei yrittämistä tunnistautumisen ohi.

Linkkejä tarkastellaan vain eForms-tarjousasiakirjoihin, niiden viitteisiin tai tarjousmenettelyyn liittyvissä XML-solmuissa; tilaajaorganisaation verkkosivua ei tulkita tarjousasiakirjaksi. Polut tallennetaan lähteen XML-rakenteesta muodossa `/Notice[1]/.../URI[1]/text`.

Liitetty `workers/pilot_notice_bound_hilma.py`-raportin `document_link_evidence`-kenttään. Käynnistysehdot ovat edelleen rajatut; **P0.3b-koodimuutos ei käynnistä uusia Hilma-live-kutsuja**. Todellisia 59188/59375 linkkiluokkien lukumääriä ei ole mitattu uudella poimijalla ennen uutta erikseen rajattua ajoa tai saatavilla olevia talletettuja alkuperäis-XML:iä.

Turvaportit: `package_complete=false`, `gold_label=UNREVIEWED`, `precision_at_30=null`, `access_verified=false`. Julkiset portaalilinkit eivät automaattisesti muutu ladattaviksi ZIP/PDF-osoitteiksi.

Testit: `tests/test_eforms_document_links.py` (asiakirjalähteen viite, portaali, organisaation URL:n poisrajaus, epävarma pääsy, tyhjä osumalista).

Seuraavaksi: varmista CI, vertaa poiminnan elementtipolkuja erikseen lähteestä talletettuun autenttiseen XML:ään ja lisää tarvittavat eForms-skeeman kentät näyttöön perustuen. Älä raportoi Precision@30:a ennen riippumatonta arviointia.
