from memory import create_memory_table, save_message
from voice.microphone import record_audio
from voice.stt import speech_to_text
from agent.agent import get_response
from voice.tts import text_to_speech
from playsound3 import playsound

create_memory_table()

print("🎙️ Voice Agent Started!")
print("Say 'goodbye' to exit.\n")


while True:

    # 1. Record voice + STT
    try:
        record_audio("recording.wav")
        text = speech_to_text("recording.wav")

    except Exception as e:
        print("❌ Voice input error:", e)
        print("⚠️ Please try speaking again.")
        continue

    # 2. Check empty input
    if not text or not text.strip():
        print("⚠️ No speech detected. Try again.")
        continue

    print("👤 You:", text)

    # 3. Exit command
    command = (
        text.lower()
        .strip()
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
    )

    if command in ["goodbye", "good bye", "exit", "quit", "stop"]:
        print("🤖 Goodbye! 👋")
        break

    # 4. Agent + Memory + TTS
    try:
        response = get_response(text)
        print("🤖 Agent:", response)

        save_message("user", text)
        save_message("assistant", response)

        audio_file = text_to_speech(response)

        print("🔊 Playing response...")
        playsound(audio_file)

    except Exception as e:
        print("❌ Error:", e)
        print("⚠️ Something went wrong. Please try again.")