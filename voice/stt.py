import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

STT_API_KEY = os.getenv("STT_API_KEY")

if not STT_API_KEY:
    raise ValueError("STT_API_KEY not found in .env")

deepgram = DeepgramClient(api_key=STT_API_KEY)


def speech_to_text(audio_file):
    with open(audio_file, "rb") as audio:
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio.read(),
            model="nova-3",
            smart_format=True,
        )

    transcript = response.results.channels[0].alternatives[0].transcript

    return transcript