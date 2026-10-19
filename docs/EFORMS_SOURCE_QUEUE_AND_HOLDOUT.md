# eForms-lähdejonon käyttö ja riippumattoman arvioinnin portti

Tämä on lähdetiedon poimintaa, ei uutta validointitulosta eikä asiakkaalle toimitettava kooste.

## Tallennetut XML-tiedostot

Aja olemassa olevilla, alkuperäisillä eForms-XML-tiedostoilla:

```bash
python -B workers/build_eforms_source_queue.py --input-dir /path/to/saved-xml --output-dir /path/to/source-review
python -B -m unittest tests.test_eforms_source_queue -v
```

Syötehakemistossa pitää olla vähintään yksi oikea XML. Puuttuva aineisto on virhe, ei lupa luoda synteettistä arviointiaineistoa. Tiedostotunnus on oletusarvoisesti notice_id; tarkista tunniste alkuperäisestä lähteestä ennen gold-arviointia.

Tulosteet: `source_review_queue.csv` (osa-aluekohtainen näyttö ja puuttuvat kentät) sekä `source_manifest.json` (tiedostojen SHA-256, rivimäärät ja arvioinnin lukitusstatus). Työkalu ei lataa liitteitä, tarkista kelpoisuutta, eikä anna asiakas-GO:ta.

## Riippumattoman testijoukon hankinta

1. Kerää uusi ajallisesti erillinen Hilma-otos hyväksytyllä kutsurajalla. Älä käytä vanhoja 100 tai 52 ilmoituksen joukkoja uuden holdoutin lähteinä.
2. Tallenna alkuperäiset ilmoitukset, eForms-XML, hakuehdot, aikaleima, lähde-URL, yksilöivä tunniste, SHA-256 ja keruupäivä.
3. Jäädytä lähteet ja arviointiohje ennen luokittelijan ajoa. Arvioija ei saa nähdä mallin ennustetta.
4. Riippumaton arvioija tarkistaa sijainnin, pääasiallisen työn, yksittäisen urakan arvon, tarjousajan ja tarvittavat asiakirjat. Merkitse epävarmat erikseen; älä muuta niitä negatiivisiksi.
5. Lukitse gold-luokat ja niiden lähdeperusteet erillisessä, versionhallittavassa tiedostossa. Vertaa vasta sitten mallin ennusteita.
6. Raportoi precision, FP, FN, arvioimatta jääneet, recall, positiivisten määrä sekä lähteiden puuttumisen syyt. Jos ennustettuja positiivisia ei ole, precision on määrittelemätön, ei 100 %.
7. Käytä vanhoja 52 ja 100 ilmoituksen joukkoja vain kehitykseen ja regressioon. Älä sekoita niitä uuteen holdoutiin.

## Nykyinen hyväksyntä

Uutta holdoutia ei ole vielä kerätty eikä gold-luokkia lukittu. Ei mergeä, julkaisua, asiakasviestejä tai automaattisia GO-suosituksia.
