import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

TTS_API_KEY = os.getenv("TTS_API_KEY")

if not TTS_API_KEY:
    raise ValueError("TTS_API_KEY not found in .env")

client = ElevenLabs(api_key=TTS_API_KEY)


def text_to_speech(text, output_file="response.mp3"):
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128",
    )

    with open(output_file, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return output_file