from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class PasswordEntryMemento:
    """Memento class to store password entry state"""
    state: Dict[str, Any]
    timestamp: str
    
    @property
    def description(self) -> str:
        return f"Backup from {self.timestamp} - {self.state['website']}"

class PasswordEntryCaretaker:
    """Manages and stores mementos"""
    def __init__(self):
        self._mementos = []
    
    def add_memento(self, memento: PasswordEntryMemento) -> None:
        self._mementos.append(memento)
        if len(self._mementos) > 10:  # Keep only last 10 states
            self._mementos.pop(0)
    
    def get_memento(self, index: int) -> PasswordEntryMemento:
        return self._mementos[index]
    
    def get_all_mementos(self) -> list:
        return self._mementos