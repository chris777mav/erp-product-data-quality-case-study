# Untersuchung von Produktdatenfehlern und Verfügbarkeitsproblemen im Rahmen einer ERP-Migration und Produkteinführung

## Phase 3 – Konkretes Untersuchungsszenario, fachliches Datenmodell und Geschäftsregeln

**Dokument:** Fachkonzept und Modellierungsfreigabe, Version **1.0**  
**Datum:** 25. Oktober 2026  
**Status:** Fachliche Festlegung für eine *simulierte Fallstudie*; Datensätze, Prüfprogramme und Ergebnisse sind **noch nicht erstellt**.  
**Verwendung:** Interner, überprüfbarer Arbeitsnachweis für das Portfolio; die öffentliche Portfolio-Zusammenfassung bleibt separat.  
**Vorgängerversion:** Fachkonzept 0.1 (technischer Fachgroßhandel / Fliesen und Verlegeprofile) wird durch die hier begründete Schwerpunktsetzung **ersetzt**.

---

## 1. Begründung, Untersuchungsauftrag und Fallgrenzen

### 1.1 Reale Referenz und eigene Simulation

Der **Target-Canada-Fall** ist der historische Ausgangspunkt für die Problemmechanismen: Fehler in Produktabmessungen, Mengen- und Verpackungsinformationen, Schwierigkeiten im Zusammenspiel der Warenwirtschaft und Lagerverwaltung sowie Störungen der Warenverteilung und Regalverfügbarkeit. Die investigative Berichterstattung enthält **keine verwendbaren Originaldatensätze und keinen nachweislich betroffenen Einzelartikel**. Das vielfach zitierte Zahnbürstenbeispiel ist ausdrücklich hypothetisch. Target Canada richtete im Zuge seines Markteintritts eine neue IT-Landschaft ein; es war **keine klassische Legacy-ERP-Migration**.

**Konsequenz:** Unsere Fallstudie ist **nicht** „die Lösung des Target-Canada-Falls“. Wir entwickeln eine **eigenständige Untersuchung** für ein fiktives Handelsunternehmen, einschließlich einer ausdrücklich simulierten ERP-Migration. In der Fallstudie werden keine tatsächlichen Systemkonfigurationen, Produktfehler, Leistungskennzahlen oder Lieferanten von Target behauptet. Der reale Fall belegt das betriebliche Problem – nicht unsere simulierten Ereignisse.

**Quellenbasis:** Originalbericht Maclean’s/Canadian Business vom 22. Januar 2016; GS1-Regelwerk für Handelsartikel und Verpackungshierarchien; SAP-Dokumentation als allgemeine Fachreferenz. Die Quellen sind am Dokumentende verlinkt.

### 1.2 Verbindliche Geschäftsfall-Festlegung

| Dimension | Festlegung für die Fallstudie |
|---|---|
| **Unternehmen** | Fiktives Handelsunternehmen, das verpackte Hygiene- und Drogerieprodukte einkauft, in einem Zentrallager lagert und Filialen beliefert. |
| **Produktart** | **Verpackte Hygiene- und Drogerieprodukte** als abgegrenzte Warengruppe. Keine bestimmte reale Zahnbürstenmarke und kein historischer Target-Artikel erforderlich. |
| **Beschaffung** | Ein oder mehrere Lieferanten mit Artikel- und Verpackungsinformationen; für jede beschaffbare Kombination wird eine führende, bestätigte Lieferanten- und Verpackungsvereinbarung benötigt. |
| **Systeme** | Simulierter Datenauszug des **Altsystems (Legacy ERP)**, **Ziel-ERP**, **Bestellungen**, **Lieferavis / Versandinformation** und **Lagerverwaltung (WMS)**. Keine Nachbildung eines SAP- oder Manhattan-Produkts. |
| **Warenfluss** | Lieferant → Bestellung / angekündigte Verpackung → Wareneingang im Zentrallager → Bestandsführung / mögliche Weiterverteilung an Filiale. |
| **Produkteinführung** | Neuanlage von Artikeln nach oder parallel zum Cutover, die vor Beschaffung oder Freigabe die passenden Stammdaten und Verpackungsregeln erfüllen müssen. |
| **Auslöser der Untersuchung** | Nach dem simulierten Go-live werden Artikel-, Einheiten- und Verpackungsabweichungen gemeldet; einzelne Bestellungen oder Wareneingänge befinden sich im Klärungsstatus; neue Artikel sind teilweise noch nicht freigegeben. |
| **Zentrale Frage** | Entstand eine Abweichung bereits bei Lieferant oder Altsystem, bei Mapping/Transformation/Import, durch veraltete Verpackungsangaben, bei der Übergabe zum WMS oder aufgrund einer **gültigen** Sperr- bzw. Änderungssituation? |
| **Bearbeitungsumfang** | Fachliche Datenprüfung, Reconciliation, Ursachennachweise, Maßnahmen- und Freigabelogik. Keine Realmigration, keine Entwicklung eines vollständigen ERP/WMS, keine echte Filialversorgung. |

**Drei Untersuchungslinien bilden zusammen einen Arbeitsauftrag:**

- **U1 – ERP-Übernahme:** Sind migrationspflichtige Artikel und relevante Verpackungsinformationen korrekt und nachvollziehbar im Ziel-ERP angekommen?
- **U2 – Bestellung und Wareneingang:** Sind Bestellmenge, zulässige Verpackungskonfiguration und angekündigte/empfangene Ware zeitlich und fachlich konsistent? Können Abweichungen erklärt und kontrolliert bearbeitet werden?
- **U3 – Produkteinführung / Freigabe:** Können neue Artikel nach definierten Daten- und Prozessregeln für Beschaffung, Lagerverarbeitung und Filialbelieferung freigegeben werden? Eine berechtigte Sperre ist **kein Fehler**.

### 1.3 Was „Verfügbarkeit“ hier bedeutet

Wir vermeiden einen pauschalen, nicht messbaren Verfügbarkeitsbegriff:

| Zustand | Festgelegte Bedeutung | Im Pilot überprüfbar? |
|---|---|---|
| **ERP-Existenz** | Ein Artikel ist im definierten Ziel-ERP-Datenstand eindeutig auffindbar. | Ja. |
| **Beschaffbarkeit** | Der Artikel ist laut freigegebenem Status, Lieferanten-/Bestellbedingungen und Verpackungsdaten in einer zulässigen Einheit bestellbar. | Ja, regelbasiert. |
| **Wareneingangs-Verarbeitbarkeit** | Eine Lieferung kann aufgrund konsistenter Identität, Bestellbezug, Einheiten und Packstückinformationen ohne ungelösten Konflikt verbucht werden. | Ja, als simuliertes Regelurteil. |
| **Systemisch verfügbarer Lagerbestand** | Bestand am angegebenen Lagerort und Zeitpunkt, abzüglich expliziter Sperr-/Reservierungsmengen. | Ja, **Systembestand**, keine physische Inventurbestätigung. |
| **Filial-Belieferungsfähigkeit** | Artikel ist freigegeben, lagerseitig zuordenbar und der Bestand kann für die Filiale bereitgestellt werden. | Eingeschränkt: nur nach festgelegten, simulierten Regeln. |
| **Regalverfügbarkeit** | Der Artikel liegt tatsächlich kaufbar im Filialregal. | **Nein**: ohne Filial-Scans / Regalprüfung nicht nachweisbar. Nur als dokumentiertes reales Referenzproblem. |

