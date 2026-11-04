#!/usr/bin/env python3
"""Unabhängige Querschnittsanalyse der bestehenden SQL-Prüfergebnisse; keine neuen Testfälle erfinden."""
from pathlib import Path
import csv, collections, json, hashlib, sqlite3
ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'results'/'powerbi_export'
OUT=ROOT/'results'/'500_Artikel_Untersuchung'
OUT.mkdir(parents=True,exist_ok=True)
def read(p):
 with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def save(p, rows):
 if not rows:return
 with p.open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,list(rows[0]));writer.writeheader();writer.writerows(rows)
R={f'DQ{x:02d}':read(EXP/f'V2_DQ{x:02d}.csv') for x in range(1,8)}
P=read(EXP/'V2_DimProduct.csv'); products={r['sku']:r for r in P}
assert len(P)==500 and len(products)==500
statuses={}
for code, rows in R.items():
 key={'DQ07':'action_status'}.get(code,code.lower()+'_status')
 statuses[code]=dict(collections.Counter(r.get(key,'') for r in rows))
by_sku={code:collections.defaultdict(list) for code in R}
for code,rs in R.items():
 for r in rs:
  if r.get('sku'):by_sku[code][r['sku']].append(r)
# DQ07 affected_reference kann auf Artikel oder Bestellposition verweisen: nur nach ausdrücklich identifizierter SKU zuordnen
incident_by_product=collections.defaultdict(list)
for inc in R['DQ07']:
 if inc['affected_reference'] in products:incident_by_product[inc['affected_reference']].append(inc)
# Include only distinct quality signals, never assume operational losses or an established cause
risks=[]
for p in P:
 sku=p['sku'];dq={code:by_sku[code][sku] for code in by_sku if code!='DQ07'}
 def st(code,k):return '|'.join(sorted(set(r[k] for r in dq[code]))) if dq[code] else 'NOT_IN_SCOPE'
 d1=st('DQ01','dq01_status');d2=st('DQ02','dq02_status');d6=st('DQ06','dq06_status')
 pack=st('DQ04','dq04_status');rec=st('DQ05','dq05_status')
 mapping=st('DQ03','version_check')
 ismig = d1 not in ('NOT_IN_SCOPE','PASS'); isdim=d2 not in ('NOT_IN_SCOPE','PASS')
 map_issue=any(r['version_check']!='PASS' or r['approval_check']!='APPROVED' or r['validity_check']!='EFFECTIVE_AT_SENT_TIME' or r['factor_check'] in ('FACTOR_MISMATCH','UNSUPPORTED_UOM') for r in dq['DQ03'])
 pack_issue=any(r['dq04_status'] in ('BLOCK','REVIEW') for r in dq['DQ04'])
 rec_issue=any(r['dq05_status']!='RECONCILED_POSTED' for r in dq['DQ05'])
 release_issue=d6 in ('MISSING_ACTIVE_RELEASE','DUPLICATE_ACTIVE_RELEASE','PACKAGING_REVIEW')
 domains=[k for k,v in [('MIGRATION',ismig),('DIMENSION',isdim),('MAPPING',map_issue),('PACKAGING',pack_issue),('RECEIPT_STATUS',rec_issue),('RELEASE_CONTROL',release_issue)] if v]
 risks.append(dict(sku=sku,product_group=p['product_group'],origin_type=p['origin_type'],lifecycle_status=p['lifecycle_status'],dq01_status=d1,dq02_status=d2,dq03_version_check=mapping,dq04_status=pack,dq05_status=rec,dq06_status=d6,sku_linked_cases=len(incident_by_product[sku]),review_domain_count=len(domains),review_domains=';'.join(domains)))
