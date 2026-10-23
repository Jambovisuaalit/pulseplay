# P0.3d – 30 ilmoituksen sijainti-, sisältö-, määräaika- ja versiotarkistus

Päiväys 19.10.2026 klo 10:35 Suomen aikaa (07:35 UTC). Lähteinä kaksi GitHubiin tallennettua alkuperäisen Hilma-metadatahaun otosta (100+52 uniikkia ilmoitusta). 30 rivin tarkistusjonon arvioidut kohteet: `data/validation/p0_3d_30_metadata_review_2026-10-19.json`.

## Tarkistuksen tulokset
- 30 / 30 ilmoituksen otsikko ja lähdekuvaus käyty läpi.
- 26 / 30 ilmoituksessa kuvataan nimettyä työkohdetta tai palvelualuetta eksplisiittisesti; 4 / 30 sijainti perustuu hankkeen nimeen ja kontekstiin, ei varmistettuun työkohteen osoitteeseen.
- 1 / 30 sijaitsee eksplisiittisesti Uudenmaan ulkopuolella: 57598 (Lempäälän jäteasema).
- 9 / 30 määräajasta on jo kulunut tallennetun tiedon mukaan 19.10.2026 klo 07:35 UTC.
- 1 / 30 on eksplisiittisesti keskeytetty otsikossa: 59352.
- 2 mahdollista samaa hankintaa koskevaa versioryhmää: 59352/59399 (Maunulan kirkko) ja 58430/59464 (Espoon Asuntojen yhdeksän kiinteistöä). Näitä EI ole vielä todistettu virallisen ilmoitusversion viiteketjulla.
- Negatiiviset rakennustyyppikontrollit (kadut, uudisrakennukset, maanrakennus, puistot, laiturit) pysyvät rekisterissä eikä niitä esitetä saneerauskohteina.
- Kaikki 30 alkuperäisten asiakirjojen kelpoisuus-, arvo- ja liitetarkistukset ovat avoinna. Varmennettuja gold-positiivisia 0, Precision@30 null.

## Virhelähteet ja seuraavat hyväksymisportit
Aineisto on **malliavusteinen tallennettujen ilmoituskuvausten katselmointi**, ei jokaisen ilmoituksen koko hankinta-asiakirjakokonaisuuden tarkastus. Kuvaus voi olla vanhentunut; peruutus, korjattu julkaisu tai muutettu määräaika voi puuttua otoksesta. Erityisesti 57598 on esimerkki siitä, miten ostajaan tai kuvauksen satunnaiseen paikannimeen perustuva alkuperäinen alueheuristiikka voi tuoda väärän sijaintiosuman.

1. P0.3d.2: tarkista **virallisista ilmoitusversioista** 59352/59399 ja 58430/59464; määritä mahdollinen korvaava ilmoitus ja viimeisin voimassa oleva määräaika.
2. P0.3d.3: vahvista jokaisen urakan sijainti ja työlaji joko alkuperäisestä eForms-projektierästä tai julkisesta portaalikuvauksesta; luokitus `SOURCE_WORKSITE_VERIFIED` vasta yksilöityyn näyttöön nojaten.
3. P0.3d.4: kasvata 30–50 **lähteestä varmennetun Uudenmaan kohteen** joukkoa vain uusilla oikeilla ilmoituksilla; dokumentoi keruuhorisontti ja näytevirhe.
4. P0.4: riittävän lähteen kattavuuden jälkeen erillinen sokkoutettu riippumaton kelpoisuusarvio; älä nimeä tallennettujen kuvauksien manuaalista analyysiä riippumattomaksi goldiksi.

PR #8 pidetään luonnoksena. Ei asiakastoimitusta, tuotantojulkaisua eikä uusia Hilma-API-kutsuja tässä työssä.
