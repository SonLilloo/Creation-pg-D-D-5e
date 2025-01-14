Per compilare il programma digitare a terminale il comando "uv run streamlit run project.py"

OBIETTIVO:
Questo progetto permette di creare le basi della scheda di un personaggio in D&D 5 edizione.
Quando si inizia a dare forma al proprio personaggio, la principale difficoltà è confrontare il manuale di D&D, un libro o un file digitale da più di 300 pagine. L'obiettivo di questo progetto è di minimizzare il confronto del manuale e automatizzare il calcolo delle statistiche. In questo modo l'utente può prestare maggiore attenzione alla costruzione della "biuld" del personaggio, a discapito di una conoscenza generale di base delle regole.

STRUTTURA PROGRAMMA:
Il codice del programma presenta come prima parte una serie di funzioni che gestiscono le richieste alla rete e le decisioni dell'utente. La seconda parte, costituita dalla funzione main(), coordina le funzioni tra loro e cura la visulizzazione delle informazioni e l'interfaccia con l'utente.
Sono state implementate strutture dati tipiche della libreria "urllib" per comunicare con la struttura API del sito www.dnd5eapi.co e la libreria "streamlit" per la visulizzazione e la gestione delle scelte dell'utente.
La parte finale del codice ci concentra sull'analisi di un file csv.

MIGLIORAMENTI:
Come scritto prima, questo programma getta la basi della creazione di un personaggio, infatti tralascia completamente aspetti come scelta dell'allineamento e del backgruond del personaggio, armi, armature, incantesimi... E' stata fatta questa scelta perchè si è preferito approfondire altre tipologie di gestione di dati, al posto di utilizzare gli stessi strumenti.
I dati contenuti nel file "pg_data.csv" sono stati generati casualmente tramite IA. Sarebbe interessante riuscire a trovare dei dati reali che potessano fornire all'utente dei consigli effettivamente validi.
Un altro miglioramento sarebbe quello di dare la possibilità all'utente di creare più personaggi alla volta; senza la rindondanza di rieseguire il programma per avere dei punteggi caratteristica diversi.