**Nicht enthalten:** E-Commerce, dynamische Nachfrageprognose, tatsächliche Transportplanung, Kassensysteme und die Bewertung realer Target-Filialen. Ein späteres Dashboard darf keine nicht beobachtete Regalverfügbarkeit vortäuschen.

---

## 2. Prozessmodell und verbindliche Datenübergaben

### 2.1 Zeitlicher Bezugsrahmen

- **T0 – Quellsystem-Stichtag:** eingefrorener Legacy-Datenstand und dokumentierte Auswahl der zu migrierenden Artikel.
- **T1 – Migration:** Mapping-Regelversion, Migrationslauf, Importstatus, Ziel-ERP-Datenstand. Der Zeitraum zwischen T0 und T1 wird dokumentiert.
- **T2 – Bestellung:** Bestellzeitpunkt, gültiger Lieferantenvertrag bzw. gültige Verpackungskonfiguration, Ziel-ERP-Status.
- **T3 – Lieferavis (ASN):** vom Lieferanten angekündigte Mengen, Packstück- und Verpackungsstruktur, ggf. freigegebene Änderung.
- **T4 – Wareneingang:** tatsächlich erfasste Packstücke, Mengen, Klärungsstatus und Zeitpunkt.
- **T5 – Bestands-/Freigabeprüfung:** Lager-Snapshot und Freigabestand zum Auswertungszeitpunkt.

Stichtage dienen als **Vergleichslogik**. Exakte Kalenderdaten und Datensätze werden erst in der späteren Datenerstellung festgelegt. Wir vergleichen niemals stillschweigend Werte verschiedener Zeitstände oder Regelversionen.

### 2.2 Zwei getrennte, zusammenhängende Prozesse

**A. Bestehende Artikel – Migrationsprozess**

```text
Lieferanten-Referenzdaten ────────┐
                                 v
Legacy-ERP-Snapshot -> Profiling / Scope / Mapping -> Transferlauf -> Ziel-ERP-Snapshot
                                      |                 |                  |
                               Transformationsregeln  Importprotokoll   Reconciliation
                                                                         |
                                                             Freigabe / Klärungsfall
```

**B. Bestehende und neue Artikel – operativer Prozess**

```text
Bestätigte Lieferanten- und Verpackungsdaten ----┐
                                                 v
Ziel-ERP-Artikel + Pack-Hierarchie -> Bestellung -> Lieferavis (ASN)
             |                        |                 |
             +---- Artikelübergabe zum WMS              |
                                      |                 v
                                      +----------> WMS-Wareneingang
                                                       |
                                             Abgleich / Quarantäne /
                                              Freigabe / Bestand
                                                       |
                                         Filialbelieferung (Regelurteil)
```

**Neue Artikel** werden unabhängig von einer Legacy-ID im Ziel-ERP angelegt und durchlaufen dieselbe Prüfung von Referenzdaten, Verpackungsstruktur und Freigabe. Sie dürfen im Migrationsabgleich **nicht** als „fehlende Altartikel“ bewertet werden.

### 2.3 Datenvertrag je Systemübergang (fachlich, nicht technisch)

| Übergang | Führende bzw. sendende Information | Erwarteter Empfänger / Verwendung | Notwendige Referenzen | Pflichtkontrolle | Hauptzuständigkeit |
|---|---|---|---|---|---|
| **D1 Lieferant → Produktdatenpflege** | Lieferantenartikelnummer, Bezeichnung, Einheit, Verpackungslevels/-mengen, Maße/Gewicht soweit benötigt, Versions-/Gültigkeitsstand | Artikelanlage / Master Data | Lieferant, Artikelbeziehung, Datenstand, Bestätigung | Identität, Aktualität, Vollständigkeit, fachliche Freigabe | Einkauf / Stammdaten |
| **D2 Legacy ERP → Ziel-ERP** | Migrierte Artikelstammsätze, Identifikatoren, Basiseinheiten, gültige Verpackungszuordnungen | Ziel-ERP | Migrations-Scope, Identifier-Mapping, Regelversion, Lauf-ID | Scope-Abdeckung, Feldvergleich nach Regeln, Importstatus | ERP-Projekt / Stammdaten |
| **D3 Ziel-ERP → Bestellung** | Artikelkennung, beschaffbare Einheit, Umrechnung, zugelassene Verpackung, Status | Bestellposition | Artikelversion, Lieferant, Gültigkeit | Statusfreigabe, zulässige Einheit, korrekte Mengenumrechnung | Einkauf |
| **D4 Bestellung → Lieferant** | Bestellreferenz, Artikel, bestellte Menge + Einheit, ggf. vereinbarte Verpackungsversion | Lieferantenbestätigung/-lieferung | Bestellnummer, Position, Lieferantenbezug | Vollständige Bestellidentität und erwartete Menge | Einkauf |
| **D5 Lieferant → Lieferavis (ASN)** | Referenz auf Bestellposition, gelieferte Artikel, angekündigte Packstücke + Stück je Packstück, Liefer-/Packversion | Wareneingang | PO-Position, Artikel-/Verpackungsbezug, Zeitstand | Bestellung ↔ angekündigte Gesamtmenge und Packstruktur; zulässige Abweichung kennzeichnen | Lieferant / Einkauf |
| **D6 Ziel-ERP → WMS** | WMS-relevanter Artikel und Verpackungshierarchie | Anlage/Abgleich WMS-Artikelstamm | ERP-/WMS-ID, Versions-/Sendezeitpunkt, Übergabestatus | Ankunft, Zuordnung, Versionsstand; Fehlernachricht | ERP-IT / Lager-IT |
| **D7 ASN + Bestellung + WMS → Wareneingang** | Erwartete und beobachtete Packstücke, Mengen, Identifikatoren, Verarbeitungsstatus | Wareneingangsprüfung / Bestandsbuchung | Bestellung, ASN, WMS-Artikel, Pack-/Case-Ebene | Mengen- **und** Verpackungsprüfung; offene Konflikte isolieren | Lager / ERP Support |
| **D8 Wareneingang → Bestand / Filialfreigabe** | Verbuchte, gesperrte oder reservierte Menge, Artikelstatus und Verwendungsstatus | Verfügbarkeitsbewertung | Lagerort, Zeitpunkt, Freigabestatus | Bestand nur aus zulässig verbuchten Bewegungen; Sperren berücksichtigen | Logistik / Vertrieb |

**Keine unbegründeten Annahmen:** Die simulierte Schnittstelle muss keine echte SAP-/Manhattan-Verbindung sein. Sie wird durch datierte Exporte/Nachrichten- und Verarbeitungsstände repräsentiert. Nicht übertragene Information ist „fehlend / unbekannt“, nicht automatisch ein bestimmter Schnittstellenfehler.

### 2.4 Zuständige fachliche Quelle (Source of Truth)

