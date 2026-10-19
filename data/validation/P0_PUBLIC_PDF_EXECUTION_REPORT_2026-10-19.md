# P0 – julkisten tarjouspyyntö-PDF:ien keruu ja lähdevertailu (19.10.2026)

## 1. GitHub Actions -lähtötila

Edeltävä PR #8 -revisio `e6562e7`: regressioajot [39192872422](https://github.com/Jambovisuaalit/pulseplay/actions/runs/39192872422) ja [39192869183](https://github.com/Jambovisuaalit/pulseplay/actions/runs/39192869183) **PASS**. Tämän työn uudet muutokset tarvitsevat oman CI-tarkistuksensa.

## 2. Keräin

- `workers/collect_public_tender_pdfs.py`: manifestin sallimat HTTPS-lähteet, enintään 8 PDF:ää, 12 MiB/PDF, 80 sivua/PDF, ohjausten host-rajaus, PDF-allekirjoituksen tarkistus, SHA-256, noutoaika, sivukohtainen teksti, raportti.
- `data/validation/public_pdf_manifest_2026-10-19.json`: yksi alkuperäinen kaupungin tarjouspyyntö (Äänekosken kaupunki, Koiviston perinnetalon julkisivun maalausurakka, tunniste 602658).
- `.github/workflows/urakkaluotsi-public-pdf-pilot.yml`: rajattu nouto ja seitsemän päivän artefakti. Nolla onnistunutta PDF-noutoa **on nyt CI-virhe**, ei vihreä onnistuminen.
- `tests/test_public_pdf_collector.py`: hostin, HTTPS:n, portin ja PDF-allekirjoituksen regressiotestit.
- Ei portaalikirjautumista, lomakkeiden lähettämistä, Hilma-API-kutsuja, asiakastoimituksia tai tuotantojulkaisua.

## 3. Todellinen PDF-testiajo

Ensimmäinen testiajo: https://github.com/Jambovisuaalit/pulseplay/actions/runs/39193018819

| Mittari | Tulos |
|---|---|
| Lähde-URL:eja manifestissa | 1 |
| Ladatut ja tekstinä käsitellyt PDF:t | **0** |
| Virhe | `URLError` alkuperäisen kaupungin PDF:n HTTPS-noudossa GitHub Actions -ympäristössä |
| Täydet tarjousasiakirjapaketit | 0 |
| Riippumattomat gold-positiiviset | 0 |

Ensimmäinen workflow palautti teknisen **PASS**-tilan, vaikka nouto epäonnistui, koska se tarkisti vain ettei keksittyjä gold-tuloksia synny. Tämä oli hyväksyntäportin puute. Seuraavassa muutoksessa lisättiin vaatimus `full_text_documents > 0`; uusi nollanoudon ajo merkitään epäonnistuneeksi. Tätä ei saa kuvata onnistuneena PDF-keruuna.

Lähde-PDF on julkisesti indeksoitu: https://web28.aanekoski.fi/dynasty10/vhp/202643420.43423.PDF. Hakukoneen palauttamassa PDF-tekstissä sivulla 1 on alkuperäisen ilmoituksen tarkka kohdeosoite: **Koivistonkyläntie 143, 44250 Äänekoivisto**. PDF:n teksti osoittaa korjaus- ja maalaustyön, mutta työmaa on ICP:n ulkopuolella. <Ei gold-positiivista.>

## 4. Riippumaton alustava AI-lähdearvio

`data/validation/public_pdf_paired_cases_2026-10-19.json` sisältää yhden **malliennusteista riippumattoman** lähdetulkinnan:

- `AANEKOSKI_KOIVISTO_PAINT_2026`: `NEGATIVE_OUT_OF_REGION` (alustava AI-lähdetulkinta). Tarkka sivu- ja osoiteviite yllä.
- Koska PDF:n alkuperäisiä tavuja ja täydellistä liitekokonaisuutta ei saatu varmennettua, `gold_label=UNREVIEWED`. Ei muuteta indeksoitua otetta täydeksi dokumenttivarmennukseksi.
- Aiemmasta Hilma-otoksesta ei ole samaa ilmoitusta eikä tähän luotu riippumatonta parillista metadata-ennustetta. `baseline_label=null`, `enhanced_label=null`.

## 5. Osuvuuden laskenta

`workers/evaluate_paired_source_gold.py` tuottaa TP/FP/FN/TN:n ja parillisen precision-eron vain **samoille tapauksille**, joilla on vahvistettu gold-luokka, alkuperäinen lähdeote ja molemmat ennusteet. Puuttuvat jätetään nimettyinä arvioinnin ulkopuolelle. `tests/test_paired_source_gold.py` testaa tätä myös synteettisillä positiivisilla/negatiivisilla; ne **eivät ole mitattuja todellisia tuloksia**.

| Mittari | Todellinen tila |
|---|---|
| Löydettyjä uusia PDF-ehdokkaita | 1 |
| Riippumattomasti lähdevarmennettuja, parillisia arviointitapauksia | **0** |
| Vahvistettuja gold-positiivisia | **0** |
| Vahvistettuja gold-negatiivisia | **0** |
| TP/FP/FN/TN todellisesta aineistosta | **Ei mitattavissa** |
| Parillinen precision-muutos | **null** |
| Precision@30 | **null** |
| 80 % hyväksymisraja | **Todentamatta** |

## 6. Portti ja jatko

**STOP: SOURCE_ACQUISITION_BLOCKED / GOLD_INSUFFICIENT.** Jatka vain julkisilla suoraan ladattavilla alkuperäisillä tarjouspyynnöillä. Hanki vähintään yksi teknisesti varmennettu täydellinen asiakirjapaketti ja lähteeseen sidottu riippumaton arvio ennen osuvuusvertailua. Valikoitu negatiivinen kontrolli ei ole riippumaton satunnaisotos. Älä yhdistä PR #8:aa, älä julkaise tuotantoon äläkä tee asiakastoimituksia.
