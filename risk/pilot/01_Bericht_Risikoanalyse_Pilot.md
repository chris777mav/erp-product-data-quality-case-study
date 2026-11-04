# Vertiefung der Portfolio-Fallstudie – Ausführung 1 von 4
## Risikoorientierter Pilot: Datenausgangslage, Bewertungsmodell und vollständige Ersttriage der 20 Artikel

**Fallstudie:** Untersuchung von Produktdatenfehlern und Verfügbarkeitsproblemen im Rahmen einer ERP-Migration und Produkteinführung  
**Datenbasis:** unveränderte, vollständig synthetische V1-SQLite-Datenbank mit 20 Artikeln. Alle genannten ERP-, Lieferanten-, WMS- und Incident-Daten in diesem Bericht sind simuliert.  
**Stand:** 03.11.2026  
**Bearbeitungsstand:** Ersttriage und Bewertungsrahmen abgeschlossen; vertiefte Einzelfallermittlung, Maßnahmenentscheidung und Validierung folgen in Ausführung 2.

---

## 1. Fragestellung und Position in der Gesamtuntersuchung

Im bisherigen Portfolio wurden bereits sieben SQL-Kontrollen entwickelt, Datenquellen aus einem vereinfachten ERP-/WMS-Prozess abgeglichen und einzelne Fehler detailliert untersucht. Was noch fehlte, war ein einheitliches, nachvollziehbares Verfahren zur **Priorisierung sämtlicher im Pilot erkannter Auffälligkeiten**. Die neue Untersuchung beantwortet zunächst:

- Welche der 20 SKUs zeigen ein fachlich relevantes Kontrollsignal, und welche nicht?
- Sind Abweichungen, zulässige Ausnahmen, mangelnde Nachweise und dokumentierte Prozessentscheidungen sauber voneinander getrennt?
- Welche **elf** bereits registrierten Incidents lassen sich welchen Produkten zuordnen, auch wenn der Incident eine PO oder Receipt als Referenz trägt?
- Wo besteht zusätzlicher Prüfbedarf, weil ein negatives fachliches Signal auf ein dokumentiertes `ALL_PROCESSES_ALLOW` trifft?
- Welche Priorisierung ist anhand der vorhandenen Daten vertretbar, **ohne tatsächliche Umsatzverluste, Wahrscheinlichkeiten oder technische Ursachen zu erfinden**?

### Warum zuerst die 20 und erst danach die 500?

Die 20 Artikel sind die methodische *Entwicklungs- und Vertiefungsstufe*. Wir müssen zunächst wissen, ob die Klassifikation, Referenzzuordnung und Priorisierung am transparenten Pilot fachlich sinnvoll sind und die beabsichtigten Sollfälle bestehen. Erst dann darf dieselbe **vorab eingefrorene Methode** als zweite Stufe auf 500 Artikel übertragen werden. Ein größerer Datensatz allein beweist keine bessere Untersuchung.

## 2. Datenprovenienz und Vergleichsgrenzen

| Merkmal | Aus der historischen V1-Datenbank geprüft |
|---|---:|
| SKUs in `products` | 20 |
| `origin_type=MIGRATED` | 15 |
| `origin_type=NEW` | 5 |
| Für Migration `in_scope=YES` | 14 |
| Dokumentierter Ausschluss vor Cutover | 1 |
| DQ-01 `PASS` | 13 von 14 |
| DQ-02 `PASS` | 12 von 13 bewertbaren Fällen |
| DQ-06 `ALL_PROCESSES_ALLOW` | 17 von 20 |
| Registrierte V1-Incidents | 11, historisch sämtlich `OPEN` |

**Grain:** Die Produkt-Risikomatrix hat exakt eine Zeile je `products.sku`. DQ-04 und DQ-05 liegen dagegen auf der Ebene der ASN-Position, DQ-07 auf Incident-Ebene. Vor der Übertragung auf das Produkt werden diese Signale **ohne unkontrollierte Mehrfachzählung** gruppiert. Bei zwei ASNs zu demselben Artikel (HYG-1011) darf weder der Artikel noch der Incident durch einen JOIN verdoppelt werden.

