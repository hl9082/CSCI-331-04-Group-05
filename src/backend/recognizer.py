'''
Author: Huy Le (hl9082)
Co-author: Will Stott, Zoe Shearer, Josh Elliot
Purpose:
  This module contains the SpeechRecognizer class, which handles the
  conversion of spoken language into text. It captures audio from the
  microphone and uses a speech recognition service to transcribe it in
  real-time.
Importance:
  This module is one of the two core input methods for the application. It
  enables communication from hearing individuals to the user of the glasses
  by converting their speech into text for display.
'''

import speech_recognition as sr
from typing import Callable
import threading

class SpeechRecognizer:
    """
    Handles capturing audio from the microphone and converting it to text.
    """

    def __init__(self):
        """
        Initializes the SpeechRecognizer.
        """
        self.recognizer: sr.Recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        print("Speech Recognizer initialized.")
        self._calibrate_microphone()

    def _calibrate_microphone(self):
        """
        Calibrates the microphone for ambient noise to improve recognition accuracy.
        """
        print("Calibrating microphone for ambient noise... Please be quiet.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Calibration complete.")


    def start_recognition(self, on_recognition: Callable[[str], None], stop_event: threading.Event):
        """
        Starts listening for speech and processing it.

        Args:
            on_recognition (Callable[[str], None]): A callback function to be called
                when speech is recognized. It takes the recognized text as an argument.
            stop_event (threading.Event): An event to signal when to stop the loop.
        """
        print("Starting speech recognition service...")
        on_recognition("Speech service is active...")
        with self.microphone as source:

            while not stop_event.is_set():
                print("Listening for speech...")
                try:

                    # Use a timeout to prevent listen() from blocking indefinitely
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=5)
                    # The `recognize_google` function is used here to send the captured
                    # audio to Google's Web Speech API for transcription. 
                    # Use getattr to dynamically access the method. 
                    text = getattr(self.recognizer, "recognize_google")(audio)
                    print(f"Speech Detected: {text}")

                    on_recognition(f"Speech: {text}")
                except sr.UnknownValueError:
                    # This error means the recognizer could not understand the audio.
                    # We can safely ignore it and just continue listening.
                    pass
                except sr.WaitTimeoutError:
                    # No speech was detected within the timeout. This is normal.
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
        print("Speech recognition service stopped.")