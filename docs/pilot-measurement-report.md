# Sisäisen mittaripilotin tulos

Ajo: 2026-10-19T00:14:26.477Z. **30 toimituksen synteettinen simulaatio**, ei toteutunut 30 päivän asiakaspilotti.

| Mittari | Toteutunut tulos | Tulkinta |
|---|---:|---|
| Toimituksia | 30 | Kuvitteellinen asiakas |
| Lopullisia nostoja | 90 | Synteettiset kontrollit |
| Automaation ajoaika yhteensä | 134.07 ms | Mitattu koneaika, ei ihmistyötä |
| Automaation mediaani / toimitus | 3.90 ms | Domain, QA ja tiedostoviennit paikallisesti |
| Automaation p95 / toimitus | 5.53 ms | Ei API-/selainviivettä |
| Estettyjä vientiyrityksiä | 32 | 30 ennen hyväksyntää + 2 mitätöinnin jälkeen |
| Korjaustapahtumia | 2 | Kaksi tarkoituksella lisättyä testiskenaariota |
| Korjattuja toimituksia | 2/30 | Ei arvio oikeasta virheosuudesta |
| Sisäinen hyötyarvio | 30 kyllä / 30 ei / 30 epäselvää | Ennalta määritetyt kontrollit |
| Aktiivinen ihmistyöaika | Ei mitattu | Alle 10 min / asiakas / päivä tavoite avoin |
| Asiakkaan kokema hyöty | Ei mitattu | Edellyttää oikeaa palautetta |

## Havainto ja korjaus

Monipäiväistä simulaatiota valmisteltaessa havaittiin, että hyväksynnän mitätöinti käytti seinäkelloa, vaikka muu työnkulku käytti testin lukittua aikaa. Yhtenäistin kellon välityksen ja lisäsin regressiotestin. Tämä on yksi toteutuksesta löydetty ja korjattu mittaustestauksen virhe; se on erillinen kahdesta tarkoituksella lisätystä korjausskenaariosta.

## Oikean pilotin hyväksyntä

1. Nimetty ja suostunut pilottiasiakas, vahvistettu profiili ja tuotantotallennus.
2. Ajasta aktiivinen päivittäinen työ, tauota odotusajat; onboarding erikseen.
3. Kirjaa korjaukset syineen ja toimitusversioineen. Tavoite: 0 kriittistä asiakasvirhettä.
4. Asiakas arvioi jokaisen oikeasti toimitetun noston: hyödyllinen / ei hyödyllinen / ei vielä ratkaistavissa.
5. Raportoi osuus vain arvioiduista, arvioimatta jääneet erikseen ja palautteen kattavuus. Tavoite ≥80 % hyödyllisiä arvioiduista; vähintään 80 % palautepeitto ja otoskoko näkyviin. Tämä ei korvaa riippumatonta relevanssitestiä eikä mittaa vääriä negatiivisia.
6. Hyväksy toimitusmalli, kun todellinen aktiivinen työ jää alle 10 min / asiakas / päivä ja laatu täyttää portin.
