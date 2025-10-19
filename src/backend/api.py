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
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from translator import ASLTranslator
from recognizer import SpeechRecognizer

 
# --- Global State and Services ---
latest_transcriptions = {"asl": "Initializing...", "speech": "Initializing..."}
asl_translator = ASLTranslator()
speech_recognizer = SpeechRecognizer()

def update_asl_translation(text: str):
    """Callback to update the latest ASL transcription."""
    latest_transcriptions["asl"] = text

def update_speech_recognition(text: str):
    """Callback to update the latest speech recognition."""
    latest_transcriptions["speech"] = text

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown of background services.
    """
    print("--- Starting background services ---")
    # Run services in background threads
    asl_thread = threading.Thread(target=asl_translator.start_translation, args=(update_asl_translation,), daemon=True)
    speech_thread = threading.Thread(target=speech_recognizer.start_recognition, args=(update_speech_recognition,), daemon=True)
    
    asl_thread.start()
    speech_thread.start()
    
    yield
    
    print("--- Application shutdown ---")

app = FastAPI(lifespan=lifespan)

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


@app.get("/asl-to-text")
async def get_asl_transcription():
    """

    Endpoint to get the latest ASL transcription.
    """

    return {"text": latest_transcriptions["asl"]}

@app.get("/speech-to-text")
async def get_speech_transcription():
    """

    Endpoint to get the latest speech recognition.
    """

    return {"text": latest_transcriptions["speech"]}
