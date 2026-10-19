# Korjauslista uusintatestin jälkeen

**SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS**

| Prioriteetti | Tehtävä | Tila 19.10.2026 |
| --- | --- | --- |
| P0 | Keskeytetty tai peruttu ilmoitus ei saa GO-tilaa, vaikka määräaika olisi tuleva. | **KORJATTU**, Python + TypeScript -regressiot |
| P0 | Sitova viiden kunnan työmaarajaus; erota ostajan sijainti todellisesta urakkakohteesta. | **AVOIN**, PR #4:n laajempi rajaus ei kelpaa |
| P0 | Lähteen ja asiakkaan todelliset kelpoisuusvaatimukset sekä täydet tarjousliitteet tarkistettava ennen GO:ta. | **AVOIN**; nykyinen esto toimii, mutta lähdetarkistuksia ei ole |
| P0 | Vahvistettu riippumaton 100 kohteen gold-luokitus tarvitaan hyväksymismittariin. | **AVOIN**; 100 AI-silver-luokkaa on alustava, ei gold |
| P1 | Precisionin, väärien positiivisten ja väärien negatiivisten korjaaminen ja uusintatestaus eri holdout-otoksella. | **AVOIN**; AI-precision-väli 6,7–33,3 % |
| P1 | CPV-rakenteen ja raportoidun hanke- vs. osa-urakka-arvon oikeellisuus. | **AVOIN**, havaitut lähdetason riskit PR #4:ssä |
| P1 | Määräajat, päivitykset, duplikaattien mahdolliset ilmoitusversiot, kysymysmääräajat ja asiakirjalinkit. | **AVOIN**, hakumetadatan saatavuus ei riitä |
| P1 | Vertaile PR #4 ja #8 viiden päällekkäisen tiedoston tasolla; älä yhdistä #4 sellaisenaan. | **ARVIOITU**, yhdistäminen jätetty tekemättä |
| P2 | 30 päivän jatkuvan seurannan todellinen aktiivinen työaika, infra ja yksikkökannattavuus. | **EI MITATTU** |
| P2 | Oikean pilottiasiakkaan käyttöpalautteen mittaus, ei synteettinen palaute. | **EI MITATTU** |

Tuotantoseurantaa, live-Hilma-API:a, sähköpostitoimitusta, PR-yhdistämistä
tai Vercel-julkaisua ei ole käynnistetty.
