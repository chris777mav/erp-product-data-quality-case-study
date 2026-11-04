# V2 – Einzelakten aller 32 registrierten Incidents

**Geltung:** reine synthetische Fallstudie. Die Fachentscheidungen sind dokumentierte Empfehlungen, keine tatsächlich ausgeführten Unternehmensfreigaben. 32 historische V2-Incidents bleiben OPEN.
**Methode:** RISK-PILOT-1.1 unverändert; exakt aufgelöste PO-/Receipt-Referenzen, sieben SQL-Kontrollen, strikt dokumentierte Grenzen.
**Verknüpfung:** 28 direkte SKU-Referenzen; 4 indirekte fachliche Referenzen; 32 betroffene eindeutige Artikel.

Alle Empfehlungen erfordern echte Quellbelege und gegebenenfalls Freigaben; fehlende Receipts oder Events sind keine bewiesene physische Nichtlieferung oder ETL-Ursache.

## INC-001 — HYG-1004 — TARGET_RECORD_NOT_VISIBLE (P1)

**Referenzauflösung:** `HYG-1004` → `HYG-1004` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MIGRATION_TARGET_MISSING. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-001, EVID-002).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Migrierten Zielartikel und Eventquellen unter alter und neuer Identität prüfen. — *ERP-Migration / MDM*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-002 — HYG-1006 — DIMENSION_DISCREPANCY (P1)

**Referenzauflösung:** `HYG-1006` → `HYG-1006` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DIMENSION_MISMATCH | MAPPING_NONCOMPLIANT. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-003).
**Ursachenbewertung:** URSACHE_TEILWEISE_BELEGT. Nicht genehmigter Faktor 25,0 ist belegt; Auswahlgrund dieser Version offen. Korrektur nur in getrennter Testsandbox geschlossen.
**Nächste Maßnahme / Besitzer:** Quellwert, Umrechnungsregel und S2-Länge mit technischer Laufversion vergleichen. — *MDM / ERP / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-003 — HYG-1007 — PACKAGING_DIFFERENCE (P1)

**Referenzauflösung:** `PO-0007` → `HYG-1007` (PO->SKU). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_BLOCK | RECEIPT_HOLD. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-004, EVID-005).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** PO/ASN/Packversion/zeitliche Freigabe abgleichen; HOLD getrennt beurteilen. — *Einkauf / Lieferant / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-004 — HYG-1008 — PACKAGING_DIFFERENCE (P2)

**Referenzauflösung:** `PO-0008` → `HYG-1008` (PO->SKU). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_REVIEW. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-006).
**Ursachenbewertung:** URSACHE_OFFEN. Genehmigte Packänderung vor ASN; Bestellzeitpunkt verlangt eine dokumentierte Rückfrage. Kein Fehler als sicher behauptbar.
**Nächste Maßnahme / Besitzer:** PO/ASN/Packversion/zeitliche Freigabe abgleichen; HOLD getrennt beurteilen. — *Einkauf / Lieferant / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-005 — HYG-1011 — ORDER_PARTIALLY_DELIVERED (P2)

**Referenzauflösung:** `PO-0011` → `HYG-1011` (PO->SKU). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** RECEIPT_MISSING. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-007).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** ASN-Zeilen und Receipts getrennt abstimmen; fehlender Beleg keine Nichtlieferung. — *WMS / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-006 — HYG-1012 — RECEIPT_QUARANTINED (P1)

**Referenzauflösung:** `REC-0012` → `HYG-1012` (Receipt->ASN/PO->SKU). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** RECEIPT_HOLD. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-008).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** HOLD-Grund, gesperrten Bestand, Freigabegate und mögliche Prozessfolgen prüfen. — *WMS / Logistik*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-007 — HYG-1009 — WMS_RECORD_MISSING (P1)

**Referenzauflösung:** `HYG-1009` → `HYG-1009` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** WMS_REFERENCE_MISSING. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-009).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Schnittstellen- und WMS-Protokolle getrennt prüfen, kein bestimmter Root Cause ableitbar. — *WMS / Schnittstellenbetreuung*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-008 — HYG-1010 — WMS_RECORD_MISSING (P1)

**Referenzauflösung:** `HYG-1010` → `HYG-1010` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** WMS_REFERENCE_MISSING. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-010).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Schnittstellen- und WMS-Protokolle getrennt prüfen, kein bestimmter Root Cause ableitbar. — *WMS / Schnittstellenbetreuung*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-009 — HYG-1013 — PRODUCT_MEASURE_NOT_VERIFIED (P2)

**Referenzauflösung:** `HYG-1013` → `HYG-1013` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** SUPPLIER_EVIDENCE_UNCONFIRMED. **Evidenz:** NACHWEIS_UNBESTAETIGT (EVID-011).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Lieferantenmaßreferenz und Genehmigung nachfordern, nicht blind als Fehlmaß klassifizieren. — *MDM / Lieferant*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-010 — HYG-1016 — ARTICLE_NOT_ORDERABLE (P3)

