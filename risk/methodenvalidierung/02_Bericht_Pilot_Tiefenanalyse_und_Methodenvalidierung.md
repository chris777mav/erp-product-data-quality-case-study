# Vertiefte Pilotfallbearbeitung und Methodenvalidierung – Ausführung 2/4

## Befund in einem Satz
**Alle elf registrierten Pilot-Incidents wurden einzeln anhand ihrer Ursprungsdaten geprüft, fachlich eingeordnet, einer konkreten nächsten Handlung und einem expliziten Abschlusskriterium zugeordnet; sie sind deshalb nicht automatisch alle geschlossen.**

Die Daten sind synthetisch. Risikoprioritäten schätzen potenzielle Tragweite, ohne empirische Wahrscheinlichkeit oder Geschäftsschaden zu behaupten.
## Datenstand und Nachweisdisziplin
- Historische V1-Quelle unverändert, SHA-256 `01b071db832cb21f25f7fc0e39811c101e78f66b0febea5720e068209e5b3ee7`.
- Alle 20 SKUs bleiben exakt einmal in der Matrix; alle 11 Incidents haben einen nachvollziehbaren Referenzpfad.
- Ein gemeldeter Incident (Grain: Case) ist nicht dasselbe wie eine SKU oder eine ASN-Position. Bei HYG-1011 existieren zwei ASN-Positionen.
- Abgleich von Freigaben (18.09. 18 Uhr) und Ziel-ERP-Snapshot S2 (15.09.) zeigt **mögliche** Kontrollkonflikte, keinen bewiesenen zeitgleichen Policy-Verstoß.
- `AVAILABLE` im Evidenzregister bedeutet vorhandenen Beleg, nicht zwangsläufig bestätigte technische Ursache.

## Ergebnisse der vertieften Einzelfallprüfung