- **Produktspezifikation und vereinbarte Packung:** die *fachlich bestätigte*, zum Vorgang gültige Lieferanteninformation; nicht jede beliebige, möglicherweise veraltete Lieferantendatei.
- **Migrationspflicht:** der genehmigte Migrationsumfang bei T0, nicht die bloße Existenz im Altsystem.
- **Transformation:** genehmigte, versionierte Mapping-/Umrechnungsregel.
- **Bestellung:** die bestätigte Bestellposition und ihr gültiger Vertrags-/Packbezug bei T2.
- **Ankündigung:** tatsächlich übermitteltes Lieferavis bei T3 (nicht automatisch korrekte Wahrheit über Ware).
- **Wareneingang:** beobachtete und erfasste Eingangsmenge / Packstruktur bei T4; physische Richtigkeit außerhalb der kontrollierten Simulation nicht verifizierbar.
- **Systembestand:** zeitlich definierter WMS-Bestandsstand bei T5. Keine Aussage über tatsächlich gefüllte Regale.

Ein Konflikt zwischen Quellen wird nicht durch blindes Überschreiben gelöst. Er erzeugt einen dokumentierten Klärungsfall mit benanntem Datenverantwortlichen.

---

## 3. Fachliches Datenmodell (Conceptual + Logical Business Data Model)

### 3.1 Identitäten und fachliche Grundannahmen

1. Die **interne SKU** ist die einzelne in der Fallstudie geführte Artikelvariante. Für die Simulation liegt **eine Basiseinheit (EA/Stück)** je SKU vor. Ein Verbrauchsprodukt mit mehreren Packungsgrößen kann mehrere SKUs besitzen; nicht jeder Karton ist eine eigene verkaufbare SKU.
2. Legacy-Artikel-ID und Ziel-ERP-Artikel-ID sind **systemlokal**; Gleichheit darf nicht vorausgesetzt werden. Ein durch den Migrationsumfang genehmigtes `LegacyID → TargetID`-Mapping dient als Identitätsnachweis. Zusammenführungen / Aufteilungen müssen als explizite Ausnahme dokumentiert werden.
3. Die **Lieferantenartikelnummer** ist nur zusammen mit der Lieferantenkennung zuverlässig identifizierbar.
4. Eine **GTIN** identifiziert, soweit vorhanden und zulässig verwendet, eine Handelsartikelebene. Eine GTIN der Verbrauchereinheit darf nicht ungeprüft als GTIN der Kartonebene verwendet werden. Die GTIN ist **nicht** gleichzusetzen mit einer Seriennummer einer konkreten Sendung; logistischer Sendungsbezug ggf. über separate ID/SSCC.
5. Eine **Verpackungsstruktur** besitzt einen zeitlich gültigen Versionsstand. Sie kann sich ändern, ohne dass sich die Verbrauchereinheit oder deren Bestellmenge ändert. Bei GTIN-gekennzeichneten Verpackungsebenen sind GS1-Regeln zur Vergabe einer neuen GTIN bei Änderung der Pack-/Case-Menge zu berücksichtigen.
6. Eine `PO-Position`, ein `ASN-Posten` und ein `Wareneingangs-Posten` sind unterschiedliche Geschäftsvorfälle. Sie werden über eindeutige Vorgangs- und Positionsschlüssel verknüpft, **nicht** allein über SKU und Datum.

### 3.2 Geschäftsobjekte, Schlüssel und Beziehungen

| Kürzel | Geschäftsobjekt | Fachlicher Schlüssel / Identität | Kardinalität und fachliche Beziehung |
|---|---|---|---|
| **SUP** | Lieferant | `SupplierID` | 1 Lieferant → viele Lieferantenartikel und Bestellungen. |
| **ART** | Artikel / SKU | `InternalSKU` | 1 Artikel → mehrere Systemrepräsentationen, Verpackungsstände, Bestellpositionen und Fehlerfälle. |
| **SUPART** | Lieferantenartikel | `(SupplierID, SupplierArticleNo)` plus gültiger Bezug | 1 Lieferantenartikel → eine fachlich bestätigte interne SKU pro Gültigkeitsstand; eine SKU → ggf. mehrere Lieferantenartikel. |
| **REF** | Lieferanten-Referenzstand | `ReferenceVersionID` | Datierte / bestätigte Felder und Verpackungshierarchien für SUPART; mehrere Versionen möglich. |
| **SYSREC** | Systemrepräsentation | `(SystemID, SystemRecordID, SnapshotID)` | Quell- und Zielauszug je Zeitpunkt; Verknüpfung zu ART über geprüfte Identifier-Mappings. |
| **MIG** | Migrationsumfang und Zuordnung | `(MigrationRunID, LegacyRecordID)` | Erwartet ein Ziel oder explizit genehmigte Ausnahme; enthält Scope-Entscheidung und Zielzuordnung. |
| **RULEMAP** | Feld-/Transformationsregel | `(MappingRuleID, Version)` | Eine Regel ist für bestimmte Felder/Produkte und einen Zeitbereich gültig. |
| **IMP** | Import-/Übergabeereignis | `EventID` | Referenziert Lauf, Quell-/Zieldatensatz, Zeitpunkt, Verarbeitungscode und übermittelte Information. |
| **PACK** | Verpackungsebene/-version | `(SKU, PackagingVersionID, LevelID)` | Eine SKU → mehrere zeitlich gültige Ebenen; jede höhere Ebene referenziert eine enthaltene Ebene und positive Menge. |
| **PO** | Bestellung und Bestellposition | `POID` / `(POID, POLineID)` | 1 Bestellung → viele Positionen; Position referenziert SKU, Lieferant, Menge und vereinbarte Packversion. |
| **ASN** | Lieferavis und Lieferavisposition | `ASNID` / `(ASNID, ASNLineID)` | 1 Lieferavis → viele Positionen; je Position Bezug zu PO-Position. Mehrere AVIs pro Bestellung möglich. |
| **RECEIPT** | Wareneingang und Eingangsposten | `ReceiptID` / `(ReceiptID, ReceiptLineID)` | Bezieht sich auf PO-/ASN-Position und WMS-Artikel; Teil- und Mehrfacheingänge möglich. |
| **STOCK** | Lagerbestandsstand | `(SKU, LocationID, SnapshotTime)` | Eine SKU → mehrere Lagerorte und Zeitstände, mit frei / gesperrt / reserviert getrennt. |
| **RELEASE** | Artikel-/Prozessfreigabe | `(SKU, ProcessCode, ValidFrom)` | Je SKU unterschiedliche Freigaben für Migration, Beschaffung, WMS-Nutzung oder Filialbelieferung. |
| **ISSUE** | Fehlermeldung / Untersuchungsfall | `IssueID` | Verknüpft eine oder mehrere Datensatz-/Vorgangsreferenzen mit Symptom, Prüfbeleg, Hypothese, Status, Korrektur und Re-Test. |
| **EVID** | Untersuchungsnachweis | `EvidenceID` | 1 Fall → mehrere Nachweise mit Datenquelle, Zeitpunkt, Referenz und Bewertung. |

**Bewusste Modellgrenzen:** Es gibt noch keine SQL-Tabellen, SQL-Datentypen, Datenbank-DDL oder synthetischen Zeilen. Die Modellierung bleibt implementierungsneutral; technische Normalisierung und Exportformate folgen aus diesem Fachkonzept.

### 3.3 Geschäftliche Beziehungen, in Worten

