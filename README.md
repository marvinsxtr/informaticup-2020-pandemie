# README
Die komplette Dokumentation finden Sie hier: [documentation](documents/documentation.md).

Alle im Vorfeld zu installierenden Abhängigkeiten finden sie in hier: [requirements](requirements.txt).

### Schnellstart für debugging Zwecke

**Die Nachstehenden Schnellstarts sind im Projektordner auszuführen!**
Um den Tester für das `ic20_linux` Programm auszuführen, kann auf dem Projektordner folgender Befehl aufgerufen werden.
```bash
python3.8 -m pandemie.tester
```
Für die schnelle Ausführung des Programms sind bereits Standard-Parameter gesetzt. Diese können per aufgefordeter
Terminaleingabe auch geändert werden.
<br><br>
Um die Visualisierung zu starten führen sie den nachstehenden Befehl aus.
```bash
python3.8 -m pandemie.visualization
```
Öffnen sie danach ihren Webbrowser mit der URL: `localhost:8050`

Um den reinen Web Service zu starten führen sie den nachstehenden Befehl aus.
```bash
python3.8 -m pandemie.deployment
```

### Schnellstart AWS
Unser Webservice ist auf AWS deployed und kann mit dem nachstehenden Befehl angesprochen werden.

Die Domain lautet: `ec2-52-91-60-156.compute-1.amazonaws.com`

Der Port ist weiterhin `50123`
```bash
./ic20_linx -u http://ec2-52-91-60-156.compute-1.amazonaws.com:50123
```