### INC-001 · HYG-1004 · P1 — Fehlender migrationspflichtiger Zielartikel
**Datenbeobachtung:** Der genehmigte Migrationsumfang enthält ALT-1004 mit Ziel-ID ERP-9004. Im S2-Zielsnapshot fehlt HYG-1004; im bereitgestellten Eventabzug fehlt ALT-1004.
**Bewerteter Befund:** `MIGRATION_ABWEICHUNG_NACHGEWIESEN`; **Ursache:** `UNGEKLAERT`.
**Nachweisgrenze:** Das fehlende Ereignis identifiziert weder eine bestimmte ETL-Störung noch die Ursache der Nichtübernahme.
**Evidenzregister:** EVID-001|EVID-002 (vorhanden 1, fehlend 1, unbestätigt 0); Datenquellen: `migration_events|migration_scope`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `REVIEW_REQUIRED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** ERP-Migration / MDM. **Nächste Maßnahme:** Identitätsmapping und Scope erneut abstimmen; Job-/Error-/Dead-letter-Logs am Quellsystem beschaffen; keinen ungeprüften Produktdatensatz nachladen.
**Abschlussbedingung:** Zielidentität im neuen Snapshot nachgewiesen, Event-/Reconciliation-Nachweis vorhanden, angebundene Freigaben und WMS-Folgeverarbeitung getestet.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-002 · HYG-1006 · P1 — Falsche Längentransformation
**Datenbeobachtung:** Der Legacy-Wert 8 IN entspricht 203,2 mm. In S2 stehen 200,0 mm; MIG-E-1006 protokolliert Faktor 25,0 und die nicht genehmigte abgelaufene Version.
**Bewerteter Befund:** `FEHLER_UND_ANGEWENDETE_FALSCHE_MAPPINGVERSION_BELEGT`; **Ursache:** `TRANSFORMATION_REGELVERSION_BELEGT`.
**Nachweisgrenze:** Warum die falsche Regel im Lauf ausgewählt wurde, ist nicht belegt. Historischer Case bleibt OPEN. Der spätere WMS-Stubsandbox-Abschluss ist kein produktiver WMS-Test.
**Evidenzregister:** EVID-003 (vorhanden 1, fehlend 0, unbestätigt 0); Datenquellen: `migration_events`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `REVIEW_REQUIRED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** ERP / MDM / WMS. **Nächste Maßnahme:** Genehmigte R1-Regel verwenden; vierstufigen Vorher-/Nachher-, Ereignis-, WMS- und Negativretest ausschließlich im separaten Simulationszweig führen.
**Abschlussbedingung:** Genehmigte Anwendung, Zielwert 203,2 mm, DQ02-Retest, bestätigter WMS-Test und dokumentierte Freigabe; nur isolierter Simulationszweig kann als CLOSED_IN_SIMULATION gelten.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-003 · HYG-1007 · P1 — Nicht genehmigte Kartonaufteilung
**Datenbeobachtung:** PO-0007 verlangt zehn Kartons zu je 100 Stück; ASN-0007 meldet vier Kartons zu je 250 Stück ohne genehmigte Packversion. Gesamtmenge jeweils 1.000. REC-0007 steht auf HOLD.
**Bewerteter Befund:** `VERPACKUNGSKONFLIKT_UND_HOLD_BELEGT`; **Ursache:** `UNBEKANNTE_URSACHE_DER_LIEFERANTENABWEICHUNG`.
**Nachweisgrenze:** Gleiche Gesamtmenge ersetzt keine Freigabe der Verpackungsebene. Ob Lieferant, ASN-Erstellung oder ERP-Mapping ursächlich war, bleibt offen.
**Evidenzregister:** EVID-004|EVID-005 (vorhanden 1, fehlend 1, unbestätigt 0); Datenquellen: `asns|change_approvals`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `HOLD_UNTIL_PACK_APPROVED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Einkauf / Lieferant / WMS. **Nächste Maßnahme:** Lieferantennachweis und Verpackungsversion anfordern; HOLD bis zur fachlichen Packfreigabe beibehalten; WMS-Verarbeitung nicht aus Mengengleichheit ableiten.
**Abschlussbedingung:** Bestätigte, zeitlich gültige Verpackung + korrespondierendes ASN/PO + WMS-Retest; HOLD dokumentiert aufgehoben, falls fachlich gerechtfertigt.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-004 · HYG-1008 · P2 — Genehmigte nachträgliche Verpackungsänderung
**Datenbeobachtung:** CHG-1008 ist am 15.09. um 16:00 genehmigt, ab 16.09. gültig. PO-0008 wurde am 15.09. um 10:00 erstellt; ASN-0008 ging am 16.09. mit PK-1008-B und 8×125 ein. Receipt ist POSTED.
**Bewerteter Befund:** `GUELTIGE_AENDERUNG_MIT_ZEITBEZOGENEM_REVIEW`; **Ursache:** `KEIN_TECHNISCHER_FEHLER_NACHGEWIESEN`.
**Nachweisgrenze:** Freigabe liegt nach Bestellzeitpunkt; die vorhandene Regel fordert REVIEW, obwohl die Änderung zum ASN-Zeitpunkt gültig ist.
**Evidenzregister:** EVID-006 (vorhanden 1, fehlend 0, unbestätigt 0); Datenquellen: `change_approvals`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `DOCUMENTED_EXCEPTION_REVIEW`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Einkauf / MDM. **Nächste Maßnahme:** Fachliche Nachtragsentscheidung zur ursprünglichen Bestellung protokollieren; keine unbelegte Sperrung eines bereits dokumentiert zulässig geänderten ASN.
**Abschlussbedingung:** Genehmigter Nachtrag auf PO-Position oder dokumentierte Ausnahmeentscheidung samt zeitbezogener Kontrolle. Keine unbegründete Datenkorrektur.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-005 · HYG-1011 · P2 — Zweiter Wareneingangsbeleg fehlt im Auszug
**Datenbeobachtung:** PO-0011 umfasst 240 Stück. Zwei ASN-Positionen melden 96 und 144 Stück. Für ASN-0011-A ist REC-0011-A über 96 Stück POSTED; zu ASN-0011-B fehlt im Export ein Receipt.
**Bewerteter Befund:** `RECEIPT_NACHWEISLUECKE_BELEGT`; **Ursache:** `PHYSISCHER_LIEFERSTATUS_UNGEKLAERT`.
**Nachweisgrenze:** Ein fehlender Receipt-Datensatz beweist keine physische Nichtlieferung von 144 Stück.
**Evidenzregister:** EVID-007 (vorhanden 1, fehlend 0, unbestätigt 0); Datenquellen: `receipts`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `EVIDENCE_REQUIRED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Einkauf / Lager. **Nächste Maßnahme:** WMS-Beleg-/Transportjournal für ASN-0011-B recherchieren; offene Position getrennt von bereits gebuchten 96 Stück verfolgen.
**Abschlussbedingung:** Vorgangsspezifischer Receipt- oder stornierter ASN-Nachweis, Soll-Ist-Reconciliation und begründete Endentscheidung.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-006 · HYG-1012 · P1 — Wareneingang auf HOLD und blockierter Bestand
**Datenbeobachtung:** REC-0012 über 60 Stück ist HOLD. Im datierten WMS-Bestand stehen 60 on_hand und 60 blocked, damit 0 rechnerisch frei. Gleichzeitig existieren registrierte ALLOW-Freigaben.
**Bewerteter Befund:** `HOLD_UND_GEBLOCKTER_SYSTEMBESTAND_BELEGT`; **Ursache:** `HOLD_GRUND_NICHT_BELEGT`.
**Nachweisgrenze:** Aus HOLD und Sperrbestand lässt sich nicht der konkrete technische Fehler oder die tatsächlich freie Filialregalmenge ableiten.
**Evidenzregister:** EVID-008 (vorhanden 1, fehlend 0, unbestätigt 0); Datenquellen: `stock_snapshots`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `HOLD_UNTIL_WMS_CLEARANCE`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Lager / WMS. **Nächste Maßnahme:** HOLD-Grund und Quarantänebefund anfordern; fachlich vorgeschlagene Review-Schranke für operative Nutzung dokumentieren.
**Abschlussbedingung:** Dokumentierter HOLD-Grund, autorisierte Entsperrentscheidung, abgestimmter Folgebestand und Wiederprüfung der operativen Freigabe.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-007 · HYG-1009 · P1 — WMS-Zieleintrag ohne auffindbares Ereignis
**Datenbeobachtung:** HYG-1009 hat einen Ziel-ERP-Datensatz, aber keinen WMS-Snapshot-Eintrag und kein passendes interface_events-Ereignis im bereitgestellten Extrakt.
**Bewerteter Befund:** `WMS_EINTRAG_FEHLT__EVENTLUECKE`; **Ursache:** `UNGEKLAERT`.
**Nachweisgrenze:** Das Fehlen eines Logeintrags kann eine Nichtsendung, eine Loglücke oder einen anderen Stichtag bedeuten; es belegt keine Ursache.
**Evidenzregister:** EVID-009 (vorhanden 0, fehlend 1, unbestätigt 0); Datenquellen: `interface_events`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `REVIEW_REQUIRED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** ERP-Schnittstelle. **Nächste Maßnahme:** Outbound-Queue, Integrationstabelle, Übermittlungs-IDs und WMS-Empfang über definierte Stichtage korrelieren.
**Abschlussbedingung:** Nachvollziehbarer Versand-/Empfangsnachweis, WMS-Eintrag und Reconciliation auf identischem Zeitstand.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-008 · HYG-1010 · P1 — WMS-Zieleintrag fehlt bei protokolliertem Failed-Ereignis
**Datenbeobachtung:** INT-1010 ist mit FAILED und NO_WMS_ACK registriert; der WMS-Snapshot enthält keine HYG-1010-Zuordnung.
**Bewerteter Befund:** `FEHLGESCHLAGENES_INTERFACE_EVENT_BELEGT`; **Ursache:** `TECHNISCHE_FEHLERKATEGORIE_NO_WMS_ACK_BELEGT__URSACHE_OFFEN`.
**Nachweisgrenze:** NO_WMS_ACK belegt eine Fehlerkategorie im Simulationslog, nicht warum die Bestätigung ausgeblieben ist.
**Evidenzregister:** EVID-010 (vorhanden 1, fehlend 0, unbestätigt 0); Datenquellen: `interface_events`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `REVIEW_REQUIRED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Integration / WMS. **Nächste Maßnahme:** Message-ID, Timeout, WMS-Endpoint und Retry-Strategie untersuchen; idempotente Wiederholung erst nach Dublettenprüfung.
**Abschlussbedingung:** Neuer erfolgreicher Event- und WMS-Snapshot-Nachweis, Dublettenprüfung, vorgesehene Prozessfreigabe aktualisiert.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-009 · HYG-1013 · P2 — Lieferantenmaßnachweis unbestätigt
**Datenbeobachtung:** REF-1013-A ist UNCONFIRMED; confirmed_at, approved_by und case_qty fehlen. Registrierte Freigaben lauten dennoch ALLOW.
**Bewerteter Befund:** `EXTERNE_REFERENZ_UNBESTAETIGT`; **Ursache:** `KEIN_FALSCHER_MASSWERT_BEWIESEN`.
**Nachweisgrenze:** Plausible Werte in internen Daten ersetzen keinen externen verlässlichen Maß- oder Packreferenznachweis.
**Evidenzregister:** EVID-011 (vorhanden 0, fehlend 0, unbestätigt 1); Datenquellen: `supplier_references`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `SUPPLIER_EVIDENCE_REQUIRED`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** MDM / Lieferant. **Nächste Maßnahme:** Lieferantendatenblatt / Version / Verantwortlichen bestätigen lassen und danach betroffene Maß-/Packfelder prüfen.
**Abschlussbedingung:** Nachweislich bestätigte Lieferantenreferenz und dokumentierte Freigabeentscheidung; kein Wert ohne Beleg überschreiben.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-010 · HYG-1016 · P3 — Geplanter Launch-HOLD
**Datenbeobachtung:** HYG-1016 ist NEW. Für PROCUREMENT gilt BLOCK mit PLANNED_LAUNCH_HOLD, während WMS_RECEIPT und BRANCH_SUPPLY ALLOW dokumentieren.
**Bewerteter Befund:** `GUELTIGE_FACHLICHE_AUSNAHME`; **Ursache:** `KEIN_DQ_DEFEKT_NACHGEWIESEN`.
**Nachweisgrenze:** Geplanter Nichtbestellbarkeitsstatus ist für sich genommen keine Datenqualitätsabweichung. Ein formaler Caseabschluss ist in der historischen Datenbank nicht dokumentiert.
**Evidenzregister:** EVID-012 (vorhanden 1, fehlend 0, unbestätigt 0); Datenquellen: `releases`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `VALID_PLANNED_HOLD`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Produktmanagement / Einkauf. **Nächste Maßnahme:** Launch-Zeitpunkt und Sortimentsentscheidung bestätigen; Fall als gültige Ausnahme klassifizieren statt den Produktstatus gegen die Policy zu ändern.
**Abschlussbedingung:** Fachliche Ausnahme dokumentiert, Termin- und Statusverantwortung bestätigt, administrative Incident-Abschlussfreigabe vorhanden.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

