#!/usr/bin/env python3
"""Ausführung 2/4: evidenzgebundene Tiefenakten und unabhängige Pilotvalidierung.

Kein produktives System, keine externen Kundendaten. Historische SQLite-Datei read-only.
Die erwarteten Einzelfallzustände sind fachliche Testorakel aus dem zuvor definierten
Szenariokonzept; die Mutationen laufen ausschließlich in temp. SQLite-Kopien.
"""
import argparse,sqlite3,json,csv,hashlib,tempfile,subprocess,sys,collections,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]  # repository root
DEFAULT_DB=PROJECT/'input/Portfolio_Phase4_Rohdaten.sqlite'
SQL_DIR=PROJECT/'sql'

# Diese Aussagen sind fachliche Entscheidungen / hypothetische weitere Maßnahmen,
# nicht vorgetäuschte Ergebnisse zusätzlicher Systemabfragen.
CASES={
 'INC-001':dict(subject='Fehlender migrationspflichtiger Zielartikel', verdict='MIGRATION_ABWEICHUNG_NACHGEWIESEN',cause='UNGEKLAERT',owner='ERP-Migration / MDM',
  factual='Der genehmigte Migrationsumfang enthält ALT-1004 mit Ziel-ID ERP-9004. Im S2-Zielsnapshot fehlt HYG-1004; im bereitgestellten Eventabzug fehlt ALT-1004.',
  limitation='Das fehlende Ereignis identifiziert weder eine bestimmte ETL-Störung noch die Ursache der Nichtübernahme.',
  immediate='Identitätsmapping und Scope erneut abstimmen; Job-/Error-/Dead-letter-Logs am Quellsystem beschaffen; keinen ungeprüften Produktdatensatz nachladen.',
  closure='Zielidentität im neuen Snapshot nachgewiesen, Event-/Reconciliation-Nachweis vorhanden, angebundene Freigaben und WMS-Folgeverarbeitung getestet.'),
 'INC-002':dict(subject='Falsche Längentransformation', verdict='FEHLER_UND_ANGEWENDETE_FALSCHE_MAPPINGVERSION_BELEGT',cause='TRANSFORMATION_REGELVERSION_BELEGT',owner='ERP / MDM / WMS',
  factual='Der Legacy-Wert 8 IN entspricht 203,2 mm. In S2 stehen 200,0 mm; MIG-E-1006 protokolliert Faktor 25,0 und die nicht genehmigte abgelaufene Version.',
  limitation='Warum die falsche Regel im Lauf ausgewählt wurde, ist nicht belegt. Historischer Case bleibt OPEN. Der spätere WMS-Stubsandbox-Abschluss ist kein produktiver WMS-Test.',
  immediate='Genehmigte R1-Regel verwenden; vierstufigen Vorher-/Nachher-, Ereignis-, WMS- und Negativretest ausschließlich im separaten Simulationszweig führen.',
  closure='Genehmigte Anwendung, Zielwert 203,2 mm, DQ02-Retest, bestätigter WMS-Test und dokumentierte Freigabe; nur isolierter Simulationszweig kann als CLOSED_IN_SIMULATION gelten.'),
 'INC-003':dict(subject='Nicht genehmigte Kartonaufteilung', verdict='VERPACKUNGSKONFLIKT_UND_HOLD_BELEGT',cause='UNBEKANNTE_URSACHE_DER_LIEFERANTENABWEICHUNG',owner='Einkauf / Lieferant / WMS',
  factual='PO-0007 verlangt zehn Kartons zu je 100 Stück; ASN-0007 meldet vier Kartons zu je 250 Stück ohne genehmigte Packversion. Gesamtmenge jeweils 1.000. REC-0007 steht auf HOLD.',
  limitation='Gleiche Gesamtmenge ersetzt keine Freigabe der Verpackungsebene. Ob Lieferant, ASN-Erstellung oder ERP-Mapping ursächlich war, bleibt offen.',
  immediate='Lieferantennachweis und Verpackungsversion anfordern; HOLD bis zur fachlichen Packfreigabe beibehalten; WMS-Verarbeitung nicht aus Mengengleichheit ableiten.',
  closure='Bestätigte, zeitlich gültige Verpackung + korrespondierendes ASN/PO + WMS-Retest; HOLD dokumentiert aufgehoben, falls fachlich gerechtfertigt.'),
 'INC-004':dict(subject='Genehmigte nachträgliche Verpackungsänderung',verdict='GUELTIGE_AENDERUNG_MIT_ZEITBEZOGENEM_REVIEW',cause='KEIN_TECHNISCHER_FEHLER_NACHGEWIESEN',owner='Einkauf / MDM',
  factual='CHG-1008 ist am 15.09. um 16:00 genehmigt, ab 16.09. gültig. PO-0008 wurde am 15.09. um 10:00 erstellt; ASN-0008 ging am 16.09. mit PK-1008-B und 8×125 ein. Receipt ist POSTED.',
  limitation='Freigabe liegt nach Bestellzeitpunkt; die vorhandene Regel fordert REVIEW, obwohl die Änderung zum ASN-Zeitpunkt gültig ist.',
  immediate='Fachliche Nachtragsentscheidung zur ursprünglichen Bestellung protokollieren; keine unbelegte Sperrung eines bereits dokumentiert zulässig geänderten ASN.',
  closure='Genehmigter Nachtrag auf PO-Position oder dokumentierte Ausnahmeentscheidung samt zeitbezogener Kontrolle. Keine unbegründete Datenkorrektur.'),
 'INC-005':dict(subject='Zweiter Wareneingangsbeleg fehlt im Auszug',verdict='RECEIPT_NACHWEISLUECKE_BELEGT',cause='PHYSISCHER_LIEFERSTATUS_UNGEKLAERT',owner='Einkauf / Lager',
  factual='PO-0011 umfasst 240 Stück. Zwei ASN-Positionen melden 96 und 144 Stück. Für ASN-0011-A ist REC-0011-A über 96 Stück POSTED; zu ASN-0011-B fehlt im Export ein Receipt.',
  limitation='Ein fehlender Receipt-Datensatz beweist keine physische Nichtlieferung von 144 Stück.',
  immediate='WMS-Beleg-/Transportjournal für ASN-0011-B recherchieren; offene Position getrennt von bereits gebuchten 96 Stück verfolgen.',
  closure='Vorgangsspezifischer Receipt- oder stornierter ASN-Nachweis, Soll-Ist-Reconciliation und begründete Endentscheidung.'),
 'INC-006':dict(subject='Wareneingang auf HOLD und blockierter Bestand',verdict='HOLD_UND_GEBLOCKTER_SYSTEMBESTAND_BELEGT',cause='HOLD_GRUND_NICHT_BELEGT',owner='Lager / WMS',
  factual='REC-0012 über 60 Stück ist HOLD. Im datierten WMS-Bestand stehen 60 on_hand und 60 blocked, damit 0 rechnerisch frei. Gleichzeitig existieren registrierte ALLOW-Freigaben.',
  limitation='Aus HOLD und Sperrbestand lässt sich nicht der konkrete technische Fehler oder die tatsächlich freie Filialregalmenge ableiten.',
  immediate='HOLD-Grund und Quarantänebefund anfordern; fachlich vorgeschlagene Review-Schranke für operative Nutzung dokumentieren.',
  closure='Dokumentierter HOLD-Grund, autorisierte Entsperrentscheidung, abgestimmter Folgebestand und Wiederprüfung der operativen Freigabe.'),
 'INC-007':dict(subject='WMS-Zieleintrag ohne auffindbares Ereignis',verdict='WMS_EINTRAG_FEHLT__EVENTLUECKE',cause='UNGEKLAERT',owner='ERP-Schnittstelle',
  factual='HYG-1009 hat einen Ziel-ERP-Datensatz, aber keinen WMS-Snapshot-Eintrag und kein passendes interface_events-Ereignis im bereitgestellten Extrakt.',
  limitation='Das Fehlen eines Logeintrags kann eine Nichtsendung, eine Loglücke oder einen anderen Stichtag bedeuten; es belegt keine Ursache.',
  immediate='Outbound-Queue, Integrationstabelle, Übermittlungs-IDs und WMS-Empfang über definierte Stichtage korrelieren.',
  closure='Nachvollziehbarer Versand-/Empfangsnachweis, WMS-Eintrag und Reconciliation auf identischem Zeitstand.'),
 'INC-008':dict(subject='WMS-Zieleintrag fehlt bei protokolliertem Failed-Ereignis',verdict='FEHLGESCHLAGENES_INTERFACE_EVENT_BELEGT',cause='TECHNISCHE_FEHLERKATEGORIE_NO_WMS_ACK_BELEGT__URSACHE_OFFEN',owner='Integration / WMS',
  factual='INT-1010 ist mit FAILED und NO_WMS_ACK registriert; der WMS-Snapshot enthält keine HYG-1010-Zuordnung.',
  limitation='NO_WMS_ACK belegt eine Fehlerkategorie im Simulationslog, nicht warum die Bestätigung ausgeblieben ist.',
  immediate='Message-ID, Timeout, WMS-Endpoint und Retry-Strategie untersuchen; idempotente Wiederholung erst nach Dublettenprüfung.',
  closure='Neuer erfolgreicher Event- und WMS-Snapshot-Nachweis, Dublettenprüfung, vorgesehene Prozessfreigabe aktualisiert.'),
 'INC-009':dict(subject='Lieferantenmaßnachweis unbestätigt',verdict='EXTERNE_REFERENZ_UNBESTAETIGT',cause='KEIN_FALSCHER_MASSWERT_BEWIESEN',owner='MDM / Lieferant',
  factual='REF-1013-A ist UNCONFIRMED; confirmed_at, approved_by und case_qty fehlen. Registrierte Freigaben lauten dennoch ALLOW.',
  limitation='Plausible Werte in internen Daten ersetzen keinen externen verlässlichen Maß- oder Packreferenznachweis.',
  immediate='Lieferantendatenblatt / Version / Verantwortlichen bestätigen lassen und danach betroffene Maß-/Packfelder prüfen.',
  closure='Nachweislich bestätigte Lieferantenreferenz und dokumentierte Freigabeentscheidung; kein Wert ohne Beleg überschreiben.'),
 'INC-010':dict(subject='Geplanter Launch-HOLD',verdict='GUELTIGE_FACHLICHE_AUSNAHME',cause='KEIN_DQ_DEFEKT_NACHGEWIESEN',owner='Produktmanagement / Einkauf',
  factual='HYG-1016 ist NEW. Für PROCUREMENT gilt BLOCK mit PLANNED_LAUNCH_HOLD, während WMS_RECEIPT und BRANCH_SUPPLY ALLOW dokumentieren.',
  limitation='Geplanter Nichtbestellbarkeitsstatus ist für sich genommen keine Datenqualitätsabweichung. Ein formaler Caseabschluss ist in der historischen Datenbank nicht dokumentiert.',
  immediate='Launch-Zeitpunkt und Sortimentsentscheidung bestätigen; Fall als gültige Ausnahme klassifizieren statt den Produktstatus gegen die Policy zu ändern.',
  closure='Fachliche Ausnahme dokumentiert, Termin- und Statusverantwortung bestätigt, administrative Incident-Abschlussfreigabe vorhanden.'),
 'INC-011':dict(subject='Unbestätigte Verpackung vor Launch',verdict='BERECHTIGTES_REVIEW_BEI_UNBESTAETIGTER_REFERENZ',cause='FEHLENDER_BELEG_STATT_BESTAETIGTER_TRANSFORMATIONSFEHLER',owner='Produktmanagement / MDM / Lieferant',
  factual='REF-1017-A ist UNCONFIRMED; Packaging-Ebene PK-1017-A steht PENDING. Die drei Prozessfreigaben stehen auf REVIEW mit UNCONFIRMED_PACKAGING.',
  limitation='Das dokumentierte REVIEW ist kein Fehlverhalten. Weder ungültige Menge noch technischer Importfehler sind damit bewiesen.',
  immediate='Freigegebene Lieferantenspezifikation, Packversion und gültigen Launch-Zeitpunkt nachfordern; REVIEW bis dahin beibehalten.',
  closure='Referenz bestätigt, Packversion freigegeben, zeitgültige Release-Entscheidung vorhanden und Kontroll-Checks bestanden.')
}

