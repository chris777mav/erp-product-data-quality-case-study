#!/usr/bin/env python3
"""Execution 3/4: read-only V2 evidence analysis plus separately labelled counterfactual sandbox.

Retains the exact qualitative risk signals/weights and priority conditions of RISK-PILOT-1.1.
Never mutates the 20-SKU pilot, raw V2, registered releases or historical incidents.
"""
from __future__ import annotations
import csv, hashlib, json, os, sqlite3, collections, importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]  # repository root
DB=BASE/'results/Portfolio_Projekt1_V2_500SKUs.sqlite'
PILOT_DB=BASE/'input/Portfolio_Phase4_Rohdaten.sqlite'
SQL_DIR=BASE/'sql'
PILOT_MOD=BASE/'risk/methodenvalidierung/risikomodell_geprueft.py'
METHODOLOGY=BASE/'risk/methodenvalidierung/RISK_PILOT_1_1_METHODENVERTRAG.json'
HERE.mkdir(parents=True,exist_ok=True)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def connect(p,ro=True):
    c=sqlite3.connect(f'file:{Path(p).resolve()}?mode=ro',uri=True) if ro else sqlite3.connect(p)
    c.row_factory=sqlite3.Row
    return c

def qrows(c,q,pars=()):return [dict(x) for x in c.execute(q,pars)]
def dq(c,i):
    f=list(SQL_DIR.glob(f'DQ{i:02d}_*.sql'))
    assert len(f)==1,(i,f)
    return qrows(c,f[0].read_text(encoding='utf-8'))
