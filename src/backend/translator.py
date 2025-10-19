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
import torch
from torchvision import transforms
from PIL import Image
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


        # --- Model and Preprocessing Setup ---
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Define the same transformations used during model training
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        # This should map the model's output indices to class names
        # Example: 0 -> 'Hello', 1 -> 'Thank You', etc.
        self.class_labels = ['Hello', 'Thank You', 'I Love You', 'Yes', 'No'] # Replace with your actual labels

        self.model = self.load_model(model_path)
        print("ASL Translator initialized.")


    def load_model(self, model_path: str):
        """
        Loads the machine learning model for sign recognition.
        
        Args:
            model_path (str): Path to the model file.
        
        Returns:
            A loaded model object.
        """

        try:
            print(f"Loading model from {model_path}...")
            model = torch.load(model_path, map_location=self.device)
            model.eval()  # Set the model to evaluation mode
            print("Model loaded successfully.")
            return model
        except FileNotFoundError:
            print(f"Error: Model file not found at {model_path}.")
            print("ASL translation will not be available.")
            return None
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
            return None


    def _preprocess_frame(self, frame) -> torch.Tensor:
        """Converts a cv2 frame to a model-ready tensor."""
        # Convert the BGR frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        # Apply transformations and add a batch dimension
        tensor = self.transform(pil_image).unsqueeze(0)
        return tensor.to(self.device)


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

        if self.model is None:

            print("Warning: Model is not loaded. Only the camera feed will be shown.")
            on_translation("Error: Model not loaded.")

            # We don't return, so the camera feed can still start.
            
        if not self.camera.isOpened():
            self.camera.open(0) # Re-open camera if it was released

        while not stop_event.is_set():

            ret, frame = self.camera.read()
            if not ret:
                print("Failed to grab frame, exiting.")
                break


            # --- Real-time Inference (only if model is loaded) ---
            if self.model is not None:
                with torch.no_grad(): # Disable gradient calculation for efficiency
                    # 1. Preprocess the frame
                    input_tensor = self._preprocess_frame(frame)
                    # 2. Get model prediction
                    output = self.model(input_tensor)
                    # 3. Convert output to a label
                    _, predicted_idx = torch.max(output, 1)
                    predicted_label = self.class_labels[predicted_idx.item()]


                    # 4. Update the translation
                    print(f"ASL Detected: {predicted_label}")
                    on_translation(f"ASL: {predicted_label}")

            # Display the resulting frame
            cv2.imshow('ASL Translation Feed', frame)


            # Check for 'q' key press to quit the loop and close the window

            if cv2.waitKey(1) & 0xFF == ord('q') or stop_event.is_set():
                break

        # Release the camera and destroy all windows
        self.camera.release()
        cv2.destroyAllWindows()
        print("ASL translation service stopped.")