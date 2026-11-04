# Risikoorientierte Skalierung auf 500 synthetische Artikel – Ausführung 3/4

## 1. Methodische Grundlage

Die am 20-Artikel-Pilot definierte und in Ausführung 2 geprüfte Version **RISK-PILOT-1.1** wurde unverändert angewendet. Keine Risiko-Gewichte, Schwellen oder P1–P4-Regeln wurden nach Sichtung der 500er-Ergebnisse geändert. Die Adapteränderungen betreffen allein Kohortengröße, Dateinamen und die Zuordnung der weiteren registrierten Incident-IDs. **P1 bedeutet einen Prüfvorrang, nicht automatisch einen nachgewiesenen Verstoß.**

Datenquelle: 500 Artikel, 21 Relationen, 330 migrationspflichtige Zuordnungen, 191 ASN-Positionen und 32 registrierte offene Incidents. Unveränderter V2-Hash: `e212a6f317a593055aa62897d63697d613feba012427bb934157044241bc77be`.

**Regressionsprüfung:** Alle 20 ursprünglichen Pilotartikel behalten in V2 exakt dieselbe Priorität und dieselben registrierten Risikosignale wie V1 (20/20).

## 2. 500 Artikel vollständig mit Pilotmethode bewertet

| Stufe | Artikel | Fachliche Bedeutung |
|---|---:|---|
| P1 | 83 | Sofortige fachliche Prüfung |
| P2 | 29 | Zeitnah prüfen / klären |
| P3 | 1 | Geplant verifizieren / dokumentieren |
| P4 | 387 | Kontrolliert / kein aktuelles Signal |

**104** Artikel erfüllen die unveränderte Risiko-Bedingung 'ALLOW plus negatives gewichtetes Fachsignal' (dies ist *nicht* gleichbedeutend mit 104 falschen Freigabeentscheidungen). Die genau definierte DQ01/ALLOW-Kreuzkontrolle ergibt **11** unterschiedliche SKUs. Die unterschiedlichen Zahlen beziehen sich auf unterschiedliche Prüfkriterien.

Zusätzlich erhalten **28** SKUs ein ausdrückliches Warnkennzeichen für vom Pilotmodell *nicht gesondert gewichtete* Nicht-Auswertbarkeit, fehlende Logereignisse oder unvollständige/doppelte Freigaberegister. Sie wurden nicht stillschweigend als fehlerfrei eingestuft. Diese Liste ist als zusätzlicher Prüfbedarf ausgewiesen, nicht nachträglich zu P1 gerechnet.

## 3. Incident-Zuordnung und Entscheidungen

Alle 32 historischen offenen Fälle wurden anhand der passenden fachlichen Referenz auf eine eindeutige SKU zurückgeführt: **28 direkte SKUs** und **4 PO-/Receipt-/ASN-Verknüpfungen**. Damit werden Fremdschlüssel und Beleg-Grains korrekt beachtet.
**97** SKUs mit einem gewichteten oder zusätzlichen Prüfbedarf haben im vorhandenen Register keinen eindeutig zugeordneten Fall. Die Zahl ist gegenüber früheren Berichten abweichend, weil jetzt PO/Receipt-Referenzen explizit aufgelöst werden und zusätzliche Prüfflaggen berücksichtigt werden; sie ist keine neu entstandene operative Fehlerrate.
Jeder Fall ist in `V2_32_Incidents_Einzelfallbericht.md` und im zugehörigen JSON mit Kontrollbefund, dokumentierter Evidenz, Ursache/Nichtwissen, vorgeschlagenem Verantwortungsbereich, nächster Handlung und Abschlussbedingung beschrieben. **Keine Case-Schließung wurde erfunden.**

## 4. Konkrete kontrollierte Korrekturversuche in isolierter Sandbox

| Probe | SKU | Mutierter Testdatensatz | Nachweis und Grenze |
|---|---|---|---|
| SIM-A | HYG-2058 | S2-Länge 151,76 → 154,96 mm | DQ02 MISMATCH → PASS; Folgesystem-/Genehmigungsnachweis weiterhin notwendig. |
| SIM-B | HYG-2097 | S2-Zielidentität ERP-12097-BAD → ERP-12097 | DQ01 IDENTITY_MISMATCH → PASS; historische Mappingfreigabe nicht automatisch saniert. |
| SIM-C | HYG-2114 | rein synthetischer POSTED-Receipt-Beleg | DQ05 MISSING_RECEIPT → RECONCILED_POSTED; **kein Nachweis physischer Lieferung**. |
| SIM-D | HYG-2111 | ASN-Packversion UNKNOWN → erwartete A | DQ04 BLOCK → PASS; genehmigte tatsächliche Lieferung und WMS bleiben gesondert. |
| SIM-E | HYG-1006 | S2-Länge 200 → 203,2 mm | **Negativkontrolle:** DQ02 wird PASS, unzulässiges historisches DQ03-Regelereignis bleibt nachweisbar. |

| KPI / Kontrollzählung | Unveränderte V2-Quelle | Separate Simulation |
|---|---:|---:|
| DQ01_PASS | 319 | 320 |
| DQ02_PASS | 298 | 301 |
| DQ02_EVALUABLE | 310 | 311 |
| DQ04_PASS | 176 | 177 |
| DQ05_RECONCILED_POSTED | 135 | 136 |
| DQ03_UNAPPROVED_RULE | 11 | 11 |
| DQ07_OPEN | 32 | 32 |
| DQ06_ALL_ALLOW | 471 | 471 |

Der DQ02-PASS-Anstieg um drei besteht aus zwei Dimensionswertkorrekturen und einer durch die korrigierte Zielidentität wieder **auswertbar** gewordenen Position (Nenner 310 → 311); es wurden nicht drei Dimensionsfehler korrigiert.
Diese Vorher-/Nachher-Werte sind **reine Gegenproben in einer manipulierten Kopie**. Der historische Pilot- und V2-Quellbestand, alle vorhandenen Freigaben und alle 32 Incident-Statusfelder sind unverändert. Insbesondere handelt es sich **nicht um eine gemessene Verbesserung in einem Unternehmen**.

## 5. Abnahme- und Geltungsgrenzen

- Die 500 Artikel, alle 32 Incidents, 191 ASN-Positionen und 7 SQL-Kontrollen wurden aus der Original-SQLite-Quelle neu gelesen. Korrekter Grain sowie eindeutige Incidents-Koordinaten wurden geprüft.
- Sämtliche nicht betroffenen SKUs liefern nach den Sandbox-Mutationen exakt dieselben DQ-Abfragezeilen wie vorher. S1-Historie, DQ03-Logs und DQ06-Freigaben bleiben unangetastet.
- Zielwertreparatur ist weder Mappinghistorienreparatur noch Incident-Abschluss; dokumentierte HOLDs können zulässige Schutzmaßnahmen sein.
- Die Methode erkennt die Notwendigkeit zusätzlicher Kontrollen, beweist aber keine Vollabdeckung der ursprünglich 26 Fachregeln.

## 6. Übergabe an Ausführung 4/4

Die Abschlussintegration muss die Forschungsherleitung, den 20-SKU-Tiefenpilot, das fest definierte Risikomodell, seine Übertragung auf 500 Artikel und die **klar als künstlich gekennzeichnete** Maßnahmen-/Retest-Strecke in **eine** professionelle Bewerbungsfallstudie zusammenführen. Status- und Zahlenangaben müssen gegen die vorliegenden Quelldateien kontrolliert werden; ohne Desktop-Nachweis darf eine neu veränderte Power-BI-Version nicht als nativ abgenommen bezeichnet werden.
