# Ausführung 2/4 — Pilot-Tiefenanalyse und methodische Validierung

## Neu erstellt
- `Pilot_11_Incidents_Tiefenanalyse.csv`: **11** fachliche Caseakten mit Quellen, gesichertem Befund, Ursachengrenzen, Entscheidungsvorschlag, Owner, Maßnahme und Abschlussbedingungen.
- `Fallakten_Quellenauszuege_11_Incidents.json`: die konkreten Datensätze auf den relevanten 21 V1-Tabellen, je Fall mit korrekten PO-/ASN-/Receipt-Schlüsseln (nicht pauschal nur SKU verknüpft).
- `02_Bericht_Pilot_Tiefenanalyse_und_Methodenvalidierung.md`: ausführlicher Einzelbericht aller elf Incidents, Differenzierung zwischen Beobachtung, Deutung und Beweislücke.
- `Pilot_16_Akzeptanzfaelle_Abgleich.csv`: unabhängiger Bezug zu den **16 vorher festgelegten** Szenarioklassen, inklusive drei nur teilweise belegter End-to-End-Anforderungen.
- `Pilot_Negativtests_Isolierte_Kopien.csv`: sieben kontrollierte Testmutationen in temporären Datenbankkopien. Kein Originaldatensatz geändert.
- `risikomodell_geprueft.py`: methodische Korrektur: Lieferanten-/WMS-Signale jetzt daten- und symptombasiert statt allein anhand bestimmter Incident-IDs.
- `RISK_PILOT_1_1_METHODENVERTRAG.json`: **vor** Ausführung 3 dokumentierte fachliche Regeln und Grenzen für den 500-SKU-Transfer.
- `fallbearbeitung_validieren.py`: ausführbarer evidenz- und szenarienbezogener Prüflauf.
- `Pruefprotokoll_Execution2.json`: Maschinenlesbare Zahlen, SHA, Einschränkungen.

## Reproduzierbarkeit
Die historischen Rohdaten liegen ausschließlich im Ordner `../01_Pilot_Risikomodell/referenzen/`. Von hier aus:

```bash
python risikomodell_geprueft.py --db ../01_Pilot_Risikomodell/referenzen/V1_Pilot_20_Artikel.sqlite --sql-dir ../01_Pilot_Risikomodell/referenzen/sql --out .
python fallbearbeitung_validieren.py --db ../01_Pilot_Risikomodell/referenzen/V1_Pilot_20_Artikel.sqlite --sql-dir ../01_Pilot_Risikomodell/referenzen/sql --out .
```

## Wichtig
Ein Daten-Prüfresultat `PASS` beweist nicht den geschäftlichen Abschluss eines Falls. Historisch bleiben alle elf Incidents `OPEN`. Der bereits vorhandene erfolgreiche INC-002-Retest wird als **separater synthetischer Testzweig** referenziert; die Ausgangsquelle wird nicht rückdatiert. Keine reale ERP- oder WMS-Implementierung wird beansprucht.

Der Methodenvertrag ist eine fachlich dokumentierte Regelgrundlage, **nicht** die Behauptung, dass das V1-Ausführungsskript unverändert auf ein anderes DB-Schema kopiert werden könne. Ausführung 3 erstellt und prüft den notwendigen technischen Adapter auf der neuen 500-SKU-Kohorte, ohne die Entscheidungssemantik zu ändern.
