"use client";

import { useState } from "react";
import { contactFields, createContactDraft, PILOT_EMAIL, validateContact, type ContactErrors } from "./contact";

export default function PilotForm() {
  const [errors, setErrors] = useState<ContactErrors>({});
  const [draft, setDraft] = useState<ReturnType<typeof createContactDraft> | null>(null);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const result = validateContact(new FormData(form));
    setErrors(result.errors);
    if (Object.keys(result.errors).length) {
      setDraft(null);
      const firstInvalid = contactFields.find(field => result.errors[field.name]);
      if (firstInvalid) form.querySelector<HTMLElement>(`[name="${firstInvalid.name}"]`)?.focus();
      return;
    }
    const nextDraft = createContactDraft(result.values);
    setDraft(nextDraft);
    window.location.href = nextDraft.url;
  }

  return <form className="ul-form" onSubmit={handleSubmit} noValidate method="post" aria-labelledby="form-title">
    <span className="ul-form-tag">PILOTTIKESKUSTELU</span><h3 id="form-title">Selvitetään, sopiiko pilotti yrityksellesi.</h3>
    <p>Kerro lyhyesti, millaisia töitä teette ja millä alueella toimitte. Kaikki kentät ovat pakollisia. Älä kirjoita arkaluonteisia henkilötietoja.</p>
    <noscript><p>Hakemuslomake tarvitsee JavaScriptin. Voit lähettää yhteydenoton suoraan osoitteeseen <a href={`mailto:${PILOT_EMAIL}`}>{PILOT_EMAIL}</a>.</p><style>{".ul-form-fields{display:none}"}</style></noscript>
    <div className="ul-form-fields">
      {Object.keys(errors).length > 0 ? <p className="ul-error-summary" role="alert">Tarkista merkityt kentät. Sähköpostiluonnosta ei avattu.</p> : null}
      <div className="ul-form-grid">
        {contactFields.map(field => {
          const id = `pilot-${field.name}`;
          const props = { id, name: field.name, required: true, maxLength: field.max, autoComplete: field.autoComplete, placeholder: field.placeholder,
            "aria-invalid": Boolean(errors[field.name]), "aria-describedby": errors[field.name] ? `${id}-error` : undefined,
            onChange: () => { setDraft(null); setErrors(current => ({ ...current, [field.name]: undefined })); },
          };
          return <div className={field.name === "company" || field.name === "name" ? "ul-field" : "ul-field ul-field-wide"} key={field.name}>
            <label htmlFor={id}>{field.label}</label>
            {field.name === "work" ? <textarea {...props} rows={3} /> : <input {...props} type={field.name === "email" ? "email" : "text"} />}
            {errors[field.name] ? <p className="ul-field-error" id={`${id}-error`}>{errors[field.name]}</p> : null}
          </div>;
        })}
      </div>
      <p className="ul-privacy-inline">Tietojasi käytetään pilottiyhteydenoton käsittelyyn. Lue <a href="/esittely/tietosuoja">tietosuojaseloste</a> ennen viestin lähettämistä.</p>
      <button className="ul-btn" type="submit">Avaa hakemus sähköpostiin ↗</button>
      <p className="ul-form-info" role="status">{draft ? "Sähköpostiluonnos pyydettiin avattavaksi. Tarkista luonnos ja lähetä viesti itse. Hakemusta ei ole vahvistettu vastaanotetuksi." : "Painike avaa valmiin viestin omassa sähköpostisovelluksessasi. Tarkista ja lähetä viesti itse. Sivusto ei vastaanota lomaketietoja."}</p>
      {draft ? <details className="ul-draft-fallback" open><summary>Eikö sähköpostisovellus avautunut?</summary>
        <p>Kopioi alla oleva viesti omaan sähköpostiisi. Vastaanottaja: <a href={`mailto:${PILOT_EMAIL}`}>{PILOT_EMAIL}</a></p>
        <label htmlFor="pilot-draft">Aihe ja viesti</label><textarea id="pilot-draft" readOnly rows={12} value={`Aihe: ${draft.subject}\n\n${draft.body}`} onFocus={event => event.currentTarget.select()} />
      </details> : null}
    </div>
    <p className="ul-contact-fallback">Voit myös kirjoittaa suoraan: <a href={`mailto:${PILOT_EMAIL}`}>{PILOT_EMAIL}</a>.</p>
  </form>;
}
