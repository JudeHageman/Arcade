# py_client/main.py
import sys
import pygame
from arcade_app import ArcadeApp

def main():
    """
    The main entry point of the Resonance Arcade application.
    Initializes the app and starts the main game loop.
    """
    # 1. Initialize the Arcade App
    # This will set up the 1280x720 screen and load all screens.
    app = ArcadeApp()

    try:
        # 2. Start the application loop
        app.run()
    except Exception as e:
        # 3. Basic error handling to catch crashes during runtime
        print(f"⚠️ An unexpected error occurred: {e}")
    finally:
        # 4. Ensure pygame shuts down cleanly even if there's an error
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()