AT_CATALOG={
'AT-01':('Korrekte Migration','HYG-1001','PASS','DQ01=PASS und Soll-/Ziel-ID deckungsgleich'),
'AT-02':('Legitim ausgeschlossener Altartikel','HYG-1003','PASS','in_scope=NO und dokumentierter Ausschluss'),
'AT-03':('Fehlender Zielartikel, Ursache offen','HYG-1004','PASS','DQ01=MISSING_TARGET, Migrationsevent absent'),
'AT-04':('Neuartikel ohne Migration','HYG-1015','PASS','origin_type=NEW; kein Migrations-Scope nötig'),
'AT-05':('Genehmigte IN->MM-Umrechnung','HYG-1005','PASS','6 IN=152,4 mm und genehmigter Faktor 25,4'),
'AT-06':('Nichtgenehmigter Transformationsfaktor','HYG-1006','PASS','8 IN / 200 mm / factor 25,0 / nicht genehmigt'),
'AT-07':('Konsistentes PO-ASN-Receipt','HYG-1001','PASS','DQ04=PASS und DQ05=RECONCILED_POSTED'),
'AT-08':('Gleiche Basismenge, nicht genehmigte Packstruktur','HYG-1007','PASS','DQ04=BLOCK, DQ05=RECEIPT_ON_HOLD'),
'AT-09':('Zeitlich genehmigte Packänderung','HYG-1008','PASS','CHG gültig zum ASN, fachlich REVIEW wegen Bestellung'),
'AT-10':('Teil-Wareneingang / Dokumentationslücke','HYG-1011','TEILWEISE','zwei ASNs, eine Receipt; keine Nachweise über physischen Rest'),
'AT-11':('HOLD-Receipt und blockierter Lagerbestand','HYG-1012','TEILWEISE','Blocked 60/60; DQ06 historisch ALLOW, neue Review-Schranke nur als Vorschlag'),
'AT-12':('WMS fehlt, Event fehlt','HYG-1009','PASS','WMS- und Eventlücke, Ursache unklar'),
'AT-13':('WMS fehlt, Failed-Event vorhanden','HYG-1010','TEILWEISE','FAILED/NO_WMS_ACK belegt; produktiver Retest nicht vorhanden'),
'AT-14':('Geplanter Launch-HOLD','HYG-1016','PASS','DOCUMENTED_LAUNCH_HOLD statt DQ-Defekt'),
'AT-15':('Unbestätigte Lieferantenreferenz','HYG-1013','PASS','UNCONFIRMED ≠ korrektes Maß'),
'AT-16':('Korrektur ohne Folgeretest darf nicht schließen','HYG-1006','PASS','Historische OPEN-Baseline; Simulationsabschluss nur bei WMS-Retest')
}

