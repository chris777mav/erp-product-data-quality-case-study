-- Phase 4 | SIMULATED DATA, not Target Canada or any real employer.

PRAGMA foreign_keys=OFF;

-- RAW landing zone: intentionally no business CHECK/FK constraints. Diagnose before cleansing.

CREATE TABLE IF NOT EXISTS "suppliers" (
  "supplier_id" TEXT,
  "supplier_name" TEXT,
  "supplier_status" TEXT, PRIMARY KEY (supplier_id)
);

CREATE TABLE IF NOT EXISTS "products" (
  "sku" TEXT,
  "product_group" TEXT,
  "description" TEXT,
  "origin_type" TEXT,
  "lifecycle_status" TEXT,
  "base_uom" TEXT,
  "created_at" TEXT, PRIMARY KEY (sku)
);

CREATE INDEX IF NOT EXISTS "idx_products_sku" ON "products" ("sku");

CREATE TABLE IF NOT EXISTS "supplier_articles" (
  "supplier_id" TEXT,
  "supplier_article_no" TEXT,
  "sku" TEXT,
  "valid_from" TEXT,
  "valid_to" TEXT,
  "approval_status" TEXT, PRIMARY KEY (supplier_id, supplier_article_no, valid_from)
);

CREATE INDEX IF NOT EXISTS "idx_supplier_articles_sku" ON "supplier_articles" ("sku");

CREATE TABLE IF NOT EXISTS "supplier_references" (
  "reference_id" TEXT,
  "supplier_id" TEXT,
  "supplier_article_no" TEXT,
  "sku" TEXT,
  "pack_version_id" TEXT,
  "confirmed_at" TEXT,
  "valid_from" TEXT,
  "valid_to" TEXT,
  "approval_status" TEXT,
  "case_qty" INTEGER,
  "reference_source_id" TEXT,
  "approved_by" TEXT, PRIMARY KEY (reference_id)
);

CREATE INDEX IF NOT EXISTS "idx_supplier_references_sku" ON "supplier_references" ("sku");

CREATE TABLE IF NOT EXISTS "packaging_levels" (
  "pack_version_id" TEXT,
  "sku" TEXT,
  "level_code" TEXT,
  "child_level_code" TEXT,
  "units_of_child" INTEGER,
  "gtin" TEXT,
  "valid_from" TEXT,
  "valid_to" TEXT,
  "approval_status" TEXT,
  "length_mm" REAL,
  "width_mm" REAL,
  "height_mm" REAL,
  "gross_weight_g" REAL,
  "measure_evidence" TEXT, PRIMARY KEY (pack_version_id, level_code)
);

CREATE INDEX IF NOT EXISTS "idx_packaging_levels_sku" ON "packaging_levels" ("sku");

CREATE TABLE IF NOT EXISTS "legacy_snapshot" (
  "snapshot_id" TEXT,
  "extracted_at" TEXT,
  "legacy_record_id" TEXT,
  "sku" TEXT,
  "length_value" REAL,
  "dimension_uom" TEXT,
  "case_qty" INTEGER,
  "base_uom" TEXT,
  "lifecycle_status" TEXT, PRIMARY KEY (snapshot_id, legacy_record_id)
);

CREATE INDEX IF NOT EXISTS "idx_legacy_snapshot_sku" ON "legacy_snapshot" ("sku");

CREATE TABLE IF NOT EXISTS "migration_scope" (
  "migration_run_id" TEXT,
  "legacy_record_id" TEXT,
  "in_scope" TEXT,
  "exclusion_reason" TEXT,
  "expected_target_record_id" TEXT,
  "mapping_rule_version" TEXT,
  "approved_at" TEXT,
  "approved_by" TEXT, PRIMARY KEY (migration_run_id, legacy_record_id)
);

CREATE TABLE IF NOT EXISTS "mapping_rules" (
  "mapping_rule_id" TEXT,
  "rule_version" TEXT,
  "source_field" TEXT,
  "target_field" TEXT,
  "transformation" TEXT,
  "factor" REAL,
  "valid_from" TEXT,
  "valid_to" TEXT,
  "approval_status" TEXT,
  "approved_by" TEXT, PRIMARY KEY (mapping_rule_id, rule_version)
);

CREATE TABLE IF NOT EXISTS "migration_events" (
  "event_id" TEXT,
  "migration_run_id" TEXT,
  "legacy_record_id" TEXT,
  "target_record_id" TEXT,
  "sent_at" TEXT,
  "received_at" TEXT,
  "load_status" TEXT,
  "error_code" TEXT,
  "applied_rule_version" TEXT,
  "applied_length_factor" REAL, PRIMARY KEY (event_id)
);

CREATE TABLE IF NOT EXISTS "target_snapshot" (
  "snapshot_id" TEXT,
  "extracted_at" TEXT,
  "target_record_id" TEXT,
  "sku" TEXT,
  "length_mm" REAL,
  "width_mm" REAL,
  "height_mm" REAL,
  "case_qty" INTEGER,
  "pack_version_id" TEXT,
  "base_uom" TEXT,
  "lifecycle_status" TEXT, PRIMARY KEY (snapshot_id, target_record_id)
);

CREATE INDEX IF NOT EXISTS "idx_target_snapshot_sku" ON "target_snapshot" ("sku");

