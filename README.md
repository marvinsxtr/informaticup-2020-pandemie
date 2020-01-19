# README
Die komplette Dokumentation finden Sie hier: [documentation](documents/documentation.md).

Alle im Vorfeld zu installierenden Abhängigkeiten finden Sie hier: [requirements](requirements.txt).

### Schnellstart für Debugging-Zwecke

**Die Nachstehenden Schnellstarts sind im Projektordner auszuführen!**<br>
Um den Tester für das `ic20_linux` Programm auszuführen, kann auf dem Projektordner folgender Befehl aufgerufen werden.
```bash
python3.8 -m pandemie.tester
```
Für die schnelle Ausführung des Programms sind bereits Standard-Parameter gesetzt. Diese können per aufgefordeter
Terminaleingabe auch geändert werden.
<br><br>
Um die Visualisierung zu starten führen Sie den nachstehenden Befehl aus.
```bash
python3.8 -m pandemie.visualization
```
Öffnen Sie danach ihren Webbrowser mit der URL: `localhost:8050`

Um den reinen Web Service zu starten führen Sie den nachstehenden Befehl aus.
```bash
python3.8 -m pandemie.deployment
```

### Schnellstart AWS
Unser Webservice ist auf AWS deployed und kann mit dem nachstehenden Befehl angesprochen werden.

Die Domain lautet: `ec2-52-91-60-156.compute-1.amazonaws.com`

Der Port ist weiterhin `50123`
```bash
./ic20_linux -u http://ec2-52-91-60-156.compute-1.amazonaws.com:50123
```

### Dokumentation
Wenn man die Dokumentation als HTML Dokument lesen möchte, das könnte unter anderem zum Ausdrucken
hilfreich sein, da sonst die Formatierung eventuell zerstört wird, kann man `grip` wie folgend nutzen.
```bash
pip install grip
cd documents
grip documentation.md --export documentation.html
```
`grip` bietet auch die Möglichkeit, das Dokument komfortable direkt im Browser zu betrachten.
```bash
grip documentation.md
```