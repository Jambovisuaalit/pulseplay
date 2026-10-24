# P0 – alkuperäisten Hilma eForms-XML-ilmoitusten rajattu lähdevertailu

Päivä: 2026-10-19. Koodirevisio: `d5aa1cde4207f200d2678bc4d6ad39decc39f864` (testiajo). GitHub Actions: https://github.com/Jambovisuaalit/pulseplay/actions/runs/39191945598

## Keruu ja provenienssi

- 6 alkuperäisen ilmoituksen GET-kutsua `/avp-eforms/external-read/v1/notice/{noticeId}`, 5 HTTP 200 ja 1 HTTP 404.
- 5 XML-tiedostoa jäsennettiin; jokaisessa yksi `ProcurementProjectLot`.
- XML:t ja `source_comparison.json` tallennettu GitHub Actions -artefaktiin **12160491797**: https://github.com/Jambovisuaalit/pulseplay/actions/runs/39191945598/artifacts/12160491797 (säilytys 7 vrk).
- Ei tarjousliitteitä, sähköposteja, asiakastoimituksia tai tuotantojulkaisua.
- Otos on tarkoituksella valittu vanhoista hakumetadataotoksista, **ei riippumaton satunnaisotos** eikä uusi ajallinen holdout.
- XML-lähde osoittaa rakenteisia kenttiä; se ei vahvista yrityksen kelpoisuutta, tarjouksen toteutettavuutta tai yksittäisen urakan sopimusarvoa.

## Havaitut luokittelumuutokset

| Hilma | Hakumetadata | Alkuperäinen XML | XML-näyttö | Alustava lähdeperustainen tulkinta |
|---|---|---|---|---|
| 59188 | Mahdollinen | Mahdollinen | Lotin työmaakunta Espoo; saneeraussisältö; arvo tuntematon | POSITIVE_CANDIDATE_UNVERIFIED |
| 59230 | Ei priorisoitu | Ei priorisoitu | Lotin työmaakunta Helsinki; työn pääsisältö ei vahvistunut luokittelijalle | UNKNOWN_SCOPE |
| 59375 | Ei priorisoitu | Mahdollinen | Lotin työmaakunta Espoo; korjaustyö vastaa pintasaneerauksen vihjeitä; arvo tuntematon | POSITIVE_CANDIDATE_UNVERIFIED |
| 58444 | Ei priorisoitu | Ei priorisoitu | Lotista ei vahvistu työmaakuntaa eikä sopivaa pääsisältöä | UNKNOWN_SITE_AND_SCOPE |
| 54620 | Ei priorisoitu | Epärelevantti | Lotin sisältö luokiteltu poissuljettavaksi INFRA-säännöllä; sijainti tuntematon | NEGATIVE_CANDIDATE_REVIEW_SCOPE_RULE |
| 160596 | Epärelevantti | Ei arvioitu | HTTP 404, alkuperäistä XML:ää ei saatavilla | MISSING_SOURCE |

Lähdevertailun 5 käsitellystä ilmoituksesta 2 on **Mahdollinen**, 2 **Ei priorisoitu**, 1 **Epärelevantti**, 0 **Relevantti**. Kaksi ilmoitusta vaihtoi luokkaa `Ei priorisoitu -> Mahdollinen` ja `Ei priorisoitu -> Epärelevantti`. Kolme pysyi ennallaan. Kuudes jäi XML:n osalta arvioimatta.

## Alustava tekoälyavusteinen lähdetulkinta

Tämä tulkinta perustuu vain yllä kuvattuun XML-poiminnan näyttöön ja aiemmin jäädytettyihin hakumetadataotteisiin. Se **ei** ole XML:n täyden tekstin riippumaton sokkoarvio eikä gold-label. Erityisesti 54620:n `INFRA`-poissulku on tarkistettava, sillä lähdeotsikko viittaa uudisrakennukseen; väärä perustelukoodi voi peittää luokittelusäännön virheen.

- Vahvistettuja relevantteja: **0**.
- Lähteestä vahvistettuja kelpoisia yksittäisen urakan arvoja: **0**.
- Lähde-XML:n perusteella mahdollisia positiivisia jatkotarkistukseen: **2** (59188, 59375).
- Puuttuva alkuperäinen XML: **1**.
- Virallinen Precision@30, recall ja FP/FN: **NOT MEASURED**.

## Jatkotoimenpiteet

1. Tarkista 59188 ja 59375:n urakkakohtainen arvo, rajattu työn sisältö ja kelpoisuusehdot alkuperäisistä hankinta-asiakirjoista. Ilman tätä ei ole vahvistettuja positiivisia.
2. Lisää `54620`-tapaukselle päätyön poissulkusääntöjen testit, jotta virheellinen `INFRA`-syy ei jää piiloon.
3. Etsi ja lukitse uusi ajallisesti erillinen otos; tee AI-arvio lähdeotteista ennen malliennusteiden avaamista. Raportoi erikseen puuttuvat lähteet.
4. Älä yhdistä PR:ää tai lähetä asiakastoimituksia ennen kelpoisuus- ja osuvuushyväksyntää.