### INC-011 · HYG-1017 · P2 — Unbestätigte Verpackung vor Launch
**Datenbeobachtung:** REF-1017-A ist UNCONFIRMED; Packaging-Ebene PK-1017-A steht PENDING. Die drei Prozessfreigaben stehen auf REVIEW mit UNCONFIRMED_PACKAGING.
**Bewerteter Befund:** `BERECHTIGTES_REVIEW_BEI_UNBESTAETIGTER_REFERENZ`; **Ursache:** `FEHLENDER_BELEG_STATT_BESTAETIGTER_TRANSFORMATIONSFEHLER`.
**Nachweisgrenze:** Das dokumentierte REVIEW ist kein Fehlverhalten. Weder ungültige Menge noch technischer Importfehler sind damit bewiesen.
**Evidenzregister:** EVID-013 (vorhanden 0, fehlend 0, unbestätigt 1); Datenquellen: `supplier_references`.
**Risikosteuerung / vorgeschlagene Gate-Entscheidung:** `RETAIN_REVIEW`. Das ist **eine modellierte Empfehlung**, keine Änderung historischer Freigaben.
**Verantwortung:** Produktmanagement / MDM / Lieferant. **Nächste Maßnahme:** Freigegebene Lieferantenspezifikation, Packversion und gültigen Launch-Zeitpunkt nachfordern; REVIEW bis dahin beibehalten.
**Abschlussbedingung:** Referenz bestätigt, Packversion freigegeben, zeitgültige Release-Entscheidung vorhanden und Kontroll-Checks bestanden.
**Historischer Status:** `OPEN`. Keine neue Erledigung ohne Retest- und Freigabebeleg.

