"""
Theme manager for the P2P Messenger application.

Centralized theme management with observer pattern integration.
"""

from typing import Dict, List, Callable, Any
from .themes import Theme, AVAILABLE_THEMES
from .config import ThemeConfig
from core.events.observer import Observer
from core.events.events import Event, THEME_CHANGED, ACCENT_COLOR_CHANGED


class ThemeManager(Observer):
    """
    Central theme manager that handles theme switching and notifies observers.
    """

    def __init__(self, dispatcher) -> None:
        self.dispatcher = dispatcher
        self.config = ThemeConfig()
        self.current_theme = self.config.get_current_theme()
        self._observers: List[Callable[[Theme], None]] = []

        # Attach to dispatcher to receive theme change requests
        dispatcher.attach(self)

    def get_current_theme(self) -> Theme:
        """Get the current active theme."""
        return self.current_theme

    def get_available_themes(self) -> Dict[str, Theme]:
        """Get all available themes."""
        return AVAILABLE_THEMES

    def set_theme(self, theme_name: str) -> None:
        """Set the active theme."""
        if theme_name in AVAILABLE_THEMES:
            self.config.set_theme_name(theme_name)
            self.current_theme = self.config.get_current_theme()
            self._notify_theme_changed()

            # Emit event
            event = Event(THEME_CHANGED, {"theme": theme_name})
            self.dispatcher.notify(event)

    def set_accent_color(self, color: str) -> None:
        """Set the accent color."""
        self.config.set_accent_color(color)
        self.current_theme = self.config.get_current_theme()
        self._notify_theme_changed()

        # Emit event
        event = Event(ACCENT_COLOR_CHANGED, {"color": color})
        self.dispatcher.notify(event)

    def set_mode(self, mode: str) -> None:
        """Set the color mode (dark/light)."""
        self.config.set_mode(mode)
        self.current_theme = self.config.get_current_theme()
        self._notify_theme_changed()

        # Emit theme changed event
        event = Event(THEME_CHANGED, {"mode": mode})
        self.dispatcher.notify(event)

    def get_color(self, key: str) -> str:
        """Get a color value from the current theme."""
        return self.current_theme.get_color(key)

    def subscribe_to_theme_changes(self, callback: Callable[[Theme], None]) -> None:
        """Subscribe to theme change notifications."""
        self._observers.append(callback)

    def unsubscribe_from_theme_changes(self, callback: Callable[[Theme], None]) -> None:
        """Unsubscribe from theme change notifications."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_theme_changed(self) -> None:
        """Notify all subscribers of theme changes."""
        for observer in self._observers:
            try:
                observer(self.current_theme)
            except Exception as e:
                print(f"Theme observer error: {e}")

    def update(self, event: Event) -> None:
        """
        Handle events from the dispatcher.

        Currently handles theme change requests from UI.
        """
        # Theme change events are handled directly by the UI components
        # This method can be extended for future theme-related events
        pass

    def apply_theme_to_component(self, component: Any, theme: Theme) -> None:
        """
        Apply theme colors to a UI component.

        This is a helper method that components can use to apply themes.
        """
        # This method can be extended to provide common theme application logic
        pass