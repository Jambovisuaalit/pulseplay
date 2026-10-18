"use client";

import { useState } from "react";

const PILOT_EMAIL = "visualjambo@gmail.com";

export default function PilotForm() {
  const [draftOpened, setDraftOpened] = useState(false);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const field = (name: string) => String(data.get(name) ?? "").trim();
    const subject = `Urakkaluotsi – pilottihakemus: ${field("company")}`;
    const body = [
      "Hei,",
      "",
      "Olemme kiinnostuneita Urakkaluotsin 30 päivän pilotista.",
      "",
      `Yritys: ${field("company")}`,
      `Yhteyshenkilö: ${field("name")}`,
      `Työsähköposti: ${field("email")}`,
      `Toiminta-alue: ${field("region")}`,
      `Kiinnostavat urakat: ${field("work")}`,
      "",
      "Pyydämme yhteydenottoa pilotin soveltuvuuden, sisällön ja hinnan sopimiseksi.",
    ].join("\n");
    setDraftOpened(true);
    window.location.href = `mailto:${PILOT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  }

  return <form className="ul-form" onSubmit={handleSubmit} aria-labelledby="form-title">
    <span className="ul-form-tag">PILOTTIKESKUSTELU</span><h3 id="form-title">Selvitetään, sopiiko pilotti yrityksellesi.</h3>
    <p>Kerro lyhyesti, millaisia töitä teette ja millä alueella toimitte.</p>
    <div className="ul-form-grid"><label>Yritys<input name="company" autoComplete="organization" required maxLength={100} placeholder="Yrityksen nimi" /></label><label>Nimi<input name="name" autoComplete="name" required maxLength={100} placeholder="Etunimi Sukunimi" /></label></div>
    <label>Työsähköposti<input name="email" type="email" autoComplete="email" required maxLength={150} placeholder="nimi@yritys.fi" /></label>
    <label>Toiminta-alue<input name="region" required maxLength={100} placeholder="Esim. Uusimaa" /></label>
    <label>Millaisia urakoita etsitte?<textarea name="work" required rows={3} maxLength={600} placeholder="Kerro palveluistanne ja kiinnostavista urakoista" /></label>
    <button className="ul-btn" type="submit">Avaa hakemus sähköpostiin ↗</button>
    <p className="ul-privacy-inline">Tietojasi käytetään pilottiyhteydenoton käsittelyyn. Lue <a href="/esittely/tietosuoja">tietosuojatiedot</a> ennen viestin lähettämistä.</p>
    <p className="ul-form-info" role="status">{draftOpened ? "Sähköpostiluonnos pyydettiin avattavaksi. Varmista, että sähköpostisovellus avautui, ja lähetä viesti itse. Hakemusta ei ole vielä vahvistettu vastaanotetuksi." : "Painike avaa valmiin viestin omassa sähköpostisovelluksessasi. Tarkista ja lähetä viesti itse. Tietoja ei tallenneta tälle sivustolle."}</p>
    <p className="ul-contact-fallback">Jos sähköpostisovellus ei avaudu, kirjoita osoitteeseen <a href={`mailto:${PILOT_EMAIL}`}>{PILOT_EMAIL}</a>.</p>
  </form>;
}
