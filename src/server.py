import os
import json
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Response, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastrtc import (
    get_twilio_turn_credentials,
    Stream,
    ReplyOnPause,
)

from model import SessionManager
from graph import build_graph, memory
from voice import get_voice_processor
from config import settings, logger, LANDING_HTML, CURR_DIR, STATIC_DIR

# === Model Initialization ===
voice_processor = get_voice_processor()

# === Graph Setup ===
story_graph = build_graph()
session_managers = {}
profile = {}

def get_session(session_id: str = "default") -> SessionManager:
    """Return existing session manager or create a new one."""
    if session_id not in session_managers:
        logger.info("Creating new SessionManager for session_id=%s", session_id)
        session_managers[session_id] = SessionManager(session_id, story_graph, memory)
    return session_managers[session_id]

def _speak(text: str):
    """Utility to speak text (blocking)."""
    yield from voice_processor.speak(text)

def process_audio_response(audio):
    """
    Blocking generator that:
      1. converts audio -> text (STT)
      2. passes text to SessionManager
      3. streams TTS chunks back
    """
    try:
        # TODO: replace "default" with per-client session id (from auth or signaling)
        session_id = "default"
        session = get_session(session_id)
        session.parental_guidelines = profile.get("guidelines", "")
        
        # enables reseting interaction
        if session.current_state.get("story_over", False):
            logger.info("Story is over")
            user_input = voice_processor.speech_to_text(audio)
            logger.debug("STT result: %s", repr(user_input))
            if user_input.lower() in ["new story", "start new story", "start a new story", "new story.", "start new story.", "start a new story.", "start the new story.", "start the new story"]:
                session.reset()
            else:
                logger.info("User did not request new story, ignoring input")
                return
        
        # initial greeting and check for existing story
        if not session.greeted:
            story = session.get_user_story()
            if story:
                yield from _speak(f"Welcome back {profile['name']}! I found your previous story. Do you want to continue?")
            else:
                session.started_conversation = True
                yield from _speak(f"Hello {profile['name']}! Let's start a new story! Give any topic or just tell me to start!")

            session.greeted = True
            return
        
        # wait until user confirms to continue or start new story
        if not session.started_conversation:
            user_input = voice_processor.speech_to_text(audio)
            logger.debug("STT result: %s", repr(user_input)[:200])
            if user_input.lower() in ["yes", "okay", "sure", "continue", "yes.", "okay.", "sure.", "continue."]:
                yield from _speak("Great! Let's continue the story. Just tell me to start!") 
                session.started_conversation = True
            elif user_input.lower() in ["no", "stop", "end", "no.", "stop.", "end."]:
                yield from _speak("Okay, then we will start a new story. Give me any topic or just tell me to start!")
                session.started_conversation = True
            else:
                yield from _speak("I didn't understand. Please say 'yes' to continue or 'no' to stop.")
                return
        
        # 1. STT
        user_input = voice_processor.speech_to_text(audio)
        logger.debug("STT result: %s", repr(user_input)[:200])
        if len(user_input.strip()) == 0:
            yield from _speak("I didn't catch that. Please say something.")
            return
          
        # 2. process user input with the conversation/session manager
        ai_response = session.process_user_input(user_input)
        logger.info("AI response (len=%d chars) for session=%s", len(ai_response), session_id)
        
        # 3. stream TTS
        yield from _speak(ai_response)
    except Exception:
        logger.exception("Error while processing audio response")
        return

# === FastAPI App ===
app = FastAPI()
app.mount("/static", StaticFiles(directory=str(CURR_DIR / "static")), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === WebRTC Streaming Setup ===
stream = Stream(ReplyOnPause(process_audio_response), modality="audio", mode="send-receive")
stream.mount(app)

# === Routes ===
@app.get("/app.js")
async def get_app_js():
    """
    Returns static JS with injected RTC configuration if available.
    """
    js_path = STATIC_DIR / "app.js"
    if not js_path.exists():
        logger.error("app.js not found at %s", js_path)
        raise HTTPException(status_code=404, detail="JavaScript file not found")

    try:
        rtc_config = get_twilio_turn_credentials() if settings.SPACE_ID else {"iceServers": [{"urls": "stun:stun.l.google.com:19302"}]}
        js_content = js_path.read_text(encoding="utf-8")
        js_content = js_content.replace("__RTC_CONFIGURATION__", json.dumps(rtc_config))
        return Response(content=js_content, media_type="application/javascript")
    except Exception:
        logger.exception("Failed to read or process app.js")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/app", response_class=HTMLResponse)
async def index():
    html_path = CURR_DIR / "index.html"
    if not html_path.exists():
        logger.error("index.html not found at %s", html_path)
        raise HTTPException(status_code=404, detail="Index page not found")
    try:
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Failed to read index.html")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/outputs")
def outputs(webrtc_id: str):
    """
    Server-Sent Events (SSE) endpoint that streams outputs for a given webrtc_id.
    """
    async def output_stream():
        async for output in stream.output_stream(webrtc_id):
            yield f"event: output\ndata: {json.dumps(output.args[0])}\n\n"
    return StreamingResponse(output_stream(), media_type="text/event-stream")

@app.get("/", response_class=Response)
async def landing():
    return Response(content=LANDING_HTML, media_type="text/html")

@app.post("/start")
async def start(name: str = Form(...), age: int = Form(...), guidelines: str = Form(""),):
    session_id = "default" # str(uuid.uuid4())
    global profile
    profile = {
        "name": name,
        "age": int(age),
        "guidelines": guidelines,
        "created_at": datetime.utcnow(),
    }
    logger.info("Creating new profile for session_id=%s: %s", session_id, profile)
    resp = RedirectResponse(url="/app", status_code=303)
    return resp


# === Server Entrypoint ===
if __name__ == "__main__":
    logger.info(f"Starting server at http://{settings.HOST}:{settings.PORT}/start")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)