## Validierung gegen die 16 vorab definierten Akzeptanzszenarien

**Wichtig:** Ein bestandenes Datenprüfkriterium ist nicht gleichbedeutend mit vollständiger Prozessabnahme. Die Szenarien AT-10, AT-11 und AT-13 sind daher inhaltlich nur teilweise gedeckt.

| Szenario | Pilotbezug | Datentest | Fachliche Abdeckung |
|---|---|---|---|
| AT-01 – Korrekte Migration | HYG-1001 | PASS | PASS |
| AT-02 – Legitim ausgeschlossener Altartikel | HYG-1003 | PASS | PASS |
| AT-03 – Fehlender Zielartikel, Ursache offen | HYG-1004 | PASS | PASS |
| AT-04 – Neuartikel ohne Migration | HYG-1015 | PASS | PASS |
| AT-05 – Genehmigte IN->MM-Umrechnung | HYG-1005 | PASS | PASS |
| AT-06 – Nichtgenehmigter Transformationsfaktor | HYG-1006 | PASS | PASS |
| AT-07 – Konsistentes PO-ASN-Receipt | HYG-1001 | PASS | PASS |
| AT-08 – Gleiche Basismenge, nicht genehmigte Packstruktur | HYG-1007 | PASS | PASS |
| AT-09 – Zeitlich genehmigte Packänderung | HYG-1008 | PASS | PASS |
| AT-10 – Teil-Wareneingang / Dokumentationslücke | HYG-1011 | PASS | TEILWEISE |
| AT-11 – HOLD-Receipt und blockierter Lagerbestand | HYG-1012 | PASS | TEILWEISE |
| AT-12 – WMS fehlt, Event fehlt | HYG-1009 | PASS | PASS |
| AT-13 – WMS fehlt, Failed-Event vorhanden | HYG-1010 | PASS | TEILWEISE |
| AT-14 – Geplanter Launch-HOLD | HYG-1016 | PASS | PASS |
| AT-15 – Unbestätigte Lieferantenreferenz | HYG-1013 | PASS | PASS |
| AT-16 – Korrektur ohne Folgeretest darf nicht schließen | HYG-1006 | PASS | PASS |