def conn_ro(path):
 c=sqlite3.connect('file:'+str(Path(path).resolve())+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;return c

def rows(c,query,params=()):return [dict(r) for r in c.execute(query,params)]
def one(c,query,params=()):return next(iter(rows(c,query,params)),None)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dumpcsv(path,data,columns=None):
 if not data:return
 cols=columns or list(data[0]);
 with Path(path).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=cols,delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(data)

def loadcsv(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))

def get_sqldata(c,sku,case):
 # Distinct business object grain retained; no blind JOIN on SKU alone.
 order=rows(c,'SELECT * FROM purchase_orders WHERE sku=? ORDER BY po_id,po_line_id',(sku,))
 asns=rows(c,'SELECT * FROM asns WHERE sku=? ORDER BY asn_id,asn_line_id',(sku,))
 keys=[x['asn_id'] for x in asns]
 rec=rows(c,'SELECT r.* FROM receipts r JOIN asns a ON a.asn_id=r.asn_id AND a.asn_line_id=r.asn_line_id WHERE a.sku=? ORDER BY r.receipt_id',(sku,))
 return {'case':case,'sku':sku,
  'reported_cases':rows(c,'SELECT * FROM reported_cases WHERE case_id=?',(case,)),
  'issue_evidence':rows(c,'SELECT * FROM issue_evidence WHERE case_id=? ORDER BY evidence_id',(case,)),
  'correction_actions':rows(c,'SELECT * FROM correction_actions WHERE case_id=?',(case,)),
  'product':rows(c,'SELECT * FROM products WHERE sku=?',(sku,)),
  'legacy':rows(c,'SELECT * FROM legacy_snapshot WHERE sku=?',(sku,)),
  'scope':rows(c,'SELECT sc.* FROM migration_scope sc JOIN legacy_snapshot ls ON ls.legacy_record_id=sc.legacy_record_id WHERE ls.sku=?',(sku,)),
  'target_s2':rows(c,"SELECT * FROM target_snapshot WHERE sku=? AND snapshot_id='S2-2026-09-15'",(sku,)),
  'migration_events':rows(c,'SELECT ev.* FROM migration_events ev JOIN legacy_snapshot ls ON ls.legacy_record_id=ev.legacy_record_id WHERE ls.sku=?',(sku,)),
  'purchase_orders':order,'asns':asns,'receipts':rec,
  'change_approvals':rows(c,'SELECT ch.* FROM change_approvals ch WHERE ch.sku=?',(sku,)),
  'packaging_levels':rows(c,'SELECT * FROM packaging_levels WHERE sku=? ORDER BY pack_version_id,level_code',(sku,)),
  'supplier_references':rows(c,'SELECT * FROM supplier_references WHERE sku=? ORDER BY reference_id',(sku,)),
  'interface_events':rows(c,'SELECT * FROM interface_events WHERE sku=?',(sku,)),
  'wms_snapshot':rows(c,'SELECT * FROM wms_snapshot WHERE sku=?',(sku,)),
  'stock_snapshots':rows(c,'SELECT * FROM stock_snapshots WHERE sku=?',(sku,)),
  'releases':rows(c,'SELECT * FROM releases WHERE sku=? ORDER BY process_code',(sku,))}

