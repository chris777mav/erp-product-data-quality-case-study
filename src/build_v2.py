#!/usr/bin/env python3
"""Deterministic SYNTHETIC ERP simulation extension; keeps all source records intact.
Never makes claims about Target Canada and never reads real employer systems.
Run: python src/build_v2.py  [from package root]
"""
from __future__ import annotations
from pathlib import Path
import sqlite3, shutil, csv, json, collections, hashlib, random

ROOT=Path(__file__).resolve().parents[1]
SEED=421061
N_NEW=480
rng=random.Random(SEED)
INPUT=ROOT/'input'/'Portfolio_Phase4_Rohdaten.sqlite'
OUT=ROOT/'results'/'Portfolio_Projekt1_V2_500SKUs.sqlite'
MANIFEST=ROOT/'results'/'v2_szenarien_manifest.csv'
GROUPS=[('KOERPERPFLEGE','Duschgel Sensitiv'),('MUNDHYGIENE','Zahnpasta Classic'),('HAUSHALT','Universalreiniger'),('HYGIENE','Handseife Flüssig'),('BABY','Feuchttücher'),('HAARPFLEGE','Shampoo Repair'),('KOSMETIK','Hautcreme'),('WASCHMITTEL','Waschmittel Color')]
SUPS=['L-01','L-02','L-03','L-04','L-05','L-06','L-07','L-08','L-09']
S1='S1-2026-09-10';S2='S2-2026-09-15'


def insert(con,table,record):
    cols=list(record)
    con.execute('INSERT INTO '+table+' ('+','.join('"'+x+'"' for x in cols)+') VALUES ('+','.join('?' for _ in cols)+')',list(record.values()))

