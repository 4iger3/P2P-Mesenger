import queue

from core.controller import Controller
from core.state import AppState
from network.event_loop import create_network_client
from ui.main_window import MainWindow


def main() -> None:
    ui_event_queue: queue.Queue = queue.Queue()
    core_to_network_queue: queue.Queue = queue.Queue()
    network_event_queue: queue.Queue = queue.Queue()
    ui_update_queue: queue.Queue = queue.Queue()

    state = AppState()
    controller = Controller(
        ui_event_queue,
        core_to_network_queue,
        network_event_queue,
        ui_update_queue,
        state,
    )

    create_network_client(core_to_network_queue, network_event_queue)
    main_window = MainWindow(ui_event_queue, ui_update_queue)

    def poll() -> None:
        controller.process_queues()
        main_window.root.after(100, poll)

    poll()
    main_window.run()


if __name__ == "__main__":
    main()
