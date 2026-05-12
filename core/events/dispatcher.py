"""
Event dispatcher implementation (Subject in Observer pattern).

Manages observer registration and event notification with thread-safe dispatching.
"""

import threading
from typing import List

from .events import Event
from .observer import Observer


class EventDispatcher:
    """
    Thread-safe event dispatcher for broadcasting events to multiple observers.
    
    Maintains a registry of observers and notifies all of them when an event
    occurs. Uses threading.Lock to ensure thread-safe operations.
    Protects against re-entrant notify() calls to prevent infinite event loops.
    """

    def __init__(self) -> None:
        """Initialize the dispatcher with an empty observer list and a lock."""
        self._observers: List[Observer] = []
        self._lock = threading.Lock()
        self._notifying = False

    def attach(self, observer: Observer) -> None:
        """
        Register an observer for event notifications.
        
        If the observer is already registered, it will not be added again.
        
        Args:
            observer (Observer): The observer to attach.
        """
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Unregister an observer from event notifications.
        
        Args:
            observer (Observer): The observer to detach.
        """
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def notify(self, event: Event) -> None:
        """
        Dispatch an event to all attached observers.
        
        Observers are notified in the order they were attached.
        This operation is thread-safe and protects against re-entrant calls.
        If notify() is already in progress, the new event call is skipped
        to prevent infinite loops where observers re-emit events.
        
        Args:
            event (Event): The event to dispatch.
        """
        with self._lock:
            # Guard against re-entrant notify() calls
            if self._notifying:
                return
            
            self._notifying = True
            # Create a shallow copy of observers list to avoid issues
            # if observers are added/removed during iteration
            observers_copy = self._observers.copy()

        try:
            for observer in observers_copy:
                observer.update(event)
        finally:
            with self._lock:
                self._notifying = False

    def observer_count(self) -> int:
        """
        Get the number of currently attached observers.
        
        Returns:
            int: The count of attached observers.
        """
        with self._lock:
            return len(self._observers)
