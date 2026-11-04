# Recherche und Herleitung der Problemstellung

*Portfolio-Projekt 1 — überarbeiteter Textbaustein für die integrierte Fallstudie; Quellenstand: 03.11.2026.*

## 1. Von der Geschäftsfrage zum Untersuchungsthema

Ausgangspunkt meiner Fallstudie war keine vorgegebene technische Lösung, sondern eine operative Fragestellung: **Wie kann es nach einer ERP-Umstellung oder während einer Produkteinführung dazu kommen, dass Artikel im System vorhanden erscheinen, aber dennoch nicht korrekt verarbeitet, bestellt, vereinnahmt oder freigegeben werden können?** Die Frage ist für den Handel relevant, weil die Produktdaten entlang mehrerer Systeme und Verantwortungsbereiche verwendet werden. Ein formal vorhandener Artikelstammsatz beweist noch nicht, dass Identifikatoren, Maßeinheiten, Verpackungshierarchien, Systemübergaben und operative Freigaben zueinander passen.

Um die Fragestellung nicht allein auf Vermutungen zu stützen, habe ich nach öffentlich dokumentierten Zusammenhängen zwischen **Produktstammdaten**, **ERP-/PIM-Integration**, **Datenmigration** und **operativen Folgen** gesucht. Der Fokus lag auf konkret benannten Fehlerarten und Prozessfolgen, nicht auf allgemeinen Aussagen wie „Datenqualität ist wichtig“.

## 2. Recherchepfad und Auswahlprinzip

Die veröffentlichte Recherche lässt sich anhand dreier Themenfelder nachvollziehen:

| Suchfeld | Reproduzierbare Recherchebegriffe (Englisch) | Gesuchter Belegtyp |
|---|---|---|
| Operative Auswirkungen | `product data errors inventory availability ERP retail case study`, `product dimensions case pack warehouse problems` | Recherchierter Fehlermechanismus mit dokumentierter Prozessfolge |
| Produktdaten über Systemgrenzen | `product information ERP spreadsheets ecommerce PIM customer case` | Fall mit konkreter Datenfragmentierung und Publikationsproblemen |
| Migration und Stammdatenbereinigung | `ERP migration duplicate incomplete obsolete master data case study` | Beleg für Qualitätsrisiken vor oder während ERP-Überführungen |

**Transparenz zur Methode:** Diese Suchbegriffe dokumentieren einen heute reproduzierbaren Recherchepfad. Ein ursprüngliches, zeitgestempeltes Suchprotokoll mit exakter Reihenfolge der damaligen Suchanfragen liegt nicht vor. Ich behaupte daher weder eine nachträglich erfundene Suchchronologie noch eine bestimmte Zahl ursprünglich gesichteter Treffer.

Für die Fallauswahl waren vier Fragen ausschlaggebend: (1) Wird ein konkretes Datenproblem beschrieben? (2) Ist eine geschäftliche oder technische Prozessfolge benannt? (3) Lässt sich daraus eine überprüfbare SQL-/Prozessfrage ableiten? (4) Welche Grenzen besitzt die Quelle (journalistische Recherche, Anbieterbericht oder anonymisierter Kundencase)?

## 3. Warum genau diese drei Referenzen?

### Target Canada — vom Produktdatenfehler zur operativen Folge

Die journalistische Aufarbeitung von **Joe Castaldo** beschreibt bei Target Canada unter anderem Maße in uneinheitlichen Einheiten oder falscher Feldreihenfolge, unvollständige Artikelinformationen und Abweichungen zwischen erfasster Case-Pack-Konfiguration und tatsächlicher Lieferung. Ein Beispiel illustriert, warum gleiche Gesamtstückzahlen bei unterschiedlicher Kartonaufteilung nicht dieselbe operative Repräsentation bedeuten: zehn Kartons à 100 Stück versus vier Kartons à 250 Stück. Der Bericht schildert außerdem Schwierigkeiten bei Lagerverarbeitung, automatischem Nachschub und Produktverfügbarkeit.

