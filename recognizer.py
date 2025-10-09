import speech_recognition as sr
from typing import Callable

class SpeechRecognizer:
    """
    Handles capturing audio from the microphone and converting it to text.
    """

    def __init__(self):
        """
        Initializes the SpeechRecognizer.
        """
        self.recognizer = sr.Recognizer()
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

    def start_recognition(self, on_recognition: Callable[[str], None]):
        """
        Starts listening for speech and processing it.

        Args:
            on_recognition (Callable[[str], None]): A callback function to be called
                when speech is recognized. It takes the recognized text as an argument.
        """
        print("Starting speech recognition service...")
        with self.microphone as source:
            while True:
                print("Listening for speech...")
                try:
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio)
                    print(f"Speech Detected: {text}")
                    # on_recognition(f"Speech: {text}")
                except sr.UnknownValueError:
                    # This error means the recognizer could not understand the audio.
                    # We can safely ignore it and just continue listening.
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")