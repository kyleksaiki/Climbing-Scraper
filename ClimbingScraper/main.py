import logging
from Controller.main_controller import Controller
from View.app_gui import View

def main() -> None:
    """
    Initialize and run the climbing lookup application.
    Sets up logging, constructs the View and Controller,
    then starts the main event loop.
    """
    # Configure root logger for simple console output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )
    logging.info("Application starting")

    # Create the GUI and controller
    view = View()
    controller = Controller(view)

    try:
        # Enter the main loop (blocks until window is closed)
        controller.run()
    except Exception as e:
        # Log any unexpected errors
        logging.exception("Unhandled exception in main loop")
    finally:
        logging.info("Application exiting")

if __name__ == "__main__":
    # Launch the application
    main()
