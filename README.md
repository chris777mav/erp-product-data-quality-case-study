# Untersuchung von Produktdatenfehlern und Verfügbarkeitsproblemen im Rahmen einer ERP-Migration und Produkteinführung

**Portfolio-Fallstudie · finaler integrierter Projektstand · 3. November 2026**

**[Vollständige Fallstudie lesen (einzige PDF-Datei)](Portfolio_Projekt1_GESAMT_FALLSTUDIE_FINAL.pdf)**

## Ergebnis und Untersuchungslogik

Das Projekt befasst sich mit **synthetischen** Daten eines fiktiven Hygiene-/Drogerie-Handelsunternehmens. Recherchierte reale Fälle von Target Canada, DEVENTRADE und einem anonymisierten HTC-Kunden begründen den Untersuchungsansatz. Es werden ausdrücklich keine echten Produktdaten oder Geschäftsvorfälle dieser Unternehmen verwendet.

Die Untersuchung bildet eine zusammenhängende Kette: **Problemherleitung → 20-Artikel-Tiefenpilot → einheitliches Risikomodell und Validierung → unveränderte Modellanwendung auf 500 Artikel → kontrollierte Simulationskorrekturen → Empfehlungen für die Qualitätssteuerung**.

Die wichtigsten überprüfbaren Ergebnisse:

| Umfang | Befund |
|---|---|
| Pilot | 20 Artikel und 11 Incidents in individuellen Fallakten; Risiko-Prioritäten P1=6, P2=4, P3=1, P4=9. |
| Validierung | 16 vordefinierte Szenarien mit 16 bestandenen Datenprüfungen, davon 3 nur teilweise fachlich nachgewiesen; 7/7 isolierte Negativproben; 21 Prüfinvarianten. |
| Risikomodell | `RISK-PILOT-1.1`: 15 gewichtete Signale; Evidenzstatus vom Risikoscore und von der Prozessfreigabe getrennt. |
| Skalierung | 500 Artikel und 32 historische OPEN-Incidents, mit identisch angewendeten Regeln; P1=83, P2=29, P3=1, P4=387; Pilot-Regressionsprüfung 20/20. |
| Kreuzprüfung | 11 SKUs mit DQ01-negativem Migrationsnachweis bei registriertem ALLOW; 104 SKUs mit einem breiter definierten gewichteten Warnsignal bei ALLOW. Die Kriterien sind verschieden. |
| Fallabdeckung | 32 Incidents eindeutig auf SKU referenziert (28 direkt, 4 über PO/ASN/Receipt). 97 SKUs mit definiertem Prüfbedarf ohne eindeutig verbundenen Incident. |
| Sandbox | Vier unterschiedliche V2-Testkorrekturen plus eine Negativkontrolle, Originaldaten unverändert; V2 DQ02 PASS 298→301, auswertbar 310→311. |
| Pilotretest | HYG-1006 von 200,0 auf 203,2 mm; DQ02 von 12/13→13/13 in separatem Testzweig mit synthetischem WMS-Test. Historisches V1-INC-002 bleibt OPEN. |

**Wichtig:** Die priorisierten Kategorien der älteren Action-Center-Oberfläche (P0–P3) sind eine eigene operative UI-Queue und **nicht** identisch mit den fachlichen P1–P4-Stufen des Risikomodells. Die neue fachliche Priorisierung ist im Risikoregister dokumentiert; die alte UI wird nicht als entsprechend aktualisiert dargestellt.

## Projektstruktur (ein zusammenhängendes Projekt)

