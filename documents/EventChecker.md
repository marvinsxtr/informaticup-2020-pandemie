# event_checker

event_checker ist ein Analyse-Modul zum herausfiltern bisher unbekannter Viren und Events.

## Installation

Das Modul manuell in den Ordner kopieren in dem sich das eigene Python-Skript befindet, welches das Testsetup bereitstellt.

## Quick start
Schritt 1: Importieren des Moduls

`
import event_checker
`

Schritt 2: Ein Object der Klasse EventChecker erstellen

`
checker = event_checker.EventChecker()
`

### Using the EventChecker

Die Funktion parse_data aufrufen und die Rohen json-Daten übergeben

`
checker.parse_data(raw_data)
`
