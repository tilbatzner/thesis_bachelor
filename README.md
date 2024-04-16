# Code für die Bachelorarbeit von Til Batzner mit dem Thema "Filmempfehlungen mit ChatGPT im Vergleich zu herkömmlichen Methoden: Eine empirische Untersuchung"


## Über dieses Repository
Dieses Repository enthält den Quellcode und die dazugehörigen Daten für die Bachelorarbeit von Til Batzner, die darauf abzielt, drei unterschiedliche Filmempfehlungssysteme empirisch zu vergleichen. Die Befragten mussten in der Umfrage sechs favorisierte Filme angeben und erhielten von jedem System vier Filmvorschläge zur Bewertung zurück. Für die Analyse wurde das MovieLens-Dataset "ml-latest-small" aus dem Jahr 2018 verwendet, verfügbar unter '/Empfehlungssysteme_Cloud_Flask/ml-latest-small/' oder auf der Seite von GroupLens-Research unter https://grouplens.org/datasets/movielens/latest/. 


## Empfehlungssysteme

Sowohl das kollaborative als auch das hybride Empfehlungssystem sind für eine erhöhte Performance und API-Zugänglichkeit auf der Google Cloud App Engine mit dem Framework Flask implementiert. Das LLM-basierte System, in diesem Fall ChatGPT, benötigt zwangsläufig die Kommunikation mit dem externen System von OpenAI.

- Kollaboratives Empfehlungssystem: Das System nutzt eine angepasste Matrixfaktorisierung für die Erstellung personalisierter Empfehlungen, welches im Verzeichnis '/Empfehlungssysteme_Cloud_Flask' implementiert wurde.

- Hybrides Empfehlungssystem: Das hybride System verbindet einen inhaltbasierten und einen kollabortiven Filteransatz, um personalisierte Filmempfehlungen auf Basis der Nutzerinteressen zu erstellen. Die inhaltsbasierte Filterung nutzt Tags und Genres, die von Nutzern bereitgestellt werden. Diese werden zusammen mit dem kollaborativen Element der Nutzerbewertungen gewichtet, um eine kombinierte Matrix zu erstellen. Diese Relationsmatrix wurde im Vorhinein in eine .pkl Datei verarbeitet und lokal eingebunden, um hohe Rechenanforderungen effizient zu bewältigen. Da GitHub nur Uploads bis 25 MB zulässt, muss diese über die angegeben URL heruntergeladen werden. Diese Relationsmatrix wird im Code verwendet, um auf Basis der sechs Lieblingsfilme des Nutzers vier Filmvorschläge zu erzeugen.

- ChatGPT-Empfehlungssystem: Die Feinabstimmung und Datenverarbeitung für die Verwendung von ChatGPT als Empfehlungsmodell für Filme ist unter '/ChatGPT-Finetuning' zu finden.  Dieses Verzeichnis enthält auch die automatisierte Validierung der Daten fürs Finetuning und die randomisierte Aufteilung der in Trainings- und Testdaten. Die Integration der Modellanfragen in die Webanwendung erfolgt über '/ChatGPT-Anfrage/request.php', welches die Rückführung der sprachlichen Ergebnisse in movieIds beinhaltet. 


## Mitwirken

Interessierte, die zur Verbesserung des Codes beitragen möchten, können Pull Requests einreichen oder Issues im Repository erstellen, um Vorschläge oder Fehler zu melden.


## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Der Code darf für wissenschaftliche Zwecke mit einer Referenzierung weiterverwendet werden. Bei Unklarheiten wende dich bitte an den angegebenen Kontakt.


## Kontakt

Fragen, Kommentare oder Vorschläge können per E-Mail an info@til-batzner.de oder durch Erstellen eines Issues im GitHub-Repository übermittelt werden.


## Danksagungen

Besonderer Dank geht an meinen Betreuer Prof. Dr. Rolf Schillinger und alle, die bei der Erstellung dieser Arbeit unterstützt haben.
