# Authors: Huy Le (hl9082)
# Co-authors: Will Stott, Zoe Shearer, Josh Elliot
# Purpose:
#   This script serves as the main entry point for the AI-Powered ASL
#   Translation Glasses application. It is responsible for initializing all core
#   components (ASL translator, speech recognizer, display manager) and
#   orchestrating their concurrent operation in separate threads.
# Importance:
#   This file is critical as it ties all the modules together. Without it, the
#   individual components cannot run as a cohesive application. It manages the
#   main application loop and handles the startup and shutdown of services.


# For pausing the main thread and managing time-related tasks.
import time
# For running concurrent operations (ASL and speech services).
import threading
# Correctly import the classes from the local modules.
from translator import ASLTranslator # for ASL translation
from recognizer import SpeechRecognizer #for speech recognition
from overlay import DisplayManager # for result display

def main():
    """
    Main function to initialize and run the AI agent for the glasses.
    """
    print("Initializing AI-Powered ASL Translation Glasses...")

    # --- Initialization ---
    # Initialize the core components of the application.
    display_manager = DisplayManager()
    asl_translator = ASLTranslator()
    speech_recognizer = SpeechRecognizer()

    print("Initialization complete. Starting services...")

    # --- Start Services in Separate Threads ---
    # Each core function (ASL recognition, speech recognition) will run in its
    # own thread to operate concurrently.
    asl_thread = threading.Thread(
        target=asl_translator.start_translation, 
        args=(display_manager.update_display,)
    )
    speech_thread = threading.Thread(
        target=speech_recognizer.start_recognition, 
        args=(display_manager.update_display,)
    )

    # Set threads as daemon threads. This ensures they will exit automatically
    # when the main program shuts down.
    asl_thread.daemon = True
    speech_thread.daemon = True

    asl_thread.start()
    speech_thread.start()

    print("Services running. The application is now active.")
    print("Press Ctrl+C to exit.")

    # Keep the main thread alive and wait for a keyboard interrupt (Ctrl+C).
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down application...")

if __name__ == "__main__":
    main()