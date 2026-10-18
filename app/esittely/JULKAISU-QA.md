# Urakkaluotsi – julkaisuportti 19.10.2026

## Tilanne

**Ei vielä julkaisuhyväksytty.** Rakennus- ja tyyppitarkistukset läpäisevät; juridinen rekisteritieto sekä varsinainen laitetestaus puuttuvat.

| Tarkistus | Tulos | Huomio |
|---|---|---|
| Brändi, sisältö ja demo | Toteutettu | `/esittely`, hyväksytyt SVG-logot ja nelisivuinen PDF |
| Y-tunnus | Osittain valmis | Käyttäjän ilmoittama **3581581-6** lisätty sivulle; tarkistusnumero täsmää. YTJ-rekisterivastaavuutta ei erikseen varmennettu. |
| Yhteydenotto | Rajattu | Lomake avaa paikallisen sähköpostiluonnoksen; ei palvelinlähetystä eikä vahvistettua vastaanottoa. |
| Rekisteröidyn informointi | Luonnos | `/esittely/tietosuoja`; rekisterinpitäjän vahvistettava säilytys, käsittelijät ja siirrot. |
| Domain ja sähköposti | Väliaikainen | Ostettu `urakkaluotsi.fi` ja `.online`, ei käyttöönottoa; `visualjambo@gmail.com` käyttöön kunnes muuta sovitaan. |
| Next.js build / TS | PASS | `npm run build` 19.10.2026, molemmat julkiset reitit prerenderöity |
| HTML/CSS tarkistus | Osittainen | Responsiiviset säännöt 760/430 px; selaimen visuaalinen QA puuttuu |
| 375/390 px mobiili | EI TESTATTU | Tarkista vieritys, otsikkorivit, lomake, CTA ja PDF:n avautuminen laitteessa |
| 768 px tabletti | EI TESTATTU | Tarkista korttirivit, navigaatio ja lomake |
| 1440 px desktop | EI TESTATTU | Tarkista hero-kortti, PDF-linkki, lomake ja focus-järjestys |
| HTTP-avaukset | ESTYNYT | `next start` kaatuu ympäristön `uv_interface_addresses`-virheeseen, ei sovellusvirhettä osoittava tulos |
| Julkaisu / live-linkki | EI TEHTY | Odottaa hyväksyntäporttia |

## Käytännön hyväksymistesti

1. Avaa julkaistavan version esikatselu 375, 390, 768 ja 1440 px leveydellä. Ei vaakavieritystä, peittyvää CTA:ta eikä liian pieniä syöttökenttiä.
2. Testaa näppäimistöllä tabulaattorijärjestys ja näkyvä fokus. Kenttien labelit ja virhetilat ovat ymmärrettäviä.
3. Avaa esimerkkikooste linkistä: PDF sisältää neljä sivua ja avautuu uudelle välilehdelle.
4. Täytä pilottikysely ja klikkaa lähetystä: oma sähköpostiohjelma avaa luonnoksen; **vastaanotettu**-vahvistusta ei näytetä. Testaa myös mobiilissa ja ilman sähköpostiohjelman asetuksia (fallback-osoite).
5. Avaa footerin ja lomakkeen tietosuojalinkit ilman kirjautumista; varmista että sivulle pääsee takaisin.
6. Testaa valmiissa deployssa julkinen `/esittely`, tietosuojareitti ja PDF ilman käyttäjätunnusta. Pidä muu dashboard edelleen suojattuna.
7. Tarkista käyttäjän ilmoittaman Y-tunnuksen rekisterivastaavuus YTJ:ssä ja vahvista tietosuojatekstin todelliset käsittelijät ja säilytys, hyväksytä rekisterinpitäjällä.
8. Vasta tämän jälkeen tuotantoon ja kohdennettu savutesti tuotanto-URL:ssa.

## Päätös

- **GO**, kun YTJ-vastaavuus on varmennettu, tietosuojateksti kuvaa oikeaa käsittelyä ja laitetestit sekä julkiset reitit on läpäisty.
- **NO-GO** nykytilassa, vaikka build on vihreä.
