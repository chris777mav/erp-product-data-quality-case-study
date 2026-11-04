-- DQ-04: ASN-intern, gegen Stammdaten, und Approval-Scope.
-- BLOCK/REVIEW sind vorgeschlagene Pilotentscheidungen, keine reale Unternehmenspolitik.
SELECT a.asn_id,a.po_id,a.sku,p.expected_pack_version_id,a.pack_version_id,
 CASE WHEN p.po_id IS NULL THEN 'REVIEW'
      WHEN a.package_count IS NULL OR a.each_per_package IS NULL OR a.announced_base_qty IS NULL THEN 'REVIEW'
      WHEN a.package_count<=0 OR a.each_per_package<=0 OR a.announced_base_qty<=0
        OR a.package_count*a.each_per_package<>a.announced_base_qty THEN 'BLOCK'
      WHEN pkg.pack_version_id IS NULL THEN 'BLOCK'
      WHEN pkg.approval_status IS NULL OR pkg.approval_status<>'APPROVED'
        OR pkg.units_of_child IS NULL OR pkg.units_of_child<>a.each_per_package THEN 'BLOCK'
      WHEN date(a.sent_at) IS NULL OR date(pkg.valid_from) IS NULL THEN 'REVIEW'
      WHEN date(a.sent_at)<date(pkg.valid_from)
        OR (NULLIF(TRIM(pkg.valid_to),'') IS NOT NULL AND
             (date(pkg.valid_to) IS NULL OR date(a.sent_at)>=date(pkg.valid_to))) THEN 'BLOCK'
      WHEN p.expected_pack_version_id IS NULL OR a.pack_version_id IS NULL THEN 'REVIEW'
      WHEN p.expected_pack_version_id=a.pack_version_id THEN 'PASS'
      WHEN c.change_approval_id IS NULL THEN 'BLOCK'
      WHEN c.sku IS NULL OR c.approved_pack_version_id IS NULL
        OR c.sku<>a.sku OR c.approved_pack_version_id<>a.pack_version_id THEN 'BLOCK'
      WHEN datetime(c.approved_at) IS NULL OR datetime(c.effective_from) IS NULL
        OR NULLIF(TRIM(c.approved_by),'') IS NULL THEN 'REVIEW'
      WHEN datetime(c.approved_at)>datetime(a.sent_at) OR datetime(c.effective_from)>datetime(a.sent_at)
        OR (NULLIF(TRIM(c.effective_to),'') IS NOT NULL AND
             (datetime(c.effective_to) IS NULL OR datetime(a.sent_at)>=datetime(c.effective_to))) THEN 'BLOCK'
      WHEN datetime(p.order_at) IS NULL THEN 'REVIEW'
      WHEN datetime(c.approved_at)>datetime(p.order_at) THEN 'REVIEW'
      ELSE 'PASS' END dq04_status
FROM asns a
LEFT JOIN purchase_orders p ON p.po_id=a.po_id AND p.po_line_id=a.po_line_id
LEFT JOIN packaging_levels pkg ON pkg.sku=a.sku AND pkg.pack_version_id=a.pack_version_id AND pkg.level_code='CASE'
LEFT JOIN change_approvals c ON c.change_approval_id=a.change_approval_id
ORDER BY a.asn_id,a.asn_line_id;
