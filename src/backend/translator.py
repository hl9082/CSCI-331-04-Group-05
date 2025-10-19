'''
Author: Huy Le (hl9082)
Co-author: Will Stott, Zoe Shearer, Josh Elliot
Purpose:
  This module defines the ASLTranslator class, which is responsible for
  translating American Sign Language (ASL) gestures into English text. It
  uses the device's camera to capture video and a machine learning model to
  interpret the signs.
Importance:
  This is a key feature of the project and one of the two primary input
  methods. It allows the user to understand signed language by reading it as
  subtitles, directly bridging a major communication gap.
'''

import cv2
import time
from typing import Callable
import threading

class ASLTranslator:
    """
    Handles the real-time translation of ASL signs from a video feed.
    
    This class will manage capturing frames from the camera, processing them,
    and using a machine learning model to predict the signed word or phrase.
    """

    def __init__(self, model_path: str = "models/asl_model.pth"):
        """
        Initializes the ASLTranslator.

        Args:
            model_path (str): The path to the pre-trained ASL recognition model.
        """
        self.camera = cv2.VideoCapture(0)  # 0 is the default camera
        if not self.camera.isOpened():
            raise IOError("Cannot open webcam")
        
        # self.model = self.load_model(model_path) # Placeholder for loading the ML model
        print("ASL Translator initialized.")

    def load_model(self, model_path: str):
        """
        Loads the machine learning model for sign recognition.
        
        Args:
            model_path (str): Path to the model file.
        
        Returns:
            A loaded model object.
        """
        # In a real implementation, you would load a PyTorch, TensorFlow, or ONNX model here.
        print(f"Loading model from {model_path}...")
        return "dummy_model"

    def start_translation(self, on_translation: Callable[[str], None], stop_event: threading.Event):
        """
        Starts the video capture and translation loop.

        Args:
            on_translation (Callable[[str], None]): A callback function to be called
                when a translation is available. It takes the translated text as an argument.
            stop_event (threading.Event): An event to signal when to stop the loop.
        """

        print("Starting ASL translation service... (Press 'q' in the video window to stop)")
        on_translation("ASL service is active...")
        last_translation_time = time.time()

        while True:
            if not self.camera.isOpened():
                self.camera.open(0) # Re-open camera if it was released

        while not stop_event.is_set():

            ret, frame = self.camera.read()
            if not ret:
                print("Failed to grab frame, exiting.")
                break

            # Display the resulting frame
            cv2.imshow('ASL Translation Feed', frame)

            # In a real implementation, you would preprocess the frame and feed it to your model here.

            # Simulate a translation every 5 seconds
            if time.time() - last_translation_time > 5:
                translated_text = "Hello" # Placeholder for model prediction
                print(f"ASL Detected: {translated_text}")
                on_translation(f"ASL: {translated_text}")
                last_translation_time = time.time()

            # Check for 'q' key press to quit the loop and close the window
            if cv2.waitKey(1) & 0xFF == ord('q') or stop_event.is_set():
                break

        # Release the camera and destroy all windows
        self.camera.release()
        cv2.destroyAllWindows()
        print("ASL translation service stopped.")