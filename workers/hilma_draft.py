"""Local-only email drafts. Deliberately has no send transport or credentials."""
from __future__ import annotations
import hashlib
import json
from email.message import EmailMessage
from email import policy
from pathlib import Path
from hilma_http import HilmaError
from hilma_store import atomic_bytes,save_json


def build_draft(directory: Path, profile: dict, cards: list[dict], snapshot: str, *, send=False):
    if send:
        raise HilmaError('SEND_DISABLED: this workflow only writes local drafts')
    if len(cards)>3:
        raise HilmaError('digest cards: maximum 3')
    for c in cards:
        if not c.get('source_hash') or c.get('agent_source_review_complete') is not True:
            raise HilmaError('digest card: missing source or agent source review')
    body=[f"{profile['name']} - {len(cards)} hankintaa päätöksenteon tueksi",
          'Alustava kooste julkisen yritysprofiilin perusteella. Tilanne '+snapshot+'.',
          'Suositeltu käsittelyjärjestys perustuu seuraaviin määräaikoihin ja avoimiin esteisiin.','']
    for i,c in enumerate(cards,1):
        body += [f"{i}. {c.get('short_name',c['title'])}",
                 c['buyer']+' | tarjous '+c['deadline_helsinki'],
                 'Suositus: '+c.get('decision',c['next_action']),
                 'Peruste: '+c.get('priority_reason',c['summary']),
                 'Kaupallinen kuva: '+c.get('commercial',c['summary']),
                 'Ratkaiseva tarkistus: '+c.get('blocker',c['next_action']),
                 c['documents_url'],'']
    body += ['Seuraava päätös: mitkä kohteet otetaan asiakirja- ja kyvykkyystarkistukseen?',
             'Yksityiskohdat ja lähdeotteet erillisessä toimitusluonnoksessa. Profiili ja tarjouskelpoisuus vahvistamatta; ulkoisia tarjousliitteitä ei ole luettu.',
             'TenderPulse | toimitusluonnos, ei lähetetty']
    text='\n'.join(body)+'\n'
    fingerprint=hashlib.sha256(json.dumps({'profile':profile,'cards':cards,'snapshot':snapshot},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    state_path=directory/'draft-state.json'
    old=json.loads(state_path.read_text()) if state_path.exists() else {}
    unchanged=old.get('fingerprint')==fingerprint
    msg=EmailMessage(policy=policy.SMTP)
    msg['Subject']=f'TenderPulse: {len(cards)} tarkistettavaa hankintaa - toimitusluonnos'
    # No To/From/Date: this file must not become an accidentally addressed email.
    msg['X-TenderPulse-Mode']='DRY_RUN'
    msg['Message-ID']=f'<{fingerprint}@tenderpulse.invalid>'
    msg.set_content(text)
    atomic_bytes(directory/'kooste.eml',msg.as_bytes())
    atomic_bytes(directory/'kooste.txt',text.encode('utf-8'))
    save_json(state_path,{'fingerprint':fingerprint,'status':'DRAFT_NOT_SENT','recipient':None,'send_enabled':False})
    return {'drafts':1,'unchanged':unchanged,'sent':0,'recipient':None,'fingerprint':fingerprint}
