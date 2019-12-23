# event_checker

event_checker ist ein Analyse-Modul zum herausfiltern bisher unbekannter Viren und Events.

## Installation

Einfach das Modul manuell in den Ordner kopieren, in dem sich das eigene Python-Skript befindet.

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

Die Funtion parse_data aufrufen mit den Rohen json-Daten

`
checker.parse_data(raw_data)
`
