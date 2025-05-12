from PySide6.QtCore import QObject, Signal, Slot, Property, QStringListModel
import datetime

class Logger(QObject):
    logAdded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logs = QStringListModel()

    @Slot(str)
    def add_log(self, message: str):
        # Zeitstempel hinzufügen
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print("logs")
        print(f"[LOG] {log_message}")  # Optionale Konsolenausgabe für Debugging

        # Modell aktualisieren
        current_logs = self._logs.stringList()  # Bestehende Logs holen
        current_logs.append(log_message)  # Neue Log-Nachricht hinzufügen
        self._logs.setStringList(current_logs)  # Modell aktualisieren

        # Emit das Signal
        self.logAdded.emit(log_message)  # Benachrichtigen, dass ein neuer Log hinzugefügt wurde

    def get_all_logs(self):
        return self._logs  # Gibt alle gespeicherten Logs zurück

    # Property für QML
    @Property('QStringList', notify=logAdded)
    def logs(self):
       
        
        return self._logs.stringList()  # Gibt die Logs als Liste zurück
