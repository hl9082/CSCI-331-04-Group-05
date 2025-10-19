'''

 @author Huy Le (hl9082)
  @co-author Will Stott, Zoe Shearer, Josh Elliot
  @purpose
   This module provides the API endpoints for the ASL-to-subtitles application.
    It uses FastAPI to create a web server that can receive requests from the
   frontend to perform ASL and speech transcription.
  @importance
    This file is the bridge between the frontend and the backend. It exposes the
    transcription services to the user interface.
 
'''

import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from translator import ASLTranslator
from recognizer import SpeechRecognizer

 
# --- Global State and Services ---
class AppState:
    def __init__(self):
        self.latest_transcriptions = {"asl": "ASL service is off.", "speech": "Speech service is off."}
        self.active_thread = None
        self.stop_event = threading.Event()

state = AppState()
asl_translator = ASLTranslator()
speech_recognizer = SpeechRecognizer()

def update_asl_translation(text: str):
    """Callback to update the latest ASL transcription."""
    state.latest_transcriptions["asl"] = text

def update_speech_recognition(text: str):
    """Callback to update the latest speech recognition."""
    state.latest_transcriptions["speech"] = text

def stop_current_service():
    """Signals the current running service to stop."""
    if state.active_thread and state.active_thread.is_alive():
        print("--- Stopping current service ---")
        state.stop_event.set()
        state.active_thread.join() # Wait for the thread to finish
        print("--- Service stopped ---")
    state.stop_event.clear()
    state.active_thread = None

app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """

    return {"message": "Welcome to the real-time transcription API!"}

@app.post("/start/asl")
async def start_asl_service():
    """Starts the ASL translation service."""
    stop_current_service()
    state.latest_transcriptions["speech"] = "Speech service is off."
    state.active_thread = threading.Thread(
        target=asl_translator.start_translation,
        args=(update_asl_translation, state.stop_event),
        daemon=True
    )
    state.active_thread.start()
    return {"message": "ASL translation service started."}

@app.post("/start/speech")
async def start_speech_service():
    """Starts the speech recognition service."""
    stop_current_service()
    state.latest_transcriptions["asl"] = "ASL service is off."
    state.active_thread = threading.Thread(
        target=speech_recognizer.start_recognition,
        args=(update_speech_recognition, state.stop_event),
        daemon=True
    )
    state.active_thread.start()
    return {"message": "Speech recognition service started."}

@app.post("/stop")
async def stop_services():
    """Stops any currently running service."""
    stop_current_service()
    state.latest_transcriptions = {"asl": "ASL service is off.", "speech": "Speech service is off."}
    return {"message": "All services stopped."}

@app.get("/asl-to-text")
async def get_asl_transcription():
    """

    Endpoint to get the latest ASL transcription.
    """

    return {"text": state.latest_transcriptions["asl"]}


@app.get("/speech-to-text")
async def get_speech_transcription():
    """
    Endpoint to get the latest speech recognition.
    """

    return {"text": state.latest_transcriptions["speech"]}
