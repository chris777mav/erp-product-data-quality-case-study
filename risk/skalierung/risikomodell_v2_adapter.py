#!/usr/bin/env python3
"""RISK-PILOT-1.1 V2 data adapter; no modified signal scores or priority rules.

Run: python risikoanalyse_pilot.py --db path/to/Portfolio_Phase4_Rohdaten.sqlite --sql-dir path/to/sql --out path/to/output
Scores are declared editorial prioritisation assumptions, NOT empirical loss probabilities.
"""
import argparse,csv,sqlite3,hashlib,json,collections
from pathlib import Path

LEVELS = {'P1':'Sofortige fachliche Prüfung','P2':'Zeitnah prüfen / klären','P3':'Geplant verifizieren / dokumentieren','P4':'Kontrolliert / kein aktuelles Signal'}
# Impact scale is a documented qualitative triage model; not an observed loss severity.
SIGNALS = {
 'MIGRATION_TARGET_MISSING':(5,'Migrationspflichtige Zielidentität fehlt'),
 'MIGRATION_IDENTITY_MISMATCH':(5,'Zielidentität widersprüchlich'),
 'DIMENSION_MISMATCH':(4,'Länge weicht von zulässiger Umrechnung ab'),
 'MAPPING_NONCOMPLIANT':(4,'Mapping-Regelversion / Genehmigung / Zeitgültigkeit unzulässig'),
 'PACKAGING_BLOCK':(4,'ASN-Packversion / Menge fachlich nicht freigabefähig'),
 'PACKAGING_REVIEW':(3,'Verpackungsänderung benötigt fachliche Nachprüfung'),
 'RECEIPT_HOLD':(4,'Dokumentierter Wareneingang auf HOLD'),
 'RECEIPT_MISSING':(3,'Für eine ASN-Position kein Receipt im Datenabzug'),
 'RECEIPT_DISCREPANCY':(3,'ASN-Receipt Abweichung mit Klärungsbedarf'),
 'WMS_REFERENCE_MISSING':(4,'WMS-Zieleintrag im Snapshot fehlt'),
 'SUPPLIER_EVIDENCE_UNCONFIRMED':(3,'Lieferanten-/Maßnachweis unbestätigt'),
 'DOCUMENTED_LAUNCH_HOLD':(1,'Dokumentierte geplante Einführungssperre; kein DQ-Fehler'),
 'DOCUMENTED_DISCONTINUATION':(1,'Dokumentiert ausgelisteter Artikel; kein DQ-Fehler'),
 'PACKAGING_RELEASE_REVIEW':(3,'Registrierte Prozessentscheidung REVIEW'),
 'INCIDENT_UNRESOLVED':(2,'Offener registrierter Fall ohne geklärte Folgemaßnahme'),
}
SPECIAL_ACTIONS={
 'MIGRATION_TARGET_MISSING':'Migration-Scope, Event-Logs, Target-Snapshots und Identitätsmapping abgleichen; Nachladeversuch nur kontrolliert.',
 'MIGRATION_IDENTITY_MISMATCH':'Quell-/Zielidentitäten, Fremdschlüssel und Zuordnungsversion rückverfolgen; Dubletten prüfen.',
 'DIMENSION_MISMATCH':'Einheit, Regelversion, genehmigten Faktor und Quell-/Zielwert abgleichen; Test-Sandbox und Folgesystem-Retest.',
 'MAPPING_NONCOMPLIANT':'Angewendete Mapping-Version, Genehmigung und Laufzeit historisch verifizieren.',
 'PACKAGING_BLOCK':'Wareneingang vor Freigabe mit gültiger Packversion und genehmigtem Lieferantenbeleg klären.',
 'PACKAGING_REVIEW':'Änderungsfreigabe zeitlich gegen Bestellung und ASN prüfen; fachliche Entscheidung protokollieren.',
 'RECEIPT_HOLD':'HOLD-Grund und geblockte Bestände prüfen; keine physische Fehlmenge aus Status ableiten.',
 'RECEIPT_MISSING':'Zusätzliche Receipt-/Transportbelege anfordern; vorläufig offen statt Nichtlieferung unterstellen.',
 'RECEIPT_DISCREPANCY':'Mengen/Status pro ASN-Position gegen WMS und Einkauf abstimmen.',
 'WMS_REFERENCE_MISSING':'Interface- und WMS-Logs korrelieren; vorhandene und fehlende Events separat behandeln.',
 'SUPPLIER_EVIDENCE_UNCONFIRMED':'Referenzbestätigung beim Lieferanten oder MDM anfordern.',
 'DOCUMENTED_LAUNCH_HOLD':'Geplanten Launch-HOLD mit Termin und Freigabeeigner bestätigen; nicht als DQ-Fehler klassifizieren.',
 'DOCUMENTED_DISCONTINUATION':'Auslistungsentscheidung dokumentiert belassen; nicht nachmigrieren.',
 'PACKAGING_RELEASE_REVIEW':'Fachlichen REVIEW-Status nur mit dokumentierten Nachweisen in ALLOW umwandeln.',
 'INCIDENT_UNRESOLVED':'Fallprotokoll aktualisieren: Beobachtung, Nachweis, Hypothese, Eigentümer, Entscheidung und Retest getrennt.',
}
CASE_CONTEXT = {
 'INC-001':('Migrationspflicht ohne sichtbaren Zielartikel','Ereignis im Abzug fehlt; unbekannte technische Ursache.','Migration / MDM'),
 'INC-002':('Falsche Länge und nicht genehmigte Mapping-Version','Historisches V1 weiterhin OPEN; separate Sandbox beweist Korrekturzyklus.','MDM / ERP / WMS'),
 'INC-003':('ASN-0007 unbekannte Packversion trotz Mengengleichheit','Keine passende Änderungsfreigabe; Receipt auf HOLD.','Einkauf / Lieferant / WMS'),
 'INC-004':('ASN-0008 geänderte Packversion mit Freigabe','Verpackungsänderung genehmigt, DQ04 weiterhin REVIEW wegen Zeitkontext Bestellung.','Einkauf / MDM'),
 'INC-005':('Zweite ASN-Position ohne Receipt-Nachweis','Kein Nachweis einer physischen Nichtlieferung.','Einkauf / WMS'),
 'INC-006':('Gebuchter Empfang auf HOLD','Geblockter Bestand: keine automatische physische Fehlmenge.','WMS / Logistik'),
 'INC-007':('WMS-Zieleintrag und Schnittstellenereignis fehlen','Kein eingereichtes Ereignis im Abzug: Ursache nicht identifizierbar.','ERP-Support / Integration'),
 'INC-008':('WMS-Zieleintrag fehlt, Ereignis protokolliert','Nicht mit INC-007 gleichsetzen: Protokoll vorhanden.','ERP-Support / WMS'),
 'INC-009':('Lieferantenreferenz / Maßnachweis nicht bestätigt','Keine bestätigte technische Fehltransformation.','MDM / Lieferant'),
 'INC-010':('Artikel vor geplanter Produkteinführung gesperrt','Beschaffungs-BLOCK ist planmäßig; kein nachgewiesener DQ-Defekt.','Produktmanagement / Einkauf'),
 'INC-011':('Einführung mit unbestätigter Verpackungsreferenz','REVIEW ist dokumentiert; kein automatisches Freigabeversagen.','Produktmanagement / MDM'),
}