**Referenzauflösung:** `HYG-1016` → `HYG-1016` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DOCUMENTED_LAUNCH_HOLD. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-012).
**Ursachenbewertung:** URSACHE_OFFEN. Geplanter Launch-HOLD statt belegtem DQ-Fehler; keine ungeprüfte Freigabe.
**Nächste Maßnahme / Besitzer:** Launch-Termin und dokumentierte Plan-Sperre gegen echte Blockade prüfen. — *Produktmanagement / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-011 — HYG-1017 — LAUNCH_NOT_RELEASED (P2)

**Referenzauflösung:** `HYG-1017` → `HYG-1017` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_RELEASE_REVIEW | SUPPLIER_EVIDENCE_UNCONFIRMED. **Evidenz:** NACHWEIS_UNBESTAETIGT (EVID-013).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Lieferanten-/Packnachweis nachfordern, REVIEW nicht als FAIL deklarieren. — *Produktmanagement / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2058 — HYG-2058 — DIMENSION_MISMATCH (P1)

**Referenzauflösung:** `HYG-2058` → `HYG-2058` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DIMENSION_MISMATCH. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2058).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Quellwert und Zielwert belegen; Mappingevent prüfen; Retest einschließlich Folgesystem vorsehen. — *MDM / ERP / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2062 — HYG-2062 — UNAPPROVED_MAPPING (P1)

**Referenzauflösung:** `HYG-2062` → `HYG-2062` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MAPPING_NONCOMPLIANT. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2062).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Version und Genehmigung zum Versandzeitpunkt kontrollieren; Laufkonfiguration/Selektion getrennt prüfen. — *ERP-Migration / Data Engineering*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2086 — HYG-2086 — MISSING_TARGET (P1)

**Referenzauflösung:** `HYG-2086` → `HYG-2086` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MIGRATION_TARGET_MISSING. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2086).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Migration-Scope, Laufprotokoll und erlaubte Nachladung klären. — *ERP-Migration / MDM*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2114 — HYG-2114 — RECEIPT_GAP (P2)

**Referenzauflösung:** `HYG-2114` → `HYG-2114` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** RECEIPT_MISSING. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-V2-2114).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Receipt-/WMS-Journal beschaffen, vor hypothetischer Nachbuchung Transportnachweis prüfen. — *WMS / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2116 — HYG-2116 — DIMENSION_MISMATCH (P1)

**Referenzauflösung:** `HYG-2116` → `HYG-2116` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DIMENSION_MISMATCH. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2116).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Quellwert und Zielwert belegen; Mappingevent prüfen; Retest einschließlich Folgesystem vorsehen. — *MDM / ERP / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2124 — HYG-2124 — UNAPPROVED_MAPPING (P1)

**Referenzauflösung:** `HYG-2124` → `HYG-2124` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MAPPING_NONCOMPLIANT. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2124).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Version und Genehmigung zum Versandzeitpunkt kontrollieren; Laufkonfiguration/Selektion getrennt prüfen. — *ERP-Migration / Data Engineering*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2172 — HYG-2172 — MISSING_TARGET (P1)

**Referenzauflösung:** `HYG-2172` → `HYG-2172` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MIGRATION_TARGET_MISSING. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2172).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Migration-Scope, Laufprotokoll und erlaubte Nachladung klären. — *ERP-Migration / MDM*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2174 — HYG-2174 — DIMENSION_MISMATCH (P1)

**Referenzauflösung:** `HYG-2174` → `HYG-2174` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DIMENSION_MISMATCH. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2174).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Quellwert und Zielwert belegen; Mappingevent prüfen; Retest einschließlich Folgesystem vorsehen. — *MDM / ERP / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2186 — HYG-2186 — UNAPPROVED_MAPPING (P1)

**Referenzauflösung:** `HYG-2186` → `HYG-2186` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MAPPING_NONCOMPLIANT | PACKAGING_BLOCK. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2186).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Version und Genehmigung zum Versandzeitpunkt kontrollieren; Laufkonfiguration/Selektion getrennt prüfen. — *ERP-Migration / Data Engineering*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2222 — HYG-2222 — PACKAGING (P1)

**Referenzauflösung:** `HYG-2222` → `HYG-2222` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_BLOCK. **Evidenz:** NACHWEIS_UNBESTAETIGT (EVID-V2-2222).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** PO/ASN/Packversion gegen Lieferantenbestätigung abgleichen, WMS-Freigabe nicht fingieren. — *Einkauf / Lieferant / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2228 — HYG-2228 — RECEIPT_GAP (P2)