## Isolierte Negativ- und Änderungsproben

| Prüffall | Ergebnis | Warum relevant? |
|---|---|---|
| NEG-01 Ziel ergänzt: DQ01 PASS, aber Migrationslog bleibt fehlend | PASS | Der Ziel-Snapshot alleine schließt die historische Root-Cause-Lücke nicht. |
| NEG-02 Dimension richtig, falsches Mappingereignis weiter nachweisbar | PASS | Korrektur des Zielwerts heilt den nichtgenehmigten historischen Lauf nicht. |
| NEG-03 Verpackung berichtigt, HOLD bleibt bestehen | PASS | Zwei unabhängige Kontrollen dürfen nicht als eine erfolgreiche End-to-End-Freigabe verkauft werden. |
| NEG-04 Fehlende Genehmigungsrolle ist kein PASS | PASS | Eine formal unvollständige Genehmigung kann nicht stillschweigend gültig sein. |
| NEG-05 Fehlender Receipt-Beleg wird durch simulierte Nachbuchung aufgelöst | PASS | Nur künstliche Nachbuchung im Testzweig; kein Beleg einer echten Warenbewegung. |
| NEG-06 Referenz bestätigt: unbestätigt-Signal fällt dynamisch weg | PASS | Offener historischer Incident darf ohne Abschlussbeleg weiterhin administrativ markiert sein. |
| NEG-07 WMS-Snapshot ergänzt: WMS-Fehlsignal fällt weg | PASS | Ein ergänzter Datensatz beweist noch keine historisch korrekte Übermittlung. |