- **Artikel ↔ Lieferant:** n:m über Lieferantenartikel. Ein Artikel kann mehrere Bezugsquellen haben, aber jede Bestellung hat genau einen festgelegten Lieferanten.
- **Artikel ↔ Systemdatensatz:** 1:n über dokumentierte Identitätszuordnungen, da dieselbe SKU in Legacy und Ziel-ERP unterschiedliche Schlüssel besitzen kann.
- **Artikel ↔ Verpackung:** 1:n Verpackungsebenen und -versionen. Für **eine** gültige Version gibt es genau eine Basisebene, optional eine oder mehrere höhere Ebenen; im Pilot ist die prüfrelevante Standardhierarchie **Stück → Karton (Case)**. Innenkartons und Paletten bleiben Erweiterungsoptionen, nicht Pflicht.
- **Bestellung → ASN → Wareneingang:** 1:n-Beziehungen auf Positionsniveau; eine Bestellposition darf mehrere Ankündigungen und Teilwareneingänge besitzen. Die Summe wird unter Berücksichtigung von Stornierung, Teillieferung und Toleranzen verglichen.
- **Freigabe und Bestand:** Ein Bestandseintrag beweist keine Freigabe; eine Freigabe beweist keinen Bestand. Beide Zustände bleiben unabhängig.
- **Fehlerfall ↔ Nachweis:** 1:n. Eine gemeldete Anomalie darf bis zu ihrem belegten Abschluss als **ungeklärt** geführt werden.

### 3.4 Mindest-Datenwörterbuch für die spätere Umsetzung

`Text`, `Datum/Uhrzeit`, `Ganzzahl` und `Dezimalzahl` sind **fachliche Datentypen**; die spätere technische Speicherung ist noch offen.

| Objekt | Pflichtinformationen im Pilot | Gültigkeits-/Konsistenzhinweis |
|---|---|---|
| **Artikel** | `InternalSKU` (Text), `ProductGroup` (Text), `Description` (Text), `LifecycleStatus` (Text), `BaseUOM` (Text), `OriginType` (MIGRATED/NEW) | `InternalSKU` pro aktivem Stand eindeutig; `BaseUOM = EA` im Pilot. |
| **Lieferantenartikel** | `SupplierID`, `SupplierArticleNo`, `InternalSKU`, `ValidFrom`, `ValidTo`, `ApprovalStatus` | Paar `(SupplierID, SupplierArticleNo)` im gültigen Kontext eindeutig; Überlappungen explizit klären. |
| **Lieferantenstand** | `ReferenceVersionID`, `SupplierID`, `SupplierArticleNo`, `ConfirmedAt`, `ValidFrom`, `ApprovedBy`, `ReferenceSourceID` | Prüfgrundlage nur bei dokumentierter fachlicher Bestätigung. |
| **Systemauszug** | `SystemID` (LEGACY/TARGET/WMS), `SnapshotID`, `ExtractedAt`, `SystemRecordID`, `InternalSKU/MappingReference`, `ValueFields` | Speicherung des Rohwerts inkl. Herkunft; ohne Auszugszeitpunkt keine direkte Gleichheitsbehauptung. |
| **Migration** | `MigrationRunID`, `LegacyRecordID`, `InScope`, `ExclusionReason`, `TargetRecordID/MappingStatus`, `RuleVersion`, `LoadedAt`, `LoadStatus` | Nicht jeder Legacy-Datensatz ist migrationspflichtig; neue Artikel tragen keine Legacy-ID. |
| **Mapping-Regel** | `MappingRuleID`, `Version`, `SourceField`, `TargetField`, `Transformation`, `ValidFrom`, `ApprovedStatus` | Nur genehmigte Version für den Lauf heranziehen. |
| **Verpackungsebene** | `SKU`, `PackagingVersionID`, `LevelID`, `LevelCode` (EACH/CASE), `ChildLevelID`, `UnitsOfChild`, `GTINIfAssigned`, `ValidFrom`, `ValidTo`, `ApprovalStatus` | Positive ganze Stückzahlen; keine Zyklen; eine gültige Basisebene; GTIN je Ebene getrennt. |
| **Maß-/Gewichtsfelder** | `SKU`, `PackagingVersionID`, `LevelCode`, `Length`, `Width`, `Height`, `DimensionUOM`, `GrossWeight`, `WeightUOM`, `EvidenceSourceID` | Maße gehören zu **genau der angegebenen Ebene**; keine dimensionsbezogene fachliche „Richtigkeit“ ohne Referenz. |
| **Bestellposition** | `POID`, `POLineID`, `SupplierID`, `SKU`, `OrderedQuantity`, `OrderUOM`, `PackagingVersionID`, `OrderDate`, `OrderStatus` | Menge > 0 bei aktiver Bestellung; explizite Umrechnung in Basiseinheiten. |
| **Lieferavisposition** | `ASNID`, `ASNLineID`, `POID`, `POLineID`, `SKU`, `PackageCount`, `EachPerPackage`, `AnnouncedBaseQty`, `PackagingVersionID`, `SentAt`, `ChangeApprovalID` | Interne Mengenrechnung prüfbar; von Bestellung abweichender Verpackungsstand kann gültig sein, wenn genehmigt. |
| **Wareneingangsposten** | `ReceiptID`, `ReceiptLineID`, `ASNID/POReference`, `WMSArticleReference`, `ReceivedPackageCount`, `ReceivedEachPerPackage`, `ReceivedBaseQty`, `ReceiptTime`, `ProcessingStatus` | Wareneingangsmenge von Packstruktur trennen; HOLD/REVIEW nicht als frei verfügbar buchen. |
| **WMS-Übergabeereignis** | `EventID`, `SourceArticleReference`, `TargetWMSReference`, `SentAt`, `ReceivedAtIfKnown`, `ProcessingStatus`, `ErrorCodeIfAvailable`, `PayloadVersion` | Eine fehlende WMS-Zuordnung ist zunächst Beobachtung; Ursachenbeleg nötig. |
| **Bestandsstand** | `SKU`, `LocationID`, `SnapshotTime`, `OnHandBaseQty`, `ReservedBaseQty`, `BlockedBaseQty`, `AvailableBaseQty` | `Available` anhand fachlicher Regel ableiten, nicht mit Regalbestand gleichsetzen. |
| **Freigabe** | `SKU`, `ProcessCode`, `Decision` (ALLOW/BLOCK/REVIEW), `ReasonCode`, `ApprovedBy`, `ValidFrom`, `ValidTo` | Beschaffungsfreigabe ≠ Wareneingangsfreigabe ≠ Filialbelieferung. |
| **Fehlerfall** | `IssueID`, `OpenedAt`, `AffectedReference`, `SymptomCode`, `RuleID`, `FindingStatus`, `CauseStatus`, `CauseEvidenceID`, `Owner`, `Action`, `RecheckStatus` | Hypothese nie als bestätigte Ursache ausgeben; jeder Befund erhält nachvollziehbaren Beleg. |

**Identifikatorhinweis:** Für die Simulation dürfen künstliche IDs verwendet werden, aber sie müssen als solche gekennzeichnet werden. „Gültige GTIN“ darf nur behauptet werden, wenn eine korrekte Kennzeichnungs- und Prüflogik zugrunde liegt; eine formal korrekte Prüfziffer belegt weder rechtmäßige Vergabe noch den tatsächlichen Herstellerbezug. Der Pilot funktioniert auch ohne erfundene echte GTINs: `GTIN unbekannt` führt nicht automatisch zu `GTIN fehlerhaft`.

---

## 4. Geschäftsregeln – verbindlicher Katalog für den Pilotfall

