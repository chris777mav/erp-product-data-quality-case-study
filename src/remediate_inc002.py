#!/usr/bin/env python3
"""Phase 6: vollständiger, kontrollierter INC-002-Korrekturzyklus IN EINER SYNTHETISCHEN TESTSANDBOX.
Historische V1/V2-Daten und S2 bleiben unverändert; der neue simulierte WMS-Acknowledgement-
Test beweist ausschließlich die definierte Teststrecke, keinen echten externen WMS-Livebetrieb.
"""
from pathlib import Path
import sqlite3, shutil, csv, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'input'/'Portfolio_Phase4_Rohdaten.sqlite'
OUT=ROOT/'results'/'INC002_Simulationssandbox.sqlite'
CSV=ROOT/'results'/'INC002_Vorher_Nachher.csv'
REPORT=ROOT/'results'/'INC002_Retestbericht.json'
EVID=ROOT/'results'/'INC002_WMS_Retest_Evidenz.csv'
S2='S2-2026-09-15'; S3='S3-2026-09-19'; WMS='WMS-2026-09-19-RETEST'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_wms(c):
 """Closure gate: technical delivery, receiver acknowledgement, dimensional and identity
 consistency, packaging continuity. This gate only checks recorded synthetic evidence.
 """
 r=c.execute('SELECT * FROM wms_retest_log WHERE retest_id=?',('RETEST-INC002-001',)).fetchone()
 if not r: return False
 ev=c.execute('SELECT * FROM interface_events WHERE event_id=?',('INT-1006-RETEST',)).fetchone()
 wms=c.execute('SELECT * FROM wms_snapshot WHERE snapshot_id=? AND sku=?',(WMS,'HYG-1006')).fetchone()
 target=c.execute('SELECT * FROM target_snapshot WHERE snapshot_id=? AND sku=?',(S3,'HYG-1006')).fetchone()
 source=c.execute("SELECT * FROM legacy_snapshot WHERE snapshot_id='S0-2026-09-01' AND sku='HYG-1006'").fetchone()
 rule=c.execute("SELECT * FROM mapping_rules WHERE mapping_rule_id='UOM_LENGTH' AND rule_version='R1'").fetchone()
 if not all((ev,wms,target,source,rule)):return False
 expected=round(source['length_value']*rule['factor'],2) if source['dimension_uom']=='IN' else source['length_value']
 return all([
  rule['approval_status']=='APPROVED',abs(expected-203.2)<0.01,
  r['case_id']=='INC-002',r['sku']=='HYG-1006',r['test_environment']=='SIMULATED_WMS_STUB',
  ev['processing_status']=='DELIVERED',ev['received_at'] is not None,
  ev['sku']==target['sku']==wms['sku']==r['sku'],
  ev['target_record_id']==target['target_record_id'],ev['wms_article_id']==wms['wms_article_id'],
  ev['payload_version']==r['payload_version'],r['payload_version']=='V2_CORRECTED_S3',
  r['ack_status']=='ACK_ACCEPTED',
  abs(r['sent_length_mm']-target['length_mm'])<=.01,
  abs(r['received_length_mm']-expected)<=.01,
  r['target_record_id']==target['target_record_id'],r['wms_article_id']==wms['wms_article_id'],
  r['pack_version_id']==wms['accepted_pack_version_id']==target['pack_version_id'],
  r['case_qty']==wms['known_case_qty']==target['case_qty'],
  wms['wms_status']=='ACTIVE'])

