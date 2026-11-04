#!/usr/bin/env python3
"""Power BI PBIP structure, bindings, M data and KPI numerators independent of Desktop runtime."""
from pathlib import Path
import json,re,base64,csv,io,collections
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'powerbi'/'V2_Desktop_Bestaetigt';b=P/'Portfolio_Projekt1_V2'
model=json.loads((P/(b.name+'.SemanticModel')/'model.bim').read_text(encoding='utf-8'))
report=P/(b.name+'.Report')
assert model['compatibilityLevel']>=1601
assert (P/(b.name+'.pbip')).is_file() and (report/'definition.pbir').is_file()
tables={t['name']:t for t in model['model']['tables']}
counts={}
for name,t in tables.items():
 cols={c['name'] for c in t['columns']}
 m='\n'.join(t['partitions'][0]['source']['expression'])
 raw=base64.b64decode(re.search(r'Binary.FromText\("([A-Za-z0-9+/=]+)"',m).group(1))
 text=raw.decode('utf8');rs=list(csv.DictReader(io.StringIO(text)))
 counts[name]=len(rs)
 assert set(rs[0])==cols
 assert not text.startswith('\ufeff')
 for field in t.get('measures',[]):
  for tn,cn in re.findall(r"'([^']+)'\[([^]]+)\]",field['expression']):
   assert tn in tables and cn in {x['name'] for x in tables[tn]['columns']},(field['name'],tn,cn)
 assert len({r['sku'] for r in rs})==len(rs) if name=='V2_DimProduct' else True
assert counts['V2_DimProduct']==500 and counts['V2_DQ01']==330 and counts['V2_DQ04']==counts['V2_DQ05']==counts['V2_ASN_Prozess']==191
assert counts['INC002_Sandbox']==2 and counts['V2_Pruefmatrix']==500
rels=model['model']['relationships']
assert len(rels)==8 and all(x['toTable']=='V2_DimProduct' and x['toColumn']=='sku' for x in rels)
pages=json.loads((report/'definition'/'pages'/'pages.json').read_text())
assert len(pages['pageOrder'])==3
vcount=0
for page_id in pages['pageOrder']:
 d=report/'definition'/'pages'/page_id;page=json.loads((d/'page.json').read_text())
 visuals={}
 for f in (d/'visuals').glob('*/visual.json'):
  v=json.loads(f.read_text());visuals[v['name']]=v;vcount+=1
  pos=v['position'];assert pos['x']>=0 and pos['y']>=0 and pos['x']+pos['width']<=page['width']+1
  assert pos['y']+pos['height']<=page['height']+1,(page['displayName'],v['name'],pos)
  for role in v['visual'].get('query',{}).get('queryState',{}).values():
   for projection in role['projections']:
    kind,obj=next(iter(projection['field'].items()))
    t=obj['Expression']['SourceRef']['Entity'];c=obj['Property']
    assert t in tables
    acceptable= {x['name'] for x in tables[t]['columns']} if kind=='Column' else {x['name'] for x in tables[t].get('measures',[])}
    assert c in acceptable,(t,c)
 for interaction in page.get('visualInteractions',[]):
  assert interaction['source'] in visuals and interaction['target'] in visuals
assert vcount>=30
assert counts['V2_DQ07']==32
out={'status':'SOURCE_CHECKS_PASS','desktop_opened':False,'source_tables':counts,'relationship_count':len(rels),'report_pages':len(pages['pageOrder']),'visual_count':vcount,'model_data_source':'in-file embedded CSV snapshots; refresh reads same frozen snapshots; not external automatic monitoring'}
(P/'POWERBI_QA_SOURCE_ONLY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('PBIP source validation PASS:',len(tables),'tables,',len(rels),'relationships,',vcount,'visuals')
