'''
 @author Huy Le (hl9082)
 @co-author Will Stott, Zoe Shearer, Josh Elliot
 @purpose
  This module provides the API endpoints for the ASL-to-subtitles application.
   It uses FastAPI to create a web server that can receive requests from the
  frontend to perform ASL and speech transcription. It uses Server-Sent Events (SSE)
  to stream transcriptions to the frontend in real-time.
 @importance
   This file is the bridge between the frontend and the backend. It exposes the
   transcription services to the user interface.
'''
import asyncio
import threading
import torch.nn.functional as F
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models
import io
import os
from fastapi.middleware.cors import CORSMiddleware
import json

from translator import ASLTranslator
from recognizer import SpeechRecognizer

# --- Broadcaster for Server-Sent Events ---
class Broadcaster:
    def __init__(self):
        self.connections = set()
        self._lock = asyncio.Lock()

    async def subscribe(self, queue):
        async with self._lock:
            self.connections.add(queue)

    async def unsubscribe(self, queue):
        async with self._lock:
            self.connections.remove(queue)

    async def publish(self, message: str):
        async with self._lock:
            for queue in self.connections:
                await queue.put(message)

broadcaster = Broadcaster()

# define class labels for ASL model
class_labels = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'space', 'nothing'
]

# -- Import Model --
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'asl_model.pth')

# initalize and eval model
model = models.mobilenet_v2(weights=None) # use mobilenet_v2 architecture
num_classes = len(class_labels)
model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)
checkpoint = torch.load(MODEL_PATH, map_location='cpu')

model.load_state_dict(checkpoint)

model.train(False)

# use the same transform as training
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# --- FastAPI Setup ---
app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, consider restricting in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global State and Services ---
class AppState:
    def __init__(self):
        self.active_thread = None
        self.stop_event = threading.Event()
        self.loop = None

state = AppState()
asl_translator = ASLTranslator()
speech_recognizer = SpeechRecognizer()

@app.on_event("startup")
async def startup_event():
    """Capture the running event loop on startup."""
    state.loop = asyncio.get_running_loop()

def update_transcription(service: str, text: str):
    """Callback to publish the latest transcription."""
    # This function is called from a background thread, so we need a thread-safe
    # way to call our async publish method on the main event loop.
    if state.loop:
        coro = broadcaster.publish(json.dumps({"service": service, "text": text}))
        asyncio.run_coroutine_threadsafe(coro, state.loop)

def stop_current_service():
    """Signals the current running service to stop."""
    if state.active_thread and state.active_thread.is_alive():
        print("--- Stopping current service ---")
        state.stop_event.set()
        state.active_thread.join()
        print("--- Service stopped ---")
    state.stop_event.clear()
    state.active_thread = None

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Welcome to the real-time transcription API!"}

@app.get("/start/asl")
async def start_asl_service():
    """Starts the ASL translation service."""
    stop_current_service()
    update_transcription("speech", "Speech service is off.")
    state.active_thread = threading.Thread(
        target=asl_translator.start_translation,
        args=(lambda text: update_transcription("asl", text), state.stop_event),
        daemon=True
    )
    state.active_thread.start()
    return {"message": "ASL translation service started."}

@app.get("/start/speech")
async def start_speech_service():
    """Starts the speech recognition service."""
    stop_current_service()
    update_transcription("asl", "ASL service is off.")
    state.active_thread = threading.Thread(
        target=speech_recognizer.start_recognition,
        args=(lambda text: update_transcription("speech", text), state.stop_event),
        daemon=True
    )
    state.active_thread.start()
    return {"message": "Speech recognition service started."}

@app.get("/stop")
async def stop_services():
    """Stops any currently running service."""
    stop_current_service()
    update_transcription("asl", "ASL service is off.")
    update_transcription("speech", "Speech service is off.")
    return {"message": "All services stopped."}

@app.get("/stream")
async def stream_transcriptions(request: Request):
    """
    Endpoint for frontend to connect to for real-time transcriptions via SSE.
    """
    async def event_generator():
        queue = asyncio.Queue()
        await broadcaster.subscribe(queue)
        try:
            while True:
                # Check if the client is still connected
                if await request.is_disconnected():
                    break
                message = await queue.get()
                yield f"data: {message}\n\n"
        finally:
            await broadcaster.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Prediction api endpoint
@app.post("/predict-asl")
async def predict_asl(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = transform(image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = F.softmax(outputs, dim=1)
            conf, pred = torch.max(probs, 1)
            label = class_labels[pred.item()]
        return JSONResponse(content={"prediction": label, "confidence": float(conf.item())})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)