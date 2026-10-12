from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from voice.stt import speech_to_text
from voice.tts import text_to_speech

from agent.graph import graph

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from memory import create_memory_table

import os
import uuid


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
async def voice(
    audio: UploadFile = File(...),
    thread_id: str = Form(...),
    user_id: str = Form(...)
):
    input_filename = f"input_{uuid.uuid4().hex}.webm"
    output_filename = f"response_{uuid.uuid4().hex}.mp3"

    input_path = input_filename
    output_path = os.path.join("audio", output_filename)

    try:
        audio_data = await audio.read()

        with open(input_path, "wb") as f:
            f.write(audio_data)

        # STT
        text = speech_to_text(input_path)

        if not text or not text.strip():
            return {"error": "No speech detected"}

        print("👤 User:", text)
        print("🧵 Thread ID:", thread_id)

        # LangGraph config
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }

        # Check whether graph is waiting for confirmation
        current_state = graph.get_state(config)
        is_interrupted = bool(current_state.interrupts)

        if is_interrupted:
            print("▶️ Resuming interrupted graph...")

            result = graph.invoke(
                Command(resume=text),
                config
            )

        else:
            print("▶️ Starting new graph turn...")

            result = graph.invoke(
                {
                    "messages": [
                        HumanMessage(content=text)
                    ]
                },
                config
            )

        # Get latest state
        state = graph.get_state(config)

        interrupted = bool(state.interrupts)

        if interrupted:
            response = str(
                state.interrupts[0].value
            )
        else:
            response = result["messages"][-1].content

        print("🤖 Agent:", response)
        print("⏸️ Interrupted:", interrupted)

        # TTS
        text_to_speech(
            response,
            output_path
        )

        return {
            "text": text,
            "response": response,
            "audio_file": f"/audio/{output_filename}",
            "interrupted": interrupted,
            "thread_id": thread_id
        }

    except Exception as e:
        print("❌ Error:", e)

        return {
            "error": str(e)
        }

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)


@app.post("/graph-test")
async def graph_test(data: dict):
    user_text = data.get("message")
    thread_id = data.get("thread_id", "default-user")

    if not user_text:
        return {"error": "Message is required"}

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_text)
            ]
        },
        config
    )

    state = graph.get_state(config)

    return {
        "response": result["messages"][-1].content,
        "interrupted": bool(state.interrupts),
        "thread_id": thread_id
    }

@app.post("/graph-resume")
async def graph_resume(data: dict):
    answer = data.get("answer")
    thread_id = data.get("thread_id")

    if not answer:
        return {"error": "Answer is required"}

    if not thread_id:
        return {"error": "Thread ID is required"}

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = graph.invoke(
        Command(resume=answer),
        config
    )

    state = graph.get_state(config)

    interrupted = bool(state.interrupts)

    if interrupted:
        response = str(state.interrupts[0].value)
    else:
        response = result["messages"][-1].content

    return {
        "text": answer,
        "response": response,
        "interrupted": interrupted,
        "thread_id": thread_id
    }

@app.get("/new-session")
def new_session():
    return {
        "thread_id": str(uuid.uuid4())
    }