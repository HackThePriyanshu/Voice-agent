import os
import uuid

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from voice.stt import speech_to_text
from voice.tts import text_to_speech
from agent.agent import get_response


app = FastAPI(title="AI Voice Agent")


# Serve frontend
@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# Serve generated audio files
app.mount(
    "/audio",
    StaticFiles(directory="audio"),
    name="audio"
)


@app.post("/voice")
async def voice(audio: UploadFile = File(...)):

    # -----------------------------
    # 1. Create unique filenames
    # -----------------------------

    input_file = f"input_{uuid.uuid4().hex}.webm"
    output_filename = f"response_{uuid.uuid4().hex}.mp3"

    input_path = input_file
    output_path = os.path.join("audio", output_filename)


    try:

        # -----------------------------
        # 2. Read uploaded audio
        # -----------------------------

        audio_data = await audio.read()

        with open(input_path, "wb") as f:
            f.write(audio_data)


        # -----------------------------
        # 3. Speech → Text
        # -----------------------------

        text = speech_to_text(input_path)

        if not text or not text.strip():
            return {
                "error": "No speech detected"
            }

        print("👤 User:", text)


        # -----------------------------
        # 4. Text → AI Agent
        # -----------------------------

        response = get_response(text)

        print("🤖 Agent:", response)


        # -----------------------------
        # 5. Agent → Speech
        # -----------------------------

        audio_file = text_to_speech(
            response,
            output_path
        )


        # -----------------------------
        # 6. Return response
        # -----------------------------

        return {
            "text": text,
            "response": response,
            "audio_file": f"/audio/{output_filename}"
        }


    finally:

        # -----------------------------
        # 7. Delete input audio
        # -----------------------------

        if os.path.exists(input_path):
            os.remove(input_path)