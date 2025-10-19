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
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# from translator import ASLTranslator
# from recognizer import SpeechRecognizer

app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# asl_translator = ASLTranslator()
# speech_recognizer = SpeechRecognizer()

@app.post("/asl-to-text")
async def asl_to_text(file: UploadFile = File(...)):
    """
    Endpoint to transcribe ASL video.
    (Placeholder implementation)
    """
    # In a real implementation, you would save the file and process it.
    # For now, we'll just return a dummy response.
    return {"text": "(ASL transcription placeholder)"}

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Endpoint to transcribe speech audio.
    (Placeholder implementation)
    """
    # In a real implementation, you would save the file and process it.
    # For now, we'll just return a dummy response.
    return {"text": "(Speech transcription placeholder)"}