def build():
    assert INPUT.is_file(),'Missing frozen V1 SQLite source'
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if OUT.exists():OUT.unlink()
    # Re-create independent V2 DB, never modify input.
    shutil.copy2(INPUT,OUT)
    con=sqlite3.connect(OUT)
    con.execute('PRAGMA foreign_keys=OFF')  # original landing design intentionally permits invalid references
    scenarios=[]
    with con:
        for j in range(4,10):
            insert(con,'suppliers',dict(supplier_id=f'L-{j:02d}',supplier_name=f'Fiktiv Partnerlieferant {j:02d}',supplier_status='ACTIVE'))
        for ix in range(1,N_NEW+1):
            no=2000+ix;sku=f'HYG-{no}'; origin='MIGRATED' if ix<=320 else 'NEW'
            group,label=GROUPS[(ix*7)%len(GROUPS)]
            supplier=SUPS[ix%len(SUPS)]
            pack_qty=[12,24,36,48,60,72,96,100,120][ix%9]
            n_in=ix%9==0
            uom='IN' if n_in else 'MM'
            length_mm=round(100+(ix*13)%175+rng.uniform(-2.75,2.75),2)
            # For IN values use millimetre lengths derived from 0.5-inch steps
            if n_in: length_value=round(2.0+(ix%15)*0.5,2);length_mm=round(length_value*25.4,2)
            else: length_value=length_mm
            active='DISCONTINUED' if ix%71==0 else 'ACTIVE'
            in_scope='NO' if origin=='MIGRATED' and active=='DISCONTINUED' else 'YES'
            missing_target=origin=='MIGRATED' and in_scope=='YES' and ix%43==0
            identity_issue=origin=='MIGRATED' and in_scope=='YES' and ix%97==0 and not missing_target
            length_missing=origin=='MIGRATED' and ix%41==0 and not missing_target
            length_wrong=origin=='MIGRATED' and ix%29==0 and not missing_target and not length_missing
            old_rule=origin=='MIGRATED' and ix%31==0 and not missing_target
            no_event=origin=='MIGRATED' and ix%59==0 and not missing_target
            unknown_uom=origin=='MIGRATED' and ix%107==0 and not missing_target
            # Three statuses may differ even where origin is NEW.
            release_pattern=('DISCONTINUATION' if active=='DISCONTINUED' else
              'LAUNCH_HOLD' if ix%67==0 else 'PACKAGING_REVIEW' if ix%61==0 else
              'MISSING_RELEASE' if ix%149==0 else 'DUPLICATE_RELEASE' if ix%151==0 else 'ALLOW')
            has_po=ix%3==0 or ix%13==0
            # ASN patterns provide control negatives and justified exceptions.
            asn_pattern=('NONE' if not has_po else
              'UNKNOWN_PACK' if ix%37==0 else 'UNAPPROVED_PACK' if ix%41==0 else
              'APPROVED_CHANGE' if ix%17==0 else 'BAD_QUANTITY' if ix%31==0 else 'STANDARD')
            receipt_pattern=('NONE' if not has_po else
              'MISSING_RECEIPT' if ix%19==0 else 'HOLD' if ix%13==0 else
              'PARTIAL' if ix%23==0 else 'EXCESS' if ix%47==0 else 'POSTED')
            # Rows in pre-existing tables remain immutable.
            insert(con,'products',dict(sku=sku,product_group=group,description=f'{label} Variante {ix%12+1}',origin_type=origin,lifecycle_status=active,base_uom='EA',created_at='2025-03-01T10:00:00' if origin=='MIGRATED' else '2026-09-11T08:00:00'))
            supplier_no=f'SYN-{no}'
            insert(con,'supplier_articles',dict(supplier_id=supplier,supplier_article_no=supplier_no,sku=sku,valid_from='2026-01-01',valid_to=None,approval_status='APPROVED'))
            pack=f'PK-{no}-A'
            insert(con,'packaging_levels',dict(pack_version_id=pack,sku=sku,level_code='EACH',child_level_code=None,units_of_child=1,gtin=None,valid_from='2026-01-01',valid_to=None,approval_status='APPROVED',length_mm=length_mm,width_mm=32+ix%23,height_mm=72+ix%19,gross_weight_g=55+ix%240,measure_evidence='SYNTHETIC'))
            insert(con,'packaging_levels',dict(pack_version_id=pack,sku=sku,level_code='CASE',child_level_code='EACH',units_of_child=pack_qty,gtin=None,valid_from='2026-01-01',valid_to=None,approval_status='APPROVED',length_mm=320+ix%25,width_mm=240+ix%28,height_mm=190+ix%31,gross_weight_g=pack_qty*(55+ix%240),measure_evidence='SYNTHETIC'))
            insert(con,'supplier_references',dict(reference_id=f'REF-{no}-A',supplier_id=supplier,supplier_article_no=supplier_no,sku=sku,pack_version_id=pack,confirmed_at='2026-08-25T09:00:00',valid_from='2026-01-01',valid_to=None,approval_status='APPROVED',case_qty=pack_qty,reference_source_id=f'SYN-REF-{supplier}',approved_by='EINKAUF-V2'))
            target=f'ERP-{no+10000}'
            if origin=='MIGRATED':
                leg=f'ALT-{no}'
                insert(con,'legacy_snapshot',dict(snapshot_id='S0-2026-09-01',extracted_at='2026-09-01T23:00:00',legacy_record_id=leg,sku=sku,length_value=length_value,dimension_uom=('CM' if unknown_uom else uom),case_qty=pack_qty,base_uom='EA',lifecycle_status=active))
                insert(con,'migration_scope',dict(migration_run_id='RUN-2026-09',legacy_record_id=leg,in_scope=in_scope,exclusion_reason='DISCONTINUED_BEFORE_CUTOVER' if in_scope=='NO' else None,expected_target_record_id=target,mapping_rule_version='R1',approved_at='2026-08-31T15:00:00',approved_by='MDM-V2'))
                if in_scope=='YES' and not missing_target:
                    if not no_event:
                        factor=25.0 if old_rule and n_in else (25.4 if n_in else 1.0)
                        insert(con,'migration_events',dict(event_id=f'MIG-E-{no}',migration_run_id='RUN-2026-09',legacy_record_id=leg,target_record_id=(target if not identity_issue else target+'-BAD'),sent_at='2026-09-09T10:00:00',received_at='2026-09-10T11:00:00',load_status='SUCCESS',error_code=None,applied_rule_version='UOM_LENGTH_V0_UNAPPROVED' if old_rule else 'R1',applied_length_factor=factor))
                    for snap in (S1,S2):
                        # handful of entries show up in S2 only; not evidence of a failure for S2 measurement
                        if snap==S1 and ix%11==0:continue
                        insert(con,'target_snapshot',dict(snapshot_id=snap,extracted_at='2026-09-10T23:00:00' if snap==S1 else '2026-09-15T23:00:00',target_record_id=target if not identity_issue else target+'-BAD',sku=sku,length_mm=None if length_missing else (round(length_mm-3.2,2) if length_wrong else length_mm),width_mm=32+ix%23,height_mm=72+ix%19,case_qty=pack_qty,pack_version_id=pack,base_uom='EA',lifecycle_status=active))
            elif origin=='NEW' and ix%49!=0:
                insert(con,'target_snapshot',dict(snapshot_id=S2,extracted_at='2026-09-15T23:00:00',target_record_id=target,sku=sku,length_mm=length_mm,width_mm=32+ix%23,height_mm=72+ix%19,case_qty=pack_qty,pack_version_id=pack,base_uom='EA',lifecycle_status=active))
            # The release registry is independent of whether master data actually passed DQ01.
            for process in ['PROCUREMENT','WMS_RECEIPT','BRANCH_SUPPLY']:
                if release_pattern=='MISSING_RELEASE' and process=='WMS_RECEIPT': continue
                decision=('BLOCK' if release_pattern=='DISCONTINUATION' else
                          'BLOCK' if release_pattern=='LAUNCH_HOLD' and process=='PROCUREMENT' else
                          'REVIEW' if release_pattern=='PACKAGING_REVIEW' else 'ALLOW')
                reason=('DISCONTINUED' if release_pattern=='DISCONTINUATION' else
                        'PLANNED_LAUNCH_HOLD' if release_pattern=='LAUNCH_HOLD' and process=='PROCUREMENT' else
                        'UNCONFIRMED_PACKAGING' if release_pattern=='PACKAGING_REVIEW' else 'CHECKS_APPROVED')
                insert(con,'releases',dict(release_id=f'REL-{no}-{process}',sku=sku,process_code=process,decision=decision,reason_code=reason,approved_by='MDM-V2',valid_from='2026-09-10T00:00:00',valid_to=None))
                if release_pattern=='DUPLICATE_RELEASE' and process=='PROCUREMENT':
                    insert(con,'releases',dict(release_id=f'REL-{no}-{process}-DUP',sku=sku,process_code=process,decision='ALLOW',reason_code='DUPLICATE_SNAPSHOT',approved_by='MDM-V2',valid_from='2026-09-10T00:00:00',valid_to=None))
            # WMS and interface presence are not proofs of valid dimensions or physical shelf stock.
            has_target=(origin=='MIGRATED' and in_scope=='YES' and not missing_target) or (origin=='NEW' and ix%49!=0)
            if has_target and ix%17!=0:
                insert(con,'wms_snapshot',dict(snapshot_id='WMS-2026-09-18',extracted_at='2026-09-18T16:00:00',wms_article_id=f'WMS-{no}',sku=sku,accepted_pack_version_id=pack,known_case_qty=pack_qty,wms_status='ACTIVE'))
            if has_target and ix%19!=0:
                insert(con,'interface_events',dict(event_id=f'INT-{no}',sku=sku,target_record_id=target,wms_article_id=f'WMS-{no}',sent_at='2026-09-15T13:00:00',received_at=None if ix%17==0 else '2026-09-15T13:00:02',processing_status='FAILED' if ix%17==0 else 'DELIVERED',error_code='WMS_VALIDATION_REVIEW' if ix%17==0 else None,payload_version='V1'))
            if has_po:
                po=f'PO-{no}';asn=f'ASN-{no}'; qty_case=4+(ix%7);q_base=qty_case*pack_qty
                insert(con,'purchase_orders',dict(po_id=po,po_line_id='10',supplier_id=supplier,sku=sku,ordered_qty=qty_case,order_uom='CASE',ordered_base_qty=q_base,expected_pack_version_id=pack,expected_case_qty=pack_qty,expected_case_count=qty_case,order_at='2026-09-15T10:00:00',order_status='OPEN'))
                version=pack;units=pack_qty;approval_id=None
                if asn_pattern=='UNKNOWN_PACK':version=f'PK-{no}-UNKNOWN';units=pack_qty
                elif asn_pattern=='UNAPPROVED_PACK':
                    version=f'PK-{no}-DRAFT';
                    insert(con,'packaging_levels',dict(pack_version_id=version,sku=sku,level_code='CASE',child_level_code='EACH',units_of_child=pack_qty,gtin=None,valid_from='2026-09-16',valid_to=None,approval_status='DRAFT',length_mm=340,width_mm=250,height_mm=200,gross_weight_g=q_base,measure_evidence='SYNTHETIC'))
                elif asn_pattern=='APPROVED_CHANGE':
                    version=f'PK-{no}-B';units=pack_qty+12
                    insert(con,'packaging_levels',dict(pack_version_id=version,sku=sku,level_code='CASE',child_level_code='EACH',units_of_child=units,gtin=None,valid_from='2026-09-16',valid_to=None,approval_status='APPROVED',length_mm=335,width_mm=255,height_mm=215,gross_weight_g=units*(55+ix%240),measure_evidence='SYNTHETIC'))
                    approval_id=f'CHG-{no}'
                    insert(con,'change_approvals',dict(change_approval_id=approval_id,sku=sku,approved_pack_version_id=version,approved_at='2026-09-14T12:00:00',effective_from='2026-09-16T00:00:00',effective_to=None,approved_by='EINKAUF-V2',change_reason='SYNTHETIC_APPROVED_CASE_CHANGE'))
                count=qty_case
                announced=count*units
                if asn_pattern=='BAD_QUANTITY': announced+=1
                insert(con,'asns',dict(asn_id=asn,asn_line_id='10',po_id=po,po_line_id='10',sku=sku,sent_at='2026-09-16T08:00:00',package_count=count,each_per_package=units,announced_base_qty=announced,pack_version_id=version,change_approval_id=approval_id))
                if receipt_pattern!='MISSING_RECEIPT':
                    rqty=announced-1 if receipt_pattern=='PARTIAL' else announced+1 if receipt_pattern=='EXCESS' else announced
                    insert(con,'receipts',dict(receipt_id=f'REC-{no}',receipt_line_id='10',asn_id=asn,asn_line_id='10',po_id=po,po_line_id='10',wms_article_id=f'WMS-{no}',received_at='2026-09-17T10:00:00',package_count=count,each_per_package=units,received_base_qty=rqty,processing_status='HOLD' if receipt_pattern=='HOLD' else 'POSTED'))
                if has_target:
                    onhand=announced if receipt_pattern=='HOLD' else int(max(0,announced//2))
                    block=onhand if receipt_pattern=='HOLD' else 0
                    insert(con,'stock_snapshots',dict(sku=sku,location_id='DC-HH-01',snapshot_at='2026-09-18T18:00:00',on_hand_base_qty=onhand,reserved_base_qty=0 if receipt_pattern=='HOLD' else min(12,onhand),blocked_base_qty=block))
            # Incidents only for a sample of generated anomalies. We must not claim an enterprise-wide case list.
            incident_type=('MISSING_TARGET' if missing_target else 'DIMENSION_MISMATCH' if length_wrong else
                  'UNAPPROVED_MAPPING' if old_rule else 'PACKAGING' if asn_pattern in ['UNKNOWN_PACK','UNAPPROVED_PACK','BAD_QUANTITY'] else
                  'RECEIPT_GAP' if receipt_pattern=='MISSING_RECEIPT' else None)
            if incident_type and ix%2==0:
                case=f'INC-V2-{no}'
                insert(con,'reported_cases',dict(case_id=case,affected_reference=sku,reported_symptom=incident_type,reported_by='SYNTHETIC-DQ-TEAM',reported_at='2026-09-18T12:00:00',investigation_status='OPEN'))
                ev=f'EVID-V2-{no}'
                insert(con,'issue_evidence',dict(evidence_id=ev,case_id=case,source_table='target_snapshot' if incident_type in ['DIMENSION_MISMATCH','MISSING_TARGET'] else 'asns',source_record_reference=sku,evidence_availability='MISSING' if incident_type=='RECEIPT_GAP' else 'UNCONFIRMED' if incident_type=='PACKAGING' else 'AVAILABLE',observed_at='2026-09-18T15:00:00',observation=f'SYNTHETIC_{incident_type}_TRIAGE_NOT_ROOT_CAUSE'))
            scenarios.append(dict(sku=sku,origin_type=origin,in_scope=in_scope if origin=='MIGRATED' else 'NOT_APPLICABLE',missing_target=int(bool(missing_target)),identity_issue=int(bool(identity_issue)),length_wrong=int(bool(length_wrong)),length_missing=int(bool(length_missing)),old_rule=int(bool(old_rule)),no_event=int(bool(no_event)),unknown_uom=int(bool(unknown_uom)),release_pattern=release_pattern,asn_pattern=asn_pattern,receipt_pattern=receipt_pattern,has_po=int(bool(has_po)),has_target=int(bool(has_target)),incident_type=incident_type or 'NONE',provenance='SYNTHETIC_GENERATED_V2',seed=SEED))
    con.execute('PRAGMA integrity_check')
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    con.close()
    with MANIFEST.open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(scenarios[0]));wr.writeheader();wr.writerows(scenarios)
    print('Created',OUT,'rows',len(scenarios))

if __name__=='__main__':build()
