import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

TTS_API_KEY = os.getenv("STT_API_KEY")

if not TTS_API_KEY:
    raise ValueError("STT_API_KEY not found in .env")

deepgram = DeepgramClient(api_key=TTS_API_KEY)


def text_to_speech(text, output_file="response.mp3"):

    audio = deepgram.speak.v1.audio.generate(
        text=text,
        model="aura-2-thalia-en",
        encoding="mp3",
    )

    with open(output_file, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return output_file