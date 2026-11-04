-- DQ-01: Identität der 14 in-scope migrierten Artikel, ERP-Snapshot S2.
-- Fehlende Ziel-Datensätze sind nicht automatisch fehlgeschlagene Läufe.
SELECT m.legacy_record_id, l.sku, m.expected_target_record_id,
 CASE WHEN l.sku IS NULL OR m.expected_target_record_id IS NULL THEN 'NOT_EVALUABLE'
 WHEN (SELECT COUNT(*) FROM target_snapshot t WHERE t.snapshot_id='S2-2026-09-15' AND t.sku=l.sku)>1
   OR (SELECT COUNT(*) FROM target_snapshot t WHERE t.snapshot_id='S2-2026-09-15' AND t.target_record_id=m.expected_target_record_id)>1
   THEN 'DUPLICATE_TARGET'
 WHEN EXISTS (SELECT 1 FROM target_snapshot t WHERE t.snapshot_id='S2-2026-09-15' AND t.sku=l.sku AND t.target_record_id=m.expected_target_record_id) THEN 'PASS'
 WHEN EXISTS (SELECT 1 FROM target_snapshot t WHERE t.snapshot_id='S2-2026-09-15' AND t.sku=l.sku)
   OR EXISTS (SELECT 1 FROM target_snapshot t WHERE t.snapshot_id='S2-2026-09-15' AND t.target_record_id=m.expected_target_record_id)
   THEN 'IDENTITY_MISMATCH'
 ELSE 'MISSING_TARGET' END AS dq01_status
FROM migration_scope m LEFT JOIN legacy_snapshot l ON l.legacy_record_id=m.legacy_record_id
WHERE m.migration_run_id='RUN-2026-09' AND m.in_scope='YES'
ORDER BY l.sku;
