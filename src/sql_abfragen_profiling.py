#!/usr/bin/env python3
"""Repeatable SQL profiles incl. EXPLAIN QUERY PLAN for both synthetic populations.
Elapsed time is only an orientation on this runner, never an SLA or scaling benchmark.
"""
from pathlib import Path
import sqlite3, time, json, statistics
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'Phase7_SQL_Ausfuehrungsnachweise.json'
obj={'method':'sqlite3 EXPLAIN QUERY PLAN; 3 measured executions after one warm up, same machine, no benchmark validity','versions':{}}
for label,p in [('V1',ROOT/'input'/'Portfolio_Phase4_Rohdaten.sqlite'),('V2',ROOT/'results'/'Portfolio_Projekt1_V2_500SKUs.sqlite')]:
 c=sqlite3.connect(p);r={}
 for sqlfile in sorted((ROOT/'sql').glob('DQ*.sql')):
  sql=sqlfile.read_text(encoding='utf-8');key=sqlfile.name[:4]
  plan=[{'id':a,'parent':b,'detail':d} for a,b,_,d in c.execute('EXPLAIN QUERY PLAN '+sql)]
  c.execute(sql).fetchall();runs=[]
  for _ in range(3):
   start=time.perf_counter_ns(); rows=c.execute(sql).fetchall();runs.append(round((time.perf_counter_ns()-start)/1000000,3))
  r[key]={'rows':len(rows),'measured_ms':runs,'median_ms':round(statistics.median(runs),3),'explain_query_plan':plan}
 obj['versions'][label]=r
 c.close()
assert len(obj['versions'])==2 and all(len(x)==7 for x in obj['versions'].values())
OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Phase7 14 SQL EXPLAIN QUERY PLAN runs, 42 timed executions, status PASS')