def validate_scenarios(c,dq):
 def d(i,sku):return [r for r in dq[i] if r['sku']==sku]
 def status(i,sku):return [r.get(f'dq{i:02d}_status') for r in d(i,sku)]
 tests={
 'AT-01': lambda:status(1,'HYG-1001')==['PASS'],
 'AT-02': lambda:one(c,'SELECT in_scope,exclusion_reason FROM migration_scope WHERE legacy_record_id=?',('ALT-1003',))['in_scope']=='NO' and 'HYG-1003' not in [r['sku'] for r in dq[1]],
 'AT-03': lambda: status(1,'HYG-1004')==['MISSING_TARGET'] and not rows(c,"SELECT 1 FROM migration_events WHERE legacy_record_id='ALT-1004'"),
 'AT-04': lambda:one(c,"SELECT origin_type FROM products WHERE sku='HYG-1015'")['origin_type']=='NEW' and not d(1,'HYG-1015'),
 'AT-05': lambda: status(2,'HYG-1005')==['PASS'] and d(2,'HYG-1005')[0]['expected_length_mm']==152.4,
 'AT-06': lambda:status(2,'HYG-1006')==['DIMENSION_MISMATCH'] and d(3,'HYG-1006')[0]['approval_check']=='UNAPPROVED_RULE',
 'AT-07': lambda:status(4,'HYG-1001')==['PASS'] and status(5,'HYG-1001')==['RECONCILED_POSTED'],
 'AT-08': lambda:status(4,'HYG-1007')==['BLOCK'] and status(5,'HYG-1007')==['RECEIPT_ON_HOLD'],
 'AT-09': lambda:status(4,'HYG-1008')==['REVIEW'] and d(4,'HYG-1008')[0]['pack_version_id']=='PK-1008-B' and bool(one(c,"SELECT 1 FROM change_approvals WHERE change_approval_id='CHG-1008' AND approved_at < '2026-09-16T08:00:00'")),
 'AT-10': lambda:status(5,'HYG-1011')==['RECONCILED_POSTED','MISSING_RECEIPT'] and len(d(5,'HYG-1011'))==2,
 'AT-11': lambda:status(5,'HYG-1012')==['RECEIPT_ON_HOLD'] and one(c,"SELECT on_hand_base_qty,blocked_base_qty FROM stock_snapshots WHERE sku='HYG-1012'")['blocked_base_qty']==60 and status(6,'HYG-1012')==['ALL_PROCESSES_ALLOW'],
 'AT-12': lambda: not rows(c,"SELECT 1 FROM interface_events WHERE sku='HYG-1009'") and not rows(c,"SELECT 1 FROM wms_snapshot WHERE sku='HYG-1009'"),
 'AT-13': lambda:bool(one(c,"SELECT 1 FROM interface_events WHERE sku='HYG-1010' AND processing_status='FAILED' AND error_code='NO_WMS_ACK'")) and not rows(c,"SELECT 1 FROM wms_snapshot WHERE sku='HYG-1010'"),
 'AT-14': lambda:status(6,'HYG-1016')==['DOCUMENTED_LAUNCH_HOLD'],
 'AT-15': lambda:bool(one(c,"SELECT 1 FROM supplier_references WHERE sku='HYG-1013' AND approval_status='UNCONFIRMED'")),
 'AT-16': lambda:one(c,"SELECT investigation_status FROM reported_cases WHERE case_id='INC-002'")['investigation_status']=='OPEN' and one(c,"SELECT dependent_retest_status FROM correction_actions WHERE case_id='INC-002'")['dependent_retest_status']=='PENDING_WMS_RECHECK'
 }
 results=[]
 for tid,(title,sku,coverage,explanation) in AT_CATALOG.items():
  success=tests[tid]()
  results.append({'test_id':tid,'szenario':title,'sku':sku,'vorgesehene_abdeckung':coverage,'datenpruefung':'PASS' if success else 'FAIL','fachliche_begruendung':explanation,'offen_bei_teilweise':('Begrenzte Nachweislage / noch kein vollständiger operativer End-to-End-Test' if coverage=='TEILWEISE' else '')})
 return results