**Snapshot-Semantik:** DQ-01/DQ-02 beziehen sich auf den Ziel-ERP-Snapshot `S2-2026-09-15`; die registrierten Freigaben auf `2026-09-18T18:00:00`. Ihre Gegenüberstellung liefert einen **Prüfhinweis**, nicht automatisch einen zeitgleich wirksamen Regelverstoß. Historische und spätere simulierte Datenzustände werden nicht gleichgesetzt.

**Sonderfall INC-002:** Die historische V1-Quelle hält `OPEN`, `applied_at=NULL` und `PENDING_WMS_RECHECK` fest. Der später erstellte, separat versionierte Simulationszweig dokumentiert eine erfolgreiche Korrektur und einen künstlichen WMS-Test. Der spätere Simulationsabschluss wird hier **nicht rückwirkend** in die ursprünglichen 20 Datensätze geschrieben.

## 3. Definiertes Modell der risikoorientierten Ersttriage

Eine Risikobewertung verlangt normalerweise **Schadenausmaß und Eintrittswahrscheinlichkeit**. Letztere ist hier nicht belastbar schätzbar: Es fehlen reale Versandvolumina, Kundenaufträge, Kosten, Häufigkeiten und Prozessauswirkungen. Deshalb verwendet dieses Pilotprojekt **keinen fiktiven Euro-Schaden und keinen erfundenen Wahrscheinlichkeitswert**. Stattdessen wird ein reproduzierbarer, ausdrücklich **qualitativer Priorisierungsindex** verwendet.

### 3.1 Potenzielle Tragweite des Signals (Skala 1–5)

| Stufe | Interpretationsregel für dieses Simulationsmodell | Beispiel |
|---|---|---|
| 5 | Migrationspflichtige Zielidentität fehlt oder ist widersprüchlich: mögliche Sperre wesentlicher Folgeprozesse | DQ-01 `MISSING_TARGET` |
| 4 | Kontrollabweichung mit potenzieller Auswirkung auf Mengen-/Maßverarbeitung, Wareneingang oder Systemintegration | Falsche Länge; unbekannte Packversion; WMS-Eintrag fehlt |
| 3 | Beleg-/Konsistenzkonflikt, der eine fachliche Prüfung benötigt; reale Folge unklar | Genehmigte Änderung nach Bestellung; fehlender Receipt-Nachweis |
| 2 | Offener administrativer Fall ohne andere dokumentierte Qualitätsabweichung | Nur Incident-Status `OPEN` |
| 1 | Vorliegende dokumentierte, im Konzept zulässige Prozessentscheidung | Geplanter Launch-HOLD; dokumentierte Auslistung |

Die Zahlen sind **Bewertungsannahmen für das Portfolio**, keine direkt aus der Datenbank gemessenen Schadenswerte. Mehrere Hinweise auf *denselben* Defekt werden nicht addiert: DQ-02-Fehler und DQ-03-Mappingverstoß bei HYG-1006 sind zwei Evidenzperspektiven auf einen möglichen gemeinsamen Fehlerkomplex und dürfen keinen künstlich aufgeblähten Score erzeugen. Für die Ersttriage gilt daher die **höchste angenommene Tragweite**, nicht deren Summe.

### 3.2 Priorität und Entscheidungskriterien

| Priorität | Auslöser in der Ersttriage | Richtige Interpretation |
|---|---|---|
| **P1 – sofort prüfen** | Schweres Signal (Stufe 4/5) **und** `ALL_PROCESSES_ALLOW`, `RECEIPT_ON_HOLD` oder WMS-Zieleintragslücke | Prüfung der operativen Entscheidung und Beweiskette; **keine automatische Sperranweisung** |
| **P2 – zeitnah klären** | Relevantes Signal Stufe 3, oder schweres Signal ohne P1-Kontext | Evidenz anfordern, Sollzustand prüfen, fachlichen Owner bestimmen |
| **P3 – dokumentiert beobachten** | Geplanter HOLD bzw. dokumentierter Ausnahmefall mit offenem Incident | Keine Fehlerrate durch legitim gesperrte Artikel aufblähen |
| **P4 – reguläre Kontrolle** | Kein registriertes Signal oder dokumentierte Auslistung ohne offene fachliche Abweichung | `P4` ist **kein Beweis globaler Fehlerfreiheit** |

