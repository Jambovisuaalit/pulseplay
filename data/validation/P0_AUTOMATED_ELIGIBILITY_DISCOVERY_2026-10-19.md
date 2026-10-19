# P0 – automaattinen kelpoisuusasiakirjojen selvitys 19.10.2026

## Menetelmä

1. Julkiset Tarjouspalvelu-sivut tarkistettiin ilmoituksille **631619 / Hilma 59188** ja **611165 / Hilma 59375**.
2. Julkinen Mercell-asiakirjaluettelo tarkistettiin Kastevuoren hankinnalle.
3. Alkuperäiset eForms-XML:t haettiin GitHub Actionsin rajatulla kuuden kutsun testillä, joka käytti olemassa olevaa `HILMA_API_KEY`-salaisuutta. Ajo: https://github.com/Jambovisuaalit/pulseplay/actions/runs/39192557454
4. Uusi `workers/extract_eforms_requirements.py` etsi XML:n suoraan luettavista tekstikentistä referenssi-, liikevaihto-, vakuus-, vakuutus-, soveltuvuus- ja arvoevidenssiä. Ei tarjousliitteiden latausta eikä kirjautumista.

## Tulos

| Kenttä | 59188 / Tietotie | 59375 / Kastevuori |
|---|---|---|
| Alkuperäinen eForms XML | HTTP 200, jäsennys onnistui | HTTP 200, jäsennys onnistui |
| Työmaa ja korjaussisältö | Lähteestä osoitettavissa | Lähteestä osoitettavissa |
| Referenssien tarkka vähimmäismäärä ja kriteerit | UNKNOWN | UNKNOWN |
| Liikevaihdon vähimmäisraja | UNKNOWN | UNKNOWN |
| Urakkavakuus tai vakuusprosentti | UNKNOWN | UNKNOWN |
| Vakuutusvaatimukset | UNKNOWN | UNKNOWN |
| Yksittäisen urakan arvo 10–250k € | UNKNOWN | UNKNOWN |
| Pakollinen kohdekäynti | Ei vahvistettua tietoa | REQUIRED, osallistuminen UNKNOWN |
| Gold-positive | EI | EI |
| Gold-negative | EI | EI |

Kummankaan alkuperäisen XML:n valituissa vaatimustekstikentissä ei havaittu luotettavia suoria avainsanamainintoja näistä kuudesta luokasta. Tämä **ei tarkoita, ettei vaatimuksia ole**: vaatimukset voivat olla erillisissä asiakirjoissa tai muissa XML-kentissä. Ei lasketa nollaa vaatimukseksi.

Kastevuoren julkisessa Mercell-luettelossa on `Liite 1 REFERENSSIT`, `Liite 2 REFERENSSIT`, alihankkijalomake sekä `TarjouspyyntoRaportti611165.pdf`. Luettelossa tiedostot edellyttävät *Show interest* -toimintoa, ja Tarjouspalvelu kertoo kaikkien tietojen näyttämisen edellyttävän rekisteröitymistä ja kirjautumista. Pelkkiä nimiä ei käytetä kelpoisuustodisteina.

## Käytetyt lähteet

- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=631619
- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=611165
- https://www.mercell.com/de-de/tender/291434616/kastevuoren-paivakodin-elinkaarta-jatkavat-korjaustyot-tender.aspx
- GitHub Actions alkuperäiset XML:t ja koneellinen raportti: https://github.com/Jambovisuaalit/pulseplay/actions/runs/39192557454

## Päätös

**STOP_GOLD_VALIDATION.** Vahvistettuja positiivisia tapauksia 0/2. Näiden kahden hankinnan osalta ei ole mahdollista todistaa koko tarjouskelpoisuutta tai yksittäisen urakan arvorajausta ilman asiakirjoja, joihin julkinen nimetön käyttö ei antanut pääsyä.

**Ei saa** päätellä, että puuttuva referenssi-/vakuus-/liikevaihtomaininta tarkoittaa nollavaatimusta. Ei asiakastoimitusta eikä tuotantojulkaisua. Seuraava itsenäisesti tehtävä työ on etsiä julkisesti kokonaisuudessaan saatavia tarjouspyyntöjä positiiviseen gold-arviointiin sen sijaan, että näille kahdelle keksitään kelpoisuustiedot.