**Warum ausgewählt:** Diese Quelle verbindet konkrete Attribut- und Verpackungsfehler mit nachvollziehbaren Warenflussproblemen. Daraus entstanden die Untersuchungsfragen zur Längenkonvertierung, Verpackungsversion und Übergabe an nachgelagerte Prozesse.

**Quellenkritik:** Die damalige kanadische Markteinführung war keine direkte Vorlage für eine klassische Legacy-ERP-Migration des fiktiven Händlers. Die berichteten Probleme hatten mehrere Ursachen, unter anderem Prognosen, Systeme und organisatorische Entscheidungen. Die Quelle begründet bestimmte Fehlerrisiken; sie beweist nicht, dass ein Datenfehler allein das Scheitern des Unternehmens verursachte.

### DEVENTRADE — verteilte Produktinformationen und Produkteinführung

Die von **Akeneo** veröffentlichte DEVENTRADE-Kundenstory beschreibt Produktinformationen, die über ERP, Tabellen und mehrere Websites verteilt verwaltet wurden. Fehlende zentrale Pflege und manuelle Aktualisierung erschwerten die Skalierung des Sortiments. Die Fallstudie nennt rund 20.000 Produkte, 1.000 Variantengruppen und 14 E-Commerce-Websites; nach Einführung einer PIM-Lösung berichtet der Anbieter über deutlich häufigere Produktaktualisierungen.

**Warum ausgewählt:** Der Fall ergänzt die Warenfluss-Perspektive um die Frage, ob eine Produktinformation vollständig, aktuell und konsistent in den benötigten Systemen beziehungsweise Vertriebskanälen ankommt. Damit lässt sich die Komponente **Produkteinführung und Produktfreigabe** unseres Untersuchungsthemas begründen.

**Quellenkritik:** Es handelt sich um eine Anbieter-Kundenstory über die Einführung einer PIM-Lösung, nicht um eine unabhängige Untersuchung eines gescheiterten ERP-Migrationsprojekts. Beschriebene Verbesserungen sind als berichtete Kundenergebnisse des Anbieters einzuordnen.

### HTC Global Services — Datenqualität als Migrationsvoraussetzung

**HTC Global Services** schildert in einer Anbieter-Success-Story die ERP-Migration eines **nicht namentlich genannten US-Softwarekunden** in Richtung SAP S/4HANA. Der Anbieter nennt veraltete, doppelte und unvollständige Stammdaten, falsch gruppierte Länderdatensätze und eine tatsächliche Datenmenge, die ungefähr zehnmal höher lag als anfänglich erwartet.

**Warum ausgewählt:** Dieser Fall liefert den unmittelbaren Bezug zur Datenbereinigung und zum Migrationsumfang. Daraus entstehen Fragen nach Identitätsabgleich, Scope, Dubletten, Pflichtfeldern sowie verlässlicher Migration-Reconciliation.

**Quellenkritik:** HTC ist der berichtende Dienstleister, **nicht** das anonymisierte Kundenunternehmen. Öffentliche Einzelbelege zu Datensätzen oder technischen Ursachen sind begrenzt. Der Fall belegt die Art der berichteten Ausgangsprobleme, nicht die späteren fiktiven HYG-Incidents.

## 4. Warum nicht ausschließlich andere Fallstudien?

Auch weitere öffentlich dokumentierte Projekte eignen sich als fachlicher Vergleich. Die **Kross-Fallstudie von Macopedia** behandelt SAP-/PIM-Integration und Attributzuordnung; die **Home-Furnishing-Nordic-Fallstudie von Forbytes** beschreibt große Produktkataloge und fragmentierte Informationen. Für den Kern der Untersuchung lieferten die ausgewählten Referenzen jedoch gemeinsam die gezieltere Kombination aus **operativem Fehlereffekt**, **verteilter Produktdatenpflege** und **qualitätskritischer ERP-Migration**. Die Auswahl ist eine begründete thematische Eingrenzung und kein statistisch repräsentativer Branchenvergleich.