**Evidenzsicherheit ist eine andere Achse:** `MISSING`, `UNCONFIRMED` und `AVAILABLE` beziehen sich auf Belegverfügbarkeit, nicht auf Eintrittswahrscheinlichkeit oder tatsächlichen Geschäftsschaden. Auch ein fehlender Protokolleintrag beweist nicht, dass ein Ereignis nie stattgefunden hat. Ein `ALLOW` dokumentiert eine Registrierung der drei Prozessentscheidungen, keine generelle Produkt- oder Lieferfreigabe.

**Kontrollkonflikt:** Wenn ein Artikel `ALL_PROCESSES_ALLOW` hat und gleichzeitig DQ-01 bis DQ-05 oder ein dokumentiertes offenes Integrationssignal eine fachliche Auffälligkeit zeigen, wird `Freigabe-Prüfbedarf=JA` gesetzt. Das ist eine Kandidatenliste zur Policy-Prüfung; **nicht bereits der Beweis einer Verletzung einer vorhandenen Freigaberichtlinie**. Zuerst ist festzustellen, ob die fragliche Kontrolle für diesen Freigabezeitpunkt und Prozess überhaupt verpflichtend war.

## 4. Ergebnis: alle 20 Artikel erstklassifiziert

Die reproduzierte SQL-Auswertung erzeugt die vollständige CSV `Pilot_20_Artikel_Risikomatrix.csv` (eine Zeile je SKU). Auf dieser Baseline ergeben sich:

| Priorität | Artikel | Bedeutung |
|---|---:|---|
| P1 | 6 | Zeitnahe, vorrangige fachliche Untersuchung nötig |
| P2 | 4 | Nachweis- oder Bewertungsbedarf |
| P3 | 1 | Dokumentierter geplanter HOLD, Incident noch offen |
| P4 | 9 | Aktuell kein priorisiertes Signal oder zulässige Auslistung |
| **Gesamt** | **20** | Alle Produktidentitäten erfasst |

Bei **neun** SKUs trifft ein registriertes `ALL_PROCESSES_ALLOW` auf mindestens ein fachliches Signal der Ersttriage. Diese Zahl ist **nicht** mit den elf Auffälligkeiten der späteren 500-Artikel-Kreuzkontrolle zu verwechseln: Die Untersuchungsregeln und Signalmengen sind hier breiter; die Kohorte und die Zeitstände unterscheiden sich. Ein Policy-Verstoß ist dadurch noch nicht bestätigt.

### 4.1 Die priorisierten Artikel im Pilot

| SKU | Klasse | Aus vorhandenen Daten beobachteter Kernbefund | Fachliche Folgerung |
|---|---|---|---|
| HYG-1004 | P1 | `MISSING_TARGET`, kein passendes Migrationsereignis im Abzug; drei ALLOW-Einträge | Umfang, Identität, Event- und Ziel-ERP-Daten korrelieren; Ursache offen |
| HYG-1006 | P1 | Länge 200 statt 203,2 mm, nicht genehmigte alte Mapping-Version; ALLOW | Genehmigung / Transformationszeit rekonstruieren; separaten Retest-Zweig referenzieren |
| HYG-1007 | P1 | Unbekannte Packversion; ASN 4×250 = 1.000; Receipt `HOLD`, gleichzeitig ALLOW | Menge allein reicht nicht: Packfreigabe und operative Folgeverarbeitung prüfen |
| HYG-1008 | P2 | Genehmigte Packversionsänderung, aber DQ-04 `REVIEW` wegen Bestellzeitpunkt; ALLOW | Berechtigte Ausnahme mit Approval-Timeline abgleichen |
| HYG-1009 | P1 | Kein WMS-Snapshot-Eintrag und kein Interface-Ereignis im Auszug; ALLOW | Nachweislücke; technischen Ablauf nicht erfinden |
| HYG-1010 | P1 | Kein WMS-Snapshot-Eintrag, aber `INT-1010` mit `FAILED` / `NO_WMS_ACK`; ALLOW | Ereignis vorhanden: anderer Ermittlungsweg als HYG-1009 |
| HYG-1011 | P2 | Zwei ASN-Positionen; eine Receipt-Zuordnung fehlt im Datenabzug; ALLOW | Nachweis je ASN-Position, nicht pauschal pro Artikel |
| HYG-1012 | P1 | Receipt `HOLD`, Bestand 60 Stück vollständig als `blocked` ausgewiesen; ALLOW | HOLD-Grund und Prozessfreigaben abgleichen; keine Lieferverlustbehauptung |
| HYG-1013 | P2 | Lieferantenreferenz `UNCONFIRMED`, bestätigte Pack-/Maßreferenz fehlt; ALLOW | Verantwortliche Stelle um Bestätigung bitten |
| HYG-1016 | P3 | `PLANNED_LAUNCH_HOLD`, Einkauf `BLOCK` statt ALLOW | Zulässige Einführungssperre; offenem Incident administrative Entscheidung zuordnen |
| HYG-1017 | P2 | Prozess-`REVIEW`, unbestätigte Lieferantenreferenz | Vor Launch fachliche Evidenz vervollständigen |

