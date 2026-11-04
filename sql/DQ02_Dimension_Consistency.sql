-- DQ-02: geprüfte Länge (einzelnes Attribut), Toleranz im Pilot 0,01 mm.
-- DIMENSION_MISMATCH zählt nur bei vorhandenem Ziel-ERP-Datensatz.
WITH values_to_compare AS (
 SELECT l.sku, l.length_value AS source_length, l.dimension_uom AS source_uom,
        CASE WHEN UPPER(TRIM(l.dimension_uom))='IN' THEN ROUND(l.length_value*25.4,2)
             WHEN UPPER(TRIM(l.dimension_uom))='MM' THEN ROUND(l.length_value,2) END expected_length_mm,
        t.length_mm AS actual_length_mm, t.target_record_id
 FROM migration_scope m
 LEFT JOIN legacy_snapshot l ON l.legacy_record_id=m.legacy_record_id
 LEFT JOIN target_snapshot t ON t.snapshot_id='S2-2026-09-15'
                             AND t.sku=l.sku AND t.target_record_id=m.expected_target_record_id
 WHERE m.migration_run_id='RUN-2026-09' AND m.in_scope='YES'
)
SELECT sku, source_length,source_uom,expected_length_mm,actual_length_mm,
 CASE WHEN sku IS NULL OR source_length IS NULL OR source_uom IS NULL THEN 'NOT_EVALUABLE'
      WHEN target_record_id IS NULL THEN 'MISSING_TARGET'
      WHEN expected_length_mm IS NULL THEN 'UNSUPPORTED_UOM'
      WHEN actual_length_mm IS NULL THEN 'MISSING_TARGET_LENGTH'
      WHEN ABS(expected_length_mm-actual_length_mm)<=0.01 THEN 'PASS'
      ELSE 'DIMENSION_MISMATCH' END dq02_status
FROM values_to_compare ORDER BY sku;
