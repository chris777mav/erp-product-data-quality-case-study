-- DQ-06: alle 20 Artikel aus products × drei Prozesse; 18.09.2026 18:00 Uhr.
-- Die Klassen messen registrierte Prozessfreigaben, nicht allgemeine Operational Readiness.
WITH process_codes AS (SELECT 'PROCUREMENT' AS process_code UNION ALL SELECT 'WMS_RECEIPT' UNION ALL SELECT 'BRANCH_SUPPLY'),
active_counts AS (
 SELECT p.sku,pc.process_code,COUNT(r.release_id) AS active_count,
        MAX(r.decision) AS decision,MAX(r.reason_code) AS reason_code,MAX(r.approved_by) AS approved_by
 FROM products p CROSS JOIN process_codes pc
 LEFT JOIN releases r ON r.sku=p.sku AND r.process_code=pc.process_code
   AND datetime(r.valid_from)<=datetime('2026-09-18T18:00:00')
   AND (NULLIF(TRIM(r.valid_to),'') IS NULL OR datetime(r.valid_to)>datetime('2026-09-18T18:00:00'))
 GROUP BY p.sku,pc.process_code
), by_sku AS (
 SELECT sku,
   MAX(CASE WHEN process_code='PROCUREMENT' THEN decision END) procurement,
   MAX(CASE WHEN process_code='WMS_RECEIPT' THEN decision END) wms_receipt,
   MAX(CASE WHEN process_code='BRANCH_SUPPLY' THEN decision END) branch_supply,
   MAX(CASE WHEN process_code='PROCUREMENT' THEN reason_code END) procurement_reason,
   SUM(CASE WHEN active_count=0 THEN 1 ELSE 0 END) missing_processes,
   SUM(CASE WHEN active_count>1 THEN 1 ELSE 0 END) duplicate_processes,
   SUM(CASE WHEN active_count=1 AND (decision IS NULL OR decision NOT IN ('ALLOW','BLOCK','REVIEW')) THEN 1 ELSE 0 END) invalid_decisions,
   SUM(CASE WHEN active_count=1 AND (approved_by IS NULL OR TRIM(approved_by)='') THEN 1 ELSE 0 END) missing_approvers,
   SUM(CASE WHEN active_count=1 AND decision='REVIEW' AND reason_code='UNCONFIRMED_PACKAGING' THEN 1 ELSE 0 END) packaging_reviews,
   SUM(CASE WHEN active_count=1 AND decision='BLOCK' AND reason_code='DISCONTINUED' THEN 1 ELSE 0 END) discontinued_blocks
 FROM active_counts GROUP BY sku
)
SELECT sku,procurement,wms_receipt,branch_supply,missing_processes,duplicate_processes,
 CASE WHEN duplicate_processes>0 THEN 'DUPLICATE_ACTIVE_RELEASE'
      WHEN missing_processes>0 THEN 'MISSING_ACTIVE_RELEASE'
      WHEN invalid_decisions>0 THEN 'INVALID_RELEASE_DECISION'
      WHEN missing_approvers>0 THEN 'APPROVER_NOT_DOCUMENTED'
      WHEN discontinued_blocks=3 THEN 'DOCUMENTED_DISCONTINUATION'
      WHEN procurement='ALLOW' AND wms_receipt='ALLOW' AND branch_supply='ALLOW' THEN 'ALL_PROCESSES_ALLOW'
      WHEN procurement='BLOCK' AND procurement_reason='PLANNED_LAUNCH_HOLD'
       AND wms_receipt='ALLOW' AND branch_supply='ALLOW' THEN 'DOCUMENTED_LAUNCH_HOLD'
      WHEN packaging_reviews=3 THEN 'PACKAGING_REVIEW'
      ELSE 'OTHER_RELEASE_PATTERN_REVIEW' END dq06_status
FROM by_sku ORDER BY sku;
