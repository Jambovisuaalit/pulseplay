# P0 – julkisten PDF-asiakirjojen toinen keruukierros (19.10.2026)

## GitHub Actions -tulos

Ajossa https://github.com/Jambovisuaalit/pulseplay/actions/runs/39193366462 käytettiin kolmeen ennalta valittuun julkiseen PDF-osoitteeseen rajattua manifestia.

| Lähde | Tulos | Sivut | Tavua | SHA-256 |
|---|---|---:|---:|---|
| Äänekoski 602658, kaupungin tarjouspyyntö | FETCH_OR_PARSE_FAILED / URLError | – | – | – |
| Liperi 555505, korjaustöiden julkinen vertailutaulukko | VERIFIED_FULL_TEXT | 16 | 538144 | `de4d356ef325c9d644a4b7e03ef5b98e5be5a47189a82c22c1f050c3b64dde93` |
| Liperi 588687, pumppaamojen huolto- ja korjaustöiden vertailutaulukko | VERIFIED_FULL_TEXT | 15 | 667426 | `6e9fdd0e54791bfedb1176e2ba14fa117776e0d4e11f13e95eb2dcc00e29c2ab` |

**2/3 PDF:ää onnistuneesti ladattu, 0/3 täydellistä tarjouspyyntöpakettia.** Seitsemän päivän GitHub Actions -artefakti sisältää alkuperäiset PDF:t, poimitut sivutekstit ja `acquisition.json`-raportin.

## Lähdepohjainen alustava arvio: Liperi 555505

Julkisen vertailutaulukon alkuperäinen URL:
https://tarjouspalvelu.fi/Julkiset/AvaaViesTied/4ebfa1ec-b55e-4f66-b0f1-6328f17db598?naytaSelaimessa=False

Asiakirja sisältää tarjouspyynnöstä vertailuun kopioituja kelpoisuusehtoja:

- Vastaavalla työnjohtajalla tulee olla **kaksi vastaavaa referenssiä viimeiseltä kahdeksalta vuodelta**. Referenssin kohdeluokkia on eritelty, ja lopullisen vastaavuuden ratkaisee tilaaja.
- Vastaavalta työnjohtajalta vaaditaan **vähintään viiden vuoden kokemus** vastaavan työnjohtajan tehtävistä.
- Tarjoajan on tullut osallistua **22.4.2025 järjestettyyn kohteen näyttötilaisuuteen**, ja vertailussa kuvataan tarjouksen hylkääminen osallistumisen puuttuessa.
- Vertailutaulukossa on kohdekohtaisia **tarjottuja hintoja**: Paloaukean kouluyksikkö **233 036 €** ja päiväkoti **121 177 €** (alv 0 %). Nämä ovat tarjoajan hintoja, **eivät tarjouspyynnön vahvistettuja ennakoituja arvoja**.
- Liikevaihdon, vakuuksien ja vakuutusten täydellistä ehtokokonaisuutta ei tässä auditissa vahvistettu.

Alustava AI-lähdetulkinta: **OUT_OF_REGION**, koska kohde on Liperissä. Kyseessä on historiallinen tarjousvertailu, ei nykyisin avoin tarjousmahdollisuus.

## Liperi 588687

Lähde: https://tarjouspalvelu.fi/Julkiset/AvaaViesTied/30041e6e-4ed1-4de9-b231-2dcec9af5bd2?naytaSelaimessa=False

Julkinen 15-sivuinen vertailutaulukko on ladattu ja teksti poimittu. Hankinta koskee Liperin kunnan jätevedenpumppaamojen huolto- ja korjaustöitä vuosille 2026–2029. Alustava AI-lähdetulkinta: **OUT_OF_REGION_AND_SCOPE**; sijainti ei ole hyväksytyssä ICP-alueessa, eikä päätyö ole huoneisto- tai pintasaneeraus.

## Tekninen muutos

`workers/extract_public_pdf_requirements.py` tekee sivukohtaisen, lähde-URL:iin sidotun avainsanaosumien poiminnan. `workers/collect_public_tender_pdfs.py` tallentaa jokaiselle onnistuneelle PDF:lle erillisen `*.requirements.json`-tiedoston, jossa on viitteelliset tekstiotteet, ei hyväksyttyjä soveltuvuusväittämiä. Näiden tuottaminen vaatii uuden GitHub Actions -ajon.

## Validointitulos

- Ladattuja alkuperäisiä PDF-asiakirjoja: **2**
- Kokonaisia lähdeasiakirjapaketteja: **0**
- Alustavia negatiivisia AI-lähdetulkintoja näistä kahdesta: **2**
- Gold-positiiviset: **0**
- Gold-negatiiviset: **0** (tiukka gold-portti vaatii täydet asiakirjat)
- Parilliset gold-arvioinnit: **0**
- Precision@30: **NOT MEASURED**
- Hyväksymisraja 80 %: **TODENTAMATTA**

**STOP_GOLD** pysyy voimassa. Vahvistettu yksittäinen julkinen tarjousvertailu ei korvaa tarjouspyyntöä liitteineen, eikä tarjousvertailun tarjoushintaa saa syöttää malliin varmennettuna ennakoituna sopimusarvona.
