#!/usr/bin/env python3
"""Narrow factual audit for the public synthetic case-study package. Stdlib only."""
from pathlib import Path
import sqlite3,csv,collections,hashlib
R=Path(__file__).resolve().parents[1]
assert len(list(R.rglob('*.pdf')))==1, 'Expected exactly one PDF'
pdf=R/'Portfolio_Projekt1_GESAMT_FALLSTUDIE_FINAL.pdf'
assert pdf.read_bytes()[:5]==b'%PDF-' and pdf.stat().st_size>100000
assert not (R/'powerbi/V3_Aktionssteuerung_Entwurf').exists()
assert (R/'powerbi/Phase6_DataQuality_CommandCenter_OFFLINE.html').is_file()
assert (R/'powerbi/V2_Desktop_Bestaetigt/Portfolio_Projekt1_V2.pbip').is_file()

C=0
for db,total in [('input/Portfolio_Phase4_Rohdaten.sqlite',20),('results/Portfolio_Projekt1_V2_500SKUs.sqlite',500)]:
    c=sqlite3.connect(R/db)
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
    assert c.execute('select count(*) from products').fetchone()[0]==total
    assert len(c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall())==21
    c.close(); C+=3

def rows(name):
    with (R/'results/powerbi_export'/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))
q1=rows('V2_DQ01.csv');q2=rows('V2_DQ02.csv');q6=rows('V2_DQ06.csv');q7=rows('V2_DQ07.csv');a=rows('V2_ActionQueue.csv')
assert len(q1)==330 and collections.Counter(x['dq01_status'] for x in q1)['PASS']==319
assert collections.Counter(x['dq02_status'] for x in q2)['PASS']==298
assert len(q6)==500 and collections.Counter(x['dq06_status'] for x in q6)['ALL_PROCESSES_ALLOW']==471
assert len(q7)==32 and all(x['investigation_status']=='OPEN' for x in q7)
assert len(a)==500 and collections.Counter(x['priority_code'] for x in a)=={'P1':11,'P2':94,'P3':20,'P0':375}
assert len({x['sku'] for x in a})==500
m={x['sku']:x for x in q6}
conflict=sum(x['dq01_status']!='PASS' and m[x['sku']]['dq06_status']=='ALL_PROCESSES_ALLOW' for x in q1)
assert conflict==11, conflict
C+=8
for sql in (R/'sql').glob('DQ*.sql'):
    assert 'SELECT' in sql.read_text(encoding='utf8').upper()
    C+=1
assert C>=21
print('Public release data and PDF inventory PASS; reference checks',C)
