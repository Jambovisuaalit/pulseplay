# P0: Pohjola Sairaalan ZIP-liitteet ja Uspenskin RU-tarjouspyyntö – lähdeauditointi

Päiväys 19.10.2026. Tutkittu julkisia, kirjautumatta saatavia lähteitä. Tämä on historiallisten asiakirjojen **lähdeketjun selvitys**, ei ilmoituksen tai tarjoajan kelpoisuuden vahvistus.

## 1. Pohjola Sairaala Helsinki, 4. kerroksen muutostyöt (2020)

Alkuperäinen tarjouspyyntö: https://cdn.hankintailmoitukset.fi/public-attachments/42f2a55c-dc72-4832-4445-08d8241b96e8

- Tilaaja alkuperäisessä dokumentissa: Psyykkisen hyvinvoinnin keskus Komppi Oy.
- Kohde: Puutarhurinkuja 2, Helsinki, 4. kerros; kolme potilashuonetta jaetaan kuudeksi.
- Erilliset tarjousosat: rakennus-, LVIA- ja sähköurakka; osatarjoukset sallittu.
- Liiteluettelo tarjouspyynnön lopussa: **Liite 1 Rakennusurakka.zip**, **Liite 2 LVIA urakka.zip**, **Liite 3 Sähköurakka.zip**.
- Julkinen ZIP:n **suora URL ei löytynyt** tehdyillä täsmähauilla; ZIP:n sisältöä, täydellisyyttä tai SHA-256:ta **ei voitu varmentaa**.
- Vastuuvakuutus vähintään 500 000 euroa; kolmen vuoden liikevaihdot, luottoluokitustieto, kolme soveltuvaa referenssiä vaaditaan. Nämä ovat tarjouspyynnön vaatimuksia, eivät todiste tarjoajan kelpoisuudesta.
- Alkuperäisen hankintailmoituksen yksilöivää ID:tä **ei vahvistettu**; tarjouspyynnön URL ei yksin riitä ilmoituslinkitykseen.
- Yksittäisen rakennusurakan ennakoitu arvo **ei tiedossa**. Ei voi päätellä kolmen osaurakan yhteisestä arvosta eikä siitä, että hankinta ilmoitettiin kansallisen kynnysarvon alittavaksi.

## 2. Uspenskin katedraalin sähkösaneeraus 2021, rakennusurakka (RU)

**Uusi alkuperäinen lähde:** [Urakkalaskenta-asiakirjaluettelo 24.4.2021](https://hnshilmaprodsa.blob.core.windows.net/attachments/75491beb-82be-440b-e865-08d906e43da0?sv=2020-04-08&se=9999-12-31T23%3A59%3A59Z&sr=b&sp=r&rscd=attachment%3B+filename%3D%221.+ASIAKIRJALUETTELO.pdf%22&sig=TFRnsFP6YTmE1IjAOg6E6fFUzhlrCSZ6XNeFN0ftBho%3D). PDF avautui julkisesti, HTTP 200, 2 sivua.

Asiakirjaluettelossa **RU = rakennusurakka eli pääurakka**, **SU = sähköurakka**. RU:n kaupallisiksi asiakirjoiksi on nimetty:

1. **2.1 Tarjouspyyntökirje RU, 1.4.2021** – suora julkinen tiedosto **ei löytynyt**.
2. **3.1 Tarjouslomake RU** – ei löytynyt.
3. **4 Yksikköhintaluettelot RU** – ei löytynyt.
4. **5 Urakkaohjelma, 1.4.2021** – ei löytynyt.
5. **6.1 Turvallisuusasiakirja, 1.4.2021** – ei löytynyt.
6. **6.2 Haitta-ainekartoitus, 20.10.2017** – ei löytynyt.
7. **7 Urakkarajaliite, 1.4.2021** – ei löytynyt.

Luettelossa mainitaan lisäksi arkkitehti-, sähkö-, valaistus-, geotekniset ja muut piirustukset sekä **Sisäseinien korjaus- ja entisöintityöselostus / Maalausvalvonta Laeslehto Oy**. Tähän täsmää julkisesta Hilman arkistosta löytynyt [alkuperäinen yhdeksänsivuinen rakennustyöselostus](https://cdn.hankintailmoitukset.fi/public-attachments/4efc21a0-a41e-4fb0-6f5d-08d813538d7d).

**Lähdeketjun taso:** asiakirjaluettelo todentaa Uspenskin 2021 projektin asiakirjatyypit ja viittaa samannimiseen työselostukseen. Se ei yksilöi Hilma-ilmoitustunnusta eikä anna ladattavia linkkejä muihin RU-asiakirjoihin. Samanniminen projekti ja työselostus **eivät ole riittävä todiste** ilmoitustason täydellisestä asiakirjapaketista.

## 3. Lopputila

| Mittari | Tulos |
|---|---|
| Tutkitut kohteet | 2 |
| Uusia löytyneitä alkuperäisiä asiakirjaluetteloita | 1 (Uspenski, 2 sivua) |
| Pohjolan rakennusurakan ZIP:n lataus vahvistettu | Ei |
| Uspenskin RU-tarjouspyyntökirjeen lataus vahvistettu | Ei |
| Alkuperäisen ilmoitustunnuksen linkitys vahvistettu | 0/2 |
| Yksittäisen urakan arvo vahvistettu | 0/2 |
| Täydet tarjousasiakirjapaketit | 0/2 |
| Riippumattomat gold-positiiviset | 0 |
| Precision@30 | Ei laskettavissa |

Päivitetty koneellisesti tarkastettava rekisteri: `data/validation/helsinki_original_tender_discovery_2026-10-19.json`. Fail-closed-portti: `workers/evaluate_helsinki_tender_linkage.py`, testit `tests/test_helsinki_tender_linkage.py`. **Kaikki tapaukset ovat edelleen UNREVIEWED ja kelpoisuusarvio CONDITIONAL_SOURCE_INCOMPLETE.**

## 4. Seuraava hakureitti

Etsi **alkuperäinen Hilma-ilmoitus ja siihen sidottu liitemanifesti** (vanhoissa hankinnoissa myös Hilman vanha blob-arkisto), jonka avulla voidaan noutaa oikea RU-tarjouspyyntö ja Pohjolan ZIP. Ei saa generoida blob-tunnuksia, allekirjoituksia tai muita yksilöiviä latauslinkkejä arvaamalla. Lähteiden julkinen saatavuus ja alkuperä on todennettava. Historialliset 2020–2021 hankinnat soveltuvat vain laadun ja tiedonpoiminnan kontrolliksi, eivät vuoden 2026 avoimiksi tarjousmahdollisuuksiksi. Ei PR:n yhdistämistä, tuotantojulkaisua eikä asiakastoimituksia.
