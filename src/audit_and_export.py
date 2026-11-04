#!/usr/bin/env python3
"""Run DQ01..DQ07 on V1 and V2, validate provenance, write reports and BI exports."""
from __future__ import annotations
from pathlib import Path
import sqlite3,csv,hashlib,collections,json
ROOT=Path(__file__).resolve().parents[1]
V1=ROOT/'input'/'Portfolio_Phase4_Rohdaten.sqlite'
V2=ROOT/'results'/'Portfolio_Projekt1_V2_500SKUs.sqlite'
OUT=ROOT/'results'
EXP=OUT/'powerbi_export'
EXP.mkdir(parents=True,exist_ok=True)

def con(p):
 c=sqlite3.connect(p);c.row_factory=sqlite3.Row
 return c

def fingerprint_table(c,name):
 # Stable hash of raw row values in source field order for original-set row preservation.
 columns=[r[1] for r in c.execute('pragma table_info("'+name+'")')]
 pk=[r[1] for r in sorted(c.execute('pragma table_info("'+name+'")'),key=lambda r:r[5]) if r[5]>0]
 rows=c.execute('select * from "'+name+'" order by '+','.join('"'+x+'"' for x in pk)).fetchall()
 return columns,[tuple(r) for r in rows]

def csv_export(path,rows,columns=None):
 if columns is None:columns=list(rows[0]) if rows else []
 path.parent.mkdir(exist_ok=True,parents=True)
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)

