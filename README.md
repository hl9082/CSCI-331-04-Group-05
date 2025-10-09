# CSCI-331-04-Group-05
Developers: Huy Le, Will Stott, Josh Elliot, Zoe Shearer

## Project: AI-Powered ASL Translation Glasses

This project aims to develop an AI agent integrated into glasses to bridge the communication gap between the deaf/hard-of-hearing community and the hearing community. It provides real-time translation services for both American Sign Language (ASL) and spoken English.

### Core Features

1.  **ASL to English:** Real-time translation of ASL gestures into English subtitles.
2.  **Speech to English:** Real-time conversion of spoken words into English subtitles.

### Technology Stack & Methods

*   **Python**: The core programming language for the application.
*   **OpenCV**: Used for capturing and processing video frames from the camera for ASL recognition.
*   **SpeechRecognition**: Manages microphone input and uses Google's Web Speech API to convert spoken words into text.
*   **Threading**: A key method used to run the ASL translation and speech recognition services concurrently, ensuring a responsive user experience.

### Getting Started

#### Prerequisites

*   Python 3.7+
*   A connected webcam
*   A functional microphone

#### Important Commands

1.  **Install Dependencies:**
    Before running the application, install the necessary packages from `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    To start the main application, run the `main.py` script. This will initialize all services.
    ```bash
    python main.py
    ```
    To stop the application, press `Ctrl+C` in the terminal where it is running.
