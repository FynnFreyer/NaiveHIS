# Objekte der Anschauung

```mermaid
erDiagram
    WORKER   ||--|{ REPORT:        "writes/written by"
    WORKER   }|--O{ CASE:          "assigned to"
    CASE     }O--|| PATIENT:       "concerns/has"
    WORKER   }|--O| STATION:       "works on/worked by"
    CASE     ||--O{ REPORT:        "concerned by/concerns"
    WORKER   }|--|{ QUALIFICATION: "has/provided by"
    WORKER   ||--|{ POSITION:      "has/held by"
    DIVISION }|--|| ROOM:          "has/belongs to"
    WORKER   }O--O{ ORDER:         "fulfills/fullfilled by"
    WORKER   }O--O{ ORDER:         "issues/issued by"
    ORDER    }|--|| CASE:          "relates to/caused"

    DIVISION {
        int id
        datetime created
        datetime updated
        list_qualifications requirements
        list_room rooms
        list_worker workers
    }
    
    ROOM {
        int id
        datetime created
        datetime updated
        int capacity
        int room_number
        int building_number
    }

    WORKER {
        int id
        datetime created
        datetime updated
        string first_name
        string last_name
        string username
        function worker_function
        position worker_position
    }

    PATIENT {
        int id
        datetime created
        datetime updated
        string first_name
        string last_name
        case cases
    }

    CASE {
        int id
        datetime created
        datetime updated
        datetime closed
        worker attending_physician
    }

    REPORT {
        int id
        datetime created
        datetime updated
        worker written_by
    }
```

Fehlende Relationen:

- Position, Worker und Station hängen zusammen
- Qualification und Station hängen zusammen
- Order und Case hängen zusammen

## Patient

- Name
- Geburtsdatum
- Adresse
- [Fallhistorie](#Fall)

## Fall

Die Basiseinheit des Prozesses.

- Einlieferungsdatum
- Entlassdatum
- Untersuchungs[berichte](#Report)
- behandelnder Arzt
- weitere Zugriffsberechtigte

## Mitarbeiter

- Name (Vor/Nach)
- Geburtsdatum
- Adresse
- Kann sich einloggen, hat also
    - Username und
    - Password.
- Qualifikation (Fachrichtung)
- Stellung (Hierarchie)
- Arbeitet in einer [Abteilung](#Abteilung).

```mermaid
flowchart RL
    ArztFunktion --> MitarbeiterFunktion
    ArztStellung --> MitarbeiterStellung
```

### Arzt

- Hat Fälle, die er betreut.
- Die Fachrichtung ist relevant für die
    - Berichte, die geschrieben werden können und
    - Stationen auf denen gearbeitet werden kann.
- Die Stellung ist relevant für
    - Zugriffsberechtigungen (in Realität läuft das eher über die Stationsmitgliedschaft),
    - Freigabe von Diagnose[reports](#Report),
    - Weisungsbefugnisse ([Aufträge](#Aufträge)),
    - Entlohnung und Abrechnung (wird ignoriert).

Nur ein Oberarzt oder ein noch höherrangiger Arzt gibt Befunde frei!

Zugriff auf Patientendaten **sollte** laufen **über behandelnden Arzt Status**, läuft **in Realität** aber eher **über Stationsmitgliedschaft**

### Pfleger

- Hat Fälle, die er betreut.

### Labormediziner

- Bekommen [Aufträge](#Aufträge) für Untersuchungen.
- Führen Untersuchungen durch und schreiben [Reports](#Report).

### Transporteur

- Hat **keine** Fälle, die er betreut.

## Report

- Art des Reports
- geschrieben von
- geschrieben am
- betroffener [Fall](#Fall)
- Inhalt
    - unterscheidet sich je nach Art des Reports

### Arten von Reports

- Untersuchungsreport
    - Pathologiereport
    - Radiologiereport
    - Laborreport
- Diagnosereport
    - [ICD](../../Archiv/EGI/Klassifikation%20von%20Krankheiten/ICD.md)-Codes
    - kann sich auf Untersuchung beziehen
- Therapiereport
    - OPS-Codes
    - kann sich auf Diagnose beziehen

Vielleicht auch

- Entlassbrief
    - Freitext
- Arztbrief
    - Freitext

## Abteilung

Ist ein Zusammenschluss von Räumen, mit einer bestimmten Funktion, in der eine Menge von Mitarbeitern arbeitet.

- Bezeichnung
- [Mitarbeiter](#Mitarbeiter)
- [Räume](#Raum)

## Raum

- Funktionsbezeichnung. (Abteilung?)
- Raumnummer.
- Gebäudenummer.
- Kapazität.
- Belegung durch
    - Patienten und/oder
    - Mitarbeiter (?).

## Aufträge

Ärzte können Untersuchungen beauftragen.
Transportaufträge sind potentiell nötig bei Untersuchungen, oder bei Verlegungen.

Aufträge werden erfüllt.

An die Erfüllung kann ein bestimmtes Artefakt geknüpft sein.

- Zeitpunkt der Anforderung
- Erfüllungszeitpunkt
- Art des Auftrags
- betroffener [Fall](#Fall)
- potentiell ein Artefakt

### Arten von Aufträgen

- Behandlungsauftrag
    - sorgt für Vergabe von behandelnder Arzt-Status
- Transportauftrag
    - zieht Raumänderung nach sich
- Untersuchungsauftrag
    - produziert Report
