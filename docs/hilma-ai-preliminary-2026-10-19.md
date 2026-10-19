# Hilma 100 — tekoälyavusteinen esiluokittelu, 19.10.2026

Tämä on *alustava* mallipohjainen analyysi tallennetusta 100 aktiivisen määräajan ilmoituksen joukosta. **Ei riippumatonta vertailutotuutta.** Mallin luokkia ei saa siirtää manual_label-kenttään tai käyttää Precision@30-hyväksyntään.

Aineisto: GitHub Actions 39179825192; 152 ilmoitusta haussa, 117 määräajan perusteella aktiivista, 100 valittu pisteytysjärjestykseen.

## Luokittelun kooste

| Mallin esiarvio | Kaikki 100 | Top 30 |
| --- | ---: | ---: |
| Alustavasti sopiva | 5 | 2 |
| Lisäselvitys | 8 | 6 |
| Alustavasti ei sovi | 87 | 22 |
| Yhteensä | 100 | 30 |

CSV: data/validation/hilma_100_ai_preliminary.csv. Kentät alkavat ai_-etuliitteellä ja validation_status = EI_VERTAILUTOTUUS. Luokitus perustuu ilmoituksen tallennettuun otsikkoon ja kuvaukseen sekä testin Uusimaa-saneeraus-ICP:hen. Erityisesti kapasiteetti, urakan ehdot ja tarjousten liitteet ovat tarkistamatta.

## Ensisijaiset tarkistettavat

- #58217 Mäntsälän rakennustekninen puite ja #59375 Espoon päiväkodin korjaustyöt: alustavasti soveltuvat, edellyttävät kelpoisuuden, ehtojen ja laajuuden tarkistusta.
- #58502 Hyria: osittainen alueosuvuus, palvelualue ja reagointikyky varmistettava.
- #59555 VAV: ikkunoiden/ovien vaihtotyön erityisosaaminen ja pääurakkavastuu varmistettava.
- #59399 Maunulan kirkko, #59139 Helsingin vankila, #59022 Heka Maunula: mahdollinen työtyypin osuvuus, mutta erikoisehdot ja urakan koko epävarmoja.
- #58545 käyttövesisaneeraus: sijainti ja LVI-toteutuskyky varmistettava.
- #59569: tallennetusta ilmoituksesta puuttuvat otsikko ja kuvaus.

## Havaitut tekniset riskit

1. **Sijainti ei ole riittävän vahva pisteytyskriteeri.** Top 30:ssä on useita muualla Suomessa sijaitsevia puite- ja korjausurakoita. Tämä tulee käsitellä ICP-profiilin alueosuvuudessa.
2. **Keskeytetyn ilmoituksen suodatus ei toimi.** #59352, jonka otsikko alkaa KESKEYTETTY, sijoittui sijalle 6, vaikka määräaika oli tallenteessa tulevaisuudessa. Tätä ei saa ehdottaa asiakkaalle ilman uutta tilatarkistusta.
3. **CPV-koodien sarjoitus on virheellinen.** CSV:ssä merkkijonona saapuneet CPV-koodit on yhdistetty merkki kerrallaan pystypalkeilla. Raaka Hilma-aineisto säilyy erillisenä; CSV-kentän vienti täytyy normalisoida.
4. **Mallin luokitukset eivät riitä hyväksyntään.** Vasta lähteisiin perustuva, riippumaton kaikkien 100 kohteen luokittelu tuottaa todellisen Precision@30:n.

## Suositeltu seuraava korjausjärjestys

1. Estä keskeytetyt/perutut ilmoitukset ja korjaa CPV-normalisointi tulevia poimintoja varten (älä muuta jäädytettyä alkuperäisotosta).
2. Lisää todellinen alueosuvuuden arviointi pisteytykseen ja erota se CPV- tai otsikko-osuvuudesta.
3. Toimita sokkoutettu 100 kohteen lomake riippumattomalle arvioijalle.
4. Lasketaan todellinen Precision@30. Hyväksymisraja vähintään 24/30, kaikki 100 arvioitu.