**Die übrigen neun Artikel** stehen mit ihrer genauen Herkunft, Freigabeklasse und den leeren bzw. zulässigen Signalen ebenfalls in der vollständigen CSV. Sie dürfen nicht pauschal als vollständig produktionsreif bezeichnet werden, weil die sieben DQ-Regeln keinen Volltest sämtlicher Geschäftsregeln darstellen.

## 5. Alle elf Incidents: Traceability ist hergestellt, Fälle sind noch nicht künstlich geschlossen

Die Incident-Register wurden nicht bloß nach SKU-Text durchsucht: Incidents mit `PO-...` werden über `purchase_orders` und solche mit `REC-...` über `receipts` zu den Produkten geführt. Somit wird der Grain korrekt transformiert und jeder der elf registrierten Fälle einer Pilot-SKU zugeordnet. Die zugehörigen Evidence-Status werden separat ausgewiesen. Vollständige Einzelsachverhalte stehen in `Pilot_11_Incidents_Triage.csv`.

| Fall | SKU | Beweis- und Entscheidungsgrenze | Bearbeitung in Stufe 2 |
|---|---|---|---|
| INC-001 | HYG-1004 | Migration gefordert, Ziel fehlt; kein Logeintrag beweist keine konkrete Root Cause | Migrations- und Identitätskette vertiefen |
| INC-002 | HYG-1006 | Falsche Dimension/Regelversion belegt; historisch offen, Sandbox-Abschluss separat | Baseline und Retest-Zweig sauber versionieren |
| INC-003 | HYG-1007 | Unbekannte Packversion, fehlende Änderungsfreigabe, Receipt auf HOLD | Lieferanten-/Packversion und WMS-Status korrelieren |
| INC-004 | HYG-1008 | Änderung genehmigt, aber DQ-04 fordert wegen Bestellzeitpunkt REVIEW | Freigabezeitpunkte und Policy definieren |
| INC-005 | HYG-1011 | Receipt-Nachweis für eine ASN-Position fehlt | Teil-/Fehlbeleg prüfen, keine physische Fehlmenge behaupten |
| INC-006 | HYG-1012 | WMS-HOLD und geblockter Bestand dokumentiert | Bedingung für Entblockung und Nachweisbedarf festlegen |
| INC-007 | HYG-1009 | WMS-Ziel fehlt, Schnittstellennachweis fehlt | Sendestatus/Logs anfordern |
| INC-008 | HYG-1010 | WMS-Ziel fehlt, aber FAILED-Ereignis vorhanden | NO_WMS_ACK-Kette getrennt untersuchen |
| INC-009 | HYG-1013 | Supplier-Evidenz unbestätigt | Lieferantenbestätigung und Maßfreigabe prüfen |
| INC-010 | HYG-1016 | Geplanter Launch-HOLD, keine nachgewiesene DQ-Störung | Ausnahme bestätigen und Case-Status entscheiden |
| INC-011 | HYG-1017 | Supplier-Evidenz unbestätigt; Prozess-REVIEW dokumentiert | Launch-Freigabekriterien prüfen |

