# Ausführung 3 von 4 – 500 Artikel und kontrollierte Maßnahmen

1. `risikomodell_v2_adapter.py` – exakte Pilotprioritäten RISK-PILOT-1.1, V2-Kohortenadapter.
2. `auswertung_und_retests_v2.py` – alle 500 und 32 Fälle mit Original-SQLite und 7 DQ-Queries; Nachweislücken; fünf simulierte Einzelfall-Tests; unabhängige Assertions.
3. `V2_500_Artikel_Risikomatrix.csv` – rohe, unveränderte Pilotgewichtung auf V2.
4. `V2_500_Artikel_Entscheidungsregister.csv` – zusätzliche nichtgewichtete Kontrolllücken und vollständige Fallzuordnung.
5. `V2_32_Incidents_Einzelfallbericht.md` plus `.json`/`.csv` – 32 fallbezogene Quellnachweise, Entscheidungen und Gate-Kriterien.
6. `V2_Abdeckungsluecken_manueller_Pruefbedarf.csv` – Warnsignale außerhalb des eingefrorenen V1-Score.
7. `V2_EINZELFALL_RETTEST_SANDBOX.sqlite` – **nur hypothetische Testveränderungen**, keine historische Ursprungsdatenbank.
8. `V2_Retest_Vorher_Nachher.csv` und `Ausfuehrung_3_Abnahmeprotokoll.json` – direkt nachgerechnete Werte, Quelle unverändert.

Reproduzierbarer Aufruf:
```bash
python risikomodell_v2_adapter.py --db /pfad/zur/Portfolio_Projekt1_V2_500SKUs.sqlite --sql-dir /pfad/zum/sql --out .
python auswertung_und_retests_v2.py
```

Die zweite Datei verweist für die Nachrechenbarkeit auf die im aktuellen Projektstand vorhandenen Originaldaten. Für eine eigenständige finale ZIP-Version werden Pfade in Ausführung 4/4 relativ und ausführbar gemacht.
