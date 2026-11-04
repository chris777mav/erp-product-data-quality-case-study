-- DQ-07: erst Aggregation von Evidence und Actions, dann JOIN zu Incidents.
-- Fehlt applied_at, ist die Umsetzung nicht DOKUMENTIERT (nicht zwingend ausgeblieben).
WITH e AS (
 SELECT case_id,COUNT(*) evidence_count,
 SUM(CASE WHEN UPPER(TRIM(evidence_availability))='AVAILABLE' THEN 1 ELSE 0 END) available_count,
 SUM(CASE WHEN UPPER(TRIM(evidence_availability))='MISSING' THEN 1 ELSE 0 END) missing_count,
 SUM(CASE WHEN UPPER(TRIM(evidence_availability))='UNCONFIRMED' THEN 1 ELSE 0 END) unconfirmed_count
 FROM issue_evidence GROUP BY case_id
),a AS (
 SELECT case_id,COUNT(*) action_count,
 SUM(CASE WHEN NULLIF(TRIM(approved_by),'') IS NOT NULL AND NULLIF(TRIM(approved_at),'') IS NOT NULL THEN 1 ELSE 0 END) approved_count,
 SUM(CASE WHEN NULLIF(TRIM(applied_at),'') IS NOT NULL THEN 1 ELSE 0 END) documented_applied_count,
 SUM(CASE WHEN UPPER(TRIM(COALESCE(dependent_retest_status,''))) LIKE 'PENDING%' THEN 1 ELSE 0 END) pending_retest_count,
 SUM(CASE WHEN UPPER(TRIM(closure_status))='CLOSED' THEN 1 ELSE 0 END) closed_action_count
 FROM correction_actions GROUP BY case_id
)
SELECT c.case_id,c.affected_reference,c.investigation_status,
 COALESCE(e.evidence_count,0) evidence_count,COALESCE(e.available_count,0) available_count,
 COALESCE(e.missing_count,0) missing_count,COALESCE(e.unconfirmed_count,0) unconfirmed_count,
 COALESCE(a.action_count,0) action_count,COALESCE(a.approved_count,0) approved_count,
 COALESCE(a.documented_applied_count,0) documented_applied_count,COALESCE(a.pending_retest_count,0) pending_retest_count,
 CASE WHEN COALESCE(e.evidence_count,0)=0 THEN 'NO_EVIDENCE_RECORDED'
      WHEN COALESCE(e.missing_count,0)>0 THEN 'MISSING_EVIDENCE_RECORDED'
      WHEN COALESCE(e.unconfirmed_count,0)>0 THEN 'UNCONFIRMED_EVIDENCE_RECORDED'
      WHEN e.available_count=e.evidence_count THEN 'ALL_RECORDED_EVIDENCE_AVAILABLE'
      ELSE 'EVIDENCE_STATUS_REVIEW' END evidence_status,
 CASE WHEN COALESCE(a.action_count,0)=0 THEN 'NO_ACTION_RECORDED'
      WHEN a.approved_count<a.action_count THEN 'APPROVAL_NOT_FULLY_DOCUMENTED'
      WHEN a.documented_applied_count<a.action_count THEN 'APPROVED_APPLICATION_NOT_DOCUMENTED'
      WHEN a.pending_retest_count>0 THEN 'RETEST_PENDING'
      WHEN a.closed_action_count=a.action_count THEN 'ACTIONS_MARKED_CLOSED'
      ELSE 'ACTION_FOLLOW_UP_REQUIRED' END action_status
FROM reported_cases c LEFT JOIN e ON e.case_id=c.case_id LEFT JOIN a ON a.case_id=c.case_id
ORDER BY c.case_id;