**Wichtige Trennung:** In dieser ersten Ausführung wurde für alle elf Fälle die Triage erstellt, aber **keine zusätzliche Korrektur behauptet und kein historischer Incident geschlossen**. Ermittlung, Ursachenbelege, Freigabe-/Abschlusskriterien und ausgewählte nachprüfbare Korrekturen folgen in Ausführung 2.

## 6. Übertragungsbedingung für den 500-Artikel-Test

Bevor die Methode auf die 500 SKU ausgerollt wird, müssen im Pilot folgende Punkte überprüft sein:

1. **Referenztreue:** Alle 20 SKUs genau einmal und alle elf Cases mit eindeutiger Zuordnung vorhanden; komplexe PO-/Receipt-Verknüpfungen kontrolliert.
2. **Fachliche Sollfälle:** Fehlende Migration, falsche Transformation, genehmigte Verpackungsänderung, tatsächlicher Packkonflikt, WMS-Protokolllücke und geplanter Launch-HOLD unterscheidbar.
3. **Evidenzdisziplin:** `AVAILABLE`, `MISSING`, `UNCONFIRMED` getrennt; keine Vermischung von Prüfsignal und Ursache.
4. **Entscheidungsregel:** Was zu einer technischen/operativen Sperre führt, braucht eine vorher erklärte Fachrichtlinie; `ALLOW + Signal` allein ist nur ein Prüfhinweis.
5. **Korrekturkontrolle:** Vorher, genehmigte Änderung, nachher, abhängige Prozesse, Gegenprobe, Endentscheidung und offene Restrisiken werden getrennt dokumentiert.
6. **Fixierte Regeln:** Bewertungsmaßstäbe werden nach der Pilot-Validierung mit Versionsnummer eingefroren. Änderungen während der 500er-Untersuchung müssen protokolliert und separat ausgewertet werden.

**Ziel des Transfers:** In der 500er-Kohorte werden **alle 500 SKUs automatisiert untersucht**, alle erkannten Signale und Case-Zuordnungen bewertet und priorisierte Fälle mit denselben Regeln in einer begrenzten, aber nachvollziehbaren Tiefenanalyse untersucht. „500 Einzelgutachten“ sind **nicht** Ziel; eine flächendeckende Prüfung und ein belastbarer Bearbeitungsprozess dagegen schon.

## 7. Nachweise und technische Grenzen

- `risikoanalyse_pilot.py`: Read-only-SQLite-Leser; führt die **unveränderten Originalabfragen DQ-01 bis DQ-07** auf V1 aus. Berechnet Produkt- und Incident-Triage nach der hier beschriebenen Methodik.
- `Pilot_20_Artikel_Risikomatrix.csv`: vollständige 20-SKU-Analyse mit Risikosignalen, angenommener Tragweite, Priorität, Freigabe-Prüfbedarf, Evidenzstatus und nächster fachlicher Aktion.
- `Pilot_11_Incidents_Triage.csv`: alle Incident-Referenzen samt zugeordneter SKU, Evidenzlage und Untersuchungslücke.
- `Pruefprotokoll_Execution1.json`: Wiederholungszahlen und SHA-256 der **unveränderten** ursprünglichen V1-Datenbank.
- `referenzen/`: Original-SQLite-Datei und sieben verwendete SQL-Prüfungen zur selbstständigen Reproduktion.

**Grenzen:** Die Priorisierung beruht auf expliziten Annahmen über *potenzielle* Auswirkungen, nicht auf Messung realer Schäden. Die Indikatoren sind eine **Ersttriage**; sie liefern keine Ursache und kein rechtlich/organisatorisch verbindliches Release-Regelwerk. Die 26 Geschäftsregeln sind nicht durch sieben SQL-Abfragen lückenlos abgedeckt. Genau diese Grenzen werden in der Tiefenanalyse und den späteren Tests berücksichtigt.

---

**Teilabschluss Ausführung 1/4:** Die Ausgangsdaten, das qualitative Bewertungsmodell, das vollständige SKU-Risikoregister und die vollständige Incident-Zuordnung sind reproduzierbar erstellt und kontrolliert. **Die Validierung der Fallentscheidungen und die tatsächliche vertiefte Fallbearbeitung sind noch offen und gehören in Ausführung 2.**