def run():
 before_hash=sha(IN)
 if OUT.exists():OUT.unlink()
 shutil.copy2(IN,OUT)
 c=sqlite3.connect(OUT);c.row_factory=sqlite3.Row
 c.execute('BEGIN IMMEDIATE')
 try:
  action=c.execute("SELECT * FROM correction_actions WHERE action_id='FIX-1006-01'").fetchone()
  assert action and action['approved_at'] and action['approved_by'] and action['applied_at'] is None
  assert (action['old_value'],action['proposed_value'],action['field_name'])==(200.0,203.2,'target_snapshot.length_mm')
  source_rows=[dict(x) for x in c.execute('SELECT * FROM target_snapshot WHERE snapshot_id=?',(S2,))]
  assert len(source_rows)==18
  for row in source_rows:
   row['snapshot_id']=S3;row['extracted_at']='2026-09-19T11:00:00'
   if row['sku']=='HYG-1006':
    assert row['length_mm']==200.0
    row['length_mm']=203.2
   keys=list(row)
   c.execute('INSERT INTO target_snapshot ('+','.join(keys)+') VALUES ('+','.join('?' for _ in keys)+')',[row[k] for k in keys])
  c.execute("UPDATE correction_actions SET applied_at='2026-09-19T10:30:00',dependent_retest_status='PENDING_WMS_RECHECK',closure_status='OPEN' WHERE action_id='FIX-1006-01'")
  # Hier wird ausdrücklich eine NEUE, fiktive WMS-Teststrecke aufgebaut, nicht ein fehlendes
  # historisches WMS-Log rückdatiert. Das unveränderte Original-Snapshot bleibt erhalten.
  c.execute('INSERT INTO interface_events VALUES (?,?,?,?,?,?,?,?,?)',(
   'INT-1006-RETEST','HYG-1006','ERP-9006','WMS-1006',
   '2026-09-19T11:15:00','2026-09-19T11:15:01','DELIVERED',None,'V2_CORRECTED_S3'))
  c.execute('INSERT INTO wms_snapshot VALUES (?,?,?,?,?,?,?)',(
   WMS,'2026-09-19T11:16:00','WMS-1006','HYG-1006','PK-1006-A',24,'ACTIVE'))
  c.execute('''CREATE TABLE wms_retest_log(
   retest_id TEXT PRIMARY KEY,case_id TEXT,sku TEXT,test_environment TEXT,
   target_record_id TEXT,wms_article_id TEXT,payload_version TEXT,
   sent_length_mm REAL,received_length_mm REAL,pack_version_id TEXT,case_qty INTEGER,
   ack_status TEXT,checked_at TEXT,checked_by TEXT)''')
  # Simulierte Antwort des WMS-Stub: aus dem generierten Testfixture, NICHT vom echten WMS.
  c.execute('INSERT INTO wms_retest_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
   'RETEST-INC002-001','INC-002','HYG-1006','SIMULATED_WMS_STUB','ERP-9006','WMS-1006',
   'V2_CORRECTED_S3',203.2,203.2,'PK-1006-A',24,'ACK_ACCEPTED',
   '2026-09-19T11:16:30','SIMULATED_QA_GATE'))
  assert verify_wms(c),'WMS positive test failed'
  # Gegenprobe: ein erneut falscher Wert würde das Closure-Gate sperren.
  c.execute("UPDATE wms_retest_log SET received_length_mm=200.0 WHERE retest_id='RETEST-INC002-001'")
  assert not verify_wms(c),'WMS negative test did not detect mismatch'
  c.execute("UPDATE wms_retest_log SET received_length_mm=203.2 WHERE retest_id='RETEST-INC002-001'")
  assert verify_wms(c)
  sql=(ROOT/'sql'/'DQ02_Dimension_Consistency.sql').read_text(encoding='utf8')
  comparison=[]
  for snap,label in [(S2,'BEFORE'),(S3,'AFTER')]:
   rows=[dict(r) for r in c.execute(sql.replace(S2,snap))]
   sku=next(r for r in rows if r['sku']=='HYG-1006')
   evaluable=[r for r in rows if r['dq02_status'] in ('PASS','DIMENSION_MISMATCH')]
   passed=sum(r['dq02_status']=='PASS' for r in evaluable)
   comparison.append(dict(stage=label,snapshot_id=snap,sku='HYG-1006',
    expected_length_mm=sku['expected_length_mm'],actual_length_mm=sku['actual_length_mm'],
    dq02_status=sku['dq02_status'],pass_count=passed,evaluable_count=len(evaluable),
    pass_ratio=round(passed/len(evaluable),6),action_applied_in_simulated_sandbox=int(label=='AFTER'),
    wms_dependent_retest_status='PASSED_SIMULATED_WMS' if label=='AFTER' else 'PENDING_WMS_RECHECK',
    incident_status='CLOSED_IN_SIMULATION' if label=='AFTER' else 'OPEN'))
  assert [(x['pass_count'],x['evaluable_count'],x['dq02_status']) for x in comparison]==[(12,13,'DIMENSION_MISMATCH'),(13,13,'PASS')]
  assert c.execute("SELECT length_mm FROM target_snapshot WHERE snapshot_id=? AND sku='HYG-1006'",(S2,)).fetchone()[0]==200.0
  assert c.execute("SELECT length_mm FROM target_snapshot WHERE snapshot_id=? AND sku='HYG-1006'",(S3,)).fetchone()[0]==203.2
  # Abschluss erst NACH positivem kontrolliertem WMS-Nachtest, nie als realer Incident-Abschluss.
  c.execute("UPDATE correction_actions SET dependent_retest_status='PASSED_SIMULATED_WMS',closure_status='CLOSED' WHERE action_id='FIX-1006-01'")
  c.execute("UPDATE reported_cases SET investigation_status='CLOSED' WHERE case_id='INC-002'")
  c.execute('INSERT INTO issue_evidence VALUES (?,?,?,?,?,?,?)',(
   'EVID-INC002-RETEST','INC-002','wms_retest_log','RETEST-INC002-001','AVAILABLE',
   '2026-09-19T11:16:30','Controlled simulated WMS stub accepted 203.2 mm; negative receiver-value check rejected 200.0 mm'))
  c.commit()
 except Exception:c.rollback();c.close();raise
 v=c.execute("SELECT * FROM reported_cases WHERE case_id='INC-002'").fetchone()
 ac=c.execute("SELECT * FROM correction_actions WHERE action_id='FIX-1006-01'").fetchone()
 assert v['investigation_status']=='CLOSED' and ac['closure_status']=='CLOSED' and verify_wms(c)
 dq07=[dict(r) for r in c.execute((ROOT/'sql'/'DQ07_Incident_Action_Monitoring.sql').read_text())]
 d=next(r for r in dq07 if r['case_id']=='INC-002')
 assert d['action_status']=='ACTIONS_MARKED_CLOSED' and d['investigation_status']=='CLOSED',d
 assert sum(r['investigation_status']=='OPEN' for r in dq07)==10
 assert sha(IN)==before_hash
 with CSV.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
 wmsdict=[dict(r) for r in c.execute('SELECT * FROM wms_retest_log')]
 with EVID.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(wmsdict[0]));w.writeheader();w.writerows(wmsdict)
 REPORT.write_text(json.dumps({
  'environment':'SYNTHETIC_ISOLATED_WMS_STUB_ONLY','original_v1_sha256_preserved':before_hash,
  'historical_s2_unchanged':True,'s3_added':True,'correction_applied_in_sandbox':True,
  'rule_check':'approved R1 * 25.4 verified','dq02_before':'12/13',
  'dq02_after':'13/13','wms_retest_passed_in_simulation':True,
  'wms_negative_control_passed':True,'incident_closed_in_sandbox':True,
  'historic_incident_still_open_in_original_v1_and_v2':True,
  'dqo7_after_sandbox':d,'rows':comparison,
  'wms_test_evidence':wmsdict,
  'limitations':['Synthetic WMS response is a test fixture, not a real WMS system log.',
  'No real operations, real supplier/warehouse, or external independent validation.',
  'Sandbox-only closure does not modify V1/V2 historical incident status or 500-product Power BI KPI.']
 },indent=2,ensure_ascii=False),encoding='utf8')
 c.close()
 print('PHASE6: INC-002 CLOSED IN SYNTHETIC SANDBOX ONLY; DQ02 12/13 -> 13/13, WMS closure gate & negative test PASS, V1 unchanged')
if __name__=='__main__':run()
