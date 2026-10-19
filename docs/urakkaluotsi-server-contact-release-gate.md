# Urakkaluotsi: palvelimelle lähetettävä pilottiyhteydenotto (ei julkaistu)

## Päätetyt kaupalliset tiedot
- Palveluntarjoaja: Tmi Jami Harju, Y-tunnus 3581581-6 (käyttäjän vahvistama).
- Käyttäjän ilmoitus: ei ALV-rekisterissä. Virallisen YTJ-rekisterimerkinnän tarkistus on vielä kesken; laskutukselle ei anneta rekisterivarmennusta.
- Pilotti 249 € / 30 päivää. Jos ei ALV-velvollinen, veroa ei lisätä laskulle eikä laskulla eritellä arvonlisäveroa.
- Maksunsaajan Holvi IBAN ja BIC löytyvät vain yksityisestä laskutusmateriaalista; niitä EI ole lisätty julkiseen repoon.

## Palvelinlomake
- `POST /esittely/api/contact` vastaanottaa validoidun JSON-lomakkeen ja välittää viestin Resend API:iin vain ympäristömuuttujien ollessa kunnossa.
- Vaaditut palvelinasetukset: `RESEND_API_KEY`, `URAKKALUOTSI_CONTACT_FROM` (Resendissä vahvistettu lähettäjä), `URAKKALUOTSI_CONTACT_TO` (vahvistettu vastaanottaja).
- Ilman näitä endpoint vastaa HTTP 503 eikä väitä viestiä lähetetyksi. Onnistunut HTTP 202 merkitsee lähetyspalvelun hyväksyntää, ei todistettua inbox-toimitusta.
- Sama origin, syöterajat, vaaditut kentät, honeypot ja palvelinpuolen validointi. Lisäksi tuotantoon tarvitaan kestävä rate limit / bot-suojaus, palveluntarjoajan sopimus- ja tietosuojatarkistus sekä todellinen testiviesti.
- Julkisella sivulla säilytetään suora sähköpostiyhteydenotto varapolkuna.

## Portti 1 edelleen suljettu
1. Tarkista ALV-rekisterimerkintä YTJ:n ajantasaisesta hakutuloksesta.
2. Varmista Resend-lähettäjä, vastaanottaja, oikeus lähettää ja henkilötietojen käsittely.
3. Lisää palvelinmuuttujat vain hyväksyttyyn deployment-ympäristöön.
4. Toteuta pysyvä palvelinpuolen rate limit / CAPTCHA ja testaa onnistunut vastaanotto; varmista 4xx/5xx-virhetilat.
5. Varmista Vercel-projektin täsmällinen nimi, production SHA, domain, TLS ja linkit.
6. Tee viimeinen live-kanavien OG- ja LinkedIn-peittoaluetarkistus.
7. Älä mergeä äläkä julkaise ilman käyttäjän lopullista hyväksyntää.
