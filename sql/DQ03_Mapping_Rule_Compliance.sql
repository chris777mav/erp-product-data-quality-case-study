-- DQ-03: Ereignisse, Soll-Version, tatsächlicher Faktor, Genehmigung, Gültigkeitsintervall.
-- Sent-At ist Proxy für Transformationszeit; valid_to vorläufig exklusiv.
SELECT l.sku, m.mapping_rule_version AS expected_version,
       e.applied_rule_version,e.applied_length_factor,e.load_status,
       mr.approval_status,mr.valid_from,mr.valid_to,e.sent_at,
 CASE WHEN e.event_id IS NULL THEN 'NO_EVENT'
      WHEN e.applied_rule_version IS NULL OR m.mapping_rule_version IS NULL THEN 'NOT_EVALUABLE'
      WHEN e.applied_rule_version<>m.mapping_rule_version THEN 'VERSION_MISMATCH'
      ELSE 'PASS' END version_check,
 CASE WHEN e.event_id IS NULL THEN 'NO_EVENT'
      WHEN mr.rule_version IS NULL THEN 'RULE_NOT_FOUND'
      WHEN mr.approval_status='APPROVED' THEN 'APPROVED'
      WHEN mr.approval_status IS NULL THEN 'APPROVAL_UNKNOWN'
      ELSE 'UNAPPROVED_RULE' END approval_check,
 CASE WHEN e.event_id IS NULL THEN 'NO_EVENT'
      WHEN mr.rule_version IS NULL THEN 'RULE_NOT_FOUND'
      WHEN date(e.sent_at) IS NULL OR date(mr.valid_from) IS NULL THEN 'TEMPORAL_CHECK_NOT_EVALUABLE'
      WHEN date(e.sent_at)<date(mr.valid_from) THEN 'NOT_YET_EFFECTIVE'
      WHEN NULLIF(TRIM(mr.valid_to),'') IS NOT NULL AND (date(mr.valid_to) IS NULL OR date(e.sent_at)>=date(mr.valid_to)) THEN 'EXPIRED'
      ELSE 'EFFECTIVE_AT_SENT_TIME' END validity_check,
 CASE WHEN e.event_id IS NULL THEN 'NO_EVENT'
      WHEN l.dimension_uom='MM' THEN CASE WHEN e.applied_length_factor=1.0 THEN 'NOT_APPLICABLE' ELSE 'MM_COPY_FACTOR_REVIEW' END
      WHEN l.dimension_uom='IN' THEN CASE WHEN mr.factor IS NULL OR e.applied_length_factor IS NULL THEN 'NOT_EVALUABLE'
         WHEN ABS(e.applied_length_factor-mr.factor)>0.000001 THEN 'REGISTERED_FACTOR_MISMATCH'
         WHEN ABS(e.applied_length_factor-25.4)>0.000001 THEN 'FACTOR_MISMATCH' ELSE 'PASS' END
      ELSE 'UNSUPPORTED_UOM' END factor_check
FROM migration_scope m
LEFT JOIN legacy_snapshot l ON l.legacy_record_id=m.legacy_record_id
LEFT JOIN migration_events e ON e.migration_run_id=m.migration_run_id AND e.legacy_record_id=m.legacy_record_id
LEFT JOIN mapping_rules mr ON mr.mapping_rule_id='UOM_LENGTH' AND mr.rule_version=e.applied_rule_version
WHERE m.migration_run_id='RUN-2026-09' AND m.in_scope='YES'
ORDER BY l.sku,e.event_id;