def readcsv(path,sep=';'):
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=sep))
def writecsv(path,rs):
    assert rs
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(rs)
def dumpjson(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

baseline_hash=sha(DB);pilot_hash=sha(PILOT_DB);pilot_method_hash=sha(PILOT_MOD)
method=json.loads(METHODOLOGY.read_text(encoding='utf-8'))
assert method['version']=='RISK-PILOT-1.1'
spec=importlib.util.spec_from_file_location('risk_pilot_fixed',PILOT_MOD)
risk_pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(risk_pilot)
assert len(risk_pilot.SIGNALS)==15
triage=readcsv(HERE/'V2_500_Artikel_Risikomatrix.csv')
ci_triage=readcsv(HERE/'V2_32_Incidents_Triage.csv')
# Regression gate: the first 20 V1 pilot products must retain exactly the same pilot risk priority and signals in V2.
PILOT_RESULTS=BASE/'risk/methodenvalidierung/Pilot_20_Artikel_Risikomatrix.csv'
pilot_reference={r['sku']:r for r in readcsv(PILOT_RESULTS)}
triage_index={r['sku']:r for r in triage}
assert len(pilot_reference)==20 and all(r['sku'] in triage_index for r in pilot_reference.values())
assert all((row['prioritaet'],row['dq_signale'])==(triage_index[sku]['prioritaet'],triage_index[sku]['dq_signale']) for sku,row in pilot_reference.items()), 'V1 risk logic changed for original 20 SKUs'
assert len(triage)==500 and len({r['sku'] for r in triage})==500
assert len(ci_triage)==32 and len({r['incident'] for r in ci_triage})==32
triage_by_sku={r['sku']:r for r in triage}

with connect(DB) as conn:
    controls={i:dq(conn,i) for i in range(1,8)}
    products=qrows(conn,'SELECT * FROM products ORDER BY sku')
    cases=qrows(conn,'SELECT * FROM reported_cases ORDER BY case_id')
    evidence=qrows(conn,'SELECT * FROM issue_evidence ORDER BY evidence_id')
    asns=qrows(conn,'SELECT * FROM asns ORDER BY asn_id,asn_line_id')
    receipts=qrows(conn,'SELECT * FROM receipts ORDER BY receipt_id,receipt_line_id')
    purchase=qrows(conn,'SELECT * FROM purchase_orders ORDER BY po_id,po_line_id')
    stock=qrows(conn,'SELECT * FROM stock_snapshots ORDER BY sku')
    source_schema={r['name'] for r in qrows(conn,"SELECT name FROM sqlite_master WHERE type='table'")}
    assert len(source_schema)==21
    assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'

by_sku={i:collections.defaultdict(list) for i in range(1,7)}
for i in range(1,7):
    for r in controls[i]:by_sku[i][r['sku']].append(r)
qbycase=collections.defaultdict(list)
for r in evidence:qbycase[r['case_id']].append(r)
po_to_sku=collections.defaultdict(set)
for r in purchase:po_to_sku[r['po_id']].add(r['sku'])
asn_to_sku=collections.defaultdict(set)
for r in asns:asn_to_sku[r['asn_id']].add(r['sku'])
rec_to_sku=collections.defaultdict(set)
for r in receipts:
    rec_to_sku[r['receipt_id']].update(asn_to_sku.get(r['asn_id'],set()))
    if not rec_to_sku[r['receipt_id']]:rec_to_sku[r['receipt_id']].update(po_to_sku.get(r['po_id'],set()))
products_set={r['sku'] for r in products}

def resolve(ref):
    if ref in products_set:return {ref},'SKU direkt'
    if ref in po_to_sku:return po_to_sku[ref],'PO->SKU'
    if ref in rec_to_sku:return rec_to_sku[ref],'Receipt->ASN/PO->SKU'
    if ref in asn_to_sku:return asn_to_sku[ref],'ASN->SKU'
    return set(),'nicht zugeordnet'

# Keep additional unscored control exceptions visible. Do not retroactively change frozen risk score.
additional=[]
coverage_by_sku=collections.defaultdict(list)
for r in controls[2]:
    if r['dq02_status'] in ('MISSING_TARGET_LENGTH','UNSUPPORTED_UOM'):
        coverage_by_sku[r['sku']].append('DQ02_NICHT_AUSWERTBAR_'+r['dq02_status'])
for r in controls[3]:
    if r['version_check']=='NO_EVENT':coverage_by_sku[r['sku']].append('DQ03_EVENT_FEHLT_IM_ABZUG')
for r in controls[6]:
    if r['dq06_status'] in ('MISSING_ACTIVE_RELEASE','DUPLICATE_ACTIVE_RELEASE'):
        coverage_by_sku[r['sku']].append('DQ06_'+r['dq06_status'])
for sku,flags in sorted(coverage_by_sku.items()):
    additional.append({'sku':sku,'ausserhalb_gewichteter_v1_signale':' | '.join(sorted(set(flags))),
        'v1_prioritaet_bleibt':triage_by_sku[sku]['prioritaet'],
        'erforderliche_entscheidung':'ZUSAETZLICHE_FACHLICHE_PRUEFUNG','hinweis':'Nicht automatisch als PASS oder riskofrei interpretieren.'})
writecsv(HERE/'V2_Abdeckungsluecken_manueller_Pruefbedarf.csv',additional)

# Cross-control consistency, strict grains: report anomalous migrations + releases, not arbitrary incidents.
migration_nonpass={r['sku'] for r in controls[1] if r['dq01_status']!='PASS'}
allow={r['sku'] for r in controls[6] if r['dq06_status']=='ALL_PROCESSES_ALLOW'}
assert len(migration_nonpass)==11
assert len(migration_nonpass & allow)==11
legacy_coverage={r['sku'] for r in controls[1]}
assert len(legacy_coverage)==330
assert len(asns)==191 and len({(r['asn_id'],r['asn_line_id']) for r in asns})==191
assert len(products)==500 and len(cases)==32
assert collections.Counter(r['prioritaet'] for r in triage)=={'P1':83,'P2':29,'P3':1,'P4':387}
assert sum(r['freigabe_pruefbedarf']=='JA' for r in triage)==104

cases_all=[]
link_by_sku=collections.defaultdict(list)
status_to_evidence={
 'TARGET_RECORD_NOT_VISIBLE':'Migrierten Zielartikel und Eventquellen unter alter und neuer Identität prüfen.',
 'MISSING_TARGET':'Migration-Scope, Laufprotokoll und erlaubte Nachladung klären.',
 'DIMENSION_DISCREPANCY':'Quellwert, Umrechnungsregel und S2-Länge mit technischer Laufversion vergleichen.',
 'DIMENSION_MISMATCH':'Quellwert und Zielwert belegen; Mappingevent prüfen; Retest einschließlich Folgesystem vorsehen.',
 'UNAPPROVED_MAPPING':'Version und Genehmigung zum Versandzeitpunkt kontrollieren; Laufkonfiguration/Selektion getrennt prüfen.',
 'PACKAGING_DIFFERENCE':'PO/ASN/Packversion/zeitliche Freigabe abgleichen; HOLD getrennt beurteilen.',
 'PACKAGING':'PO/ASN/Packversion gegen Lieferantenbestätigung abgleichen, WMS-Freigabe nicht fingieren.',
 'ORDER_PARTIALLY_DELIVERED':'ASN-Zeilen und Receipts getrennt abstimmen; fehlender Beleg keine Nichtlieferung.',
 'RECEIPT_GAP':'Receipt-/WMS-Journal beschaffen, vor hypothetischer Nachbuchung Transportnachweis prüfen.',
 'RECEIPT_QUARANTINED':'HOLD-Grund, gesperrten Bestand, Freigabegate und mögliche Prozessfolgen prüfen.',
 'WMS_RECORD_MISSING':'Schnittstellen- und WMS-Protokolle getrennt prüfen, kein bestimmter Root Cause ableitbar.',
 'PRODUCT_MEASURE_NOT_VERIFIED':'Lieferantenmaßreferenz und Genehmigung nachfordern, nicht blind als Fehlmaß klassifizieren.',
 'ARTICLE_NOT_ORDERABLE':'Launch-Termin und dokumentierte Plan-Sperre gegen echte Blockade prüfen.',
 'LAUNCH_NOT_RELEASED':'Lieferanten-/Packnachweis nachfordern, REVIEW nicht als FAIL deklarieren.'}
owner_rule={'TARGET_RECORD_NOT_VISIBLE':'ERP-Migration / MDM','MISSING_TARGET':'ERP-Migration / MDM',
 'DIMENSION_DISCREPANCY':'MDM / ERP / WMS','DIMENSION_MISMATCH':'MDM / ERP / WMS',
 'UNAPPROVED_MAPPING':'ERP-Migration / Data Engineering','PACKAGING_DIFFERENCE':'Einkauf / Lieferant / WMS','PACKAGING':'Einkauf / Lieferant / WMS',
 'RECEIPT_GAP':'WMS / Einkauf','ORDER_PARTIALLY_DELIVERED':'WMS / Einkauf','RECEIPT_QUARANTINED':'WMS / Logistik',
 'WMS_RECORD_MISSING':'WMS / Schnittstellenbetreuung','PRODUCT_MEASURE_NOT_VERIFIED':'MDM / Lieferant',
 'ARTICLE_NOT_ORDERABLE':'Produktmanagement / Einkauf','LAUNCH_NOT_RELEASED':'Produktmanagement / Einkauf'}

for case in cases:
    skus,via=resolve(case['affected_reference'])
    ev=qbycase[case['case_id']]
    assert len(skus)==1,(case,skus)
    sku=next(iter(skus));link_by_sku[sku].append(case['case_id'])
    r=triage_by_sku[sku]
    controls_one={f'DQ-{i:02d}':[dict(row) for row in by_sku[i][sku]] for i in range(1,7)}
    # Note: these tables are only the observed and registered source records. No generated success receipts/approvals.
    recs=[dict(x) for x in receipts if sku in asn_to_sku.get(x['asn_id'],set())]
    asns_one=[dict(x) for x in asns if x['sku']==sku]
    if any(row['evidence_availability']=='MISSING' for row in ev):ep='NACHWEIS_FEHLT_IM_ABZUG'
    elif any(row['evidence_availability']=='UNCONFIRMED' for row in ev):ep='NACHWEIS_UNBESTAETIGT'
    elif ev:ep='REGISTRIERTE_BELEGE_VERFUEGBAR'
    else:ep='KEIN_EVIDENZREGISTER_EINTRAG'
    causal='URSACHE_TEILWEISE_BELEGT' if case['case_id']=='INC-002' else 'URSACHE_OFFEN'
    if case['case_id']=='INC-002':causal_note='Nicht genehmigter Faktor 25,0 ist belegt; Auswahlgrund dieser Version offen. Korrektur nur in getrennter Testsandbox geschlossen.'
    elif case['case_id']=='INC-004':causal_note='Genehmigte Packänderung vor ASN; Bestellzeitpunkt verlangt eine dokumentierte Rückfrage. Kein Fehler als sicher behauptbar.'
    elif case['case_id']=='INC-010':causal_note='Geplanter Launch-HOLD statt belegtem DQ-Fehler; keine ungeprüfte Freigabe.'
    else:causal_note='Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.'
    nxt=status_to_evidence.get(case['reported_symptom'],'Fachliche Abklärung mit Quelle/Prüfprotokoll und verantwortetem Retest.')
    gates=['Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen','Betroffene SQL-Kontrollen nach Maßnahme wiederholen',
            'Abhängige ERP-/WMS-/Freigabefolgen dokumentieren','Administrative Entscheidung erst danach freigeben']
    outcomes={'INC-002':'HISTORISCH_OFFEN; SEPARATE_PILOT_SANDBOX_CLOSED',
              'INC-004':'GENEHMIGTE_AENDERUNG; ADMINISTRATIVER_REVIEW',
              'INC-010':'PLANMAESSIGER_HOLD; FACHLICH_GUELTIGE_AUSNAHME'}
    entry={'incident_id':case['case_id'],'betroffene_referenz':case['affected_reference'],'sku':sku,'link_via':via,
        'gemeldetes_symptom':case['reported_symptom'],'historischer_status':case['investigation_status'],
        'prioritaet_nach_festem_pilotmodell':r['prioritaet'],'risikosignale':r['dq_signale'],
        'dokumentierte_evidenzlage':ep,'evidenz':ev,'dq_pruefresultate':controls_one,
        'asn_vorgaenge':asns_one,'receipt_belege':recs,'ursachenstatus':causal,'ursachengrenze':causal_note,
        'kontrollentscheidung_vorgeschlagen':('FACHLICHES_REVIEW' if r['prioritaet'] in ('P1','P2') else 'DOKUMENTIERTE_NACHVERFOLGUNG'),
        'prozess_eigner_vorgeschlagen':owner_rule.get(case['reported_symptom'],'DQ / Fachbereich'),
        'massnahme_vorgeschlagen':nxt,'abschlussbedingungen':gates,
        'aktueller_untersuchungsentscheid':outcomes.get(case['case_id'],'OFFEN_MIT_NAECHSTER_MASSNAHME'),
        'abschluss_nach_nachgewiesenem_retest':False,
        'quelle':'V2-Ausgangsstand, keine Mutation der historischen Case-Tabelle'}
    cases_all.append(entry)
assert len(cases_all)==32

# Distinguish cases vs products: complete source linkage (PO/receipt) is not same as direct SKU matches.
case_link_skus={r['sku'] for r in cases_all}
triggered_skus={r['sku'] for r in triage if r['prioritaet']!='P4' or r['sku'] in coverage_by_sku}
case_coverage={
    'all_cases':len(cases_all),'direct_SKU':sum(x['link_via']=='SKU direkt' for x in cases_all),
    'indirect_PO_Receipt_ASN':sum(x['link_via']!='SKU direkt' for x in cases_all),
    'distinct_case_skus':len(case_link_skus),
    'unique_risk_or_coverage_flag_skus':len(triggered_skus),
    'risk_or_coverage_flags_without_mapped_case_skus':len(triggered_skus - case_link_skus),
    'original_v2_report_direct_sku_only_figure':101}
# All flags need a documented disposition, but cases may be missing and must not be fabricated.
product_matrix=[]
for row in triage:
    sku=row['sku'];anomalies=' | '.join(sorted(set(coverage_by_sku.get(sku,[]))))
    caseids=' | '.join(sorted(link_by_sku.get(sku,[]))) or 'KEIN_ZUGEORDNETER_FALL'
    if row['prioritaet']=='P1':action='P1_FACHLICHES_REVIEW_SO_GEWICHTET'
    elif row['prioritaet']=='P2':action='P2_FALLTRIAGE'
    elif row['prioritaet']=='P3':action='P3_AUSNAHME_ODER_ADMINISTRATIV'
    else:action='P4_REGULAERES_MONITORING'
    if anomalies:action+='__ZUSAETZLICHER_OFFENER_ABDECKUNGSBEFUND'
    product_matrix.append({**row,'zusaetzliche_nicht_gewichtete_pruefsignale':anomalies or 'KEINE',
         'zugeordnete_incidents_nach_referenzaufloesung':caseids,'bearbeitungsstatus_v2':'ERFASST_UND_PRIORISIERT',
         'naechste_steuerungsstufe':action,'schlussfolgerung':'KEINE_AUTOMATISCHE_RELEASE_UMSTELLUNG'})
writecsv(HERE/'V2_500_Artikel_Entscheidungsregister.csv',product_matrix)
dumpjson(HERE/'V2_32_Incidents_vollstaendige_Fallakten.json',cases_all)
cases_summary=[{k:v for k,v in entry.items() if k not in ('evidenz','dq_pruefresultate','asn_vorgaenge','receipt_belege','abschlussbedingungen')} for entry in cases_all]
writecsv(HERE/'V2_32_Incidents_Fachentscheidungen.csv',cases_summary)

markdown=['# V2 – Einzelakten aller 32 registrierten Incidents','',
  '**Geltung:** reine synthetische Fallstudie. Die Fachentscheidungen sind dokumentierte Empfehlungen, keine tatsächlich ausgeführten Unternehmensfreigaben. 32 historische V2-Incidents bleiben OPEN.',
  '**Methode:** RISK-PILOT-1.1 unverändert; exakt aufgelöste PO-/Receipt-Referenzen, sieben SQL-Kontrollen, strikt dokumentierte Grenzen.',
  f"**Verknüpfung:** {case_coverage['direct_SKU']} direkte SKU-Referenzen; {case_coverage['indirect_PO_Receipt_ASN']} indirekte fachliche Referenzen; {len(case_link_skus)} betroffene eindeutige Artikel.",
  '','Alle Empfehlungen erfordern echte Quellbelege und gegebenenfalls Freigaben; fehlende Receipts oder Events sind keine bewiesene physische Nichtlieferung oder ETL-Ursache.','']
for c in cases_all:
    markdown+= [f"## {c['incident_id']} — {c['sku']} — {c['gemeldetes_symptom']} ({c['prioritaet_nach_festem_pilotmodell']})",'',
      f"**Referenzauflösung:** `{c['betroffene_referenz']}` → `{c['sku']}` ({c['link_via']}). **Historischer Status:** `{c['historischer_status']}`.",
      f"**Kontrollbefunde:** {c['risikosignale']}. **Evidenz:** {c['dokumentierte_evidenzlage']} ({', '.join(e['evidence_id'] for e in c['evidenz']) or 'kein Eintrag'}).",
      f"**Ursachenbewertung:** {c['ursachenstatus']}. {c['ursachengrenze']}",
      f"**Nächste Maßnahme / Besitzer:** {c['massnahme_vorgeschlagen']} — *{c['prozess_eigner_vorgeschlagen']}*.",
      '**Abschlusskriterien:** '+'; '.join(c['abschlussbedingungen'])+'.','',
    ]
(HERE/'V2_32_Incidents_Einzelfallbericht.md').write_text('\n'.join(markdown),encoding='utf-8')

# Independent counterfactual simulations with a SQLite backup. Historical truth stays intact.
# Case order: one dimension, one identity, one receipt-documentation, one pack/reference, plus negative control.
SANDBOX=HERE/'V2_EINZELFALL_RETTEST_SANDBOX.sqlite'
# Always use a fresh derivative sandbox on reruns; never overwrite source DBs.
if SANDBOX.exists(): SANDBOX.unlink()
with connect(DB) as sr, connect(SANDBOX,ro=False) as dest:sr.backup(dest)
assert sha(DB)==baseline_hash
sim=connect(SANDBOX,ro=False)
befores={i:dq(sim,i) for i in range(1,8)}

def pick(rows,sku,status):
    k=f'dq{status:02d}_status'
    matches=[r for r in rows if r.get('sku')==sku]
    assert len(matches)==1,(sku,matches)
    return matches[0][k]

def ct(rows,col):return collections.Counter(r[col] for r in rows)
mutations=[]
assert pick(befores[2],'HYG-2058',2)=='DIMENSION_MISMATCH'
actual=sim.execute("SELECT length_mm FROM target_snapshot WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-2058'").fetchone()[0]
expected=sim.execute("SELECT length_value FROM legacy_snapshot WHERE sku='HYG-2058'").fetchone()[0]
assert (round(actual,2),round(expected,2))==(151.76,154.96)
sim.execute("UPDATE target_snapshot SET length_mm=? WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-2058'",(expected,))
mutations.append({'id':'SIM-A','sku':'HYG-2058','art':'TARGET_DIMENSION_RETEST','vorher':actual,'nachher':expected,
   'annahme':'Hypothetische genehmigte Zielwertkorrektur nur im S2-Testsnapshot, kein WMS-End-to-End-Nachweis',
   'status':'TEST_ONLY'} )

assert pick(befores[1],'HYG-2097',1)=='IDENTITY_MISMATCH'
oldtarget=sim.execute("SELECT target_record_id FROM target_snapshot WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-2097'").fetchone()[0]
target=sim.execute("SELECT expected_target_record_id FROM migration_scope WHERE legacy_record_id='ALT-2097' AND in_scope='YES'").fetchone()[0]
assert oldtarget=='ERP-12097-BAD' and target=='ERP-12097'
sim.execute("UPDATE target_snapshot SET target_record_id=? WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-2097'",(target,))
mutations.append({'id':'SIM-B','sku':'HYG-2097','art':'TARGET_IDENTITAET_RETEST','vorher':oldtarget,'nachher':target,
   'annahme':'Simulierter Identitätsabgleich; produktive Mapping-/Duplikatklärung bleibt erforderlich','status':'TEST_ONLY'})

r=next(r for r in befores[5] if r['sku']=='HYG-2114')
assert r['dq05_status']=='MISSING_RECEIPT' and r['announced_qty']==576
asn=sim.execute("SELECT * FROM asns WHERE asn_id='ASN-2114' AND asn_line_id='10'").fetchone()
assert asn is not None
assert sim.execute("SELECT COUNT(*) FROM receipts WHERE asn_id=? AND asn_line_id=?",(asn['asn_id'],asn['asn_line_id'])).fetchone()[0]==0
sim.execute('''INSERT INTO receipts (receipt_id,receipt_line_id,asn_id,asn_line_id,po_id,po_line_id,
    wms_article_id,received_at,package_count,each_per_package,received_base_qty,processing_status)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
  ('SIM-REC-2114','10',asn['asn_id'],asn['asn_line_id'],asn['po_id'],asn['po_line_id'],
  'WMS-2114','2026-09-19T10:00:00',asn['package_count'],asn['each_per_package'],asn['announced_base_qty'],'POSTED'))
mutations.append({'id':'SIM-C','sku':'HYG-2114','art':'RECEIPT_NACHWEIS_RETEST','vorher':'MISSING_RECEIPT','nachher':'SIMULATED_POSTED_RECEIPT',
   'annahme':'Erfundener Posteingang ausschließlich zur Testprobe; kein Beleg realer Lieferung und keine Nachbuchung in historischen Daten',
   'status':'TEST_ONLY'})

r=next(r for r in befores[4] if r['sku']=='HYG-2111')
assert r['dq04_status']=='BLOCK'
asn=sim.execute("SELECT * FROM asns WHERE asn_id='ASN-2111' AND asn_line_id='10'").fetchone()
assert asn['pack_version_id']=='PK-2111-UNKNOWN'
assert asn['each_per_package']==48
ps=sim.execute("SELECT expected_pack_version_id FROM purchase_orders WHERE po_id=? AND po_line_id=?",(asn['po_id'],asn['po_line_id'])).fetchone()
assert ps['expected_pack_version_id']=='PK-2111-A'
sim.execute("UPDATE asns SET pack_version_id=? WHERE asn_id='ASN-2111' AND asn_line_id='10'",(ps['expected_pack_version_id'],))
mutations.append({'id':'SIM-D','sku':'HYG-2111','art':'ASN_PACKVERSION_RETEST','vorher':'PK-2111-UNKNOWN','nachher':'PK-2111-A',
   'annahme':'Geänderte ASN-Version allein beweist keine bestätigte Lieferantenpackung; WMS- und Lieferantenfreigabe bleiben getrennt',
   'status':'TEST_ONLY'})

assert pick(befores[2],'HYG-1006',2)=='DIMENSION_MISMATCH'
sim.execute("UPDATE target_snapshot SET length_mm=203.2 WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-1006'")
mutations.append({'id':'SIM-E','sku':'HYG-1006','art':'NEGATIVTEST_REGELPROTOKOLL_BLEIBT','vorher':200.0,'nachher':203.2,
  'annahme':'Korrigierter Zielwert allein korrigiert weder historisches unzulässiges Mapping-Event noch schließt er den Incident',
  'status':'NEGATIVE_CONTROL_ONLY'})
sim.commit()
after={i:dq(sim,i) for i in range(1,8)}
assert pick(after[2],'HYG-2058',2)=='PASS'
assert pick(after[1],'HYG-2097',1)=='PASS'
assert next(r for r in after[5] if r['sku']=='HYG-2114')['dq05_status']=='RECONCILED_POSTED'
assert next(r for r in after[4] if r['sku']=='HYG-2111')['dq04_status']=='PASS'
assert pick(after[2],'HYG-1006',2)=='PASS'
assert next(r for r in after[3] if r['sku']=='HYG-1006')['approval_check']=='UNAPPROVED_RULE'
assert all(r['investigation_status']=='OPEN' for r in after[7]) and len(after[7])==32
assert len(after[6])==500
assert sim.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert sim.execute('PRAGMA foreign_key_check').fetchall()==[]
assert sim.execute("SELECT length_mm FROM target_snapshot WHERE snapshot_id='S1-2026-09-10' AND sku='HYG-2058'").fetchone()[0]==151.76
assert sim.execute("SELECT target_record_id FROM target_snapshot WHERE snapshot_id='S1-2026-09-10' AND sku='HYG-2097'").fetchone()[0]=='ERP-12097-BAD'
assert sim.execute('SELECT COUNT(*) FROM products').fetchone()[0]==500
assert sim.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]==len(receipts)+1
for i in (1,2,3,4,5,6,7):
    assert len(after[i])==len(befores[i]),(i,len(after[i]),len(befores[i]))
assert befores[3]==after[3],'Mapping evidence must remain immutable in sandbox'
assert befores[6]==after[6],'Registered releases cannot be mutated by DQ correction'
# Verify each control row of untouched SKUs remains identical (stable row order and grain).
affected={'HYG-2058','HYG-2097','HYG-2114','HYG-2111','HYG-1006'}
for i in range(1,7):
    a=[r for r in befores[i] if r.get('sku') not in affected]
    b=[r for r in after[i] if r.get('sku') not in affected]
    assert a==b, f'DQ-{i:02d} unintended SKU modification'

delta={
 'DQ01_PASS':(ct(befores[1],'dq01_status')['PASS'],ct(after[1],'dq01_status')['PASS']),
 'DQ02_PASS':(ct(befores[2],'dq02_status')['PASS'],ct(after[2],'dq02_status')['PASS']),
 'DQ02_EVALUABLE':(sum(r['dq02_status'] in ('PASS','DIMENSION_MISMATCH') for r in befores[2]),sum(r['dq02_status'] in ('PASS','DIMENSION_MISMATCH') for r in after[2])),
 'DQ04_PASS':(ct(befores[4],'dq04_status')['PASS'],ct(after[4],'dq04_status')['PASS']),
 'DQ05_RECONCILED_POSTED':(ct(befores[5],'dq05_status')['RECONCILED_POSTED'],ct(after[5],'dq05_status')['RECONCILED_POSTED']),
 'DQ03_UNAPPROVED_RULE':(ct(befores[3],'approval_check')['UNAPPROVED_RULE'],ct(after[3],'approval_check')['UNAPPROVED_RULE']),
 'DQ07_OPEN':(sum(r['investigation_status']=='OPEN' for r in befores[7]),sum(r['investigation_status']=='OPEN' for r in after[7])),
 'DQ06_ALL_ALLOW':(ct(befores[6],'dq06_status')['ALL_PROCESSES_ALLOW'],ct(after[6],'dq06_status')['ALL_PROCESSES_ALLOW'])}
assert delta['DQ01_PASS']==(319,320)
assert delta['DQ02_PASS']==(298,301)
assert delta['DQ04_PASS']==(176,177)
assert delta['DQ05_RECONCILED_POSTED']==(135,136)
assert delta['DQ02_EVALUABLE']==(310,311)
assert delta['DQ03_UNAPPROVED_RULE']==(11,11)
assert delta['DQ07_OPEN']==(32,32)
assert delta['DQ06_ALL_ALLOW']==(471,471)
sim.close()
assert sha(DB)==baseline_hash and sha(PILOT_DB)==pilot_hash and sha(PILOT_MOD)==pilot_method_hash

risk_summary={'version':'RISK-PILOT-1.1','method_contract_sha256':sha(METHODOLOGY),'pilot_method_code_sha256':pilot_method_hash,
 'v2_raw_sqlite_sha256':baseline_hash,'v1_raw_sqlite_sha256':pilot_hash,
 'rows':{'v2_products':500,'v2_cases':32,'v2_asn_positions':len(asns),'v2_receipts_source':len(receipts),
         'v2_receipts_sandbox':len(receipts)+1},
 'source_tables':len(source_schema),'v1_pilot_20_score_signal_regression':'20/20 IDENTISCH','status_500':dict(sorted(collections.Counter(r['prioritaet'] for r in triage).items())),
 'allow_with_weighted_warning_500':sum(r['freigabe_pruefbedarf']=='JA' for r in triage),
 'migration_nonpass_allow_overlap':len(migration_nonpass & allow),
 'unweighted_coverage_flags_skus':len(coverage_by_sku),
 'case_reconciliation':case_coverage,
 'before_after_sandbox':{k:{'source':x[0],'simulation':x[1],'difference':x[1]-x[0]} for k,x in delta.items()},
 'changes_test_only':mutations,
 'tests':{
   'sku_grain_500_distinct':'PASS','migration_scope_330':'PASS','asn_line_grain_191':'PASS',
   'incidents_32_resolved_exactly_one_sku':'PASS','pilot_method_unaltered':'PASS','v1_risk_results_20_of_20_identical':'PASS',
   'original_v1_v2_unchanged':'PASS','sql_controls_7_run_baseline_and_sandbox':'PASS',
   'validity_sqlite_integrity_foreign_keys':'PASS','negative_mapping_control':'PASS',
   'no_auto_release_or_incident_closure':'PASS','no_unintended_non_target_record_changes':'PASS',
   'four_distinct_test_only_corrective_cases_plus_one_negative_control':'PASS'},
 'caveats':['Kriterien und Risikostufen sind qualitative fachliche Annahmen; keine Empirie oder monetäre Schadensmessung.',
  'RISK-PILOT-1.1 bewertet bestimmte Nicht-Auswertbarkeiten und fehlende Event-/Release-Sonderfälle nicht mit separaten Gewichten; sie stehen im zusätzlichen manuellen Prüfregister.',
  'Kritische P1-/P2-Kategorien sind verdachtsbasierte priorisierte Reviewaufgaben, keine nachgewiesenen Fehler und keine bindende Policy.',
  'Sandbox-Nachbuchung beweist keine Wareneingangsrealität; alle 32 historische V2-Incidents bleiben OPEN.',
  'Die sieben SQL-Prüfungen implementieren nicht sämtliche 26 Geschäftsregeln.',
  'S2 und as-of Freigabe-Snapshot 18.09 sind zeitlich verschieden; Kreuzsignale verlangen fachliche Zeitprüfung.']}
dumpjson(HERE/'Ausfuehrung_3_Abnahmeprotokoll.json',risk_summary)
writecsv(HERE/'V2_Retest_Vorher_Nachher.csv',[{'kontrolle':k,'quelle':v['source'],'sandbox':v['simulation'],'delta':v['difference']} for k,v in risk_summary['before_after_sandbox'].items()])

lines=[
 '# Risikoorientierte Skalierung auf 500 synthetische Artikel – Ausführung 3/4','',
 '## 1. Methodische Grundlage','',
 'Die am 20-Artikel-Pilot definierte und in Ausführung 2 geprüfte Version **RISK-PILOT-1.1** wurde unverändert angewendet. Keine Risiko-Gewichte, Schwellen oder P1–P4-Regeln wurden nach Sichtung der 500er-Ergebnisse geändert. Die Adapteränderungen betreffen allein Kohortengröße, Dateinamen und die Zuordnung der weiteren registrierten Incident-IDs. **P1 bedeutet einen Prüfvorrang, nicht automatisch einen nachgewiesenen Verstoß.**','',
 f"Datenquelle: 500 Artikel, 21 Relationen, 330 migrationspflichtige Zuordnungen, {len(asns)} ASN-Positionen und 32 registrierte offene Incidents. Unveränderter V2-Hash: `{baseline_hash}`.",'',
 '**Regressionsprüfung:** Alle 20 ursprünglichen Pilotartikel behalten in V2 exakt dieselbe Priorität und dieselben registrierten Risikosignale wie V1 (20/20).', '', '## 2. 500 Artikel vollständig mit Pilotmethode bewertet','',
 '| Stufe | Artikel | Fachliche Bedeutung |','|---|---:|---|',
 *[f"| {p} | {sum(r['prioritaet']==p for r in triage)} | {risk_pilot.LEVELS[p]} |" for p in ('P1','P2','P3','P4')],
 '',
 f"**{sum(r['freigabe_pruefbedarf']=='JA' for r in triage)}** Artikel erfüllen die unveränderte Risiko-Bedingung 'ALLOW plus negatives gewichtetes Fachsignal' (dies ist *nicht* gleichbedeutend mit 104 falschen Freigabeentscheidungen). Die genau definierte DQ01/ALLOW-Kreuzkontrolle ergibt **{len(migration_nonpass & allow)}** unterschiedliche SKUs. Die unterschiedlichen Zahlen beziehen sich auf unterschiedliche Prüfkriterien.",
 '',
 f"Zusätzlich erhalten **{len(coverage_by_sku)}** SKUs ein ausdrückliches Warnkennzeichen für vom Pilotmodell *nicht gesondert gewichtete* Nicht-Auswertbarkeit, fehlende Logereignisse oder unvollständige/doppelte Freigaberegister. Sie wurden nicht stillschweigend als fehlerfrei eingestuft. Diese Liste ist als zusätzlicher Prüfbedarf ausgewiesen, nicht nachträglich zu P1 gerechnet.",
 '',
 '## 3. Incident-Zuordnung und Entscheidungen','',
 f"Alle 32 historischen offenen Fälle wurden anhand der passenden fachlichen Referenz auf eine eindeutige SKU zurückgeführt: **{case_coverage['direct_SKU']} direkte SKUs** und **{case_coverage['indirect_PO_Receipt_ASN']} PO-/Receipt-/ASN-Verknüpfungen**. Damit werden Fremdschlüssel und Beleg-Grains korrekt beachtet.",
 f"**{case_coverage['risk_or_coverage_flags_without_mapped_case_skus']}** SKUs mit einem gewichteten oder zusätzlichen Prüfbedarf haben im vorhandenen Register keinen eindeutig zugeordneten Fall. Die Zahl ist gegenüber früheren Berichten abweichend, weil jetzt PO/Receipt-Referenzen explizit aufgelöst werden und zusätzliche Prüfflaggen berücksichtigt werden; sie ist keine neu entstandene operative Fehlerrate.",
 'Jeder Fall ist in `V2_32_Incidents_Einzelfallbericht.md` und im zugehörigen JSON mit Kontrollbefund, dokumentierter Evidenz, Ursache/Nichtwissen, vorgeschlagenem Verantwortungsbereich, nächster Handlung und Abschlussbedingung beschrieben. **Keine Case-Schließung wurde erfunden.**','',
 '## 4. Konkrete kontrollierte Korrekturversuche in isolierter Sandbox','',
 '| Probe | SKU | Mutierter Testdatensatz | Nachweis und Grenze |','|---|---|---|---|',
 '| SIM-A | HYG-2058 | S2-Länge 151,76 → 154,96 mm | DQ02 MISMATCH → PASS; Folgesystem-/Genehmigungsnachweis weiterhin notwendig. |',
 '| SIM-B | HYG-2097 | S2-Zielidentität ERP-12097-BAD → ERP-12097 | DQ01 IDENTITY_MISMATCH → PASS; historische Mappingfreigabe nicht automatisch saniert. |',
 '| SIM-C | HYG-2114 | rein synthetischer POSTED-Receipt-Beleg | DQ05 MISSING_RECEIPT → RECONCILED_POSTED; **kein Nachweis physischer Lieferung**. |',
 '| SIM-D | HYG-2111 | ASN-Packversion UNKNOWN → erwartete A | DQ04 BLOCK → PASS; genehmigte tatsächliche Lieferung und WMS bleiben gesondert. |',
 '| SIM-E | HYG-1006 | S2-Länge 200 → 203,2 mm | **Negativkontrolle:** DQ02 wird PASS, unzulässiges historisches DQ03-Regelereignis bleibt nachweisbar. |',
 '',
 '| KPI / Kontrollzählung | Unveränderte V2-Quelle | Separate Simulation |', '|---|---:|---:|',
 *[f"| {k} | {v['source']} | {v['simulation']} |" for k,v in risk_summary['before_after_sandbox'].items()],
 '',
 'Der DQ02-PASS-Anstieg um drei besteht aus zwei Dimensionswertkorrekturen und einer durch die korrigierte Zielidentität wieder **auswertbar** gewordenen Position (Nenner 310 → 311); es wurden nicht drei Dimensionsfehler korrigiert.',
 'Diese Vorher-/Nachher-Werte sind **reine Gegenproben in einer manipulierten Kopie**. Der historische Pilot- und V2-Quellbestand, alle vorhandenen Freigaben und alle 32 Incident-Statusfelder sind unverändert. Insbesondere handelt es sich **nicht um eine gemessene Verbesserung in einem Unternehmen**.','',
 '## 5. Abnahme- und Geltungsgrenzen','',
 '- Die 500 Artikel, alle 32 Incidents, 191 ASN-Positionen und 7 SQL-Kontrollen wurden aus der Original-SQLite-Quelle neu gelesen. Korrekter Grain sowie eindeutige Incidents-Koordinaten wurden geprüft.',
 '- Sämtliche nicht betroffenen SKUs liefern nach den Sandbox-Mutationen exakt dieselben DQ-Abfragezeilen wie vorher. S1-Historie, DQ03-Logs und DQ06-Freigaben bleiben unangetastet.',
 '- Zielwertreparatur ist weder Mappinghistorienreparatur noch Incident-Abschluss; dokumentierte HOLDs können zulässige Schutzmaßnahmen sein.',
 '- Die Methode erkennt die Notwendigkeit zusätzlicher Kontrollen, beweist aber keine Vollabdeckung der ursprünglich 26 Fachregeln.','',
 '## 6. Übergabe an Ausführung 4/4','',
 'Die Abschlussintegration muss die Forschungsherleitung, den 20-SKU-Tiefenpilot, das fest definierte Risikomodell, seine Übertragung auf 500 Artikel und die **klar als künstlich gekennzeichnete** Maßnahmen-/Retest-Strecke in **eine** professionelle Bewerbungsfallstudie zusammenführen. Status- und Zahlenangaben müssen gegen die vorliegenden Quelldateien kontrolliert werden; ohne Desktop-Nachweis darf eine neu veränderte Power-BI-Version nicht als nativ abgenommen bezeichnet werden.',''
]
(HERE/'03_Untersuchungsbericht_Skalierung_500.md').write_text('\n'.join(lines),encoding='utf-8')
(HERE/'README.md').write_text('''# Ausführung 3 von 4 – 500 Artikel und kontrollierte Maßnahmen

1. `risikomodell_v2_adapter.py` – exakte Pilotprioritäten RISK-PILOT-1.1, V2-Kohortenadapter.
2. `auswertung_und_retests_v2.py` – alle 500 und 32 Fälle mit Original-SQLite und 7 DQ-Queries; Nachweislücken; fünf simulierte Einzelfall-Tests; unabhängige Assertions.
3. `V2_500_Artikel_Risikomatrix.csv` – rohe, unveränderte Pilotgewichtung auf V2.
4. `V2_500_Artikel_Entscheidungsregister.csv` – zusätzliche nichtgewichtete Kontrolllücken und vollständige Fallzuordnung.
5. `V2_32_Incidents_Einzelfallbericht.md` plus `.json`/`.csv` – 32 fallbezogene Quellnachweise, Entscheidungen und Gate-Kriterien.
6. `V2_Abdeckungsluecken_manueller_Pruefbedarf.csv` – Warnsignale außerhalb des eingefrorenen V1-Score.
7. `V2_EINZELFALL_RETTEST_SANDBOX.sqlite` – **nur hypothetische Testveränderungen**, keine historische Ursprungsdatenbank.
8. `V2_Retest_Vorher_Nachher.csv` und `Ausfuehrung_3_Abnahmeprotokoll.json` – direkt nachgerechnete Werte, Quelle unverändert.

Reproduzierbarer Aufruf:
```bash
python risikomodell_v2_adapter.py --db /pfad/zur/Portfolio_Projekt1_V2_500SKUs.sqlite --sql-dir /pfad/zum/sql --out .
python auswertung_und_retests_v2.py
```

Die zweite Datei verweist für die Nachrechenbarkeit auf die im aktuellen Projektstand vorhandenen Originaldaten. Für eine eigenständige finale ZIP-Version werden Pfade in Ausführung 4/4 relativ und ausführbar gemacht.
''',encoding='utf-8')
print(json.dumps({'status':'PASS','counts':risk_summary['status_500'],'cases':case_coverage,
                  'coverage':len(coverage_by_sku),'baseline_hash':baseline_hash,
                  'sandbox_delta':risk_summary['before_after_sandbox']},ensure_ascii=False,indent=2))
