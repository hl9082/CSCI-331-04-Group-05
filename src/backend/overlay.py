'''
Author: Huy Le (hl9082)
Co-author: Will Stott, Zoe Shearer, Josh Elliot
Purpose:
  This module defines the DisplayManager class, which is responsible for
  managing the visual output on the smart glasses' display. It provides a
  clean interface for rendering subtitles and other visual information.
Importance:
  This module is the primary output channel for the user. Its proper
  functioning is essential for displaying the translated text from both ASL
  and speech, making the entire system useful. The implementation will be
  highly dependent on the specific hardware SDK of the glasses.
'''

class DisplayManager:
    """
    Manages the display on the glasses.

    This class is responsible for rendering text (subtitles) or animations
    (ASL signs) onto the display overlay. The actual implementation will be
    highly dependent on the specific hardware and SDK of the smart glasses.
    """

    def __init__(self):
        """
        Initializes the DisplayManager.
        """
        # Here you would initialize the connection to the glasses' display SDK.
        print("Display Manager initialized.")

    def update_display(self, text: str):
        """
        Updates the display with the provided text.
        
        Attributes:
          test (str) : The text to display on the screen.
        """
        # In a real application, this method would draw the text on the screen.
        print(f"DISPLAY: {text}")