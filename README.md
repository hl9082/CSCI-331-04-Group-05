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


1.  **Install Backend Dependencies:**
    Install the necessary Python packages.
    ```bash
    pip install -r requirements.txt
    ```


2.  **Install Frontend Dependencies:**
    Navigate to the frontend directory and install its dependencies (assuming a standard Node.js setup).
    ```bash
    cd src/frontend
    npm install
    ```

3.  **Run the Backend Server:**
    From the project's root directory, run the `main.py` script. This will initialize the backend services.
    ```bash
    cd ../.. 
    ```bash
    python main.py
    ```


4.  **Run the Frontend Application:**
    In a **new terminal**, navigate to the frontend directory and start the development server.
    ```bash
    cd src/frontend
    npm start
    ```
    You can then access the application in your web browser, typically at `http://localhost:3000`. To stop the application, press `Ctrl+C` in the terminals where the backend and frontend are running.