**Verbindlich** bedeutet hier: *für den fiktiven Pilotfall fachlich beschlossen*, nicht „dies gilt gesetzlich für alle Hygieneprodukte“. Die tatsächliche Testimplementierung muss gegen diese Version geprüft werden. Jede Regel benötigt im späteren Regelregister zusätzlich die ausgeführte Prüfdefinition, Version und den Re-Test-Nachweis.

### 4.1 Identität, Migration und Provenienz

| ID | Regel / Entscheidung | Konkrete Datenbasis | Bei Verletzung |
|---|---|---|---|
| **BR-01** | Nur `InScope=ja` bei T0 ist verpflichtender Teil der Migration. | Legacy-Snapshot, Migrationsumfang | Außerhalb des Umfangs: **kein Migrationsfehler**; fehlender Scope-Status: REVIEW. |
| **BR-02** | Identitätsabgleich erfolgt über freigegebenes Legacy-zu-Target-Mapping. Beschreibungsgleichheit allein genügt nicht. | Legacy-/Target-ID, Mapping | Unklarer Match: REVIEW statt behaupteter Verlust. |
| **BR-03** | Eine aktive interne SKU darf je System und Snapshot nicht widersprüchlich mehrfach geführt werden. | SKU, System, Snapshot, Status | Duplikat-/Konsistenzbefund. |
| **BR-04** | Neue Artikel (`OriginType=NEW`) haben keine notwendige Legacy-ID und werden als Einführungsfälle, nicht als Migrationsfehler geprüft. | SKU, Herkunft, Anlagedatum | Falsche Kohortenzuordnung korrigieren. |
| **BR-05** | Zielwerte sind gegen *genehmigte Transformationsregeln* und den korrekten Stichtag zu vergleichen. | Quell-/Zielwert, Regelversion, Zeitstand | Regelkonforme Abweichung PASS; abweichender Wert FAIL/REVIEW je Evidenz. |
| **BR-06** | Ohne belastbares Import-/Verarbeitungsereignis kann eine fehlende Ziel-SKU als Abweichung gelten, die technische Ursache bleibt jedoch offen. | Source/Target-Snapshots, Importlog | `CauseStatus=UNCONFIRMED`. |

### 4.2 Produktstamm, Maße und Verpackung

| ID | Regel / Entscheidung | Konkrete Datenbasis | Bei Verletzung |
|---|---|---|---|
| **BR-07** | Produktstammdaten für Freigabe besitzen SKU, Produktgruppe, zugelassene Basiseinheit, Lieferantenbezug und bestätigte, relevante Verpackungsversion. | Artikel, SUPART, REF, PACK | Fehlender notwendiger Wert: BLOCK für betreffende Nutzung. |
| **BR-08** | Basiseinheit je SKU ist im Pilot `EA` (Stück). Jede alternative Bestell- oder Packeinheit muss einen dokumentierten Umrechnungsfaktor besitzen. | Artikel, Umrechnung, Verpackung | Fehlt der Faktor: REVIEW/BLOCK der Mengenverarbeitung. |
| **BR-09** | Jede höhere Verpackungsebene enthält eine **positive ganze** Anzahl untergeordneter Einheiten; Hierarchie ist zyklenfrei. | Verpackungsversion, Eltern-Kind-Bezug | Fehlerhafte Hierarchie: BLOCK der betroffenen Packebene. |
| **BR-10** | Für eine Bestellung/Sendung gilt eine zum Vorgang gültige, bestätigte Verpackungsversion; überlappende widersprüchliche Versionen ohne Auflösung sind nicht zulässig. | `ValidFrom/To`, Bestell-/ASN-Datum, Bestätigung | REVIEW bis zur fachlichen Klärung. |
| **BR-11** | GTINs der Verbrauchereinheit und der Verpackungsebene dürfen nicht verwechselt werden. Bei dokumentiertem Case-Mengenwechsel muss die Identifikation der geänderten Packebene gemäß GS1 behandelt werden, soweit diese Ebene eine GTIN führt. | GTIN je Level, Versionsänderung, GS1-Regel | Falsche Level-Zuordnung oder ungeregelter Wechsel: REVIEW/BLOCK. |
| **BR-12** | Maße und Gewicht werden mit eigener Einheit und **Packebene** geführt. Absolute Plausibilität ist ohne unabhängige Referenz kein Korrektheitsnachweis. | Dimensions-/Gewichtsfelder, Einheit, Referenz | Fehlende Einheit/Level: FAIL; auffälliger Wert ohne Referenz: REVIEW. |
| **BR-13** | Eine Lieferantenartikelnummer wird nur zusammen mit `SupplierID` auf Identität geprüft. | Lieferant, Lieferantenartikelnummer | Unterschiedliche Lieferanten mit gleichem Text sind kein automatisches Duplikat. |

### 4.3 Bestellung, ASN, Wareneingang, Bestand

| ID | Regel / Entscheidung | Konkrete Datenbasis | Bei Verletzung |
|---|---|---|---|
| **BR-14** | Aktive PO-Position: Menge > 0, identifizierter Lieferant/Artikel, zulässige Einheit, beschaffbarer Status und gültige Packvereinbarung. | Bestellung, Artikel, Freigabe, PACK | BLOCK oder REVIEW der **Bestellung**, nicht globale Artikelsperre. |
| **BR-15** | Bestellte, angekündigte und empfangene Mengen werden in **Basiseinheiten** verglichen; die je Vorgang geltende Umrechnungsregel muss bekannt sein. | PO, ASN, Receipt, UOM-Faktoren | Nicht interpretierbarer Mengenstand: REVIEW. |
| **BR-16** | Zusätzlich zur Basismenge werden Packstückanzahl, Stück je Packstück und vereinbarte Verpackungsversion verglichen. Gleiche Gesamtmenge beweist **nicht** gleiche Verpackungsstruktur. | PO-Packstand, ASN-Packstand, Receipt-Packstand | Abweichung: REVIEW; nachgewiesen unzulässige Packung: FAIL. |
| **BR-17** | Eine abweichende Packstruktur ist **nicht** automatisch ein Fehler, wenn eine rechtzeitig gültige, fachlich genehmigte alternative Konfiguration vorliegt und die Identifikations-/Prozessanforderungen erfüllt. | Änderungsfreigabe, Packversion, Zeitstempel | Genehmigter Wechsel: PASS mit dokumentiertem Change; ohne Freigabe: REVIEW. |
| **BR-18** | Teil- und Mehrfachlieferungen werden positionsweise kumuliert; offen, storniert und bereits verbucht werden getrennt betrachtet. | PO-Status, mehrere ASN/Receipts, Teillieferungskennzeichen | Teilanlieferung allein ist kein Mengenfehler. |
| **BR-19** | Nicht freigegebene Wareneingänge (HOLD/REVIEW) erhöhen **nicht** den frei verfügbaren Systembestand. | Receipt-Status, WMS-Buchung, STOCK | Falsche Bestandsfreigabe: BLOCK / Datenkorrektur. |
| **BR-20** | Der verwendbare Systembestand ist grundsätzlich `OnHand − Reserved − Blocked` in derselben Basiseinheit und demselben Zeit-/Lagerkontext; negative Ergebnisse werden geklärt, nicht stillschweigend auf null gesetzt. | STOCK, Standort, Zeitpunkt | Widersprüchlicher Bestand: REVIEW/FAIL je Regel. |
| **BR-21** | Fehlgeschlagener WMS-Datentransfer ist erst bei geeignetem Ereignis-/Quell-Ziel-Nachweis als Integrationsfehler bestätigt. | Übergabestatus, Nachricht, WMS-Auszug | Ohne Evidenz `CauseStatus=UNCONFIRMED`. |

