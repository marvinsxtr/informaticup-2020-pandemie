# Pandemie!

## Contents
* [Einleitung](documentation.md#einleitung)
* [Grundlagen](documentation.md#grundlagen-(install,-run,-etc))
* [Installation](documentation.md#installation)
* [Schnellstart](documentation.md#schenllstart)
* [Wie benutze ich das Programm](documentation.md#wie-benutze-ich-das-programm)
* [Wissenschaftlicher Hintergrund](documentation.md#wissenschaftlicher-hintergrund)
* [Erklärung des Programmcodes](documentation.md#erklaerung-des-programmcodes)
* [API](documentation.md#api)
* [Software Architektur](documentation.md#software-architektur)
* [FAQ](documentation.md#faq)
* [Zusatzfunktion: Visualisierung](documentation.md#zusatzfunktion:-visualisierung)
* [Der Web service](documentation.md#der-web-service)
* [Warum unsere Idee die Beste ist.](documentation.md#warum-unsere-idee-die-beste-ist)
* [Auswertung der Ergebnisse](documentation.md#auswertung-der-ergebnisse)

## Einleitung
(Alex)
## Grundlagen
(Alex, kleine Intro schreiben)
### Installation
(Alex)
### Schenllstart
(Alex)
## Wie benutze ich das Programm
(Ruwen)
Nach der Installation des Programms und einem einfachen Ausführungsbeispiel wird nun die Verwendung der einzelnen 
Funktionen des Programms erklärt.
### Den Tester richtig nutzen
Zum testen von Strategien ist das Modul `tester.py` vorgesehen. Hier werden verschiedene Funktionalitäten zum 
analysieren und testen eigener Strategien bereitgestellt. Um eigene Strategien zu testen muss lediglich das Modul
`tester.py` ausgeführt werden. <br>
```bash
$ python3 tester.py
```
Im ersten Schritt wird man nun nach dem Namen der zu testenden Strategie gefragt:<br>
```bash
Enter the full name of the strategy you want to test (no .py):	
```
Hier ist einfach der Dateiname der Strategie ohne die `.py` Endung einzugeben und mit `ENTER` zu bestätigen.
<br> Hierbei ist zu beachten, dass sich die Strategie im Ordner `pandemie/tester/strategies` befindet. Falls der 
eingegebene Strategiename nicht in diesem Ordner zu finden ist wird der Fehler 
`StrategyModule [strategy-name] not found! Exiting...` ausgegeben und und das Programm terminiert.

Im nächsten Schritt 
### Eigene Strategien entwickeln
#### Event-Checker als Daten-Analyse-Tool
## Wissenschaftlicher Hintergrund
(Marvin)
## Erklaerung des Programmcodes
## API
## Software Architektur
## FAQ
(Marvin)
## Zusatzfunktion: Visualisierung
(Marvin)
Zur Analyse und zum Vergleich verschiedener Strategien ist es sinnvoll, diese zu visualisieren. Hierbei können Stärken
und Schwächen einer Strategie ausgemacht werden und so eine Verbesserung des Scores erzielt werden. Zudem sollen
Strategien von Grund auf neu entwickelt werden können. Dies ist ein iterativer Prozess, welcher schlussendlich zu einer 
Strategie führen kann, welche auf verschiedene Ereignisse angemessen reagiert und eine gute Erfolgswahrscheinlichkeit
an den Tag legt. Für den Zweck der Entwicklung unserer Teamstrategie haben wir bereits einige Daten gesammelt und
visualisiert. Im Folgenden wird erklärt, wie auf diese zugegriffen werden kann und wie eigene Erweiterungen realisiert 
werden können.
### Wie starte ich die Visualisierung
### Eigene Visualisierung hinzufügen
## Der Web Service
## Warum unsere Idee die Beste ist
(Alex)
## Auswertung der Ergebnisse