## Methodenanpassung vor der Skalierung
Die ursprüngliche Ersttriage verwendete bei ausgewählten WMS- und Lieferantensignalen feste Incident-IDs als Auslöser. Das wäre bei weiteren Incident-IDs auf der 500er-Datenbasis nicht zulässig.
Das neue, versionierte Skript `risikomodell_geprueft.py` nutzt stattdessen **Symptom und tatsächliche Datensätze**. In den zwei Negativproben zur Lieferantenbestätigung und zum WMS-Eintrag verschwindet das entsprechende negative Prüfsignal nach einer simulierten Datenänderung; der historische Incident wird dadurch **nicht** automatisch geschlossen.
Die 20-Artikel-Ausgangsverteilung bleibt trotz Anpassung unverändert: P1=6, P2=4, P3=1, P4=9. Der Quellzustand wurde nicht verändert.

## Erforderliche Zusatzsteuerung (Vorschlag, kein produktives Gate)
Eine `ALLOW`-Registrierung darf nicht automatisch die separat ermittelte Qualitätslage überschreiben. Für P1-Konflikte wird eine **Review-Queue** empfohlen; für dokumentierte geplante HOLDs keine Fehler-Eskalation. Dieses fachliche Gate benötigt vor produktiver Übernahme eine bestätigte Unternehmensrichtlinie, Verantwortliche und zeitliche Gültigkeit.

## Offen bleibende Grenzen
- AT-10: fehlender Beleg ist keine bewiesene physische Fehlmenge.
- AT-11: HOLD/blocked trotz ALL_PROCESSES_ALLOW – erst die vorgeschlagene Kontrollschranke würde eine zusätzliche Review-Entscheidung erzwingen; die historischen Freigaben bleiben bestehen.
- AT-13: FAILED/NO_WMS_ACK ist registriert; Ursache und späterer produktiver Retry fehlen.
- Weitere 26 im Fachkonzept definierte Geschäftsregeln sind nicht vollständig durch die sieben implementierten SQL-Kontrollen abgedeckt.
- Kein echtes ERP/WMS und keine Beobachtung realer wirtschaftlicher Auswirkungen.

## Übergabe an Ausführung 3/4
Das methodisch getestete Verfahren `RISK-PILOT-1.1` sowie die Grenzfallregel (keine automatische Incident-Schließung; keine automatische BLOCK-Umstellung) dienen als fixierte Grundlage für die Untersuchung **aller 500** synthetischen Artikel. Die 500er-Stufe muss zunächst die Datengrains, die Feld-/Statussemantik und die Übertragbarkeit von WMS- und Lieferantensignalen unabhängig prüfen. Fachlich ungeklärte Fälle werden nicht nachträglich als PASS umetikettiert.
