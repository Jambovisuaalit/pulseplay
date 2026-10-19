# Uudenmaan Korjausrakentajat Oy – testiprofiili ja seurannan rajaus

**SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS**

## Testiprofiili

Kuvitteellinen 8 työntekijän korjaus- ja saneerausyritys, ei oikea sopimusosapuoli.
Palvelut: huoneistosaneeraukset; pintaremontit ja maalaustyöt; lattia- ja
kalustekorjaukset; kiinteistöjen pienkorjaukset; toimitilojen sisäpuoliset
korjaustyöt. Pääurakoitsija pienissä korjaushankkeissa, aliurakoitsija suuremmissa.

Jäsennetty profiili: `yritysprofiili.json`; nykyistä sovelluksen varsinaista
`data/company_profile.json`-tiedostoa **ei ole aktivoitu eikä ylikirjoitettu**.
Testiprofiilin tila on tarkoituksella `UNCONFIGURED`, koska väitettyjä palveluja
ei ole varmennettu ulkoisilla todisteilla.

## Sisällytys / poissulut

- Sallitut toteutuskunnat **täsmälleen** Helsinki, Espoo, Vantaa, Kauniainen,
  Kirkkonummi. Ostajan kotikunta ei osoita työmaan sijaintia.
- Sopivan yksittäisen urakan kiinnostava koko **10 000–250 000 euroa**.
  Puitejärjestelyn yhteenlaskettua arvoa ei saa käyttää yksittäisen työn arvona
  ilman tarjousasiakirjojen tarkistusta.
- Sisään: korjaus-, pintasaneeraus-, maalaus-, lattia-, kaluste- ja pienkorjaustyöt,
  joissa laajuus ja kohde tukevat asiakkaan palveluita.
- Pois: uudisrakentaminen, laaja talotekniikkakokonaisuus, ikkunoiden ja ovien
  kokonaisvaihto, kattourakka, yksittäinen yli 250 000 euron hanke,
  toimintakuntien ulkopuolinen työmaa sekä lähteessä keskeytetty tai peruttu ilmoitus.
- Ehdollinen: työnkuvaan sisältyy sekä saneerausta että LVIS-töitä, urakan
  erittely tai kokoluokka puuttuu, työmaa on epäselvä, tai määräajan / liitteiden
  tarkistus on kesken. Ehdollinen ei tarkoita yrityksen pätevyyden hyväksymistä.
- CPV 45000000, 45200000, 45400000 ja 45450000 ovat nykyisen **hakukeruun
  laajoja siemenkoodeja**, eivät automaattisia kelpoisuus- tai sisällytysehtoja.
  CPV ei yksin vahvista urakan sisältöä tai paikkaa.
- Hakumetadatan määräaika näytetään alkuperäisen aikavyöhykkeen kanssa.
  Päivämäärän tarkkuudella ilmoitettu sama päivä ei ole automaattisesti avoin;
  kysymysmääräajan puuttuminen on dokumentoitava.

## Todentamattomat seikat

Yrityksen referenssit, pätevyydet, liikevaihto, vakuudet, vasteaika,
taloudellinen asema, todellinen kapasiteetti ja kaikkien urakoiden yksityiskohtaiset
kelpoisuusehdot ovat vahvistamatta. `certifications: []` tarkoittaa **ei tietoa**,
ei osoitusta pätevyyksien puuttumisesta. Yhtään vahvistettua GO-päätöstä ei saa
tuottaa tästä testiprofiilista.