### 4.4 Produkteinführung, Freigabe und Ursachenbeleg

| ID | Regel / Entscheidung | Konkrete Datenbasis | Bei Verletzung |
|---|---|---|---|
| **BR-22** | Für neue Artikel erfolgt Beschaffungs- und WMS-Freigabe erst nach der zugehörigen Stammdaten-/Verpackungsprüfung. Filialfreigabe ist ein **separater** Entscheidungsschritt. | `OriginType=NEW`, RELEASE, Prüfresultate | Nicht freigegeben = gültige Sperre, solange kein Prozessbruch nachgewiesen. |
| **BR-23** | Jede Regelprüfung ergibt **PASS**, **FAIL** oder **NOT_EVALUABLE**; ein fehlender Nachweis darf nicht stillschweigend als PASS gelten. | Prüflauf, Daten- und Referenzstatus | `NOT_EVALUABLE` erzeugt Klärung, keine automatische Fehlerbehauptung. |
| **BR-24** | Die Ursache wird nur dann als **CONFIRMED** geführt, wenn Ursache, relevanter Zeitstand und unterstützende Belege dokumentiert sind. | ISSUE, EVID, Versionen, Protokolle | Sonst HYPOTHESIS/UNCONFIRMED. |
| **BR-25** | Korrekturen brauchen fachliche Zustimmung, unveränderten Originalwert, Änderungsbeleg, Revalidierung aller abhängigen Prüfungen und dokumentiertes Ergebnis. | ISSUE, Änderungsprotokoll, Prüfung vor/nach | Ohne Re-Test keine abschließende Freigabe. |
| **BR-26** | Eine rechtmäßige oder fachlich genehmigte Sperre, Auslistung oder bewusste Migrationsausnahme ist als **gültige Geschäftsentscheidung** getrennt von Fehlerfällen auszuweisen. | Status, Genehmigung, Gültigkeit | `VALID_EXCLUSION`, nicht „Fehlerquote“. |

**Abgrenzung zu allgemeinen Branchenregeln:** Die obigen Anforderungen sind Regeln unserer simulierten Organisation. GS1 bestätigt fachliche Konzepte von Verpackungsebenen und Kennzeichnungen; SAP-Dokumentation beschreibt die Trennung zwischen Basiseinheit und alternativen Einheiten. Ein Hinweis auf GS1/SAP belegt **nicht**, dass die historische Target-Implementierung genau so aufgebaut war.

---

## 5. Prüfentscheidung, Priorisierung und Ursachenklassifikation

### 5.1 Drei getrennte Entscheidungen

1. **Befundstatus:** `PASS` / `FAIL` / `NOT_EVALUABLE`. Beschreibt, was eine konkrete Regelprüfung ergeben hat.
2. **Prozessfreigabe:** `ALLOW` / `BLOCK` / `REVIEW`. Beschreibt, was angesichts aller für den Prozess relevanten Befunde geschehen darf.
3. **Ursachenstatus:** `CONFIRMED` / `HYPOTHESIS` / `UNCONFIRMED` / `NOT_APPLICABLE`. Beschreibt den epistemischen Status einer Ursachenbehauptung.

Beispielhafte Logik: Eine Änderung der Verpackungsversion kann einen auffälligen Quell-/Zielvergleich erzeugen; ist sie korrekt genehmigt und zum Stichtag wirksam, lautet die fachliche Entscheidung `ALLOW`, nicht „Datenfehler“. Ein fehlendes WMS-Ereignis führt möglicherweise zu `REVIEW`, nicht automatisch zu `Integration Failure`.

### 5.2 Ursachenklassifikation

| Ursachencode | Bedeutung | Minimaler Nachweis für „bestätigt“ |
|---|---|---|
| `SRC` | Ursprungs-/Lieferantendaten unzutreffend | Im ursprünglichen bestätigten Datensatz bereits Abweichung gegenüber belastbarer, unabhängiger Referenz. |
| `ENTRY` | Fehler bei manueller Datenerfassung | Bestätigte Referenz korrekt; im Erfassungsstand abweichender Wert + Zeit-/Vorgangsbezug. |
| `MAP` | Feldzuordnung falsch | Quellfeld, Mapping-Spezifikation und tatsächlich genutztes Zielfeld belegen Fehlzuordnung. |
| `TRANSFORM` | Umrechnung/Transformation falsch | Genehmigte Rechenregel und tatsächlich berechneter Zielwert widersprechen sich nachweislich. |
| `LOAD` | Datensatz beim Ladevorgang abgelehnt, verloren oder falsch geladen | Erwarteter Datensatz plus Lauf-/Importbeleg (oder anderweitiger gleichwertiger Nachweis). |
| `INTERFACE` | Datenübergabe zum WMS fehlgeschlagen oder beschädigt | Korrekte Senderinformation + nachweisbar fehlgeschlagene / beschädigte Übergabe am gleichen Zeitstand. |
| `PACK_CHANGE` | Korrekte Änderung der Verpackungskonfiguration | Zeitlich gültige Lieferanten-/Fachfreigabe und passende aktualisierte Verpackungsebene. **Kein Fehler**, sofern prozesskonform. |
| `BUSINESS_RULE` | Gültige fachliche Sperre / Auslistung | Dokumentierte aktive Freigaberegel oder Genehmigung. **Kein technischer Fehler**. |
| `UNKNOWN` | Ursache nicht hinreichend feststellbar | Fehlende oder widersprüchliche Evidenz dokumentiert. |

Ein Fehler kann **mehrere Befunde** haben; die primäre Ursache wird nicht nach einem pauschalen Ursachenranking, sondern anhand der nachweisbaren Kausalkette zugeordnet. Mögliche Prognose- oder Lagerkapazitätsprobleme werden **nicht** als Produktdatenursachen umetikettiert.

### 5.3 Geschäftliche Priorität

- **Kritisch:** bereits ausgelöste oder drohende fehlerhafte Bestandsbuchung, nicht verarbeitbarer Wareneingang mit operativem Rückstau, falsche Identität/Umrechnung bei aktiven Bestellungen.
- **Hoch:** Migrationspflichtiger Artikel nicht eindeutig nutzbar oder Beschaffungsfreigabe eines geplanten Neuartikels durch ungeklärten, prüfbaren Stammdatenkonflikt blockiert.
- **Mittel:** nicht operative oder vorläufig tolerierte Qualitätsabweichung mit bekanntem Owner und genehmigter Ausnahme.
- **Kein Fehler:** fachlich legitime, dokumentierte Sperre oder vereinbarte Verpackungsänderung.

Es werden noch **keine** Fallzahlen, Fehlerquoten oder Einsparungen erfunden.

---

## 6. Akzeptanzfälle und Abnahmekriterien

Die folgenden **Szenarioklassen** sind zukünftige Abnahmetests, **keine schon erzeugten Datenfälle**. Ihr erwartetes Ergebnis wird **vor** der Datenerstellung festgehalten. Sie schützen die spätere Prüfung vor einer reinen „Fehler genau passend zur Regel“-Simulation.

