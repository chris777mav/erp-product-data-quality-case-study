#!/usr/bin/env python3
"""Versionierte BI-Reporting-Erweiterung: (asn_id,asn_line_id) ohne Ausgangskontrollen zu verändern."""
from pathlib import Path
import sqlite3,csv,collections,json
ROOT=Path(__file__).resolve().parents[1]
SQL=ROOT/'sql'/'reporting';SQL.mkdir(exist_ok=True)
DB=ROOT/'results'/'Portfolio_Projekt1_V2_500SKUs.sqlite'
OUT=ROOT/'results'/'powerbi_export'

def export(f,rows):
 with f.open('w',newline='',encoding='utf-8-sig') as h:
  w=csv.DictWriter(h,list(rows[0]));w.writeheader();w.writerows(rows)
with sqlite3.connect(DB) as c:
 c.row_factory=sqlite3.Row
 result={}
 for i in (4,5):
  original=next((ROOT/'sql').glob(f'DQ{i:02d}_*.sql'))
  sql=original.read_text(encoding='utf-8')
  assert 'SELECT a.asn_id,' in sql
  enriched=sql.replace('SELECT a.asn_id,','SELECT a.asn_id,a.asn_line_id,',1)
  (SQL/f'DQ{i:02d}_Reporting_mit_ASN_Position.sql').write_text('-- Erweiterte Felder für geprüftes BI-Grain (ASN-ID, ASN-Positions-ID).\n'+enriched,encoding='utf-8')
  before=[dict(r) for r in c.execute(sql)]
  after=[dict(r) for r in c.execute(enriched)]
  assert len(before)==len(after)==191
  assert [ {k:v for k,v in row.items() if k!='asn_line_id'} for row in after]==before
  keys=[(r['asn_id'],r['asn_line_id']) for r in after]
  assert len(keys)==len(set(keys))
  export(OUT/f'V2_DQ{i:02d}_LineLevel.csv',after)
  result[f'DQ{i:02d}']={'rows':len(after), 'original_control_results_unchanged':True,'unique_asn_line_key':True}
 pack=[dict(r) for r in c.execute((SQL/'DQ04_Reporting_mit_ASN_Position.sql').read_text(encoding='utf-8'))]
 receipt=[dict(r) for r in c.execute((SQL/'DQ05_Reporting_mit_ASN_Position.sql').read_text(encoding='utf-8'))]
 index={(r['asn_id'],r['asn_line_id']):r for r in receipt}
 merged=[]
 for p in pack:
  r=index[(p['asn_id'],p['asn_line_id'])]
  assert p['sku']==r['sku']
  merged.append({**p,'announced_qty':r['announced_qty'],'received_qty':r['received_qty'],'receipt_count':r['receipt_count'],'posted_count':r['posted_count'],'hold_count':r['hold_count'],'dq05_status':r['dq05_status']})
 assert len(merged)==191
 export(OUT/'V2_ASN_Business_Process_Join.csv',merged)
 result['ASN_Combined']={'rows':len(merged),'key':'asn_id + asn_line_id','reconciliation':'191 unique positions; original DQ04/DQ05 statuses unchanged'}
 (ROOT/'results'/'500_Artikel_Untersuchung'/'ASN_Join_Validierung.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
 print('PASS BI line-level 191 distinct ASN positions and status preservation')
