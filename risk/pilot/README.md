# Ausführung 1 von 4 – reproduzierbare Pilotersttriage

## Zweck
Die 20 Artikel sind die kontrollierte Tiefenstufe der Portfolio-Fallstudie. Erst wird ein belastbares Risikomodell an allen 20 SKUs und elf Incidents entwickelt, geprüft und weiter vertieft. Danach wird **dieselbe** Methode auf 500 Artikel übertragen. Dieser Teil enthält den ersten nachvollziehbaren Schritt: vollständige Ersttriage, noch keinen Abschluss sämtlicher Incidents.

## Inhalt
- `01_Bericht_Risikoanalyse_Pilot.md` – ausführliche fachliche Dokumentation und Evidenzgrenzen.
- `Pilot_20_Artikel_Risikomatrix.csv` – 20 eindeutige Produktzeilen.
- `Pilot_11_Incidents_Triage.csv` – 11 fachlich zugeordnete Cases.
- `risikoanalyse_pilot.py` – aus tatsächlichen Tabellen und sieben Original-SQL-Abfragen erzeugte Triage.
- `Pruefprotokoll_Execution1.json` – Zählungen und SHA-256 der eingefrorenen V1-Quelle.
- `referenzen/V1_Pilot_20_Artikel.sqlite`, `referenzen/sql/` – Nachweise der Quelle.

## Erneut ausführen
```bash
python risikoanalyse_pilot.py --db referenzen/V1_Pilot_20_Artikel.sqlite --sql-dir referenzen/sql --out .
```

Das Programm **liest** die Originaldatenbank ohne Schreibzugriff. Die Baseline ändert sich dadurch nicht.

## Folgeausführungen
2. Alle elf Pilot-Incidents vertiefen, Sollfälle/Entscheidungs- und Retestlogik prüfen und den Bewertungsmaßstab validieren.
3. Den **unveränderten, versionierten** Maßstab auf alle 500 SKUs anwenden; sämtliche Auffälligkeiten klassifizieren und die priorisierten Fälle mit Maßnahmen, Retests und Ergebnissen untersuchen.
4. Gesamtanalyse, Vorher/Nachher-Evidenz, Cross-Scale-Prüfung, überarbeitete Fallstudie und finale unabhängige Abnahme integrieren. Das vereinbarte zusätzliche Recherchekapitel wird erst bei dieser Endintegration eingebaut.
