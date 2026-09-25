import os
import uuid

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from voice.stt import speech_to_text
from voice.tts import text_to_speech

from agent.agent import get_response, get_last_tool_used

from memory import create_memory_table, save_message


# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------

app = FastAPI(title="AI Voice Agent")


# --------------------------------------------------
# Initialize Memory Database
# --------------------------------------------------

create_memory_table()


# --------------------------------------------------
# Create audio directory
# --------------------------------------------------

os.makedirs("audio", exist_ok=True)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# --------------------------------------------------
# Serve Audio Files
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

    input_filename = f"input_{uuid.uuid4().hex}.webm"
    output_filename = f"response_{uuid.uuid4().hex}.mp3"

    input_path = input_filename
    output_path = os.path.join("audio", output_filename)

    try:

        # ------------------------------------------
        # 1. Receive Audio
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

        tool_used = get_last_tool_used()

        print("🔧 Tool used:", tool_used)


        # ------------------------------------------
        # 4. Save Conversation
        # ------------------------------------------

        save_message("user", text)
        save_message("assistant", response)


        # ------------------------------------------
        # 5. Text To Speech
        # ------------------------------------------

        text_to_speech(
            response,
            output_path
        )


        # ------------------------------------------
        # 6. Return Response
        # ------------------------------------------

        return {
        "text": text,
        "response": response,
        "tool_used": tool_used,
        "audio_file": f"/audio/{output_filename}"
        }


    except Exception as e:

        print("❌ Error:", e)

        return {
            "error": str(e)
        }


    finally:

        # ------------------------------------------
        # Delete temporary input file
        # ------------------------------------------

        if os.path.exists(input_path):
            os.remove(input_path)