| Test-ID | Fachlicher Testfall | Erwartete Entscheidung / Fachnachweis |
|---|---|---|
| **AT-01** | Migrationspflichtiger Legacy-Artikel im Ziel mit korrektem Mapping und regelkonformen Feldwerten. | PASS – migriert; keine fälschliche Fehlermeldung. |
| **AT-02** | Altartikel dokumentiert außerhalb des Migrationsumfangs und deshalb im Ziel nicht vorhanden. | VALID_EXCLUSION – kein Migrationsdefekt. |
| **AT-03** | Migrationspflichtiger Altartikel im Ziel nicht auffindbar, Importprotokoll nicht vorhanden. | Abweichung FAIL / Ursache UNCONFIRMED. |
| **AT-04** | Neues Produkt ohne Legacy-ID, fachlich vollständiger Artikelstamm. | Einführungsprüfung; kein Migrationsdefekt. |
| **AT-05** | Im Legacy-Datensatz abweichende Längen-Einheit; korrekt genehmigte Umrechnung zum Ziel. | PASS – regelkonforme Änderung; kein Fehler. |
| **AT-06** | Zielsystem nutzt nachweislich falschen Umrechnungsfaktor. | FAIL; TRANSFORM nur mit Regel-/Laufnachweis bestätigt. |
| **AT-07** | PO, ASN und Wareneingang stimmen in Basismenge **und** zugelassener Packstruktur überein. | PASS – Verarbeitung möglich, sofern auch andere Regeln erfüllt. |
| **AT-08** | Gesamtmenge gleich, Kartonzahl × Inhalt anders als vertraglich erwartete Konfiguration; keine Freigabe verfügbar. | Verpackungskonflikt; REVIEW bzw. BLOCK nach Prozessregel, nicht stillschweigend PASS. |
| **AT-09** | Andere Packstruktur mit gültiger, rechtzeitig dokumentierter Lieferantenfreigabe und passender Ebenenkennung. | Zulässige Änderung; keine fälschliche Sperre. |
| **AT-10** | Teilwareneingang mit noch offener Restmenge, korrekt dokumentiert. | Kein pauschaler Mengenfehler; offener Rest ausgewiesen. |
| **AT-11** | Wareneingang HOLD; Bestand ist im Lager vorhanden, aber für Filialbelieferung gesperrt. | Systembestand getrennt von freiem Bestand; Freigabe BLOCK/REVIEW. |
| **AT-12** | ERP-Artikel korrekt, WMS-Artikel fehlt; Übertragungslog fehlt. | Integrationsverdacht; keine bestätigte Schnittstellenursache. |
| **AT-13** | ERP-Artikel korrekt, WMS-Sende-/Empfangslog zeigt eindeutige fehlgeschlagene Übergabe. | INTERFACE bestätigt; gezielte Korrektur und Re-Test. |
| **AT-14** | Neue SKU erfüllt Pflichtfelder, besitzt aber bewusste, gültige Einführungs-/Sortimentssperre. | VALID_EXCLUSION – keine Fehlklassifikation als Qualitätsfehler. |
| **AT-15** | Werte sehen plausibel aus, externe Referenz ist unbekannt. | Validitäts-/Richtigkeitsaussage nur im Rahmen der bekannten Regeln; ggf. NOT_EVALUABLE statt „korrekt“. |
| **AT-16** | Fehler korrigiert, aber abhängige WMS-/Bestelldaten nicht erneut geprüft. | Fall **nicht** als erfolgreich abgeschlossen markieren. |

**Abnahmekriterien für Phase 3:**

1. Jeder der fünf verlangten Bereiche **Lieferant, Legacy ERP, Ziel-ERP, Bestellung, Lager** ist im Prozessmodell mit führenden Daten und Prüfpunkt erfasst.
2. Die Beziehung zwischen SKU, Verpackungsebene, Version, Bestellung und Wareneingang ist eindeutig beschrieben.
3. Migrationskohorte und Neuartikel sind unterscheidbar.
4. Regeln für Basiseinheit, Packstruktur, Zeitbezug und zulässige Änderungen sind definiert.
5. Messbares Regelergebnis, Prozessentscheidung und Ursachennachweis sind getrennt.
6. Gültige Ausnahmen und ungeklärte Fälle können im Modell ausdrücklich abgebildet werden.
7. Es werden **keine** historischen Target-Einzelartikel, Datenbestände oder Resultate vorgetäuscht.

**Abnahmeurteil:** Das Fachkonzept erfüllt diese sieben **Modellierungsanforderungen auf Spezifikationsebene**. Die spätere Prüfung muss zeigen, dass die technische Implementierung dieselben Kriterien erfüllt.

---

## 7. Rollen, Datenverantwortung und Korrekturfreigabe

| Gegenstand | Fachliche Verantwortung | Technische Unterstützung | Genehmigt die fachliche Änderung |
|---|---|---|---|
| Produkt-/Lieferantenidentität | Einkauf / Stammdaten | ERP-Team | Stammdatenverantwortliche Rolle |
| Lieferanten-Packung / Gültigkeit | Einkauf | Stammdaten / ERP | Einkauf nach Lieferantenbestätigung |
| Migrationsumfang und Mapping | ERP-Projekt + Stammdaten | ERP-Team | Verantwortliche Projekt-/Fachrolle |
| Bestellmenge / akzeptierte Packversion | Einkauf | ERP Application Support | Einkauf |
| Tatsächlicher Wareneingang / HOLD | Lager | WMS Support | Lagerleitung / autorisierte Warenannahme |
| Produkt-/Beschaffungsfreigabe | Produktmanagement / Einkauf | Stammdaten / ERP | Fachlich autorisierte Freigaberolle |
| Filialbelieferungsstatus | Logistik / Vertrieb | WMS / ERP Support | Logistik / Vertrieb |
| Prüfung, Nachweissicherung, Reporting | Business Analyst / Data Quality Analyst | ERP-/WMS-Team | Keine selbständige Freigabe ohne fachlichen Owner |

Ein Analyst kann Unstimmigkeiten belegen und Maßnahmen empfehlen, aber **nicht** ohne Genehmigung Lieferantenverträge, Packdaten oder Warenbestände als neue Wahrheit festlegen.

---

## 8. Prüf- und Auswertungsziele für die folgende Umsetzung

### 8.1 Geplante Arbeitsnachweise (noch nicht umgesetzt)

- Versioniertes Datenwörterbuch mit Artikel-, Lieferanten-, Pack-, Migrations-, Bestell- und Wareneingangsfeldern.
- Getrennte Roh- und Prüfdatenstände; nachvollziehbarer Source-to-Target-Abgleich.
- Fachlich dokumentierte Excel-/Power-Query-Profiling- und Standardisierungsprüfungen.
- SQL-basierte Identitäts-, Gültigkeits-, Verpackungs-, Mengen-, Stichtags- und Quell-/Ziel-Abgleiche.
- Untersuchungsjournal (Issue/Evidence/Owner/Action/Retest) mit bestätigten und ungeklärten Ursachen.
- Reproduzierbare positive und negative Abnahmetests, einschließlich legitimer Ausnahmen.
- Power-BI-Darstellung der Datenqualität, der Vorgangsausnahmen und des Bearbeitungsstatus.
- Management Summary mit belegten Ergebnissen und präventiven Maßnahmen.

