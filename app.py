"""
Main application entry point for P2P Messenger.

Initializes the event dispatcher and wires all components (UI, network, core)
through the Observer pattern for event-driven communication.
"""

from core.events.dispatcher import EventDispatcher
from core.controller import Controller
from core.state import AppState
from network.event_loop import create_network_client
from ui.main_window import MainWindow


def main() -> None:
    """
    Initialize and run the P2P Messenger application.
    
    Sets up the event dispatcher and attaches all components:
    - AppState: Maintains application state based on events
    - Controller: Routes and validates user actions
    - WebSocketClient: Handles network communication
    - MainWindow: Provides the user interface
    """
    # Create the central event dispatcher
    dispatcher = EventDispatcher()

    # Create application state
    state = AppState()
    
    # Create and attach the state observer
    dispatcher.attach(state)

    # Create and start the network client
    network_client = create_network_client(dispatcher)

    # Create and attach the controller
    controller = Controller(dispatcher, state, network_client)

    # Create and start the main window (which attaches to dispatcher)
    main_window = MainWindow(dispatcher)

    # Run the GUI
    main_window.run()


if __name__ == "__main__":
    main()
