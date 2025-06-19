import os
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal, Property, QUrl
from PySide6.QtQml import QmlElement
from .logger import Logger

# Stellen Sie sicher, dass das Backend-Verzeichnis im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importieren Sie das Support-System
from .support_system import SupportSystem

# QML-Element-Registrierung
QML_IMPORT_NAME = "com.rzgcs.support"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class SupportController(QObject):
    """
    Controller-Klasse für die Integration des Support-Systems mit der QML-Oberfläche.
    """
    # Signale, die in QML verwendet werden
    supportTicketSubmittedChanged = Signal(bool, str)
    diagnosisCompletedChanged = Signal(dict)
    knowledgeBaseArticleLoadedChanged = Signal(str, str)
    errorOccurredChanged = Signal(str)
    
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self._logger = logger
        self._support_system = SupportSystem(logger=logger)
        
        # Verbinde Support-System-Signale mit Controller-Signalen
        self._support_system.supportTicketSubmitted.connect(self.supportTicketSubmittedChanged)
        self._support_system.diagnosisCompleted.connect(self.diagnosisCompletedChanged)
        self._support_system.knowledgeBaseArticleLoaded.connect(self.knowledgeBaseArticleLoadedChanged)
        self._support_system.errorOccurred.connect(self.errorOccurredChanged)
        
        if self._logger:
            self._logger.addLog("[INFO] Support-Controller initialisiert")
    
    @Slot(str, str, str, str, str, result=bool)
    def submit_support_ticket(self, subject, description, email, category, priority):
        """
        Reicht ein Support-Ticket ein und gibt einen Boolean zurück, ob erfolgreich
        
        Args:
            subject (str): Betreff des Tickets
            description (str): Beschreibung des Problems
            email (str): E-Mail-Adresse des Benutzers
            category (str): Kategorie des Problems
            priority (str): Priorität des Tickets
            
        Returns:
            bool: True, wenn erfolgreich, sonst False
        """
        if self._logger:
            self._logger.addLog(f"[INFO] Support-Ticket wird eingereicht: {subject}")
        
        # Wandle deutsche Prioritäten in englische um für das Backend
        priority_mapping = {
            "Niedrig": "Low",
            "Mittel": "Medium",
            "Hoch": "High",
            "Kritisch": "Critical"
        }
        
        # Wandle deutsche Kategorien in englische um für das Backend
        category_mapping = {
            "Hardware": "Hardware",
            "Software": "Software",
            "Lizenz": "License",
            "Verbindungsprobleme": "Connection",
            "Sonstiges": "Other"
        }
        
        eng_priority = priority_mapping.get(priority, "Medium")
        eng_category = category_mapping.get(category, "Other")
        
        return self._support_system.submit_support_ticket(
            subject, description, email, eng_category, eng_priority
        )
    
    @Slot(result=str)
    def create_support_package(self):
        """
        Erstellt ein Support-Paket mit Diagnose und Logs
        
        Returns:
            str: Pfad zum erstellten Support-Paket
        """
        if self._logger:
            self._logger.addLog("[INFO] Support-Paket wird erstellt")
        return self._support_system.create_support_package()
    
    @Slot()
    def run_system_diagnosis(self):
        """
        Führt eine Systemdiagnose durch
        
        Nach Abschluss wird das diagnosisCompletedChanged-Signal emittiert
        """
        if self._logger:
            self._logger.addLog("[INFO] Systemdiagnose wird gestartet")
        self._support_system.run_system_diagnosis()
    
    @Slot(str, result=str)
    def get_knowledge_base_article(self, article_id):
        """
        Lädt einen Artikel aus der Wissensdatenbank
        
        Args:
            article_id: ID des Artikels
            
        Returns:
            str: Inhalt des Artikels als Markdown-Text
        """
        if self._logger:
            self._logger.addLog(f"[INFO] Wissensdatenbank-Artikel wird geladen: {article_id}")
        return self._support_system.get_knowledge_base_article(article_id)
    
    @Slot(result='QVariantList')
    def get_knowledge_base_categories(self):
        """
        Gibt die verfügbaren Kategorien der Wissensdatenbank zurück
        
        Returns:
            list: Liste der Kategorien mit IDs und Namen
        """
        if self._logger:
            self._logger.addLog("[INFO] Wissensdatenbank-Kategorien werden abgerufen")
        return self._support_system.get_knowledge_base_categories()
    
    @Slot(str, result='QVariantList')
    def get_articles_by_category(self, category_id):
        """
        Gibt Artikel einer bestimmten Kategorie zurück
        
        Args:
            category_id: ID der Kategorie
            
        Returns:
            list: Liste der Artikel in dieser Kategorie
        """
        if self._logger:
            self._logger.addLog(f"[INFO] Artikel für Kategorie werden abgerufen: {category_id}")
        return self._support_system.get_articles_by_category(category_id)