### 8.2 Fachliche Kennzahlen, die später tatsächlich berechnet werden können

| Kennzahl | Fachliche Grundgesamtheit / Rechenprinzip | Warnung zur Interpretation |
|---|---|---|
| Migrationsabdeckung | InScope-Quellartikel mit belegter eindeutiger Zielzuordnung / alle InScope-Quellartikel | Sagt nichts über Attributrichtigkeit. |
| Pflichtfeldvollständigkeit | Artikel, die alle **für den betreffenden Freigabeprozess** erforderlichen Felder besitzen / im Kontext prüfpflichtige Artikel | Vollständigkeit ist nicht Accuracy. |
| Verpackungskonfliktquote | Aktive PO-/ASN-/Receipt-Vorgänge mit ungeklärter oder nachgewiesener Packabweichung / vergleichbare Vorgänge mit benötigter Evidenz | Genehmigte alternative Konfiguration separat zählen. |
| Wareneingangs-Ausnahmequote | Wareneingangsposten in HOLD/REVIEW / geprüfte Wareneingangsposten | Keine Aussage über tatsächliche physische Fehler ohne unabhängigen Beleg. |
| Ursachen-Nachweisquote | Untersuchte Fälle mit belegter Ursache / alle untersuchten Fälle | Ein nicht belegbarer Fall darf „ungeklärt“ bleiben. |
| Re-Test-Abschlussquote | Korrigierte Fälle mit bestandener erneuter Prüfung / alle korrigierten Fälle, die erneut geprüft werden müssen | Ohne Test kein „gelöst“. |
| Frei verfügbarer Systembestand | OnHand minus Reserviert minus Gesperrt, je SKU/Lagerort/Zeitstand | Nicht identisch mit Regalverfügbarkeit oder Verkaufsprognose. |

**Definitionen, Gültigkeitszeitpunkte und Grundgesamtheiten** werden bei der späteren Implementierung als maschinenprüfbare Regeln umgesetzt. Es werden keine Verbesserungswerte oder Resultate vorweggenommen.

### 8.3 Werkzeugzuordnung erst nach Fachmodell

- **Excel:** Rohdaten-Einsicht, fachliche Referenz- und Mapping-Reviews, kontrollierte Prüflisten.
- **Power Query:** Reproduzierbarer Import, Typ-/Einheitenstandardisierung, verknüpfbare Prüfstände; Rohdaten bleiben unverändert.
- **SQL:** Beziehungen und Integrität, Source-to-Target-Abgleich, Mengen-/Verpackungsprüfungen, Reconciliation, Evidenzabfragen.
- **Power BI:** Kennzahlen über definierte geprüfte Datenbestände, Untersuchungslage und Prozess-Ausnahmen.

Das Projekt entwickelt **keine** vollständige ERP-, PIM-, WMS- oder Schnittstellen-Software.

---

## 9. Übergabe in die Datenerstellung – festgehaltene Grenzen

**Freigegeben als fachliche Grundlage für die nächste Phase:**

- Produktart: **verpackte Hygiene- und Drogerieprodukte**.
- Referenzproblem: historische, dokumentierte Daten-/Warenflussprobleme von Target Canada **nur als Kontext**.
- Fiktive Situation: Migration von Legacy ERP zu Ziel-ERP, parallel Einführung neuer Artikel.
- Operativer Prüfpfad: Lieferant → Ziel-ERP → Bestellung → ASN → WMS-Wareneingang → Bestand/Freigabe.
- Pilotverpackung: Basiseinheit `EA`, Standard-Case; weitere Ebenen nur falls fachlich erforderlich.
- Fachliche Artefakte: Produkt-/Lieferantenidentität, Versions- und Verpackungshierarchie, Migration, Bestellung, ASN, Eingang, Bestand, Freigabe, Issue/Evidence.
- Regelwerk: **BR-01 bis BR-26**, jeweils mit Statuslogik; Abnahmeszenarien **AT-01 bis AT-16**.
- Festgelegte Erkenntnisgrenze: Simulierte Wirksamkeit kann später nachgewiesen werden; historische Target-Daten oder reale Betriebsverbesserungen nicht.

**Vor Datenerstellung tatsächlich umzusetzen:** Das fachliche Schema in konkrete Exportspalten übersetzen, Feldabhängigkeiten validieren, Rohdaten-/Wahrheits-/Fehler-Testbasis getrennt designen, die Abnahmeszenarien implementierungsunabhängig fixieren und Versionen verwalten. Die Anzahl der Zeilen, konkrete IDs, Datenwerte und Fehlerquoten sind **noch offen** und werden aus dem notwendigen Testumfang abgeleitet, nicht aus willkürlichen Mindestzahlen.

### Qualitätskontrolle gegen frühere Lücken

- Die frühere Fliesen-/Profilfestlegung ist **nicht mehr gültig**.
- Ein historisch betroffener Zahnbürstenartikel wird **nicht** behauptet.
- Gleiche Stückzahl ≠ automatisch gleiche Case-Konfiguration.
- Änderung einer Case-Menge kann ein neuer zulässiger Packstand mit angepasster Ebenen-GTIN sein – nicht automatisch fehlerhafte Lieferung.
- Filialregalbestand und realisierte Umsätze sind ohne Beobachtungsdaten **nicht messbar**.
- Eine unterbliebene ERP-Übernahme und eine bestätigte Migrationsursache sind verschiedene Aussagen.
- Der Projektstand ist **Fachkonzept erstellt**; noch **keine** Tests durchgeführt und **keine** Resultate erzielt.

---

## 10. Fachliche Referenzen und Evidenzgrenzen

**Historischer Referenzfall:**  
Maclean’s / Canadian Business, *What really happened at Target Canada: The retailer’s last days* (22.01.2016).  
https://macleans.ca/economy/business/what-really-happened-at-target-canada-the-retailers-last-days/

**GS1 – Trade Item Hierarchy / Packaging:**  
GS1 Global Data Model Attribute Implementation Guide; Verpackungsebenen wie `Each`, `Case`, ggf. `Pallet` mit voneinander unterscheidbaren Handelsartikel-Identifikatoren.  
https://www.gs1.org/standards/gs1-global-data-model-attribute-implementation-guide/18

**GS1 – Pack/Case Quantity:**  
Der GS1 GTIN Management Standard sieht für veränderte Mengen auf einer bestehenden höheren Verpackungsebene eine neue GTIN für die betroffene Ebene vor.  
https://www.gs1.org/1/gtinrules/en/rule/270/packcase-quantity

**GS1 – Logistische Einheit:**  
Eine einzelne logistische Einheit kann mit SSCC identifiziert werden; die SSCC ist keine GTIN eines Produkttyps.  
https://support.gs1.org/support/solutions/articles/43000734289-what-is-a-logistics-unit-and-how-is-it-identified-

**SAP Help – Units of Measure:**  
SAP unterscheidet Basis-, Bestell- und Verkaufseinheiten und verwendet definierte Umrechnungsfaktoren für alternative Einheiten. Diese offizielle Dokumentation erklärt ein allgemeines ERP-Prinzip, nicht die historische Konfiguration von Target Canada.  
https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/91b21005dded4984bcccf4a69ae1300c/a07cbd534f22b44ce10000000a174cb4.html
