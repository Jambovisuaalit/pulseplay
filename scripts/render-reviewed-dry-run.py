"""Render a reviewed internal digest; no network calls, credentials or sending."""
import hashlib
import html
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/internal-dry-run-2026-10-20'
data = json.loads((OUT / 'review.json').read_text())
assert data['mode'] == 'INTERNAL_TEST_NOT_CUSTOMER_DELIVERY'
assert data['verified_bid_recommendations'] == 0 and not data['sent_to_customer']
assert len({i['id'] for i in data['items']}) == len(data['items'])
for i in data['items']:
    assert i['source_url'].startswith('https://tarjouspalvelu.fi/')
    assert i['contract_value_eur'] is None and not i['eligibility_verified']
    for k in ['source_fact', 'assessment', 'missing', 'next_action']:
        assert i[k].strip()
    for k in ['tender_deadline', 'question_deadline']:
        assert datetime.fromisoformat(i[k]).tzinfo is not None

pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
ink, teal, muted = map(colors.HexColor, ['#142732', '#007F8B', '#52636D'])
styles = {
    'title': ParagraphStyle('title', fontName='DVB', fontSize=23, leading=29, textColor=ink, spaceAfter=20),
    'heading': ParagraphStyle('heading', fontName='DVB', fontSize=11, leading=16, textColor=teal, spaceBefore=13, spaceAfter=5),
    'body': ParagraphStyle('body', fontName='DV', fontSize=10, leading=15, textColor=ink, spaceAfter=8),
    'small': ParagraphStyle('small', fontName='DV', fontSize=8, leading=12, textColor=muted, spaceAfter=7),
}
story = []
plain = []
def add(s, kind='body'):
    story.append(Paragraph(html.escape(s), styles[kind])); plain.append(s)
def stamp(value):
    return datetime.fromisoformat(value).astimezone(ZoneInfo('Europe/Helsinki')).strftime('%d.%m.%Y klo %H.%M')

add('Urakkaluotsi', 'small')
add('Yksi seuraava tarkistus. Kolme arvioitua kohdetta.', 'title')
add('SISÄINEN TESTI - KUVITTEELLINEN YRITYS - EI ASIAKASTOIMITUS', 'heading')
add('Lähteiden julkiset tarjousportaalinäkymät tarkistettu 20.10.2026. Täysiä tarjousasiakirjoja tai yrityksen tarjouskelpoisuutta ei vahvistettu.')
add('Testiprofiili', 'heading')
add(data['profile']['name'])
add('Palvelut: ' + ', '.join(data['profile']['services']) + '. Alue: ' + ', '.join(data['profile']['municipalities']) + '.')
add('Tavoiteltu yksittäinen urakka 10 000-250 000 euroa on testiolettama. Liikevaihto, referenssit, vakuudet, kapasiteetti ja LVIS-kumppanit ovat vahvistamatta.')
add('Päätös tähän toimituskertaan', 'heading')
add('1 ensisijainen asiakirjatarkistus (Tietotie), 1 toissijainen tarkistus (Dynamicum), 1 odottava kohde (Kastevuori). Vahvistettuja tarjoussuosituksia: 0.')
add('Tee ensin: tarkista Tietotien urakkaohjelma ja kokonaisurakan LVIS-vastuut ennen 26.10. klo 12 kysymysrajaa. Älä käytä aikaa Kastevuoren laskentaan ennen käyntiehdon ratkeamista.')
add('Rajaus', 'heading')
add('Kolme tarkoituksella valittua kohdetta aiemmasta aineistosta. Tämä ei ole kaikkien avoimien hankintojen seuranta, riippumaton osuvuustesti tai osoitus palvelun 30 päivän toimituskyvystä.')
for item in data['items']:
    story.append(PageBreak())
    add('SISÄINEN TESTI / HILMA ' + item['id'], 'small')
    add(item['title'], 'title')
    add('Lähteessä todettu', 'heading'); add(item['source_fact'])
    add('Urakkaluotsin alustava arvio', 'heading'); add(item['assessment'])
    add('Puuttuva tai tarkistamaton tieto', 'heading'); add(item['missing'])
    add('Milloin pitää toimia?', 'heading')
    add('Tarjous: ' + stamp(item['tender_deadline']) + '. Kysymykset: ' + stamp(item['question_deadline']) + '. Ajat Suomen paikallisaikaa.')
    add('Seuraava konkreettinen askel', 'heading'); add(item['next_action'])
    add('Alkuperäislähde / portaalin tunniste ' + item['portal_id'], 'heading')
    story.append(Paragraph('<link href="'+item['source_url']+'" color="#007F8B">Avaa alkuperäinen tarjousportaalinäkymä</link>', styles['body']))
    add(item['source_url'], 'small')
    add('Alustava päätöstuki. Ei tarjouskelpoisuuden vahvistus, tarjouslaskenta tai urakkavoittolupaus.', 'small')

def footer(c, doc):
    c.setStrokeColor(colors.HexColor('#D9E1E5')); c.line(44, 43, 551, 43)
    c.setFont('DV', 8); c.setFillColor(muted)
    c.drawString(44, 29, 'Urakkaluotsi / sisäinen testi / 20.10.2026')
    c.drawRightString(551, 29, str(doc.page))

SimpleDocTemplate(str(OUT/'sisainen-testikooste.pdf'), pagesize=A4, topMargin=45, bottomMargin=60, leftMargin=44, rightMargin=44).build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'sahkopostiluonnos.txt').write_text('SISÄINEN LUONNOS - EI LÄHETETTY\n\nAihe: Urakkaluotsi: Tietotien asiakirjat ensin tarkistukseen\n\nTällä rajatulla tarkistuskerralla löytyi yksi ensisijainen jatkoselvitys. Tietotien tilamuutoksen alue ja osa työstä sopivat testiprofiiliin, mutta kokonaisurakan LVIS-vastuut, urakkakoko ja kelpoisuus ovat avoinna. Kysymysraja on 26.10. klo 12.\n\nKastevuori odottaa pakollisen kohdekäynnin selvitystä. Dynamicum jää toissijaiseksi lyhyen aikataulun vuoksi. Vahvistettuja tarjoussuosituksia ei ole. Katso lähteet ja tarkat seuraavat toimet liitteen koosteesta.\n\nTämä on kuvitteellisen yrityksen sisäinen testi, ei asiakasviesti.\n')
(OUT/'qa.json').write_text(json.dumps({'status':'PASS_INTERNAL_REVIEW_ONLY','pages_expected':4,'review_json_sha256':hashlib.sha256((OUT/'review.json').read_bytes()).hexdigest(),'items':len(data['items']),'verified_bid_recommendations':0,'sent':False},indent=2)+'\n')
print('Created internal PDF, email draft and QA record; no messages sent.')
