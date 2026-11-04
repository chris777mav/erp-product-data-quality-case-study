#!/usr/bin/env python3
"""Seven isolated negative tests on in-memory copies of original synthetic V1.
Not independent external data. Each test must change the corresponding DQ outcome.
"""
from pathlib import Path
import hashlib,sqlite3,json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'input'/'Portfolio_Phase4_Rohdaten.sqlite'
SQL=ROOT/'sql'
BEFORE=hashlib.sha256(SRC.read_bytes()).hexdigest()

def make_copy():
 a=sqlite3.connect(SRC);b=sqlite3.connect(':memory:');a.backup(b);a.close();b.row_factory=sqlite3.Row
 return b

def result(c,k,sku=None,case=None,asn=None):
 rows=[dict(x) for x in c.execute((SQL/(k+'_'+{'DQ01':'Migration_Completeness','DQ02':'Dimension_Consistency','DQ03':'Mapping_Rule_Compliance','DQ04':'Packaging_Compliance','DQ05':'ASN_Receipt_Reconciliation','DQ06':'Release_Readiness','DQ07':'Incident_Action_Monitoring'}[k]+'.sql')).read_text(encoding='utf8'))]
 return next(x for x in rows if (sku is None or x.get('sku')==sku) and (case is None or x.get('case_id')==case) and (asn is None or x.get('asn_id')==asn))

def test(n,k,fn,who,field,expect_before,expect_after):
 c=make_copy();b=result(c,k,**who)[field]
 assert b==expect_before,(n,b,expect_before)
 fn(c)
 a=result(c,k,**who)[field]
 assert a==expect_after,(n,a,expect_after)
 c.close();return dict(test=n,control=k,field=field,before=b,after=a,status='PASS')

checks=[
 test('Delete migrated target record','DQ01',lambda c:c.execute("delete from target_snapshot where sku='HYG-1001' and snapshot_id='S2-2026-09-15'"),{'sku':'HYG-1001'},'dq01_status','PASS','MISSING_TARGET'),
 test('Corrupt dimension','DQ02',lambda c:c.execute("update target_snapshot set length_mm=155 where sku='HYG-1001' and snapshot_id='S2-2026-09-15'"),{'sku':'HYG-1001'},'dq02_status','PASS','DIMENSION_MISMATCH'),
 test('Change applied mapping version','DQ03',lambda c:c.execute("update migration_events set applied_rule_version='BAD_VERSION' where legacy_record_id='ALT-1001'"),{'sku':'HYG-1001'},'version_check','PASS','VERSION_MISMATCH'),
 test('Corrupt ASN quantity','DQ04',lambda c:c.execute("update asns set announced_base_qty=999 where asn_id='ASN-0001'"),{'asn':'ASN-0001'},'dq04_status','PASS','BLOCK'),
 test('Delete receipt log','DQ05',lambda c:c.execute("delete from receipts where asn_id='ASN-0001'"),{'asn':'ASN-0001'},'dq05_status','RECONCILED_POSTED','MISSING_RECEIPT'),
 test('Remove active release','DQ06',lambda c:c.execute("delete from releases where sku='HYG-1001' and process_code='WMS_RECEIPT'"),{'sku':'HYG-1001'},'dq06_status','ALL_PROCESSES_ALLOW','MISSING_ACTIVE_RELEASE'),
 test('Invalidate evidence availability','DQ07',lambda c:c.execute("update issue_evidence set evidence_availability='MISSING' where case_id='INC-002'"),{'case':'INC-002'},'evidence_status','ALL_RECORDED_EVIDENCE_AVAILABLE','MISSING_EVIDENCE_RECORDED')
]
AFTER=hashlib.sha256(SRC.read_bytes()).hexdigest()
assert BEFORE==AFTER
(ROOT/'results'/'DQ_Negativproben_Ergebnisse.json').write_text(json.dumps({'simulated_data_only':True,'tests':checks,'passed':len(checks),'total':len(checks),'v1_unchanged_hash':BEFORE},ensure_ascii=False,indent=2),encoding='utf8')
print(len(checks),'of',len(checks),'negative tests PASS, original unchanged')
