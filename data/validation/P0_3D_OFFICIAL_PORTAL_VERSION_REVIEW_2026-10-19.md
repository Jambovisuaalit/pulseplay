# P0.3d – kahden hankintaversion lähdevarmennus 2026-10-19

Lähde: Cloudia Tarjouspalvelun **julkiset hankintakohtaiset sivut**, jotka näyttävät tunnuksen, ilmoitustyypin ja määräajan ilman kirjautumista. Tämä on alkuperäisen kilpailutusportaalin julkaisutietoa, ei tarjousasiakirjaliitteiden katselmointia eikä koko virallisen korjausviittausketjun todistamista.

## Maunulan kirkon tekninen peruskorjausurakka
- **59352 (vanha / keskeytetty)**: Tarjouspalvelun julkinen [629772 / KESKEYTYSILMOITUS](https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon?p=472&tpId=632427) on tulosilmoitus [E4]. **Älä toimita asiakkaalle aktiivisena.**
- **59399 (uudempi kilpailu)**: Julkinen [632428 / Maunulan kirkon tekninen peruskorjausurakka](https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=632428), ilmoitustyyppi Kilpailu [E3], julkaistu 13.10.2026 klo 14.53 Suomen aikaa, tarjousaika 3.11.2026 klo 12.00 (UTC+02). Rakennuspaikan tutustumiskäynti vaaditaan. Määräaika ei todista kelpoisuutta, eikä tutustumiskäynnin toteutumista ole vahvistettu.
- **Yhteys**: sama hankintayksikkö ja hankkeen nimi, yksi keskeytys ja toinen uudempi kilpailu. Alkuperäisten XML-ilmoitusten eksplisiittistä keskinäistä korjaus- tai korvausviitettä **ei vielä ole varmennettu**. Ryhmää ei saa laskea kahdeksi aktiiviseksi samaksi urakaksi.

## Espoon Asunnot Oy, yhdeksän kiinteistön lämpötekniset työt
- **58430 (aiempi kilpailu)**: Julkinen [629798 / kilpailuilmoitus](https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=629798), julkaistu 1.10.2026 klo 12.35 (UTC+03), määräaika 13.10.2026 klo 12.00 (UTC+03) -> **vanhentunut**, ei aktiivinen.
- **59464 (myöhempi kilpailu)**: Julkinen [632650 / hankintailmoitus](https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=632650), uuden kilpailutuksen raportoidut julkaisu- ja tarjouspäivät 14.10.2026 ja 23.10.2026. Erillinen julkinen 632650-tulosviite voi viitata myös myöhempään E4-tulosilmoitukseen, joten **ilmoitustyypin täysi merkitys ja viimeisin mahdollinen tila on pidettävä erikseen tarkistettavana**.
- **Yhteys**: sama ostaja, yhdeksän kiinteistön yksilöity kokonaisuus ja peräkkäiset määräajat. Erilliset kiinteistöt voivat muodostaa omia tarjousosia; *yhtä ilmoitusta ei saa tulkita yhdeksi vahvistetun arvon urakaksi*. Vanhan ja uuden ilmoituksen keskinäinen korvausviite on vielä varmentamatta alkuperäisestä XML:stä.

## Rekisterin käsittelysäännöt
- Poista aktiivisista ehdokkaista **59352 (keskeytys)** ja **58430 (umpeutunut tarjousaika)**.
- 59399 ja 59464 vain **ehdollisia, lähteeseen sidottuja hankintamahdollisuuksia**, kunnes hankintakohtainen nykytila, liitteet, osat ja tarjoajakohtaiset kelpoisuusehdot ovat vahvistettuja.
- Pidä virallisen ilmoitusversion suhde `UNVERIFIED`; sama nimi ei ole riittävä virallinen korvausketju.
- Ei gold-positiivisia eikä laskettavaa Precision@30:tä. PR #8 luonnoksena, ei mergeä tai asiakastoimituksia.