- **`Portfolio_Projekt1_GESAMT_FALLSTUDIE_FINAL.pdf`** – einzige PDF: Quellen, Problemherleitung, Pilot, Risiko- und Fallanalyse, Skalierung, Gegenproben, Maßnahmen, Audit und Anhang.
- `research/` – Recherchepfad, Auswahl und Kritik der realen Referenzfälle, keine erfundene historische Suchchronologie.
- `risk/pilot/` – ursprüngliche 20-SKU-Triage und bewertete 11 Cases.
- `risk/methodenvalidierung/` – fixierter Methodenvertrag, 11 tiefe Fallakten, 16 Akzeptanzfälle, sieben Mutationsproben, Python-Prüfprogramm.
- `risk/skalierung/` – 500-SKU-Risikoregister, 32 Fallakten, Nachweisregister, Testkopie und Ergebnisse der Gegenproben.
- `input/`, `results/` – eingefrorene synthetische SQLite-Quellen, Auswertungsdateien und Retest-Stände.
- `sql/` – die sieben DQ-Kontrollen, ergänzende positionsgenaue Reportingabfragen.
- `src/` – Datengenerierung, Analyse, Exporte, SQL-Retests und übergreifende Prüfung.
- `tests/` – automatische Integritäts-, Quellen- und Risikoprüfungen.
- `powerbi/V2_Desktop_Bestaetigt/` – die in Power BI Desktop getesteten drei Berichtsseiten.
- `powerbi/Phase6_DataQuality_CommandCenter_OFFLINE.html` – lokal interaktives, in Chromium getestetes Action Center (ohne Writeback ins ERP/WMS).
- `evidence/` – belegte Screenshots der tatsächlich geöffneten Oberflächen.
- `RELEASE_ABNAHME.json`, `SHA256_MANIFEST.json` – technische Prüfergebnisse und Prüfsummen.

## Selbst prüfen / erneut ausführen

**Voraussetzung:** Python 3.10 oder neuer. Die automatisierten Kern- und Risikoprüfungen verwenden nur die Python-Standardbibliothek.

```bash
python src/run_all.py
```

Gezielte Wiederholung der Pilot-Validierung und der Skalierung in diesem Projektordner:

```bash
python risk/methodenvalidierung/fallbearbeitung_validieren.py
python risk/skalierung/auswertung_und_retests_v2.py
```

Beide Programme lesen die ursprünglichen Quellen und dokumentieren künstliche Änderungen ausschließlich in abgeleiteten Simulationsdateien. **Die V2-Skalierung setzt voraus, dass die historisch erzeugten Risikoregister beibehalten werden, um den Versionsvertrag zu prüfen.** Die Original-Quell-SQLite bleibt unverändert. Die reproduzierbaren SQL-Kontrollen finden sich unter `sql/`.

## Nachweisgrenzen

- Die Risikogewichte sind **qualitativ definiert**; keine empirische Wahrscheinlichkeit, keine Euro-Schadenssumme, keine Produktionsleistung.
- Die 7 SQL-Kontrollen automatisieren **nicht** alle 26 fachlichen Designregeln. AT-10, AT-11, AT-13 sind nur teilweise fachlich belegt.
- Historische 11 Pilot- und 32 V2-Cases bleiben OPEN. Sandbox-Korrekturen bedeuten keinen operativen Incident-Abschluss und keine tatsächliche Warenlieferung.
- Ein Datenfehler- und ALLOW-Kreuzsignal über unterschiedliche Snapshot-Daten beweist noch keinen zeitgleichen Richtlinienverstoß.
- Der **V2 Power-BI-Bericht** (3 Seiten) wurde durch den Nutzer in Power BI Desktop sichtbar erfolgreich aktualisiert; die neuere V3-Vorlage ist kein nativ bestätigter Bestandteil dieses Release.
- Die lokale Git-Struktur ist vorbereitet; ein öffentliches Portfolio-Repository wurde **nicht** nachgewiesen. Der angegebene GitHub-Link im Profil ist nur ein Profil-Link.
- Die Fallstudie und technische Teile wurden mit KI-gestützter Recherche-, Generierungs- und Redaktionshilfe erstellt. Die Nachweise sind überprüfbar; eine reale oder selbstständig durchgeführte Berufsausübung wird dadurch nicht behauptet.

**Weder produktive ERP/WMS-Nutzungsnachweise noch eine bestätigte finanzielle oder betriebliche Verbesserung werden behauptet.**