**Referenzauflösung:** `HYG-2228` → `HYG-2228` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** RECEIPT_MISSING. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-V2-2228).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Receipt-/WMS-Journal beschaffen, vor hypothetischer Nachbuchung Transportnachweis prüfen. — *WMS / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2232 — HYG-2232 — DIMENSION_MISMATCH (P1)

**Referenzauflösung:** `HYG-2232` → `HYG-2232` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DIMENSION_MISMATCH. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2232).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Quellwert und Zielwert belegen; Mappingevent prüfen; Retest einschließlich Folgesystem vorsehen. — *MDM / ERP / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2246 — HYG-2246 — PACKAGING (P1)

**Referenzauflösung:** `HYG-2246` → `HYG-2246` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_BLOCK. **Evidenz:** NACHWEIS_UNBESTAETIGT (EVID-V2-2246).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** PO/ASN/Packversion gegen Lieferantenbestätigung abgleichen, WMS-Freigabe nicht fingieren. — *Einkauf / Lieferant / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2248 — HYG-2248 — UNAPPROVED_MAPPING (P1)

**Referenzauflösung:** `HYG-2248` → `HYG-2248` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MAPPING_NONCOMPLIANT. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2248).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Version und Genehmigung zum Versandzeitpunkt kontrollieren; Laufkonfiguration/Selektion getrennt prüfen. — *ERP-Migration / Data Engineering*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2258 — HYG-2258 — MISSING_TARGET (P1)

**Referenzauflösung:** `HYG-2258` → `HYG-2258` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MIGRATION_TARGET_MISSING. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2258).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Migration-Scope, Laufprotokoll und erlaubte Nachladung klären. — *ERP-Migration / MDM*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2290 — HYG-2290 — DIMENSION_MISMATCH (P1)

**Referenzauflösung:** `HYG-2290` → `HYG-2290` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** DIMENSION_MISMATCH. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2290).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Quellwert und Zielwert belegen; Mappingevent prüfen; Retest einschließlich Folgesystem vorsehen. — *MDM / ERP / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2310 — HYG-2310 — UNAPPROVED_MAPPING (P1)

**Referenzauflösung:** `HYG-2310` → `HYG-2310` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** MAPPING_NONCOMPLIANT. **Evidenz:** REGISTRIERTE_BELEGE_VERFUEGBAR (EVID-V2-2310).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Version und Genehmigung zum Versandzeitpunkt kontrollieren; Laufkonfiguration/Selektion getrennt prüfen. — *ERP-Migration / Data Engineering*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2342 — HYG-2342 — RECEIPT_GAP (P2)

**Referenzauflösung:** `HYG-2342` → `HYG-2342` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** RECEIPT_MISSING. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-V2-2342).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Receipt-/WMS-Journal beschaffen, vor hypothetischer Nachbuchung Transportnachweis prüfen. — *WMS / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2372 — HYG-2372 — PACKAGING (P1)

**Referenzauflösung:** `HYG-2372` → `HYG-2372` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_BLOCK. **Evidenz:** NACHWEIS_UNBESTAETIGT (EVID-V2-2372).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** PO/ASN/Packversion gegen Lieferantenbestätigung abgleichen, WMS-Freigabe nicht fingieren. — *Einkauf / Lieferant / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2444 — HYG-2444 — PACKAGING (P1)

**Referenzauflösung:** `HYG-2444` → `HYG-2444` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** PACKAGING_BLOCK. **Evidenz:** NACHWEIS_UNBESTAETIGT (EVID-V2-2444).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** PO/ASN/Packversion gegen Lieferantenbestätigung abgleichen, WMS-Freigabe nicht fingieren. — *Einkauf / Lieferant / WMS*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.

## INC-V2-2456 — HYG-2456 — RECEIPT_GAP (P2)

**Referenzauflösung:** `HYG-2456` → `HYG-2456` (SKU direkt). **Historischer Status:** `OPEN`.
**Kontrollbefunde:** RECEIPT_MISSING. **Evidenz:** NACHWEIS_FEHLT_IM_ABZUG (EVID-V2-2456).
**Ursachenbewertung:** URSACHE_OFFEN. Symptom und verfügbare Daten dokumentiert; genaue technische Ursache durch die vorhandenen Belege nicht abschließend ermittelt.
**Nächste Maßnahme / Besitzer:** Receipt-/WMS-Journal beschaffen, vor hypothetischer Nachbuchung Transportnachweis prüfen. — *WMS / Einkauf*.
**Abschlusskriterien:** Fachentscheidung inkl. Datum, Verantwortlichem und Event-/Quellnachweisen; Betroffene SQL-Kontrollen nach Maßnahme wiederholen; Abhängige ERP-/WMS-/Freigabefolgen dokumentieren; Administrative Entscheidung erst danach freigeben.
