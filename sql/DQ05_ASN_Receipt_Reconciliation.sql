-- DQ-05: Aggregation pro ASN-Position VOR Join; kein Beweis physischer Fehlmenge.
WITH receipt_summary AS (
 SELECT asn_id,asn_line_id,COUNT(*) AS receipt_count,SUM(received_base_qty) AS received_qty,
        SUM(CASE WHEN received_base_qty IS NULL THEN 1 ELSE 0 END) AS null_qty,
        SUM(CASE WHEN processing_status='POSTED' THEN 1 ELSE 0 END) AS posted_count,
        SUM(CASE WHEN processing_status='HOLD' THEN 1 ELSE 0 END) AS hold_count
 FROM receipts GROUP BY asn_id,asn_line_id
)
SELECT a.asn_id,a.po_id,a.sku,a.announced_base_qty AS announced_qty,rs.received_qty,
       rs.receipt_count,rs.posted_count,rs.hold_count,
 CASE WHEN rs.receipt_count IS NULL THEN 'MISSING_RECEIPT'
      WHEN a.announced_base_qty IS NULL OR rs.null_qty>0 THEN 'NOT_EVALUABLE'
      WHEN a.announced_base_qty<0 OR rs.received_qty<0 THEN 'INVALID_QUANTITY'
      WHEN rs.received_qty<a.announced_base_qty THEN 'PARTIALLY_RECORDED'
      WHEN rs.received_qty>a.announced_base_qty THEN 'EXCESS_RECORDED'
      WHEN rs.hold_count=rs.receipt_count THEN 'RECEIPT_ON_HOLD'
      WHEN rs.posted_count=rs.receipt_count THEN 'RECONCILED_POSTED'
      ELSE 'STATUS_REVIEW' END dq05_status
FROM asns a
LEFT JOIN receipt_summary rs ON rs.asn_id=a.asn_id AND rs.asn_line_id=a.asn_line_id
ORDER BY a.asn_id,a.asn_line_id;
