from enum import Enum, auto
from typing import Any, Dict
from threading import Lock

class DatabaseEvent(Enum):
    """Events that can occur in the password database"""
    ENTRY_ADDED = auto()
    ENTRY_MODIFIED = auto()
    ENTRY_DELETED = auto()
    DATABASE_IMPORTED = auto()
    DATABASE_ENCRYPTED = auto()

class DatabaseObserver:
    """Interface for database observers"""
    def update(self, event: DatabaseEvent, data: Dict[str, Any]) -> None:
        pass

class DatabaseSubject:
    """Base class for database subjects"""
    def __init__(self):
        self._observers = []
        self._lock = Lock()

    def attach(self, observer: DatabaseObserver) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def detach(self, observer: DatabaseObserver) -> None:
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def notify(self, event: DatabaseEvent, data: Dict[str, Any] = None) -> None:
        with self._lock:
            observers = self._observers.copy()
        for observer in observers:
            observer.update(event, data)