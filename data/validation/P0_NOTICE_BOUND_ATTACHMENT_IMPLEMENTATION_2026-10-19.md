# P0.1–P0.2 – GitHub CI ja ilmoitustunnukseen sidottu liitekeräin

Päiväys: 2026-10-19. PR #8: `fix/urakkaluotsi-p0-validation`. Ei mergeä, tuotantojulkaisua eikä asiakastoimituksia.

## P0.1: GitHub Actions

Ennen P0.2-muutoksia viimeisimmän aiemman HEAD-commitin `04e217c27e0d1819b17830c8b0670e0981dbf611` regressioajot:
- https://github.com/Jambovisuaalit/pulseplay/actions/runs/39204009826 – SUCCESS.
- https://github.com/Jambovisuaalit/pulseplay/actions/runs/39204005736 – SUCCESS.

P0.2:n omat commitit käynnistävät automaattiset regressiot. Niiden tulos on tarkistettava viimeisimmän HEAD-SHA:n perusteella; vanhan commitin vihreä ajo ei todista uutta muutosta läpäisseeksi.

## P0.2: toteutettu lähdeketju

`workers/collect_hilma_notice_attachments.py`:
- Lukee tallennetun alkuperäisen eForms-XML:n ilmoitustunnuksen perusteella, enintään 10 tunnusta.
- Löytää **vain XML:n tekstissä tai attribuuteissa eksplisiittisesti olevat** kanoniset `https://cdn.hankintailmoitukset.fi/public-attachments/<uuid>`-URL:t. Ei URL-arvailua, nimen perusteella liittämistä, portaaliin kirjautumista tai allekirjoitettujen URL:ien uudelleenmuodostusta.
- Tallettaa XML:n SHA-256:n, ilmoitustunnuksen, linkin alkuperän ja manifestin.
- Liitetiedoston lataaminen edellyttää **nimenomaan alkuperäisen Hilma-API:n kyseisen ilmoitustunnuksen vastauksen** varmentamista. Paikallista XML-tiedostoa ei voi väittää tämän tarkistuksen perusteella ilmoitustunnukseen sidotuksi ilman alkuperäistä noutotodistetta.
- PDF ja ZIP tunnistetaan sisällön perusteella. Enimmäiskoko 20 MiB/tiedosto; ZIP-tiedostojen enimmäismäärä 100 ja ilmoitettu purkamaton kokonaiskoko 80 MiB. ZIP:n sisältöä ei automaattisesti pureta. Polunylitykset ja salatut ZIP-merkinnät estetään.
- Alkuperäiset tavut, SHA-256 ja noutoaika tallennetaan vain rajattuun GitHub Actions -artefaktiin. **Lataus ei yksin vahvista tarjouspaketin täydellisyyttä, arvoa, tarjoajan kelpoisuutta tai gold-luokkaa.**

`workers/pilot_notice_bound_hilma.py`:
- Enintään **kaksi** Hilman API-kutsua, kiinteät alkuperäiset tunnukset **59188 ja 59375**.
- API-avain vain GitHubin `HILMA_API_KEY`-secretistä.
- Ei asiakasviestintää tai muita ulkoisia toimenpiteitä.

`.github/workflows/urakkaluotsi-notice-attachments-pilot.yml`:
- `workflow_dispatch`-käynnistys **vain käsin**, ei automaattisia API-kutsuja pushin yhteydessä.
- Kahden päivän artefaktisäilytys.
- Tarkistaa, että automaattisia gold-positiivisia ei muodostu ja Precision@30 pysyy null-arvossa.

`tests/test_hilma_notice_attachments.py`:
- Ilmoitustunnus ja XML-linkkiprovenienssi.
- SHA-256-ristiriita, ulkopuoliset/allekirjoitetut linkit, samanniminen mutta linkitön hanke.
- Latauksen rajaus, ZIP-polunylityksen esto ja väärään ilmoitustunnukseen sidotun linkin hylkäys.
- Paikallista XML-tiedostoa ei hyväksytä varmennetuksi alkuperäiseksi API-vastaukseksi.

## Rajaus ja tulkinta

**Tämä toteutus on alkuperäisen ilmoituksen XML:ssä olevien suorien julkisten liiteosoitteiden keräin, ei yleinen Hilman tai Tarjouspalvelun liiterajapinta.** Jos XML sisältää vain portaalilinkin tai liitteet on saatavilla erillisestä palvelusta, linkit jäävät `NOT_DISCOVERED` / `ACCESS_RESTRICTED` -tilaan. Koodia ei saa väittää täydelliseksi tarjousasiakirjakeräimeksi.

Live-Hilma-ajon tulosta ei tämän muutoksen yhteydessä ole vahvistettu. Erillinen käsin käynnistettävä workflow on toteutettu, mutta sen API-kutsujen, latausten ja asiakirjapeiton tuloksia ei saa raportoida ennen todellista Actions-ajon lokia ja artefaktia.

Seuraava hyväksymisportti: viimeisimmän commitin regressioajot PASS, sitten erillinen enintään kahden Hilma-kutsun live-koe. Jos alkuperäinen XML ei sisällä suoria julkisia liitteitä, raportoidaan **0 löydettyä suoraa URL:ia** eikä arvata linkkejä. Ei täydellistä tarjouspakettia, ei riippumatonta goldia, ei Precision@30-tulosta ilman erillistä näyttöä.