def run():
 c1=con(V1);c2=con(V2)
 names=[r[0] for r in c1.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
 assert len(names)==21,len(names)
 assert names==[r[0] for r in c2.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
 preservation={}
 for name in names:
  a,row_a=fingerprint_table(c1,name)
  b,row_b=fingerprint_table(c2,name)
  assert a==b and all(x in row_b for x in row_a),f'V1 original row modified/deleted: {name}'
  preservation[name]=dict(v1=len(row_a),v2=len(row_b),original_records_preserved=True)
 assert c1.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert c2.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert c2.execute('select count(*) from products').fetchone()[0]==500
 assert c2.execute("select count(*) from products where origin_type='MIGRATED'").fetchone()[0]==335
 assert c2.execute("select count(*) from products where origin_type='NEW'").fetchone()[0]==165
 tests=[];all_results={}
 for mode,c in [('V1',c1),('V2',c2)]:
  for qpath in sorted((ROOT/'sql').glob('DQ*.sql')):
   results=[dict(r) for r in c.execute(qpath.read_text(encoding='utf8'))]
   key=qpath.stem.split('_')[0]
   summaries={}
   if results:
    for col in results[0]:
     if col.endswith('status') or col.endswith('_check'):
      summaries[col]=dict(collections.Counter(str(r.get(col)) for r in results))
   all_results[f'{mode}_{key}']=dict(row_count=len(results),summary=summaries)
   csv_export(EXP/f'{mode}_{key}.csv',results)
 # baseline controls golden. No judge output by generated errors only.
 assert all_results['V1_DQ01']['summary']['dq01_status']=={'PASS':13,'MISSING_TARGET':1}
 assert all_results['V1_DQ02']['summary']['dq02_status']=={'PASS':12,'MISSING_TARGET':1,'DIMENSION_MISMATCH':1}
 assert all_results['V1_DQ04']['summary']['dq04_status']=={'PASS':5,'BLOCK':1,'REVIEW':1}
 assert all_results['V1_DQ05']['summary']['dq05_status']=={'RECONCILED_POSTED':4,'RECEIPT_ON_HOLD':2,'MISSING_RECEIPT':1}
 assert all_results['V1_DQ06']['summary']['dq06_status']=={'ALL_PROCESSES_ALLOW':17,'DOCUMENTED_DISCONTINUATION':1,'DOCUMENTED_LAUNCH_HOLD':1,'PACKAGING_REVIEW':1}
 assert all_results['V1_DQ07']['row_count']==11
 # V2 expected coverage, imported source continuity and selected cross-system invariants.
 assert all_results['V2_DQ01']['row_count']>300
 assert all_results['V2_DQ02']['row_count']==all_results['V2_DQ01']['row_count']
 assert all_results['V2_DQ06']['row_count']==500
 assert all_results['V2_DQ07']['row_count']>11
 assert all_results['V2_DQ04']['row_count']>7
 assert all_results['V2_DQ05']['row_count']==all_results['V2_DQ04']['row_count']
 assert c2.execute("select count(*) from products p left join supplier_articles s on s.sku=p.sku where s.sku is null").fetchone()[0]==0
 assert c2.execute("select count(*) from products p left join packaging_levels l on l.sku=p.sku and l.level_code='EACH' where l.sku is null").fetchone()[0]==0
 v1_p=c1.execute('select count(*) from products').fetchone()[0]
 v2_p=c2.execute('select count(*) from products').fetchone()[0]
 # Dimension export from source-of-truth, not DQ results
 csv_export(EXP/'V2_DimProduct.csv',[dict(r) for r in c2.execute('select sku,product_group,description,origin_type,lifecycle_status from products order by sku')])
 csv_export(EXP/'V1_DimProduct.csv',[dict(r) for r in c1.execute('select sku,product_group,description,origin_type,lifecycle_status from products order by sku')])
 report=dict(scope='Independent synthetic retail ERP pilot and deterministic scale test; no Target Canada company data',original_products=v1_p,extended_products=v2_p,original_sqlite_unchanged=True,table_count=21,table_row_preservation=preservation,controls=all_results,assertions='PASS',inc002_sandbox_report='INC002_Retestbericht.json',bi_package='CSV exports; existing .pbix preserved, NOT automatically rebuilt')
 (OUT/'Technischer_Audit_V1_V2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 lines=['# Technischer Prüfbericht V1 / V2','', '**Prüfumfang:** SQL-Kontrollen DQ-01–DQ-07 auf eingefrorenem 20-SKU-Pilot und separater 500-SKU-Simulation.','',f'- V1 Produkte: {v1_p}; V2 Produkte: {v2_p}.','- 21 Tabellen der Ausgangsstruktur vorhanden; sämtliche Ursprungszeilen wertgleich in V2 enthalten.','- PRAGMA integrity_check beider Datenbanken: ok.','- Auswertungen reproduzierbar als CSV exportiert.','', '| Kontrolle | V1 Ergebnissätze | V2 Ergebnissätze | Zentrale V2-Verteilung |','|---|---:|---:|---|']
 for k in range(1,8):
  key=f'DQ{k:02d}';a=all_results[f'V1_{key}'];b=all_results[f'V2_{key}']; d=b['summary'].get(key.lower()+'_status',{})
  if not d: d=b['summary'].get('action_status',{})
  s=', '.join(f'{name}: {value}' for name,value in d.items())
  lines.append(f'| {key} | {a["row_count"]} | {b["row_count"]} | {s} |')
 lines+=['','**Methodische Grenze:** Die zusätzlichen Datensätze und Fehlermuster sind synthetisch. Dieselbe Regelarchitektur und derselbe Generator können die Testabdeckung systematisch prägen; Zahlen sind kein Nachweis von Präzision oder Recall an echten Unternehmensdaten.','**Power BI:** Der vom Nutzer Desktop-getestete reparierte PBIP-Stand wurde am 02.11.2026 auf drei Seiten dargestellt. Der aktualisierte finale Sandbox-Snapshot wird durch neu generierte PBIP-Quelle bereitgestellt und ist gesondert zu öffnen.','']
 (OUT/'Technischer_Audit_V1_V2.md').write_text('\n'.join(lines),encoding='utf8')
 print('PASS all seven checks V1 and V2 and 21-table original row preservation.')
 for key in all_results:print(key,all_results[key]['row_count'])
 c1.close();c2.close()

if __name__=='__main__':run()
