'''
@author Huy Le (hl9082)
@co-author Will Stott, Zoe Shearer, Josh Elliot
@purpose
 This module provides the API endpoints for the ASL-to-subtitles application.
 It uses FastAPI to create a web server that can receive requests from the
 frontend to perform ASL transcription from an image and real-time speech
 transcription.
@importance
  This file is the bridge between the frontend and the backend. It exposes the
  transcription services to the user interface.
'''
import asyncio
import threading
import json
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from translator import ASLTranslator
from recognizer import SpeechRecognizer

# --- Broadcaster for Server-Sent Events (SSE) ---
# This class is responsible for managing active SSE connections from clients
# and broadcasting messages (like transcriptions) to all of them. This is the
# core of the real-time functionality.
class Broadcaster:
    def __init__(self):
        # A set to hold all active client connections (represented by asyncio Queues).
        self.connections = set()
        # A lock to ensure that adding/removing connections is thread-safe.
        self._lock = asyncio.Lock()

    async def subscribe(self, queue):
        """Adds a new client connection to the broadcaster."""
        async with self._lock:
            self.connections.add(queue)

    async def unsubscribe(self, queue):
        """Removes a client connection."""
        async with self._lock:
            self.connections.remove(queue)

    async def publish(self, message: str):
        """Sends a message to all connected clients."""
        async with self._lock:
            for queue in self.connections:
                await queue.put(message)

# Create a global instance of the broadcaster to be used by the app.
broadcaster = Broadcaster()


# --- FastAPI Setup ---
app = FastAPI()

# Configure CORS (Cross-Origin Resource Sharing) to allow requests from the frontend.
# This is crucial for web applications where the frontend and backend are on different "origins"
# (e.g., http://localhost:3000 and http://localhost:8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. For production, you should restrict this to your frontend's URL.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods.
    allow_headers=["*"],  # Allows all HTTP headers.
)

# --- Global State and Services ---

# This class holds the application's state, specifically for managing
# the background thread that runs the speech recognition service.
class AppState:
    def __init__(self):
        # To hold the currently running background thread (e.g., for speech recognition).
        self.active_thread = None
        # An event to signal the background thread to stop.
        self.stop_event = threading.Event()
        # To hold a reference to the main asyncio event loop.
        self.loop = None

# Create global instances of the state and service classes.
state = AppState()
asl_translator = ASLTranslator()
speech_recognizer = SpeechRecognizer()

@app.on_event("startup")
async def startup_event():
    """
    This function runs when the FastAPI application starts.
    It captures the running asyncio event loop so that we can schedule
    coroutines on it from other threads.
    """
    state.loop = asyncio.get_running_loop()

def update_transcription(service: str, text: str):
    """
    A callback function to publish the latest transcription to the frontend.
    This function is called from the background thread (speech recognizer),
    so it needs a thread-safe way to call the async 'publish' method on the
    main event loop.
    """
    if state.loop:
        # Create a JSON message to send to the frontend.
        message = json.dumps({"service": service, "text": text})
        # `run_coroutine_threadsafe` schedules the 'publish' coroutine to be
        # executed on the main event loop.
        asyncio.run_coroutine_threadsafe(broadcaster.publish(message), state.loop)

def stop_current_service():
    """
    Signals the current running background service to stop gracefully.
    """
    if state.active_thread and state.active_thread.is_alive():
        print("--- Stopping current service ---")
        # Set the event that the background thread is listening for.
        state.stop_event.set()
        # Wait for the thread to finish its cleanup and exit.
        state.active_thread.join()
        print("--- Service stopped ---")
    # Reset the state for the next service.
    state.stop_event.clear()
    state.active_thread = None

# --- API Endpoints ---

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Welcome to the ASL and Speech transcription API!"}


@app.post("/predict-asl")
async def predict_asl(file: UploadFile = File(...)):
    """
    Endpoint for translating an ASL sign from an uploaded image.
    This is a POST request that accepts a file upload.
    """
    try:
        # Read the image file from the request.
        image_bytes = await file.read()
        # Use the ASLTranslator service to get the prediction.
        label, confidence = asl_translator.translate_image(image_bytes)
        if label is not None:
            # Return the prediction and confidence as a JSON response.
            return JSONResponse(content={"prediction": label, "confidence": confidence})
        else:
            return JSONResponse(content={"error": "Translation failed"}, status_code=500)
    except Exception as e:
        # Return an error if anything goes wrong.
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/start/speech")
async def start_speech_service():
    """
    Starts the speech recognition service in a background thread.
    """
    # Stop any service that might be currently running.
    stop_current_service()
    # Send a message to the frontend to indicate the other service is off.
    update_transcription("asl", "ASL service is off.")
    # Create a new background thread for the speech recognition service.
    state.active_thread = threading.Thread(
        target=speech_recognizer.start_recognition,
        # Pass the callback and the stop event to the service.
        args=(lambda text: update_transcription("speech", text), state.stop_event),
        daemon=True  # A daemon thread will exit when the main program exits.
    )
    state.active_thread.start()
    return {"message": "Speech recognition service started."}

@app.get("/stop")
async def stop_services():
    """
    Stops any currently running service.
    """
    stop_current_service()
    # Notify the frontend that services are off.
    update_transcription("asl", "ASL service is off.")
    update_transcription("speech", "Speech service is off.")
    return {"message": "All services stopped."}

@app.get("/stream")
async def stream_transcriptions(request: Request):
    """
    Endpoint for the frontend to connect to for real-time transcriptions
    via Server-Sent Events (SSE).
    """
    async def event_generator():
        # Each client gets its own queue to receive messages.
        queue = asyncio.Queue()
        # Add the client's queue to the broadcaster.
        await broadcaster.subscribe(queue)
        try:
            while True:
                # Check if the client has disconnected.
                if await request.is_disconnected():
                    break
                # Wait for a message from the broadcaster.
                message = await queue.get()
                # Yield the message in the SSE format.
                yield f"data: {message}\n\n"
        finally:
            # Remove the client's queue from the broadcaster on disconnect.
            await broadcaster.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")