def mutation_tests(source,sql_dir,model_script):
 checks=[]
 def run_sql(c,i,sku):
  path=next(sql_dir.glob(f'DQ{i:02d}_*.sql'))
  return [dict(x) for x in c.execute(path.read_text(encoding='utf-8')) if x['sku']==sku]
 def record(name,condition,detail):
  checks.append({'test':name,'status':'PASS' if condition else 'FAIL','detail':detail})
 with tempfile.TemporaryDirectory(prefix='portfolio_pilot_tiefentest_') as td:
  td=Path(td)
  for ix,name in enumerate(['missing_target_insert','correct_dimension_without_rule_fix','pack_corrected_hold_remains','remove_pack_approval','receipt_restored','supplier_confirmed','wms_reference_restored']):
   p=td/(name+'.sqlite');shutil.copy2(source,p);c=sqlite3.connect(str(p));c.row_factory=sqlite3.Row
   if name=='missing_target_insert':
    # Copy rows from another valid target to exercise exactly the DQ01 existence/identity rule.
    c.execute("INSERT INTO target_snapshot SELECT snapshot_id,extracted_at,'ERP-9004','HYG-1004',length_mm,width_mm,height_mm,case_qty,pack_version_id,base_uom,lifecycle_status FROM target_snapshot WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-1005'")
    c.commit();record('NEG-01 Ziel ergänzt: DQ01 PASS, aber Migrationslog bleibt fehlend',run_sql(c,1,'HYG-1004')[0]['dq01_status']=='PASS' and run_sql(c,3,'HYG-1004')[0]['version_check']=='NO_EVENT','Der Ziel-Snapshot alleine schließt die historische Root-Cause-Lücke nicht.')
   elif name=='correct_dimension_without_rule_fix':
    c.execute("UPDATE target_snapshot SET length_mm=203.2 WHERE snapshot_id='S2-2026-09-15' AND sku='HYG-1006'");c.commit()
    record('NEG-02 Dimension richtig, falsches Mappingereignis weiter nachweisbar',run_sql(c,2,'HYG-1006')[0]['dq02_status']=='PASS' and run_sql(c,3,'HYG-1006')[0]['approval_check']=='UNAPPROVED_RULE','Korrektur des Zielwerts heilt den nichtgenehmigten historischen Lauf nicht.')
   elif name=='pack_corrected_hold_remains':
    c.execute("UPDATE asns SET pack_version_id='PK-1007-A',package_count=10,each_per_package=100 WHERE asn_id='ASN-0007'");c.commit()
    record('NEG-03 Verpackung berichtigt, HOLD bleibt bestehen',run_sql(c,4,'HYG-1007')[0]['dq04_status']=='PASS' and run_sql(c,5,'HYG-1007')[0]['dq05_status']=='RECEIPT_ON_HOLD','Zwei unabhängige Kontrollen dürfen nicht als eine erfolgreiche End-to-End-Freigabe verkauft werden.')
   elif name=='remove_pack_approval':
    c.execute("UPDATE change_approvals SET approved_by=NULL WHERE change_approval_id='CHG-1008'");c.commit()
    record('NEG-04 Fehlende Genehmigungsrolle ist kein PASS',run_sql(c,4,'HYG-1008')[0]['dq04_status'] in ('REVIEW','BLOCK'),'Eine formal unvollständige Genehmigung kann nicht stillschweigend gültig sein.')
   elif name=='receipt_restored':
    c.execute("INSERT INTO receipts(receipt_id,receipt_line_id,asn_id,asn_line_id,po_id,po_line_id,wms_article_id,received_at,package_count,each_per_package,received_base_qty,processing_status) VALUES ('REC-0011-B','10','ASN-0011-B','10','PO-0011','10','WMS-1011','2026-09-18T10:00:00',6,24,144,'POSTED')")
    c.commit()
    record('NEG-05 Fehlender Receipt-Beleg wird durch simulierte Nachbuchung aufgelöst',sorted(x['dq05_status'] for x in run_sql(c,5,'HYG-1011'))==['RECONCILED_POSTED','RECONCILED_POSTED'],'Nur künstliche Nachbuchung im Testzweig; kein Beleg einer echten Warenbewegung.')
   elif name=='supplier_confirmed':
    c.execute("UPDATE supplier_references SET confirmed_at='2026-09-19T10:00:00',approved_by='MDM-TEST',approval_status='APPROVED',case_qty=36 WHERE sku='HYG-1013'");c.commit()
    proc=subprocess.run([sys.executable,str(model_script),'--db',str(p),'--sql-dir',str(sql_dir),'--out',str(td/'risiko_1013')],capture_output=True,text=True)
    if proc.returncode!=0:raise RuntimeError('Methoden-Testlauf gescheitert: '+proc.stderr)
    new=[x for x in loadcsv(td/'risiko_1013'/'Pilot_20_Artikel_Risikomatrix.csv') if x['sku']=='HYG-1013'][0]
    record('NEG-06 Referenz bestätigt: unbestätigt-Signal fällt dynamisch weg', 'SUPPLIER_EVIDENCE_UNCONFIRMED' not in new['dq_signale'] and new['prioritaet'] in ('P3','P4'),'Offener historischer Incident darf ohne Abschlussbeleg weiterhin administrativ markiert sein.')
   elif name=='wms_reference_restored':
    c.execute("INSERT INTO wms_snapshot(snapshot_id,extracted_at,wms_article_id,sku,accepted_pack_version_id,known_case_qty,wms_status) VALUES ('WMS-2026-09-18','2026-09-18T16:00:00','WMS-1009','HYG-1009','PK-1009-A',24,'ACTIVE')")
    c.commit()
    proc=subprocess.run([sys.executable,str(model_script),'--db',str(p),'--sql-dir',str(sql_dir),'--out',str(td/'risiko_1009')],capture_output=True,text=True)
    if proc.returncode!=0:raise RuntimeError(proc.stderr)
    new=[x for x in loadcsv(td/'risiko_1009'/'Pilot_20_Artikel_Risikomatrix.csv') if x['sku']=='HYG-1009'][0]
    record('NEG-07 WMS-Snapshot ergänzt: WMS-Fehlsignal fällt weg','WMS_REFERENCE_MISSING' not in new['dq_signale'],'Ein ergänzter Datensatz beweist noch keine historisch korrekte Übermittlung.')
   c.close()
 return checks

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--db',default=str(DEFAULT_DB));pa.add_argument('--sql-dir',default=str(SQL_DIR));pa.add_argument('--out',default=str(ROOT)); args=pa.parse_args()
 source=Path(args.db);sql_dir=Path(args.sql_dir);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 before=sha(source);c=conn_ro(source)
 pilot=loadcsv(out/'Pilot_20_Artikel_Risikomatrix.csv');triage=loadcsv(out/'Pilot_11_Incidents_Triage.csv')
 by_case={x['incident']:x for x in triage};assert len(by_case)==len(CASES)==11
 gate_codes={
  'INC-001':'REVIEW_REQUIRED', 'INC-002':'REVIEW_REQUIRED','INC-003':'HOLD_UNTIL_PACK_APPROVED',
  'INC-004':'DOCUMENTED_EXCEPTION_REVIEW','INC-005':'EVIDENCE_REQUIRED','INC-006':'HOLD_UNTIL_WMS_CLEARANCE',
  'INC-007':'REVIEW_REQUIRED','INC-008':'REVIEW_REQUIRED','INC-009':'SUPPLIER_EVIDENCE_REQUIRED',
  'INC-010':'VALID_PLANNED_HOLD','INC-011':'RETAIN_REVIEW'
 }
 case_rows=[];packets={}
 for cid,definition in CASES.items():
  t=by_case[cid];sku=t['zugeordnete_sku'];data=get_sqldata(c,sku,cid);packets[cid]=data
  ev=data['issue_evidence'];refs=sorted({x['source_table'] for x in ev})
  release_ids=[x['process_code']+':'+x['decision'] for x in data['releases']]
  if not data['reported_cases'] or data['reported_cases'][0]['investigation_status']!='OPEN':raise AssertionError('Historischer Fall nicht mehr OPEN '+cid)
  if not ev:raise AssertionError('Fehlende Belegmetadaten '+cid)
  case_rows.append({'incident':cid,'sku':sku,'pilot_prioritaet':t['prioritaet_pilot'],'gegenstand':definition['subject'],
   'nachgewiesener_sachverhalt':definition['factual'],'befund_status':definition['verdict'],
   'ursachenstatus':definition['cause'],'kenntnisgrenze':definition['limitation'],
   'evidence_ids':'|'.join(x['evidence_id'] for x in ev),'evidence_tables':'|'.join(refs),
   'evidenz_verfuegbar':sum(x['evidence_availability']=='AVAILABLE' for x in ev),
   'evidenz_fehlend':sum(x['evidence_availability']=='MISSING' for x in ev),
   'evidenz_unbestaetigt':sum(x['evidence_availability']=='UNCONFIRMED' for x in ev),
   'releases_registriert':'|'.join(release_ids),
   'vorgeschlagene_zusaetzliche_fachpruefung':gate_codes[cid],
   'verantwortungsbereich':definition['owner'],'unmittelbare_massnahme':definition['immediate'],
   'abschlussbedingung':definition['closure'],
   'historischer_incident_status':'OPEN','abschluss_nach_neuer_pruefung':'OFFEN__NICHT_AUTOMATISCH_GESCHLOSSEN',
   'nachweisumfang':'SYNTHE TISCH'.replace(' ','')})
 dq={}
 for i in range(1,8):
  sql=next(sql_dir.glob(f'DQ{i:02d}_*.sql')).read_text(encoding='utf-8')
  dq[i]=[dict(r) for r in c.execute(sql)]
 at=validate_scenarios(c,dq)
 muts=mutation_tests(source,sql_dir,ROOT/'risikomodell_geprueft.py')
 # Independent invariants supporting each case. Many of these test *raw records*, not only DQ output.
 validations=[]
 def check(name,flag,detail=''):
  validations.append({'pruefung':name,'status':'PASS' if flag else 'FAIL','detail':detail})
 check('20 einzigartige SKU im Pilot',len(pilot)==20 and len({x['sku'] for x in pilot})==20)
 check('11 Cases mit einzigartiger Zuordnung',len(case_rows)==11 and len({x['incident'] for x in case_rows})==11)
 check('INC001: fehlende Target-Reconciliation',not packets['INC-001']['target_s2'] and not packets['INC-001']['migration_events'])
 check('INC002: Legacy-IN = 8 und ERP = 200',packets['INC-002']['legacy'][0]['length_value']==8 and packets['INC-002']['target_s2'][0]['length_mm']==200)
 check('INC002: Eventfaktor=25 und unapproved',packets['INC-002']['migration_events'][0]['applied_length_factor']==25.0 and any(x['approval_check']=='UNAPPROVED_RULE' for x in dq[3] if x['sku']=='HYG-1006'))
 check('INC003: 10*100 Bestellmenge vs 4*250 Avis, Gesamtmenge identisch', packets['INC-003']['purchase_orders'][0]['expected_case_count']==10 and packets['INC-003']['asns'][0]['package_count']==4 and packets['INC-003']['asns'][0]['announced_base_qty']==1000)
 check('INC003: ASN nicht genehmigt und Receipt HOLD',packets['INC-003']['asns'][0]['pack_version_id']=='UNKNOWN_PACK_VERSION' and packets['INC-003']['receipts'][0]['processing_status']=='HOLD')
 ch=packets['INC-004']['change_approvals'][0];asn=packets['INC-004']['asns'][0];po=packets['INC-004']['purchase_orders'][0]
 check('INC004: Approval nach PO aber vor ASN',po['order_at'] < ch['approved_at'] < asn['sent_at'] and ch['effective_from']<=asn['sent_at'])
 check('INC005: zwei ASNs und nur ein Receipt',len(packets['INC-005']['asns'])==2 and len(packets['INC-005']['receipts'])==1 and sum(x['announced_base_qty'] for x in packets['INC-005']['asns'])==240)
 s=packets['INC-006']['stock_snapshots'][0]
 check('INC006: 60 vorhanden und 60 geblockt',s['on_hand_base_qty']==s['blocked_base_qty']==60 and packets['INC-006']['receipts'][0]['processing_status']=='HOLD')
 check('INC007: WMS fehlend, Event fehlt',not packets['INC-007']['wms_snapshot'] and not packets['INC-007']['interface_events'])
 check('INC008: WMS fehlt, failed event vorhanden',not packets['INC-008']['wms_snapshot'] and packets['INC-008']['interface_events'][0]['processing_status']=='FAILED' and packets['INC-008']['interface_events'][0]['error_code']=='NO_WMS_ACK')
 check('INC009: Supplier unconfirmed',packets['INC-009']['supplier_references'][0]['approval_status']=='UNCONFIRMED')
 check('INC010: planmäßiger PROCUREMENT-BLOCK',any(r['process_code']=='PROCUREMENT' and r['reason_code']=='PLANNED_LAUNCH_HOLD' and r['decision']=='BLOCK' for r in packets['INC-010']['releases']))
 check('INC011: Referenz unconfirmed + drei REVIEW',packets['INC-011']['supplier_references'][0]['approval_status']=='UNCONFIRMED' and all(x['decision']=='REVIEW' for x in packets['INC-011']['releases']))
 check('Historische 11 Fälle bleiben OPEN',all(x['historischer_incident_status']=='OPEN' for x in case_rows))
 check('Kein Fall aus fehlender Evidenz als bestätigt-ursächlich markiert',all(not('UNBEKANNT' in x['ursachenstatus'] and 'BELEGT' in x['ursachenstatus']) for x in case_rows))
 check('16 Szenario-Nachweise erfolgreich ausgewertet',all(x['datenpruefung']=='PASS' for x in at))
 check('7 isolierte negative Veränderungstests bestanden',all(x['status']=='PASS' for x in muts))
 check('20-SKU-Klassifikation gegenüber Ausführung 1 unverändert',collections.Counter(x['prioritaet'] for x in pilot)=={'P1':6,'P2':4,'P3':1,'P4':9})
 c.close()
 check('Quell-SHA vor und nach der Untersuchung identisch',sha(source)==before)
 if any(x['status']!='PASS' for x in validations+muts):
  print(json.dumps([x for x in validations+muts if x['status']!='PASS'],ensure_ascii=False,indent=2));sys.exit(1)
 dumpcsv(out/'Pilot_11_Incidents_Tiefenanalyse.csv',case_rows)
 dumpcsv(out/'Pilot_16_Akzeptanzfaelle_Abgleich.csv',at)
 dumpcsv(out/'Pilot_Negativtests_Isolierte_Kopien.csv',muts)
 (out/'Fallakten_Quellenauszuege_11_Incidents.json').write_text(json.dumps(packets,ensure_ascii=False,indent=2),encoding='utf-8')
 summary={
 'ausfuehrung':'2/4','datenherkunft':'V1, 20 synthetische Artikel, historischen Snapshot nicht modifiziert',
 'quell_sha256_anfang_und_ende':before,'fallakten':len(case_rows),'akzeptanzszenarien':len(at),
 'szenarien_kontrollnachweis_PASS':sum(x['datenpruefung']=='PASS' for x in at),
 'szenarien_inhaltlich_vollstaendig':sum(x['vorgesehene_abdeckung']=='PASS' for x in at),
 'szenarien_begrenzt':sum(x['vorgesehene_abdeckung']=='TEILWEISE' for x in at),
 'historische_incidents_offen':sum(x['historischer_incident_status']=='OPEN' for x in case_rows),
 'isolierte_mutationstests':len(muts),'isolierte_mutationstests_bestanden':sum(x['status']=='PASS' for x in muts),
 'invarianten':len(validations),'invarianten_bestanden':sum(x['status']=='PASS' for x in validations),
 'verteilung':dict(collections.Counter(x['pilot_prioritaet'] for x in case_rows)),
 'risk_model_sha256':sha(ROOT/'risikomodell_geprueft.py'),'risikomodell_version':'RISK-PILOT-1.1',
 'freigabe_500_uebertragung':'METHODISCH_BEDINGT__GRENZEN_DOKUMENTIERT',
 'restluecken':['AT-10: physischer Restlieferstatus ohne zusätzliche Belege offen',
 'AT-11: registrierte ALLOW-Freigaben trotz geblocktem Bestand; vorgeschlagene Review-Schranke noch keine bindende Richtlinie',
 'AT-13: Eventfehler dokumentiert, Ursache und erfolgreicher echter Retry offen',
 '7 DQ-SQL-Checks decken nicht 26 Geschäftsregeln vollständig ab',
 'Keine reale Prozesswirkung und kein realer WMS-Test']}
 (out/'Pruefprotokoll_Execution2.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 report=['# Vertiefte Pilotfallbearbeitung und Methodenvalidierung – Ausführung 2/4','',
 '## Befund in einem Satz',
 '**Alle elf registrierten Pilot-Incidents wurden einzeln anhand ihrer Ursprungsdaten geprüft, fachlich eingeordnet, einer konkreten nächsten Handlung und einem expliziten Abschlusskriterium zugeordnet; sie sind deshalb nicht automatisch alle geschlossen.**',
 '', 'Die Daten sind synthetisch. Risikoprioritäten schätzen potenzielle Tragweite, ohne empirische Wahrscheinlichkeit oder Geschäftsschaden zu behaupten.',
 '## Datenstand und Nachweisdisziplin',
 f'- Historische V1-Quelle unverändert, SHA-256 `{before}`.',
 '- Alle 20 SKUs bleiben exakt einmal in der Matrix; alle 11 Incidents haben einen nachvollziehbaren Referenzpfad.',
 '- Ein gemeldeter Incident (Grain: Case) ist nicht dasselbe wie eine SKU oder eine ASN-Position. Bei HYG-1011 existieren zwei ASN-Positionen.',
 '- Abgleich von Freigaben (18.09. 18 Uhr) und Ziel-ERP-Snapshot S2 (15.09.) zeigt **mögliche** Kontrollkonflikte, keinen bewiesenen zeitgleichen Policy-Verstoß.',
 '- `AVAILABLE` im Evidenzregister bedeutet vorhandenen Beleg, nicht zwangsläufig bestätigte technische Ursache.',
 '', '## Ergebnisse der vertieften Einzelfallprüfung','']
 for x in case_rows:
  report.extend([f"### {x['incident']} · {x['sku']} · {x['pilot_prioritaet']} — {x['gegenstand']}",
   f"**Datenbeobachtung:** {x['nachgewiesener_sachverhalt']}",
   f"**Bewerteter Befund:** `{x['befund_status']}`; **Ursache:** `{x['ursachenstatus']}`.",
   f"**Nachweisgrenze:** {x['kenntnisgrenze']}",
   f"**Evidenzregister:** {x['evidence_ids']} (vorhanden {x['evidenz_verfuegbar']}, fehlend {x['evidenz_fehlend']}, unbestätigt {x['evidenz_unbestaetigt']}); Datenquellen: `{x['evidence_tables']}`.",
   f"**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `{x['vorgeschlagene_zusaetzliche_fachpruefung']}`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.",
   f"**Verantwortung:** {x['verantwortungsbereich']}. **Nächste Maßnahme:** {x['unmittelbare_massnahme']}",
   f"**Abschlussbedingung:** {x['abschlussbedingung']}",
   f"**Historischer Status:** `{x['historischer_incident_status']}`. Keine neue Erledigung ohne Retest- und Freigabebeleg.",''])
 report.extend(['## Validierung gegen die 16 vorab definierten Akzeptanzszenarien','',
 '**Wichtig:** Ein bestandenes Datenprüfkriterium ist nicht gleichbedeutend mit vollständiger Prozessabnahme. Die Szenarien AT-10, AT-11 und AT-13 sind daher inhaltlich nur teilweise gedeckt.',
 '', '| Szenario | Pilotbezug | Datentest | Fachliche Abdeckung |','|---|---|---|---|'])
 for x in at:report.append(f"| {x['test_id']} – {x['szenario']} | {x['sku']} | {x['datenpruefung']} | {x['vorgesehene_abdeckung']} |")
 report.extend(['','## Isolierte Negativ- und Änderungsproben','','| Prüffall | Ergebnis | Warum relevant? |','|---|---|---|'])
 for x in muts:report.append(f"| {x['test']} | {x['status']} | {x['detail']} |")
 report.extend(['','## Methodenanpassung vor der Skalierung',
 'Die ursprüngliche Ersttriage verwendete bei ausgewählten WMS- und Lieferantensignalen feste Incident-IDs als Auslöser. Das wäre bei weiteren Incident-IDs auf der 500er-Datenbasis nicht zulässig.',
 'Das neue, versionierte Skript `risikomodell_geprueft.py` nutzt stattdessen **Symptom und tatsächliche Datensätze**. In den zwei Negativproben zur Lieferantenbestätigung und zum WMS-Eintrag verschwindet das entsprechende negative Prüfsignal nach einer simulierten Datenänderung; der historische Incident wird dadurch **nicht** automatisch geschlossen.',
 'Die 20-Artikel-Ausgangsverteilung bleibt trotz Anpassung unverändert: P1=6, P2=4, P3=1, P4=9. Der Quellzustand wurde nicht verändert.',
 '', '## Erforderliche Zusatzsteuerung (Vorschlag, kein produktives Gate)',
 'Eine `ALLOW`-Registrierung darf nicht automatisch die separat ermittelte Qualitätslage überschreiben. Für P1-Konflikte wird eine **Review-Queue** empfohlen; für dokumentierte geplante HOLDs keine Fehler-Eskalation. Dieses fachliche Gate benötigt vor produktiver Übernahme eine bestätigte Unternehmensrichtlinie, Verantwortliche und zeitliche Gültigkeit.',
 '', '## Offen bleibende Grenzen',
 '- AT-10: fehlender Beleg ist keine bewiesene physische Fehlmenge.',
 '- AT-11: HOLD/blocked trotz ALL_PROCESSES_ALLOW – erst die vorgeschlagene Kontrollschranke würde eine zusätzliche Review-Entscheidung erzwingen; die historischen Freigaben bleiben bestehen.',
 '- AT-13: FAILED/NO_WMS_ACK ist registriert; Ursache und späterer produktiver Retry fehlen.',
 '- Weitere 26 im Fachkonzept definierte Geschäftsregeln sind nicht vollständig durch die sieben implementierten SQL-Kontrollen abgedeckt.',
 '- Kein echtes ERP/WMS und keine Beobachtung realer wirtschaftlicher Auswirkungen.',
 '', '## Übergabe an Ausführung 3/4',
 'Das methodisch getestete Verfahren `RISK-PILOT-1.1` sowie die Grenzfallregel (keine automatische Incident-Schließung; keine automatische BLOCK-Umstellung) dienen als fixierte Grundlage für die Untersuchung **aller 500** synthetischen Artikel. Die 500er-Stufe muss zunächst die Datengrains, die Feld-/Statussemantik und die Übertragbarkeit von WMS- und Lieferantensignalen unabhängig prüfen. Fachlich ungeklärte Fälle werden nicht nachträglich als PASS umetikettiert.',
 ''])
 (out/'02_Bericht_Pilot_Tiefenanalyse_und_Methodenvalidierung.md').write_text('\n'.join(report),encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
