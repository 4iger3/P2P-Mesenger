"""
Observer interface for event-driven architecture.

Implements the Observer pattern for decoupled communication between
components in the P2P Messenger application.
"""

from abc import ABC, abstractmethod

from .events import Event


class Observer(ABC):
    """
    Abstract base class for event observers.
    
    Components that need to react to events should extend this class
    and implement the update() method.
    """

    @abstractmethod
    def update(self, event: Event) -> None:
        """
        Called when an observed event is dispatched.
        
        Args:
            event (Event): The event that occurred.
        """
        pass