CREATE TABLE IF NOT EXISTS "change_approvals" (
  "change_approval_id" TEXT,
  "sku" TEXT,
  "approved_pack_version_id" TEXT,
  "approved_at" TEXT,
  "effective_from" TEXT,
  "effective_to" TEXT,
  "approved_by" TEXT,
  "change_reason" TEXT, PRIMARY KEY (change_approval_id)
);

CREATE INDEX IF NOT EXISTS "idx_change_approvals_sku" ON "change_approvals" ("sku");

CREATE TABLE IF NOT EXISTS "releases" (
  "release_id" TEXT,
  "sku" TEXT,
  "process_code" TEXT,
  "decision" TEXT,
  "reason_code" TEXT,
  "approved_by" TEXT,
  "valid_from" TEXT,
  "valid_to" TEXT, PRIMARY KEY (release_id)
);

CREATE INDEX IF NOT EXISTS "idx_releases_sku" ON "releases" ("sku");

CREATE TABLE IF NOT EXISTS "wms_snapshot" (
  "snapshot_id" TEXT,
  "extracted_at" TEXT,
  "wms_article_id" TEXT,
  "sku" TEXT,
  "accepted_pack_version_id" TEXT,
  "known_case_qty" INTEGER,
  "wms_status" TEXT, PRIMARY KEY (snapshot_id, wms_article_id)
);

CREATE INDEX IF NOT EXISTS "idx_wms_snapshot_sku" ON "wms_snapshot" ("sku");

CREATE TABLE IF NOT EXISTS "interface_events" (
  "event_id" TEXT,
  "sku" TEXT,
  "target_record_id" TEXT,
  "wms_article_id" TEXT,
  "sent_at" TEXT,
  "received_at" TEXT,
  "processing_status" TEXT,
  "error_code" TEXT,
  "payload_version" TEXT, PRIMARY KEY (event_id)
);

CREATE INDEX IF NOT EXISTS "idx_interface_events_sku" ON "interface_events" ("sku");

CREATE TABLE IF NOT EXISTS "purchase_orders" (
  "po_id" TEXT,
  "po_line_id" TEXT,
  "supplier_id" TEXT,
  "sku" TEXT,
  "ordered_qty" INTEGER,
  "order_uom" TEXT,
  "ordered_base_qty" INTEGER,
  "expected_pack_version_id" TEXT,
  "expected_case_qty" INTEGER,
  "expected_case_count" INTEGER,
  "order_at" TEXT,
  "order_status" TEXT, PRIMARY KEY (po_id, po_line_id)
);

CREATE INDEX IF NOT EXISTS "idx_purchase_orders_sku" ON "purchase_orders" ("sku");

CREATE TABLE IF NOT EXISTS "asns" (
  "asn_id" TEXT,
  "asn_line_id" TEXT,
  "po_id" TEXT,
  "po_line_id" TEXT,
  "sku" TEXT,
  "sent_at" TEXT,
  "package_count" INTEGER,
  "each_per_package" INTEGER,
  "announced_base_qty" INTEGER,
  "pack_version_id" TEXT,
  "change_approval_id" TEXT, PRIMARY KEY (asn_id, asn_line_id)
);

CREATE INDEX IF NOT EXISTS "idx_asns_sku" ON "asns" ("sku");

CREATE TABLE IF NOT EXISTS "receipts" (
  "receipt_id" TEXT,
  "receipt_line_id" TEXT,
  "asn_id" TEXT,
  "asn_line_id" TEXT,
  "po_id" TEXT,
  "po_line_id" TEXT,
  "wms_article_id" TEXT,
  "received_at" TEXT,
  "package_count" INTEGER,
  "each_per_package" INTEGER,
  "received_base_qty" INTEGER,
  "processing_status" TEXT, PRIMARY KEY (receipt_id, receipt_line_id)
);

CREATE TABLE IF NOT EXISTS "stock_snapshots" (
  "sku" TEXT,
  "location_id" TEXT,
  "snapshot_at" TEXT,
  "on_hand_base_qty" INTEGER,
  "reserved_base_qty" INTEGER,
  "blocked_base_qty" INTEGER, PRIMARY KEY (sku, location_id, snapshot_at)
);

CREATE INDEX IF NOT EXISTS "idx_stock_snapshots_sku" ON "stock_snapshots" ("sku");

CREATE TABLE IF NOT EXISTS "reported_cases" (
  "case_id" TEXT,
  "affected_reference" TEXT,
  "reported_symptom" TEXT,
  "reported_by" TEXT,
  "reported_at" TEXT,
  "investigation_status" TEXT, PRIMARY KEY (case_id)
);

CREATE TABLE IF NOT EXISTS "issue_evidence" (
  "evidence_id" TEXT,
  "case_id" TEXT,
  "source_table" TEXT,
  "source_record_reference" TEXT,
  "evidence_availability" TEXT,
  "observed_at" TEXT,
  "observation" TEXT, PRIMARY KEY (evidence_id)
);

CREATE TABLE IF NOT EXISTS "correction_actions" (
  "action_id" TEXT,
  "case_id" TEXT,
  "affected_reference" TEXT,
  "field_name" TEXT,
  "old_value" REAL,
  "proposed_value" REAL,
  "approved_by" TEXT,
  "approved_at" TEXT,
  "applied_at" TEXT,
  "dependent_retest_status" TEXT,
  "closure_status" TEXT, PRIMARY KEY (action_id)
);
