'''
Author: Huy Le (hl9082)
Co-author: Will Stott, Zoe Shearer, Josh Elliot
Purpose:
  This module defines the ASLTranslator class, which is responsible for
  translating American Sign Language (ASL) gestures into English text. It
  uses a machine learning model to interpret sign images.
Importance:
  This is a key feature of the project and one of the two primary input
  methods.
'''

import torch
from torchvision import models, transforms
from PIL import Image
import io
import torch.nn.functional as F


class ASLTranslator:
    """
    Handles the translation of ASL signs from an image file.
    
    This class will manage processing an image and using a machine learning 
    model to predict the signed word or phrase.
    """

    def __init__(self, model_path: str = "models/asl_model.pth"):
        """
        Initializes the ASLTranslator.

        Args:
            model_path (str): The path to the pre-trained ASL recognition model.
        """
        # --- Model and Preprocessing Setup ---
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Define the same transformations used during model training
        self.transform = transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

        # This should map the model's output indices to class names
        self.class_labels = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'space', 'nothing'
        ]  # Replace with your actual labels

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
            # The model is MobileNetV2, we need to initialize it first
            model = models.mobilenet_v2(weights=None)
            
            # Adjust the classifier for our number of classes
            num_classes = len(self.class_labels)
            model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)

            # Load the saved state dictionary
            state_dict = torch.load(model_path, map_location=self.device)
            model.load_state_dict(state_dict)
            
            model.to(self.device)
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

    def translate_image(self, image_bytes: bytes):
        """
        Translates an ASL sign from an image.

        Args:
            image_bytes (bytes): The bytes of the image to be translated.

        Returns:
            A tuple containing the predicted label and the confidence score.
        """
        if self.model is None:
            raise Exception("Model is not loaded.")

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_tensor = self.transform(image).unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(img_tensor)
                probs = F.softmax(outputs, dim=1)
                conf, pred = torch.max(probs, 1)
                label = self.class_labels[pred.item()]
            
            return label, float(conf.item())
        except Exception as e:
            print(f"An error occurred during translation: {e}")
            return None, None