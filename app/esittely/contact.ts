export const PILOT_EMAIL = "visualjambo@gmail.com";
export const contactFields = [
  { name: "company", label: "Yritys", max: 100, autoComplete: "organization", placeholder: "Yrityksen nimi" },
  { name: "name", label: "Nimi", max: 100, autoComplete: "name", placeholder: "Etunimi Sukunimi" },
  { name: "email", label: "Työsähköposti", max: 150, autoComplete: "email", placeholder: "nimi@yritys.fi" },
  { name: "region", label: "Toiminta-alue", max: 100, autoComplete: "off", placeholder: "Esim. Uusimaa" },
  { name: "work", label: "Millaisia urakoita etsitte?", max: 600, autoComplete: "off", placeholder: "Kerro palveluistanne ja kiinnostavista urakoista" },
] as const;
export type FieldName = (typeof contactFields)[number]["name"];
export type ContactValues = Record<FieldName, string>;
export type ContactErrors = Partial<Record<FieldName, string>>;

export function validateContact(data: FormData): { values: ContactValues; errors: ContactErrors } {
  const values = {} as ContactValues;
  const errors: ContactErrors = {};
  for (const field of contactFields) {
    const raw = data.get(field.name);
    values[field.name] = typeof raw === "string" ? raw.trim() : "";
    if (!values[field.name]) errors[field.name] = `Täytä kenttä: ${field.label}.`;
    else if (values[field.name].length > field.max) errors[field.name] = `Enintään ${field.max} merkkiä.`;
    else if (field.name !== "work" && /[\r\n]/.test(values[field.name])) errors[field.name] = "Kirjoita tieto yhdelle riville.";
  }
  if (!errors.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = "Kirjoita sähköpostiosoite muodossa nimi@yritys.fi.";
  }
  return { values, errors };
}

export function createContactDraft(values: ContactValues) {
  const subject = `Urakkaluotsi – pilottihakemus: ${values.company}`;
  const body = ["Hei,", "", "Olemme kiinnostuneita Urakkaluotsin 30 päivän pilotista.", "",
    ...contactFields.map(field => `${field.label}: ${values[field.name]}`), "",
    "Pyydämme yhteydenottoa pilotin soveltuvuuden, sisällön ja hinnan sopimiseksi.",
  ].join("\n");
  return { subject, body, url: `mailto:${PILOT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}` };
}