## 5. Vom Quellenbefund zur überprüfbaren Testfrage

| Reale Quelle / dokumentierter Mechanismus | Daraus abgeleitete Untersuchungsfrage | Fiktiver Nachweis im Portfolio |
|---|---|---|
| Target Canada: Dimensions- und Einheitenprobleme | Stimmt die wirksame, genehmigte Konvertierung mit dem ERP-Zielwert überein? | **HYG-1006 / INC-002**, DQ02 und Mapping-Version; 200,0 mm gegenüber 203,2 mm |
| Target Canada: Case-Pack-/WMS-Probleme | Stimmen Bestellung, Verpackungsversion, Lieferavis und Wareneingang fachlich überein? | **HYG-1007/1008**, DQ04 und DQ05 |
| DEVENTRADE: fragmentierte Produktinformationen | Sind Pflichtinformationen und Freigaben für die vorgesehenen Prozesse vollständig und gültig? | **DQ06**, Freigabemuster und Einführungssperren |
| HTC: obsolete, doppelte und unvollständige Migrationsdaten | Welche Artikel gehören in den Migrationsumfang, und welche Zielnachweise fehlen? | **HYG-1004 / INC-001**, DQ01; fehlender Zielnachweis, Ursache offen |

Die Zuordnung ist ausdrücklich eine **Übertragung von real beschriebenen Risikomechanismen auf selbst konstruierte Testfragen**. Keine Fallstudie stellt die HYG-Stammdaten, die 20-/500-Artikel-Population, die Incident-Nummern oder die gemessenen SQL-Ergebnisse bereit.

## 6. Begründete Entscheidung für die synthetische Fallstudie

Aus den drei Perspektiven ergab sich der Untersuchungsrahmen: ein fiktives Handelsunternehmen mit verpackten Hygiene- und Drogerieprodukten, einer ERP-Migration und paralleler Produkteinführung. Diese Produktgruppe erlaubt plausible und prüfbare Felder zu Einheiten, Abmessungen, Case-Packs, Lieferavisen, Wareneingängen und Prozessfreigaben. Sie ist **keine Behauptung**, dass die drei realen Referenzen demselben Handelsunternehmen oder derselben Branche angehören.

Damit entstand die zentrale fachliche Hypothese: **Eine technische Übertragung oder eine registrierte Prozessfreigabe ist noch kein hinreichender Nachweis für fachlich korrekte und operativ verwendbare Produktdaten.** Diese Hypothese habe ich durch definierte Geschäftsregeln, versionierte Testdaten, SQL-Kontrollen, Incident-Nachweise und kontrollierte Retests untersucht. Die ersten 20 Artikel dienten als Pilot; die getrennte 500-Artikel-Population der Prüfung von Wiederverwendbarkeit und zusätzlichen Fehlerszenarien.

## Quellen

1. Joe Castaldo, *What really went wrong with Target Canada*, Canadian Business / Marketing Magazine, 22.01.2016. https://marketingmag.ca/brands/what-really-went-wrong-with-target-canada-166300/
2. Akeneo, *DEVENTRADE – Customer Story*. https://www.akeneo.com/de/customer-story/deventrade/
3. HTC Global Services, *Standardizing Master Data, Enabling On Time ERP System Migration*. https://www.htcinc.com/insights/success-stories/standardizing-master-data-enabling-on-time-erp-system-migration/
4. Macopedia, *Kross – PIM in the Bicycle Industry*. https://macopedia.com/en/case-study/kross
5. Forbytes, *Custom Product Information Management System for Home Furnishing Nordic*. https://forbytes.com/case-studies/home-furnishing-nordic-pim/
