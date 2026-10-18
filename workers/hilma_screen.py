"""Conservative metadata triage, not customer relevance or ground truth."""
from __future__ import annotations
import datetime as dt
import re
from hilma_http import HilmaError

RULE_VERSION = 'es-triage-v1.1'
CONSULT = r'suunnittel|valvonta|rakennuttajakonsult|konsulttipalvel|asiantuntijapalvel|energiatodistu|sisäilmatutkim|lupapäätö|maastokartoit|merenmittau'
SPECIAL = r'purku-urakka|kokonaispurk|rakennusten purku|rakennuksen purku|\brakentaminen\b|uudisrakenn|kvr-urakka|sr-urakka|sähköurakka|lvi.?urakka|hiss|nostolait|automaatio|sprinkler|paloilmoit|lämpötekn|sähkönsyöttö|ilmanvaihtojärjestelmien'


def screen(item: dict, profile: dict, now: dt.datetime) -> dict:
    for field in ('noticeId','titleFi','datePublished','expirationDate','nutsCodes','cpvCodes','mainType'):
        if field not in item:
            raise HilmaError(f'screen {field}: missing')
    if not isinstance(item['nutsCodes'], str) or not isinstance(item['cpvCodes'],str):
        raise HilmaError('screen nutsCodes/cpvCodes: expected strings')
    if item['titleFi'] is not None and not isinstance(item['titleFi'],str):
        raise HilmaError('screen titleFi: expected string or null')
    title = item['titleFi'] or ''
    reasons=[]
    state='REVIEW_REQUIRED'
    deadline=item['expirationDate']
    days=None
    if deadline is not None:
        try:
            end=dt.datetime.fromisoformat(deadline.replace('Z','+00:00'))
            if end.tzinfo is None:raise ValueError()
            days=(end-now).total_seconds()/86400
        except (ValueError,AttributeError,TypeError):
            raise HilmaError('screen expirationDate: invalid timezone timestamp') from None
    regions=item['nutsCodes'].split()
    if days is not None and days <= 0:
        state='EXCLUDED_DEADLINE';reasons=['Tarjousmääräaika on päättynyt.']
    elif re.search(r'keskeytetty|peruutettu',title,re.I):
        state='EXCLUDED_CANCELLED_SIGNAL';reasons=['Otsikossa keskeytys-/peruutussignaali.']
    elif regions and not set(regions)&set(profile['allowed_regions']) and 'FI' not in regions:
        state='EXCLUDED_REGION';reasons=['NUTS-alue on tämän Uusimaa-koeajon rajauksen ulkopuolella.']
    elif re.search(CONSULT,title,re.I):
        state='EXCLUDED_SERVICE_POLICY';reasons=['Otsikon suunnittelu-/asiantuntijapalvelu rajattu koeajon rakennusurakoinnin ulkopuolelle.']
    elif re.search(SPECIAL,title,re.I):
        state='EXCLUDED_SERVICE_POLICY';reasons=['Otsikon erikois-, purku- tai uudisurakka ei kuulu tämän koeajon palvelurajaukseen; ei väite yrityksen kyvyttömyydestä.']
    elif any(term in title.casefold() for term in profile['service_terms']):
        state='CANDIDATE';reasons=['Otsikossa alustavan korjausrakentamisprofiilin palvelutermi; sisältö ja kelpoisuus tarkistettava.']
    else:
        reasons=['Otsikko ei riitä palvelusopivuuden ratkaisemiseen; sisältötarkistus tai lisätieto tarvitaan.']
    if not set(regions)&set(profile['allowed_regions']) and state in ['CANDIDATE','REVIEW_REQUIRED']:
        reasons.append('Toteutusalue on tarkistettava; valtakunnallinen/puuttuva NUTS ei osoita Uusimaa-sopivuutta.')
    if days is not None and 0 < days < 10:reasons.append('Tarjousaikaa alle 10 päivää.')
    return {'notice_id':str(item['noticeId']),'title':title,'state':state,'reasons':reasons,
            'days_to_deadline':None if days is None else round(days,3),'rule_version':RULE_VERSION,
            'relevance':None,'win_probability_estimate':None,'client_profile_confirmed':False}
