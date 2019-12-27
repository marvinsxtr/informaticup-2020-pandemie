# Pandemie!

## Inhaltsverzeichnis
* [Einleitung](documentation.md#einleitung)
* [Grundlagen](documentation.md#grundlagen)
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
In dieser Dokumentation wird die Verwendung und Funktionsweise unserer Lösung des Problems des Informaticups 2019
beschrieben.<br>
Durch das bereitgestellte Programm "ic20", welches von den Herrausgebern des Informaticups zur Verfügung gestellt wird,
wird eine Epedemie der Welt simmuliert.
Ziel ist es, dass in möglichst kurzer Zeit, die Menschheit auf dem Planeten Erde überlebt und die Seuchen
ausgerottet werden. Diese Seuchen, mit unterschiedlichen Eigenschaften treten zufällig auf.
Für die Lösung wurde unsererseits ein Webservice entwickelt, welcher in Kombination mit einer Lösungsstrategie dem
Programm "ic20" rundebasiert Antworten schickt, die dazu führen sollen, dass die Simmulation der Epedemie positiv
entschieden wird.<br>
Um das Verhalten des Simmulationsprogramms zu analysieren und eine effektive Lösungsstrategie zu entwickeln, wurden
weitere Programme durch die Gruppe entwickelt.<br>
Des Weiteren enthält die von unserer Gruppe bereitgestellte Softwarelösung die Möglichkeit zur Visualisierung einer
abgeschlossenen Simmulation.
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
Zum Testen von Strategien ist das Modul `tester.py` vorgesehen. Hier werden verschiedene Funktionalitäten zum 
Analysieren und Testen eigener Strategien bereitgestellt. Um eigene Strategien zu testen, muss lediglich das Modul
`tester.py` ausgeführt werden. <br>
```bash
$ python3 tester.py
```
Im ersten Schritt wird man nun nach dem Namen der zu testenden Strategie gefragt:<br>
```bash
Enter the full name of the strategy you want to test (no .py):	
```
Hier ist einfach der Dateiname der Strategie ohne die `.py` Endung einzugeben und mit `ENTER` zu bestätigen.
<br> Es ist zu beachten, dass sich die Strategie im Ordner `pandemie/tester/strategies` befindet. Sollte der 
eingegebene Strategiename nicht in diesem Ordner zu finden sein, wird der Fehler 
`StrategyModule [strategy-name] not found! Exiting...` ausgegeben und und das Programm terminiert.

Nach der Eingabe des Namens wird gefragt, ob das Testen der Strategie geloggt werden soll:<br>
```bash
Should a log be created? (y/n, default=n):
```
Das Loggen beinhaltet das Ergebnis und die Anzahl der Runden, die bis zu diesem Ergebnis gespielt wurden, für jedes
einzelne gespielte Spiel. Außerdem werden für jedes Spiel alle aufgetretenen Pathogene inklusive ihrer Eigenschaften
geloggt. Am Ende der Log-Datei steht dann der berechnete Score der Strategie. Dieser befindet sich immer zwischen 1 und
-1, wobei 1 ein perfekter Score wäre.<br>
Hier ein Beispiel für die Strategie `example_strategy.py` mit zwei gespielten Runden:<br>
```
loss:	11
{'name': 'N5-10', 'infectivity': '+', 'mobility': '++', 'duration': 'o', 'lethality': '+'}
{'name': 'Admiral Trips', 'infectivity': '++', 'mobility': '+', 'duration': '-', 'lethality': '++'}
{'name': 'Plorps', 'infectivity': 'o', 'mobility': 'o', 'duration': '+', 'lethality': '-'}

win:	26
{'name': 'Shanty', 'infectivity': '+', 'mobility': '-', 'duration': 'o', 'lethality': '-'}
{'name': 'Phagum vidiianum', 'infectivity': 'o', 'mobility': 'o', 'duration': '+', 'lethality': '+'}

-0.1635815380187609
```

Im dritten Schritt muss angegeben werden, ob die gespieleten Runden für die Visualisierung gespiechert werden sollen:
<br>
```bash
Do you want the data of one round to be saved for visualization? (y/n, default=n):
```
Die Visualisierung dient wie auch das Loggen dem Analysieren und Verstehen der Strategie. Wie die Visualisierung 
funktioniert, wird detailiert im Kapitel 
[Zusatzfunktion: Visualisierung](documentation.md#zusatzfunktion:-visualisierung) erläutert.

Als nächstes muss angegeben werden, wie viele Spiele gleichzeitig gespielt werden sollen:
```bash
How many simulations should be run simultaneously? (default=5):
```
Umso mehr Spiele gespielt werden, desto besser lässt sich die Strategie am Ende bewerten. Allerdings ist zu 
beachten, dass bei zu vielen Spielen gleichzeitig der Computer sehr viel zu arbeiten hat und es sein kann, dass er etwas
langsamer als gewöhnlich läuft.

Im letzten Schritt wird gefragt, ob für jedes Spiel ein zufälliger Seed generiert werden soll:<br>
```bash
Do you want a random seed? (y/n, default=y):
```
Wird hier `n` angegeben, so werden die Seeds von 1 aufsteigend verwendet. Dies ist nützlich, um die Konsistenz einer
Strategie zu beurteilen, aber auch um zwei Strategien bei exakt gleichen bedingungen zu vergleichen.
Wird aber `y` angegeben, so wird für jedes Spiel ein zufälliger Seed zwischen 1 und 100.000.000.000 generiert.

### Standardeinstellungen des Testers
Zum schnellen Testen einer Strategie kann die Standardkonfiguration des Testers genutzt werden. Als standartd festgelegt
sind:
 * Kein Log-Output wird erstellt
 * Die Runden werden nicht Visualisiert
 * Es werden 5 Spiele gleichzeitig gespielt
 * Für jedes Spiel wird ein zufälliger Seed generiert
 
 Somit muss lediglich angegeben werden, welche Strategie ausgeführt werden soll.
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
Zur Analyse und zum Vergleich verschiedener Strategien ist es sinnvoll, diese zu visualisieren. Dazu werden entweder
einzelne Runden oder das gesamte Spiel mithilfe von verschiedenen Graphen oder Karten dargestellt. Hiermit können 
Stärken und Schwächen einer Strategie ausgemacht werden und so eine Verbesserung des Scores erzielt werden. Zudem sollen
Strategien von Grund auf neu entwickelt werden können. Dies ist ein iterativer Prozess, welcher schlussendlich zu einer 
Strategie führen kann, welche auf verschiedene Ereignisse angemessen reagiert und eine gute Erfolgswahrscheinlichkeit
an den Tag legt. Für den Zweck der Entwicklung unserer Teamstrategie existiert bereits die Implementierung zur 
Darstellung einiger Graphen und Karten. Im Folgenden wird erklärt, wie auf diese zugegriffen werden kann und wie eigene 
Erweiterungen realisiert werden können.
### Wie starte ich die Visualisierung
Um die Visualisierung zu starten muss zunächst mindestens einmal der 
[Tester](documentation.md#den-tester-richtig-nutzen) mit der Visualisierungs-Option gestartet werden. Dies führt dazu, 
dass im Ordner `pandemie/tester/tmp` die JSON-Dateien der einzelnen Runden abgelegt werden. Ist diese Voraussetzung 
erfüllt, kann die Visualisierung mit dem Modul `visualization.py` gestartet werden: <br>
```bash
$ python3 visualization.py
```
Sobald die Visualisierung fertig ist, wird anschließend ein Webserver gestartet, welcher über `localhost:8050`
aufgerufen werden kann. Im Log wird hierzu auch ein Link angezeigt. Wenn die Seite aufgerufen wird, kann oben im
Dropdown-Menü ausgewählt werden, welche Runde oder ob das gesamte Spiel visualisiert werden soll.
### Eigene Visualisierung hinzufügen
Die Visualisierung wird mithilfe von `Plotly` mit `Dash` als Dashboard Anwendung realisiert. Plotly kann also dazu 
genutzt werden, eigene Visualisierungen einzubinden. Hierbei soll zwischen Preprocessing und der eigentlichen 
Darstellung unterschieden werden, wobei ersteres in `preprocessing.py` und letzteres in `visualization.py` stattfindet. 
<br> Soll eine Visualisierung für das gesamte Spiel hinzugefügt werden, so muss das Preprocessing in der Funktion 
`preprocess_game` stattfinden. Hier können benötigte Lists/Dicts erstellt und mithilfe der jeweiligen JSON-Datei
generiert werden. Anschließend sollen generierte Daten in dem Dict `game_visualizations` abgelegt werden, um später auf
sie zuzugreifen. Analog können für einzelne Runden in der Funktion `preprocess_round` Daten gesammelt und in dem Dict 
`round_visualizations[<Runden-Nummer>]` gespeichert werden.<br>
In `visualization.py` kann nun eine Funktion hinzugefügt werden, welche einen 
[Dash component](https://dash.plot.ly/dash-core-components) zurückgibt, was ein Graph aber auch andere GUI-Elemente sein
kann. Zusätzlich muss in der Funktion `visualize_game` der entsprechende Funktionsaufruf der zurückgegebenen Liste 
hinzugefügt werden. Die Visualisierungen werden entsprechend der Reihenfolge in dieser Liste untereinander angezeigt.
Für die Visualisierung einzelner Runden kann hierfür analog die Funktion `visualize_round` verwendet werden.
## Der Web Service
## Warum unsere Idee die Beste ist
(Alex)
## Auswertung der Ergebnisse