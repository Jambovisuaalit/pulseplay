# Urakkaluotsi – ICP V2:n erillinen 52 ilmoituksen holdout-testi

**SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS**

Alkuperäinen arviointi 19.10.2026, uusinta ja raportin täsmäytys 20.10.2026. Tekninen kohde: Uudenmaan Korjausrakentajat Oy (kuvitteellinen).
Tämä ei ole uusi 30 päivän seuranta, täydellinen tarjousasiakirja-arvio eikä
ensimmäisen maksavan asiakkaan toimitus.

## V2:ssa toteutetut kolme korjausta

1. **Työmaan sijainti**: hyväksyttyjen kuntien joukko on tarkalleen Helsinki,
   Espoo, Vantaa, Kauniainen ja Kirkkonummi. Ostajan nimi tai kotikunta ei
   vahvista työmaan sijaintia. Puuttuva tai ristiriitainen sijainti jää
   `UNKNOWN`-tilaan, ei myönteiseksi osumaksi. Tekstistä löytyväksi väitetty
   rakenteinen sijainti tarvitsee täsmällisen lähdeotteen.
2. **Yksittäisen urakan koko**: 10 000–250 000 € koskee eriteltyä urakkaa.
   Hankinnan puitearvoa ja usean osa-alueen yhteissummaa ei saa lukea
   yksittäisen työn hinnaksi. Puuttuvat, nolla- ja tarkistamattomat arviot
   säilyvät tuntemattomina. Metadatan arvio ei yksin todista urakkakokoa.
3. **Työn todellinen sisältö**: uudisrakennukset, purku, silta-/katuinfra,
   katto-, ikkuna-/ovi- ja laajat LVIS-kokonaisuudet erotetaan pienistä
   sisäkorjauksista. Esimerkiksi *lattianostimen peruskorjaus* ei ole
   lattiaremontti eikä paloilmoittimen saneeraus ole huoneistosaneeraus.

V2 on erillinen `workers/relevance_v2.py`-luokittelija. Edellinen
`workers/build_validation_set.py`-pisteytys ja sen 100 ilmoituksen jäädytetty
vertailu säilyvät muuttumattomina historiallista auditointia varten.

## Holdout-otoksen riippumattomuus ja rajat

| Tarkistus | Tulos |
| --- | --- |
| Uusia aidon Hilma-hakumetadatan ilmoitustunnisteita | **52** |
| Päällekkäisiä tunnisteita vanhan 100 kanssa | **0** |
| Päällekkäisiä menettelytunnisteita | **0** |
| Saman nimisiä normalisoituja hankintoja | **0** |
| Erillinen lähdearkisto | GitHub Actions -artefakti **12155344561** |
| Lähteen keruuhetki | **2026-10-19T00:13:54.618749+00:00** |
| Uusia live-Hilma-kutsuja tähän arvioon | **0** |
| Tunnisteiltaan erillinen otos | **PASS** |
| Ajallisesti riippumaton otos | **EI** – keruu noin minuutti vanhan jälkeen |
| Täysien tarjousliitteiden lähdetarkistus | **NOT TESTED** |

Jäädytetyt `holdout_raw.json`, `manifest.json`, `ai_source_only_seed.tsv`,
`ai_silver_labels.csv` ja `ai_silver_manifest.json` tallentavat lähteen,
lähdesitaatit, aikaleiman, nimilistan ja SHA-256-tiivisteet.
AI-silver-luokat kirjoitettiin **ennen V2:n ennusteiden avaamista**. Ne eivät
silti ole riippumattomasti varmennettua ihmisen gold-totuutta.

## Tulokset samalla 52 ilmoituksen joukolla

| Mittari | Vanhalla avainsanapisteytyksellä | V2 fail-closed |
| --- | ---: | ---: |
| Relevantti | 6 | 0 |
| Ehdollinen asiakasnostoehdokas | 5 | 0 |
| Ei priorisoitu / puuttuvan tiedon vuoksi lykätty | 0 | 21 |
| Epärelevantti | 41 | 31 |
| AI:n mukaan selvästi väärät positiiviset | **6** | **0** |
| AI:n mukaan selvästi väärät negatiiviset | 0 | 0 |
| Mahdolliset väärät negatiiviset, epäselvät mukana | 0–3 | 0–3 |
| Alustava AI-precision ratkaistuissa positiivisissa | 0,0 % | **Ei määriteltävissä** |