def outcsv(path,rows,cols):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',delimiter=';');w.writeheader();w.writerows(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--db',required=True);ap.add_argument('--sql-dir',required=True);ap.add_argument('--out',required=True); args=ap.parse_args()
 db=Path(args.db).resolve(); sql=Path(args.sql_dir); out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 hash_before=hashlib.sha256(db.read_bytes()).hexdigest()
 c=sqlite3.connect(f'file:{db}?mode=ro',uri=True);c.row_factory=sqlite3.Row
 def rows(q,params=()):return [dict(x) for x in c.execute(q,params).fetchall()]
 def dq(i):
  f=list(sql.glob(f'DQ{i:02d}_*.sql'));assert len(f)==1,(i,f)
  return rows(f[0].read_text(encoding='utf-8'))
 dqs={i:dq(i) for i in range(1,8)}
 products=rows('SELECT sku,product_group,description,origin_type,lifecycle_status FROM products ORDER BY sku')
 incidents=rows('SELECT * FROM reported_cases ORDER BY case_id')
 asns=rows('SELECT asn_id,po_id,sku FROM asns')
 pos=rows('SELECT po_id,sku FROM purchase_orders')
 receipts=rows('SELECT receipt_id,asn_id,po_id FROM receipts')
 ev=rows('SELECT case_id,evidence_id,evidence_availability,source_table,observation FROM issue_evidence')
 wms_by_sku=collections.defaultdict(list)
 for record in rows('SELECT * FROM wms_snapshot'): wms_by_sku[record['sku']].append(record)
 supplier_by_sku=collections.defaultdict(list)
 for record in rows('SELECT * FROM supplier_references'): supplier_by_sku[record['sku']].append(record)
 po_sku={r['po_id']:r['sku'] for r in pos};asn_sku={r['asn_id']:r['sku'] for r in asns};rec_sku={r['receipt_id']:po_sku.get(r['po_id']) or asn_sku.get(r['asn_id']) for r in receipts}
 def infer_sku(ref):
  if ref.startswith('HYG-'):return ref
  if ref.startswith('PO-'):return po_sku.get(ref)
  if ref.startswith('REC-'):return rec_sku.get(ref)
  return None
 ci_by_sku=collections.defaultdict(list)
 for t in incidents:
  t['sku']=infer_sku(t['affected_reference']);assert t['sku'] is not None, t
  ci_by_sku[t['sku']].append(t)
 by_sku={i:collections.defaultdict(list) for i in dqs}
 for i in (1,2,3,4,5,6):
  for r in dqs[i]:by_sku[i][r['sku']].append(r)
 v=[]
 valid_dq3={'version_check':'PASS','approval_check':'APPROVED','validity_check':'EFFECTIVE_AT_SENT_TIME'}
 for p in products:
  sku=p['sku']; signals=[];refs=[];dqstates=[]
  def push(s):
   if s not in signals:signals.append(s)
  for i in range(1,7):
   sub=by_sku[i][sku]
   if sub: dqstates.append('DQ%02d:'%i + ','.join(r.get(f'dq{i:02d}_status', r.get('version_check','')) for r in sub))
  for r in by_sku[1][sku]:
   if r['dq01_status']=='MISSING_TARGET':push('MIGRATION_TARGET_MISSING')
   elif r['dq01_status'] in ('IDENTITY_MISMATCH','DUPLICATE_TARGET'):push('MIGRATION_IDENTITY_MISMATCH')
  for r in by_sku[2][sku]:
   if r['dq02_status']=='DIMENSION_MISMATCH':push('DIMENSION_MISMATCH')
  for r in by_sku[3][sku]:
   if r['version_check'] not in ('PASS','NO_EVENT') or r['approval_check'] not in ('APPROVED','NO_EVENT') or r['validity_check'] not in ('EFFECTIVE_AT_SENT_TIME','NO_EVENT') or r['factor_check'] not in ('PASS','NOT_APPLICABLE','NO_EVENT'):
    push('MAPPING_NONCOMPLIANT')
  for r in by_sku[4][sku]:
   if r['dq04_status']=='BLOCK':push('PACKAGING_BLOCK')
   if r['dq04_status']=='REVIEW':push('PACKAGING_REVIEW')
  for r in by_sku[5][sku]:
   if r['dq05_status']=='RECEIPT_ON_HOLD':push('RECEIPT_HOLD')
   if r['dq05_status']=='MISSING_RECEIPT':push('RECEIPT_MISSING')
   if r['dq05_status'] in ('EXCESS_RECORDED','PARTIALLY_RECORDED','INVALID_QUANTITY','STATUS_REVIEW','NOT_EVALUABLE'):push('RECEIPT_DISCREPANCY')
  for r in by_sku[6][sku]:
   if r['dq06_status']=='DOCUMENTED_LAUNCH_HOLD':push('DOCUMENTED_LAUNCH_HOLD')
   if r['dq06_status']=='DOCUMENTED_DISCONTINUATION':push('DOCUMENTED_DISCONTINUATION')
   if r['dq06_status']=='PACKAGING_REVIEW':push('PACKAGING_RELEASE_REVIEW')
  # Rule RISK-PILOT-1.1: classify by actual observed record state and symptom, not a case ID.
  for ic in ci_by_sku[sku]:
   if ic['reported_symptom']=='WMS_RECORD_MISSING' and not wms_by_sku[sku]:
    push('WMS_REFERENCE_MISSING')
   if ic['reported_symptom'] in ('PRODUCT_MEASURE_NOT_VERIFIED','LAUNCH_NOT_RELEASED'):
    if any(x['approval_status']!='APPROVED' or not x['confirmed_at'] for x in supplier_by_sku[sku]):
     push('SUPPLIER_EVIDENCE_UNCONFIRMED')
   if ic['reported_symptom']=='ARTICLE_NOT_ORDERABLE' and next((x['dq06_status'] for x in by_sku[6][sku]),'')=='DOCUMENTED_LAUNCH_HOLD':
    push('DOCUMENTED_LAUNCH_HOLD')
  # An open case without a modeled DQ signal is still a case requiring administrative disposition.
  if ci_by_sku[sku] and not signals:push('INCIDENT_UNRESOLVED')
  registered_release = next((r['dq06_status'] for r in by_sku[6][sku]),'')
  adverse=[s for s in signals if s not in ('DOCUMENTED_LAUNCH_HOLD','DOCUMENTED_DISCONTINUATION')]
  severity = max((SIGNALS[s][0] for s in adverse),default=0)
  approved_any = registered_release=='ALL_PROCESSES_ALLOW'
  release_conflict = approved_any and severity>=3
  if severity>=4:prio='P1' if (release_conflict or 'RECEIPT_HOLD' in adverse or 'WMS_REFERENCE_MISSING' in adverse) else 'P2'
  elif severity>=3:prio='P2'
  elif adverse:prio='P3'
  elif signals:prio='P3' if ci_by_sku[sku] else 'P4'
  else:prio='P4'
  # Product-level missing evidence is explicitly an evidence status, not inferred actual failure.
  listed_evidence=[e for t in ci_by_sku[sku] for e in ev if e['case_id']==t['case_id']]
  if listed_evidence:
   if any(x['evidence_availability']=='MISSING' for x in listed_evidence):evidence_quality='NACHWEISLUECKE'
   elif any(x['evidence_availability']=='UNCONFIRMED' for x in listed_evidence):evidence_quality='UNBESTAETIGT'
   else:evidence_quality='ALLE_REGISTRIERTEN_BELEGE_VERFUEGBAR'
  else:evidence_quality='KEIN_INCIDENT_NACHWEIS_REGISTERIERT'
  lead=next((s for s in signals if SIGNALS[s][0]==severity and s in adverse), signals[0] if signals else None)
  act=SPECIAL_ACTIONS.get(lead,'Regulaere Kontrollintervalle und dokumentierte Freigabe beibehalten.')
  if release_conflict:act='ZUSAETZLICH: ALLOW gegen negative fachliche Checks abgleichen; keine automatische Sperrung ohne Regelentscheidung. '+act
  v.append({'sku':sku,'produktgruppe':p['product_group'],'herkunft':p['origin_type'],'lebenszyklus':p['lifecycle_status'],
   'dq_signale':' | '.join(signals) or 'KEIN_REGISTRIERTES_PRUEFSIGNAL', 'signalanzahl':len(signals),'max_potenzielle_auswirkung_1_bis_5':severity,
   'prioritaet':prio, 'prioritaet_begruendung':('Negatives Prüfsignal und registrierte ALLOW-Freigaben' if release_conflict else LEVELS[prio]),
   'dq06_release_status':registered_release,'freigabe_pruefbedarf':('JA' if release_conflict else 'NEIN'),
   'referenz_incidents':' | '.join(t['case_id'] for t in ci_by_sku[sku]) or 'KEIN_INCIDENT',
   'evidenzlage':evidence_quality,'naechste_fachliche_aktion':act,
   'datenstatus':'V2_HISTORISCH_UNVERAENDERT'})
 product_by_sku={r['sku']:r for r in v}
 caseout=[]
 for t in incidents:
  evid=[x for x in ev if x['case_id']==t['case_id']];p=product_by_sku[t['sku']]
  title, caveat, owner=CASE_CONTEXT.get(t['case_id'], (t['reported_symptom'], 'V2-Fallmeldung: technische Ursache ohne zusaetzliche Event- und Prozessbelege nicht bestaetigt.', 'Data Quality / fachlicher Prozesseigner'))
  caseout.append({'incident':t['case_id'],'referenz':t['affected_reference'],'zugeordnete_sku':t['sku'],
   'zuordnungsregel':('SKU direkt' if t['affected_reference'].startswith('HYG-') else 'Bestellungszuordnung' if t['affected_reference'].startswith('PO-') else 'Receipt -> PO/ASN -> SKU'),
   'symptom':t['reported_symptom'],'fallbeschreibung':title,'prioritaet_pilot':p['prioritaet'],
   'evidenz_verfuegbar':sum(x['evidence_availability']=='AVAILABLE' for x in evid),
   'evidenz_fehlend':sum(x['evidence_availability']=='MISSING' for x in evid),
   'evidenz_unbestaetigt':sum(x['evidence_availability']=='UNCONFIRMED' for x in evid),
   'fachliche_einordnung':caveat,'vorgeschlagener_verantwortlicher_bereich':owner,
   'historischer_status':t['investigation_status'],
   'entscheidung_in_ausfuehrung_1':'TRIAGE_DOKUMENTIERT__FALLBEARBEITUNG_AUSSTEHEND',
   'naechste_aktion':p['naechste_fachliche_aktion']})
 c.close();assert hashlib.sha256(db.read_bytes()).hexdigest()==hash_before,'Quelle wurde verändert'
 assert len(v)==500 and len({r['sku'] for r in v})==500
 assert len(caseout)==32 and all(c['zugeordnete_sku'] for c in caseout)
 assert sum(x['dq01_status']=='PASS' for x in dqs[1])==319
 assert sum(x['dq02_status']=='PASS' for x in dqs[2])==298
 assert sum(x['dq06_status']=='ALL_PROCESSES_ALLOW' for x in dqs[6])==471
 outcsv(out/'V2_500_Artikel_Risikomatrix.csv',v,list(v[0]));outcsv(out/'V2_32_Incidents_Triage.csv',caseout,list(caseout[0]));
 info={'quelle_db_sha256':hash_before,'basiskohorte':len(v),'incidents':len(caseout),
 'prioritaetsverteilung':dict(sorted(collections.Counter(x['prioritaet'] for x in v).items())),
 'allow_mit_fachlichem_pruefsignal':sum(x['freigabe_pruefbedarf']=='JA' for x in v),
 'incidents_v2_open':sum(x['historischer_status']=='OPEN' for x in caseout),
 'kontrollzahlen':{'DQ01_PASS':sum(x['dq01_status']=='PASS' for x in dqs[1]),'DQ01_in_scope':len(dqs[1]),'DQ02_PASS':sum(x['dq02_status']=='PASS' for x in dqs[2]),'DQ02_evaluable':sum(x['dq02_status'] in ('PASS','DIMENSION_MISMATCH') for x in dqs[2]),'DQ06_ALL_ALLOW':sum(x['dq06_status']=='ALL_PROCESSES_ALLOW' for x in dqs[6])},
 'ausfuehrung':'3/4: dieselbe Risikomethode RISK-PILOT-1.1, nur V2-Schemaadapter und Kohortenasserts',
 'risikomodell':{'skala_auswirkung':'1-5 qualitativ angenommen; kein gemessener Schaden',
 'prioritaet':'P1 wenn schwere Auffaelligkeit (>=4) mit ALLOW, HOLD oder WMS-Luecke; P2 schwer ohne solches Merkmal oder mittlere Abweichung; P3 dokumentierter Kontroll-/Reviewstatus; P4 kein registriertes Signal',
 'keine_wahrscheinlichkeit':'Fehlende Expositionsdaten verbieten quantifizierte Eintrittswahrscheinlichkeit'}}
 (out/'Pruefprotokoll_Execution3_Risikotriage.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(info,ensure_ascii=False,indent=2))
 print('\nPRIORISIERTE PRODUKTE:')
 for t in v:
  if t['prioritaet']!='P4':print(t['sku'],t['prioritaet'],t['dq_signale'],t['referenz_incidents'],t['freigabe_pruefbedarf'])

if __name__=='__main__':main()
