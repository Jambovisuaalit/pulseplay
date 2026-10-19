"""Render an *internal*, honest zero-GO delivery dry-run in Urakkaluotsi colours."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak

DEFAULT_SUMMARY = Path("data/validation/simulation_2026-10-19/summary.json")
DEFAULT_OUTPUT = Path("data/validation/simulation_2026-10-19/sisainen_toimituskooste.pdf")
NOTICE = "SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS"
INK, TXT, MUTED, TEAL, LINE = "#142732", "#263640", "#52636D", "#007F8B", "#D9E1E5"
PALE, WARN = "#F4F7F8", "#8A4B0F"


def render(summary_path: Path = DEFAULT_SUMMARY, output: Path = DEFAULT_OUTPUT, logo: Path | None = None) -> None:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    ai_round = data.get("simulation_round") == "AI_SILVER_SECOND_OFFLINE_DRY_RUN"
    pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    title = ParagraphStyle("title", fontName="DVB", fontSize=19, leading=26, textColor=colors.HexColor(INK), spaceAfter=14)
    heading = ParagraphStyle("heading", fontName="DVB", fontSize=12, leading=17, textColor=colors.HexColor(INK), spaceAfter=8)
    body = ParagraphStyle("body", fontName="DV", fontSize=9.4, leading=14.2, textColor=colors.HexColor(TXT), spaceAfter=9)
    small = ParagraphStyle("small", fontName="DV", fontSize=8.4, leading=12.2, textColor=colors.HexColor(MUTED), spaceAfter=7)
    warning = ParagraphStyle("warning", fontName="DVB", fontSize=10.5, leading=15, textColor=colors.HexColor(WARN), spaceAfter=9)

    def p(text: str, style=body):
        return Paragraph(html.escape(str(text)), style)

    def panel(label: str, message: str):
        box = Table([[[p(label, heading), p(message, body)]]], colWidths=[497])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(PALE)),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor(LINE)),
            ("LEFTPADDING", (0, 0), (-1, -1), 13),
            ("RIGHTPADDING", (0, 0), (-1, -1), 13),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return box

    def header_footer(c, doc):
        width, height = A4
        c.saveState()
        if logo and logo.exists():
            im = ImageReader(str(logo))
            iw, ih = im.getSize()
            c.drawImage(im, 43, 798, width=iw / ih * 24, height=24, mask="auto")
        else:
            c.setFont("DVB", 16)
            c.setFillColor(colors.HexColor(INK))
            c.drawString(43, 807, "Urakkaluotsi")
        c.setFont("DV", 8)
        c.setFillColor(colors.HexColor(MUTED))
        c.drawRightString(width - 43, 804, "AI-uusintasimulaatio" if ai_round else "Uusi offline-toimitussimulaatio")
        c.setStrokeColor(colors.HexColor(LINE))
        c.line(43, 790, width - 43, 790)
        c.setFont("DVB", 7.25)
        c.setFillColor(colors.HexColor(WARN))
        c.drawString(43, 776, NOTICE)
        c.line(43, 55, width - 43, 55)
        c.setFont("DV", 7.7)
        c.setFillColor(colors.HexColor(MUTED))
        c.drawString(43, 42, "Aineisto 19.10.2026 klo 03.12 (Europe/Helsinki) | EI tarjoussuositus")
        c.drawRightString(width - 43, 42, str(doc.page))
        c.restoreState()

    source = data["source_retrieved_at"]
    deadline = data["deadline_status_counts"]
    classes = data["heuristic_classes_not_gold"]
    stats = [
        (data["notices_checked"], "Ilmoitusta"),
        (deadline.get("OPEN", 0), "Määräaika avoin"),
        (deadline.get("EXPIRED", 0), "Päättynyt"),
        (data["verified_customer_recommendations"], "Vahvistettuja nostoja"),
    ]
    cells = [[p(str(value), ParagraphStyle(f"n{i}", parent=heading, fontSize=18, leading=23, textColor=colors.HexColor(TEAL))), p(label, small)] for i, (value, label) in enumerate(stats)]
    board = Table([cells], colWidths=[127] * 4)
    board.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(PALE)),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(LINE)),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor(LINE)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story = [
        p("Hankinnat päätöksenteon tueksi", title),
        p("Uudenmaan Korjausrakentajat Oy – kuvitteellinen 8 työntekijän korjaus- ja saneerausyritys."),
        p(f"Jäädytetty Hilma-hakumetadata {source}. Ei 30 päivän aktiivisen seurannan tulos.", small),
        Spacer(1, 8), board, Spacer(1, 19),
        p("Tuloksen tulkinta", heading),
        panel("0 vahvistettua tarjousehdotusta", "Automaattinen lähdehakujen seulonta tuotti alustavia saneerausaiheisia osumia, mutta liiteaineistoa, toteutuskelpoisuutta ja riippumatonta relevanssia ei ole vahvistettu."),
        Spacer(1, 16),
        p("Koneellinen ennakkoseulonta – EI vertailutotuus", heading),
        p(f"Alustavasti relevantteja {classes.get('Relevantti',0)}, ehdollisia {classes.get('Mahdollinen',0)} ja epärelevantteja {classes.get('Epärelevantti',0)}. Luokat perustuvat testattavaan avainsanapainotukseen; ne eivät osoita oikeaa osuvuutta."),
        p("100 ilmoituksen riippumaton luokitus: 0/100. Virallinen precision NOT MEASURED." if ai_round else
          "100 ilmoituksen riippumaton luokitus: 0/100. Precision, väärät positiiviset ja väärät negatiiviset ovat NOT MEASURED.", warning),
        p("Kaikkien ilmoitusten määräajat arvioitiin lähteen jäädytyshetkellä. 93:n määräaika oli silloin avoin ja seitsemän oli jo päättynyt. Määräaikojen lähdekenttiä ei ole tarkistettu täysistä tarjousasiakirjoista.", body),
        PageBreak(),
        p("Toimituksen QA ja ratkaisevat estot", title),
        panel("Määräaikojen turvaportti – PASS", "Päättyneitä määräaikoja ei ylennetä GO-suosituksiksi, vaikka alkuperäinen analyysi olisi myönteinen."),
        Spacer(1, 9),
        panel("Liitteiden ja kelpoisuuden turvaportti – PASS", "Varmistamattomat tarjousliitteet ja yrityksen todentamattomat kelpoisuustiedot estävät varman GO-päätöksen."),
        Spacer(1, 13),
        p("Ratkaisevat avoimet vaatimukset", heading),
        p("Hankintakohtaiset tarjousliitteet, ESPD, referenssit, liikevaihtorajat, vaaditut pätevyydet, kohdekohtaiset urakkakoot, toteutusalueet sekä kysymysten ja tarjousten täsmälliset ehdot ovat vahvistamatta."),
        p("Seuraavat toimenpiteet", heading),
        p("1. Riippumaton arvioija täyttää 100 ilmoituksen sokkoutetut vertailuluokat lähdeotteineen. 2. Aja precision-, FP- ja FN-laskenta uudelleen. 3. Tarkista mahdollisten asiakasnostojen alkuperäiset tarjousasiakirjat ja yrityksen tiedot. 4. Suorita tämän jälkeen uusi hyväksymisportti."),
        p("Lähteet ja rajaukset", heading),
        p("Jäädytetty Github Actions -aineisto: artefakti 12155822339, hilma_raw.json (100 ilmoitusta) ja keruuloki. Id-tason linkitys on toimitettu classified_notices.csv-taulukossa. Ei uusia Hilma-kutsuja, ei lähetyksiä, ei Vercel-julkaisua. Aineistossa ei ole täydellisiä tarjousliitteitä eikä se takaa markkinakattavuutta.", small),
        p("CONDITIONAL PASS – tekninen turvaportti toimii; ensimmäisen maksavan asiakkaan toimitusta EI hyväksytä.", warning),
    ]
    if ai_round:
        ai = data["ai_review_metrics"]
        counts = data["ai_review_label_counts"]
        story = [
            p("Hankinnat päätöksenteon tueksi", title),
            p("Uudenmaan Korjausrakentajat Oy – kuvitteellinen 8 työntekijän korjaus- ja saneerausyritys."),
            p(f"Jäädytetty Hilma-hakumetadata {source}. Yksi offline-testi, ei 30 päivän toteutunut seuranta.", small),
            Spacer(1, 8), board, Spacer(1, 18),
            p("AI-uusintasimulaation tulos", heading),
            panel("0 vahvistettua tarjousehdotusta", "Erillinen, sokkoutettu AI-lähdearvio osoittaa ennakkoseulonnan osuvuusongelman. Täysiä tarjousasiakirjoja ja yrityskelpoisuutta ei ole tarkistettu."),
            Spacer(1, 16),
            p("100 AI-silver-luokkaa – ei ihmisen gold", heading),
            p(f"Hakumetadatan AI-arvio: relevantti {counts.get('Relevantti',0)}, ehdollinen {counts.get('Mahdollinen',0)}, epärelevantti {counts.get('Epärelevantti',0)}, arvioimatta {counts.get('NOT_EVALUATED',0)}. Algoritmin ennusteita ei käytetty AI-luokkia kirjoitettaessa."),
            p("100 AI-luokittelua mutta 0 ulkoista gold-arviota. Virallinen vähintään 80 % precision: NOT MEASURED.", warning),
            p("Määräajat: 93 avoinna ja 7 päättynyt metadatahetkellä. Yksi ilmoitus on otsikon mukaan KESKEYTETTY tulevasta määräajasta huolimatta ja estetään turvaportissa. Ajantasaisuus vaatii alkuperäisen lähteen tarkistuksen."),
            PageBreak(),
            p("QA, osuvuus ja ratkaisevat estot", title),
            panel("Keskeytys, määräajat ja liitteet – PASS", "Otsikossa KESKEYTETTY tai PERUTTU estää GO-tilan. Päättyneet määräajat, puuttuvat tarjousliitteet ja vahvistamattomat asiakastiedot estävät myönteisen toimituspäätöksen."),
            Spacer(1, 16),
            p("AI-osuvuuden alustava mittaus", heading),
            p(f"Seulonta nosti relevantiksi 15 ilmoitusta. AI-vertailun ratkaistuissa luokissa: oikein nostettuja {ai['observed_tp']}, vääriä positiivisia {ai['observed_fp']} ja vääriä negatiivisia {ai['observed_fn']}. Epävarmuus huomioiden FP {ai['fp_range'][0]}–{ai['fp_range'][1]}, FN {ai['fn_range'][0]}–{ai['fn_range'][1]}; precisionin AI-väli {100*ai['precision_range'][0]:.1f}–{100*ai['precision_range'][1]:.1f} %. Ei tuotannon KPI."),
            p("Mahdollinen jatkoselvityskohde", heading),
            p("Hilma 59188 – Espoon Tietotie 1:n vuokralaismuutos. Pintaremontin lisäksi LVIS-muutoksia. Urakkakoko, tarjousliitteet, kelpoisuusehdot ja yrityksen kapasiteetti ovat avoimia. Lähdemetadatan deadline 4.11.2026 klo 10.00 UTC, joka pitää vahvistaa alkuperäisestä ilmoituksesta. Lisäksi seitsemän AI-ehdollista kohdetta; ei GO-suosituksia."),
            p("Seuraavat toimenpiteet", heading),
            p("Tarkista ID 59188:n ja ehdollisten ilmoitusten tarjousliitteet, kysymys- ja tarjousmääräajat, urakkalaajuus ja yrityksen todellinen kyvykkyys. Mittaa osuvuus myöhemmin ulkoisesti varmennetuilla vertailuluokilla. Älä lähetä tätä testikoostetta asiakkaalle."),
            p("Lähteet ja rajaukset", heading),
            p("Hilma-hakumetadata, snapshot_2026-10-19/hilma_raw.json; artefakti 12155822339. AI-luokat: ai_silver_labels.csv, lukittu hash ja lähdeotteet. Rivikohtainen jäljitys: classified_notices.csv. Ei live-Hilma-kutsuja, lähetyksiä tai Vercel-julkaisua.", small),
            p("CONDITIONAL PASS vain tekniselle turvaportille. Ensimmäisen maksavan asiakkaan toimitus EI HYVÄKSYTTY.", warning),
        ]
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=43, rightMargin=43,
                            topMargin=89, bottomMargin=72, title="Urakkaluotsi – sisäinen uusi toimitussimulaatio")
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--logo", type=Path)
    args = parser.parse_args()
    render(args.summary, args.output, args.logo)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
