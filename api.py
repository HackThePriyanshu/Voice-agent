import os
import uuid

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from voice.stt import speech_to_text
from voice.tts import text_to_speech
from agent.agent import get_response


# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------

app = FastAPI(title="AI Voice Agent")


# --------------------------------------------------
# Create audio directory if it doesn't exist
# --------------------------------------------------

os.makedirs("audio", exist_ok=True)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# --------------------------------------------------
# Serve generated audio files
# --------------------------------------------------

app.mount(
    "/audio",
    StaticFiles(directory="audio"),
    name="audio"
)


# --------------------------------------------------
# Voice API
# --------------------------------------------------

@app.post("/voice")
async def voice(audio: UploadFile = File(...)):

    # Unique filenames for each request
    input_filename = f"input_{uuid.uuid4().hex}.webm"
    output_filename = f"response_{uuid.uuid4().hex}.mp3"

    input_path = input_filename
    output_path = os.path.join("audio", output_filename)

    try:

        # ------------------------------------------
        # 1. Read uploaded audio
        # ------------------------------------------

        audio_data = await audio.read()

        with open(input_path, "wb") as f:
            f.write(audio_data)


        # ------------------------------------------
        # 2. Speech To Text
        # ------------------------------------------

        text = speech_to_text(input_path)

        if not text or not text.strip():
            return {
                "error": "No speech detected"
            }

        print("👤 User:", text)


        # ------------------------------------------
        # 3. AI Agent
        # ------------------------------------------

        response = get_response(text)

        print("🤖 Agent:", response)


        # ------------------------------------------
        # 4. Text To Speech
        # ------------------------------------------

        text_to_speech(
            response,
            output_path
        )


        # ------------------------------------------
        # 5. Return response
        # ------------------------------------------

        return {
            "text": text,
            "response": response,
            "audio_file": f"/audio/{output_filename}"
        }


    except Exception as e:

        print("❌ Error:", e)

        return {
            "error": str(e)
        }


    finally:

        # ------------------------------------------
        # Delete temporary input audio
        # ------------------------------------------

        if os.path.exists(input_path):
            os.remove(input_path)