AI-silver-luokat: 49 epärelevanttia, 2 ehdollista, 1 ilman riittävää lähdetekstiä;
**ei yhtään selvästi relevantiksi vahvistettua kohdetta**. Vanhan seulonnan
kuusi positiivista olivat tämän AI-arvion perusteella vääriä: Mäntsälän
puitejärjestely, Jyväskylän kylpyhuonekorjaukset, lattianostinten työ,
Tampereen talotekniikkakokonaisuus, TAYSin paloilmoitin ja Tuusulan
uudisrakennus. Nykyinen V2 siirtää viisi pois rajauksesta ja yhden ei-priorisoiduksi. Ei-priorisoitu ei tarkoita lähteestä vahvistettua epärelevanttia.

**Keskeinen tulkinta:** V2:n nolla väärää positiivista saavutettiin samalla,
kun se ei antanut yhtään varmaa positiivista. Tarkkuuslukua ei voi laskea
ilman yhtään positiivista ennustetta. Tätä ei saa ilmoittaa 100 %:n precisionina.

V2:n 21 ei-priorisoidusta 18 oli AI-silver-arvion perusteella epärelevanttia,
2 epäselvää ja 1 arvioimaton. Ehdollisten tarkistusjono on siis edelleen
laaja eikä työaikatavoitetta ole todennettu. Aiempi tulostiedosto oli vanhasta luokittelijaversiosta: tässä ajossa JSON/CSV-tulokset täsmäytettiin nykyiseen kooditiivisteeseen `5c8a5f1c0b0ebe330c9820c64f13b25c1615af5f8fefd728d66455eefce5b91e`.

20.10.2026 lisätty alkuperäaineiston hashin, tunnisteiden, menettelyjen, otsikoiden ja 52 AI-lähdesitaatin uudelleentarkistus. Tarkistus laskee erillisyyden lähdetiedostoista eikä luota manifestiin merkittyihin nolliin. Päällekkäisyys, väärä sitaatti, väärä snapshot tai perusteeton täysien asiakirjojen tarkistusväite pysäyttää arvioinnin. 130 Python-testiä PASS, sisältäen neljä uutta provenienssitestiä.

100 ilmoituksen uusintasimulaatio 20.10.2026: 92 NOT_EVALUATED, 7 EXPIRED, 1 CANCELLED ja 0 GO. Tämä on saman historiallisen aineiston uusinta, ei uusi riippumaton validointijoukko.

## QA ja hyväksyntä

- Kuntajoukon ja ostajan/worksite-erottelun regressiot: **PASS**.
- 10 000 €/250 000 € -rajojen ja puitesummien regressiot: **PASS**.
- Uudis-/LVIS-/ikkuna-/infra-/purkupoissulkujen regressiot: **PASS**.
- Jäädytettyjen lähdesitaattien tarkistus: **PASS**.
- 52 tunnisteen erillisyys vanhan joukon tunnisteista, menettelyistä ja otsikoista: **PASS**.
- AI-silver ei voi avata virallista precision-porttia: **PASS**.
- Riippumaton 80 %:n relevanssiportti: **NOT MEASURED**.
- Koko tarjousasiakirja- ja asiakkaan soveltuvuustarkistus: **NOT TESTED**.
- Päivittäinen aktiivinen toimitustyö ja kannattavuus: **NOT MEASURED**.

**CONDITIONAL PASS vain uuden luokittelijan tekniselle turvallisuudelle.**
Ensimmäisen maksavan asiakkaan toimitusvalmiutta **ei hyväksytä** näillä
tuloksilla.

## Jäljellä olevat korjaukset

- **P0:** hanki aiemmista näytteistä myös ajallisesti erotettu, alkuperäisistä
  tarjousasiakirjoista arvioitu riittävän positiivinen testijoukko.
- **P0:** toteuta liitteiden, kysymysmääräajan, kelpoisuuden ja todellisen
  toteutusalueen todentaminen ennen myönteistä asiakasnostoa.
- **P1:** pienennä 21 ehdollisen kohteen jonoa lähteistä erotettavilla
  sijainti-, lot-/arvo- ja työroolitiedoilla. Älä säädä V2:ta tämän
  holdout-testin perusteella ja kutsu samaa otosta uudeksi testiksi.
- **P1:** arvioi uusi versio aidosti uudella aineistolla, sisältäen
  sopivia positiivisia ilmoituksia, ja laske precision, FN, FP sekä peitto.
- **P2:** mittaa aktiivinen työaika sekä ehdollisten tarkistusjonon kustannus.

PR ja testi pysyvät sisäisinä. Ei sähköposteja, PR-yhdistämistä,
Vercel-julkaisua eikä uutta Hilma-API-kutsua.
