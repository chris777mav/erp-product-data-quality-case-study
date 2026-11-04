#!/usr/bin/env python3
"""Stdlib-only integration checks for the unified synthetic case study.

Scope: integrity of packaged data, risk and incident files, cross-cohort
regression evidence, and transparent release boundaries. No production
ERP/WMS or live Power BI Desktop test is claimed here.
"""
from pathlib import Path
import sqlite3,csv,json,hashlib,collections
ROOT=Path(__file__).resolve().parents[1]
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(p, msg):
    if not p:raise AssertionError(msg)
    return msg
checks=[]
def t(p, msg):checks.append(check(p,msg))

base=ROOT/'input/Portfolio_Phase4_Rohdaten.sqlite'
v2=ROOT/'results/Portfolio_Projekt1_V2_500SKUs.sqlite'
t(sha(base)=='01b071db832cb21f25f7fc0e39811c101e78f66b0febea5720e068209e5b3ee7','20-article original SHA256 unchanged')
t(sha(v2)=='e212a6f317a593055aa62897d63697d613feba012427bb934157044241bc77be','500-article original SHA256 unchanged')
for path,n,k in [(base,20,11),(v2,500,32)]:
    c=sqlite3.connect(f'file:{path.resolve()}?mode=ro',uri=True)
    t(c.execute('pragma integrity_check').fetchone()[0]=='ok','SQLite integrity '+str(n))
    t(c.execute("select count(*) from sqlite_master where type='table'").fetchone()[0]==21,'21 relations '+str(n))
    t(c.execute('select count(*) from products').fetchone()[0]==n,'products count '+str(n))
    t(c.execute('select count(distinct sku) from products').fetchone()[0]==n,'products unique '+str(n))
    t(c.execute('select count(*) from reported_cases').fetchone()[0]==k,'cases count '+str(n))
    t(c.execute("select count(*) from reported_cases where investigation_status='OPEN'").fetchone()[0]==k,'historical cases OPEN '+str(n))
    c.close()

pilot=rows(ROOT/'risk/methodenvalidierung/Pilot_20_Artikel_Risikomatrix.csv')
large=rows(ROOT/'risk/skalierung/V2_500_Artikel_Risikomatrix.csv')
t(len(pilot)==20 and len({r['sku'] for r in pilot})==20,'20 unique pilot risk classifications')
t(len(large)==500 and len({r['sku'] for r in large})==500,'500 unique V2 risk classifications')
p1=collections.Counter(r['prioritaet'] for r in pilot)
p2=collections.Counter(r['prioritaet'] for r in large)
t(p1=={'P1':6,'P2':4,'P3':1,'P4':9},'pilot P1-P4 scores')
t(p2=={'P1':83,'P2':29,'P3':1,'P4':387},'V2 P1-P4 scores')
m={x['sku']:x for x in large}
t(all(x['sku'] in m and (x['prioritaet'],x['dq_signale'])==(m[x['sku']]['prioritaet'],m[x['sku']]['dq_signale']) for x in pilot),'20-of-20 pilot cohort signal regression')
ci1=rows(ROOT/'risk/methodenvalidierung/Pilot_11_Incidents_Tiefenanalyse.csv')
ci2=rows(ROOT/'risk/skalierung/V2_32_Incidents_Fachentscheidungen.csv')
t(len(ci1)==11 and len({r['incident'] for r in ci1})==11,'11 unique pilot case files')
t(len(ci2)==32 and len({r['incident_id'] for r in ci2})==32,'32 unique V2 case files')
t(all(r['historischer_incident_status']=='OPEN' and r['abschlussbedingung'] for r in ci1),'pilot cases open with closure condition')
t(all(r['historischer_status']=='OPEN' and r['massnahme_vorgeschlagen'] for r in ci2),'V2 cases open with action')
t(all(r['sku'] in m for r in ci2),'V2 case references resolved to product grain')
scenario=rows(ROOT/'risk/methodenvalidierung/Pilot_16_Akzeptanzfaelle_Abgleich.csv')
t(len(scenario)==16,'16 pilot scenarios')
t(sum(r['vorgesehene_abdeckung']=='TEILWEISE' for r in scenario)==3,'three documented scenario limitations')
t(all(r['datenpruefung']=='PASS' for r in scenario),'16 data tests PASS')
negative=rows(ROOT/'risk/methodenvalidierung/Pilot_Negativtests_Isolierte_Kopien.csv')
t(len(negative)==7 and all(r['status']=='PASS' for r in negative),'seven independent pilot mutation tests')
report=json.loads((ROOT/'risk/skalierung/Ausfuehrung_3_Abnahmeprotokoll.json').read_text(encoding='utf-8'))
t(report['v1_pilot_20_score_signal_regression']=='20/20 IDENTISCH','V2 regression evidence')
t(report['allow_with_weighted_warning_500']==104,'104 broad ALLOW with weighted signal')
t(report['migration_nonpass_allow_overlap']==11,'11 DQ01/ALLOW overlaps')
t(report['unweighted_coverage_flags_skus']==28,'28 separately flagged coverage cases')
t(report['case_reconciliation']['risk_or_coverage_flags_without_mapped_case_skus']==97,'97 unmatched flagged SKUs')
t(report['case_reconciliation']['direct_SKU']==28 and report['case_reconciliation']['indirect_PO_Receipt_ASN']==4,'32 incidents fully mapped')
t(len(report['changes_test_only'])==5,'four corrections plus one negative control')
t(report['before_after_sandbox']['DQ02_PASS']=={'source':298,'simulation':301,'difference':3},'dimension PASS source/sandbox')
t(report['before_after_sandbox']['DQ02_EVALUABLE']=={'source':310,'simulation':311,'difference':1},'dimension denominator source/sandbox')
t(report['before_after_sandbox']['DQ07_OPEN']['source']==report['before_after_sandbox']['DQ07_OPEN']['simulation']==32,'V2 cases not auto closed')
t(all(status=='PASS' for status in report['tests'].values()),'13 stage-3 audit categories PASS')
t(len(list((ROOT/'sql').glob('DQ[0-9][0-9]_*.sql')))==7,'seven SQL check files')
t(len(list(ROOT.rglob('*.pdf')))==1,'one PDF total')
t((ROOT/'Portfolio_Projekt1_GESAMT_FALLSTUDIE_FINAL.pdf').stat().st_size>250000,'full PDF exists')
t((ROOT/'research/Problemherleitung_und_Quellenauswahl.md').exists(),'researched background included')
t((ROOT/'powerbi/V2_Desktop_Bestaetigt/Portfolio_Projekt1_V2.pbip').exists(),'three-page V2 PBIP included')
t((ROOT/'powerbi/Phase6_DataQuality_CommandCenter_OFFLINE.html').exists(),'offline Action Center included')
t(not any('/mnt/data/' in (ROOT/p).read_text(encoding='utf-8') for p in ['risk/skalierung/auswertung_und_retests_v2.py','risk/methodenvalidierung/fallbearbeitung_validieren.py']),'risk regeneration scripts portable')
if __name__=='__main__':print(f'Unified risk portfolio checks: {len(checks)}/{len(checks)} PASS')