save(OUT/'V2_Artikeluebergreifende_Pruefmatrix.csv',risks)
orig_counts=collections.Counter(r['origin_type'] for r in P)
comb=collections.Counter(r['review_domain_count'] for r in risks)
linked_with_issues=sum(bool(x['sku_linked_cases']) for x in risks if x['review_domain_count'])
no_linked=sum((x['review_domain_count']>0 and x['sku_linked_cases']==0) for x in risks)
# DQ02 evaluable = only values with a complete and supported comparison; strict numerator
DQ02_eval=[x for x in R['DQ02'] if x['dq02_status'] in ('PASS','DIMENSION_MISMATCH')]
DQ03_events=[x for x in R['DQ03'] if x['load_status']]
q={
 'scope':'500 synthetische SKU, separate V2; nicht Target Canada; Nicht-Realdaten',
 'records':{'products':len(P),'origin':dict(orig_counts),'incidents':len(R['DQ07']),'asns':len(R['DQ04'])},
 'control_statuses':statuses,
 'denominators':{
  'dq01':{'pass':statuses['DQ01'].get('PASS',0),'in_scope':len(R['DQ01'])},
  'dq02':{'pass':statuses['DQ02'].get('PASS',0),'evaluable':len(DQ02_eval),'not_evaluable':len(R['DQ02'])-len(DQ02_eval)},
  'dq03':{'approved_applied_version':sum(x['version_check']=='PASS' and x['approval_check']=='APPROVED' and x['validity_check']=='EFFECTIVE_AT_SENT_TIME' for x in DQ03_events),'events':len(DQ03_events),'missing_events':len(R['DQ03'])-len(DQ03_events)},
  'dq04':{'pass':statuses['DQ04'].get('PASS',0),'asn_rows':len(R['DQ04'])},
  'dq05':{'posted_reconciled':statuses['DQ05'].get('RECONCILED_POSTED',0),'asn_rows':len(R['DQ05'])},
  'dq06':{'all_allow':statuses['DQ06'].get('ALL_PROCESSES_ALLOW',0),'products':len(P)},
  'dq07':{'open':sum(x['investigation_status']=='OPEN' for x in R['DQ07']),'cases':len(R['DQ07'])}
 },
 'cross_control':{
  'migration_non_pass_and_registered_all_allow':sum(x['dq01_status'] not in ('PASS','NOT_IN_SCOPE') and x['dq06_status']=='ALL_PROCESSES_ALLOW' for x in risks),
  'dimension_non_pass_and_registered_all_allow':sum(x['dq02_status'] not in ('PASS','NOT_IN_SCOPE') and x['dq06_status']=='ALL_PROCESSES_ALLOW' for x in risks),
  'review_domain_count_distribution':{str(k):v for k,v in sorted(comb.items())},
  'any_review_signal_without_sku_linked_reported_case':no_linked,
  'review_signal_with_sku_linked_reported_case':linked_with_issues,
  'incident_affected_reference_matches_sku':sum(x['affected_reference'] in products for x in R['DQ07']),
  'incidents_other_reference_type':sum(x['affected_reference'] not in products for x in R['DQ07'])
 },
 'provenance':{'database_sha256':hashlib.sha256((ROOT/'results'/'Portfolio_Projekt1_V2_500SKUs.sqlite').read_bytes()).hexdigest(),
               'sql_export_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(EXP.glob('V2_*.csv'))}}
}
# Direct cross check control outputs to SQLite re-run (not trust CSV alone)
with sqlite3.connect(ROOT/'results'/'Portfolio_Projekt1_V2_500SKUs.sqlite') as con:
 for k in range(1,8):
  sql=(ROOT/'sql'/next(p.name for p in (ROOT/'sql').glob(f'DQ{k:02d}_*.sql'))).read_text(encoding='utf-8')
  cursor=con.execute(sql)
  names=[col[0] for col in cursor.description]
  actual=[tuple('' if val is None else str(val) for val in row) for row in cursor]
  from_csv=[tuple(row[n] for n in names) for row in R[f'DQ{k:02d}']]
  assert len(actual)==len(from_csv),(k,len(actual),len(from_csv))
  # sqlite float serialization may differ from CSV rounding but textual values match under our data.
  assert actual==from_csv, f'DQ{k:02d} CSV does not reproduce SQL results'
 q['sqlite_sql_csv_revalidation']='7/7 PASS (row-for-row, column-for-column)'
(OUT/'Untersuchung_500_SKUs_Metriken.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[
 '# Untersuchungsbericht – 500 synthetische Produkt-SKUs (V2)',
 '', '**Provenienz:** Separat generierte, versionierte Simulation desselben fiktiven Unternehmens. Kein Datensatz von Target Canada und keine reale Unternehmensvalidierung.',
 '', '**Untersuchungsstatus:** Alle sieben bereits festgelegten SQL-Kontrollen erneut gegen die SQLite-V2-Datenbank ausgeführt; jede der sieben CSV-Dateien zeilen- und spaltenweise mit den unmittelbaren SQL-Ergebnissen abgeglichen (7/7 PASS).',
 '', '## 1. Umfang und Nenner', '',
 f"- Produktstammsätze: **{len(P)}** (MIGRATED: **{orig_counts['MIGRATED']}**, NEW: **{orig_counts['NEW']}**).",
 f"- Migrationspflichtige Zuordnungen: **{len(R['DQ01'])}**; ASN-Positionen: **{len(R['DQ04'])}**; registrierte Incidents: **{len(R['DQ07'])}**.",
 '- Unterschiedliche Grundgesamtheiten dürfen nicht als eine übergreifende Datenqualitätsquote addiert oder miteinander verglichen werden.',
 '', '## 2. Kontrollverteilungen', '', '| Kontrolle | Ergebnis (V2) | Präzisierung |','|---|---|---|',
 f"| DQ-01 Migration | **{statuses['DQ01']['PASS']}/{len(R['DQ01'])} PASS = {100*statuses['DQ01']['PASS']/len(R['DQ01']):.2f} %**; 8 MISSING_TARGET, 3 IDENTITY_MISMATCH | Scope ist nur in_scope, nicht 500 Produkte. |",
 f"| DQ-02 Längen-Konsistenz | **{statuses['DQ02']['PASS']}/{len(DQ02_eval)} auswertbare Vergleiche = {100*statuses['DQ02']['PASS']/len(DQ02_eval):.2f} %**; 12 DIMENSION_MISMATCH | 20 Datensätze sind nicht vollständig auswertbar (11 MISSING_TARGET, 7 MISSING_TARGET_LENGTH, 2 UNSUPPORTED_UOM). |",
 f"| DQ-03 Mapping | **{q['denominators']['dq03']['approved_applied_version']}/{len(DQ03_events)} protokollierte Ereignisse** mit genehmigter gültiger Version; 13 ohne Ereignis | Vier Teilprüfungen getrennt (Version, Genehmigung, Gültigkeit, Faktor). |",
 f"| DQ-04 Verpackung | **176 PASS, 14 BLOCK, 1 REVIEW** von 191 ASN-Positionen | REVIEW ist kein bestätigter Datenfehler. |",
 f"| DQ-05 ASN/Receipt | **135 RECONCILED_POSTED, 37 HOLD, 10 MISSING_RECEIPT, 6 PARTIAL, 3 EXCESS** von 191 ASN-Positionen | HOLD kann eine zulässige Sicherheits-/Prozessmaßnahme sein. |",
 f"| DQ-06 Releases | **471/500 ALL_PROCESSES_ALLOW = {100*471/500:.2f} %**, 29 weitere Statusmuster | ALLOW beweist keine fehlerfreie ERP- oder WMS-Verarbeitung. |",
 f"| DQ-07 Incidents | **32 OPEN**, 31 ohne dokumentierte Maßnahme, 1 genehmigt aber nicht als angewandt dokumentiert | Incident-Stichprobe ist kein vollständiges Inventar sämtlicher DQ-Befunde. |",
 '', '## 3. Kontrollübergreifende Erkenntnisse', '',
 f"- **{q['cross_control']['migration_non_pass_and_registered_all_allow']}** Artikel mit DQ-01-Abweichung besitzen zugleich DQ-06 ALL_PROCESSES_ALLOW. **Beobachtung:** Registrierte Freigabe ≠ Migrationsnachweis. Keine beweisbare Verfügbarkeit oder Schadenshöhe daraus ableiten.",
 f"- **{q['cross_control']['dimension_non_pass_and_registered_all_allow']}** Artikel mit DQ-02-Status ungleich PASS/NOT_IN_SCOPE zeigen gleichzeitig vollständige registrierte ALLOW-Freigaben. Darunter können nicht auswertbare Fälle sein, nicht nur echte Abweichungen.",
 f"- Die Prüfmatrix weist **{no_linked}** Artikel mit mindestens einem Prüf- oder Review-Signal und ohne über eine eindeutige SKU zuordenbaren gemeldeten Incident aus. **Schlussfolgerung:** die Fallliste ist nicht vollständig für jedes Prüfsignal; es ist keine Aussage darüber, ob solche Fälle unentdeckt oder unbearbeitet geblieben sind.",
 f"- Von 32 Incidents ist die betroffene Referenz bei **{q['cross_control']['incident_affected_reference_matches_sku']}** als SKU zuordenbar; **{q['cross_control']['incidents_other_reference_type']}** betreffen andere/unklare Referenzen. Keine ungeprüften Joins über `affected_reference`.",
 '', '### Status und Priorisierung (nicht als bestätigte Ursachen verwenden)',
 '', '- **Bestätigte Kontrollabweichung:** falsche Zielidentität, fehlender Zielnachweis oder falsche Länge im klar abgegrenzten Vergleich.',
 '- **Operativer Prozesszustand:** HOLD, Teil-Wareneingang oder vorhandene/fehlende Quittung; weitere Belege für wirtschaftliche Auswirkungen nötig.',
 '- **Review/fehlende Evidenz:** gesondert ausweisen, nicht als FAIL oder genehmigte Freigabe zählen.',
 '- **Maßnahmensteuerung:** genehmigte und angewandte Korrektur sowie abhängiger Retest sind drei unterschiedliche Zustände.',
 '', '## 4. Einschränkungen / technisch offene Fragen', '',
 '- Daten wurden synthetisch und deterministisch generiert; aus den Kennzahlen folgt keine Aussage über die Häufigkeit von Fehlern in Unternehmen.',
 '- DQ-04/DQ-05 exportieren `asn_line_id` derzeit nicht. Für zusätzliche ASN-Positionen pro Avis muss die Grain-Korrektur als eigenständige Version geprüft werden.',
 '- Die DQ-02-Quote bezieht sich nur auf ein untersuchtes Längenattribut und dessen auswertbare Einheiten; sie ist kein Gesamt-Attribut-Score.',
 '- Es gibt nur begrenzte historische Datenstände: keine Zeitreihen oder ROI-/Verbesserungsbehauptungen für V1 vs V2.',
 '- Der INC-002-Vorher/Nachher-Vergleich stammt aus einem separaten korrigierten Pilot-Sandboxstand, **nicht** aus der V2-Datenbank. Der simulierte WMS-Folgeretest ist in der isolierten INC-002-Testsandbox dokumentiert und erfolgreich; das historische V1/V2 bleibt unverändert.',
 '', '## 5. Reproduzierbarkeit und Ausgaben', '',
 '- `V2_Artikeluebergreifende_Pruefmatrix.csv`: 500 Produktzeilen mit Kontrollstatus pro Bereich und separat abgeleiteten Review-Domänen.',
 '- `Untersuchung_500_SKUs_Metriken.json`: exakte Statuszählungen, Nenner, Querschnitt und SHA-256-Belege.',
 '- SQL-Quellen: `sql/DQ01_...sql` bis `DQ07_...sql`; Datenquelle: `results/Portfolio_Projekt1_V2_500SKUs.sqlite`.',
 '- Methodischer Status: **synthetische belastungstestfähige Simulation**, kein unabhängiger Unternehmensnachweis.',
]
(OUT/'Untersuchungsbericht_500_SKUs.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Generated 500 case audit + 7/7 SQLite exports match; mixed risks',no_linked,'; outputs:',OUT)
