"use client";

export default function PilotForm() {
  return <form className="ul-form" onSubmit={(event) => { event.preventDefault(); }} aria-labelledby="form-title">
    <span className="ul-form-tag">PILOTTIKESKUSTELU</span><h3 id="form-title">Selvitetään, sopiiko pilotti yrityksellesi.</h3>
    <p>Kerro lyhyesti, millaisia töitä teette ja millä alueella toimitte.</p>
    <div className="ul-form-grid"><label>Yritys<input name="company" autoComplete="organization" required placeholder="Yrityksen nimi" /></label><label>Nimi<input name="name" autoComplete="name" required placeholder="Etunimi Sukunimi" /></label></div>
    <label>Työsähköposti<input name="email" type="email" autoComplete="email" required placeholder="nimi@yritys.fi" /></label>
    <label>Toiminta-alue<input name="region" required placeholder="Esim. Uusimaa" /></label>
    <label>Millaisia urakoita etsitte?<textarea name="work" required rows={3} placeholder="Kerro palveluistanne ja kiinnostavista urakoista" /></label>
    <button className="ul-btn" type="submit" disabled title="Vastaanottavaa sähköpostia tai käsittelijää ei ole vahvistettu">Lähetä pilottihakemus ↗</button>
    <p className="ul-form-info" role="status">Lähetys ei ole vielä käytössä. Yhteystiedot ja tietosuojatiedot vahvistetaan ennen julkaisua.</p>
  </form>;
}
