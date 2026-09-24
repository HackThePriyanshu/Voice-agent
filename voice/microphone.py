import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np


def record_audio(filename="recording.wav", sample_rate=16000):

    print("🎤 Speak now...")

    recording = []

    silence_threshold = 500
    silence_duration = 1.5

    silent_chunks = 0
    chunk_duration = 0.1
    chunk_size = int(sample_rate * chunk_duration)

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    ) as stream:

        while True:

            data, overflowed = stream.read(chunk_size)

            recording.append(data.copy())

            volume = np.abs(data).mean()

            if volume < silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks * chunk_duration >= silence_duration:
                break

    audio = np.concatenate(recording)

    write(filename, sample_rate, audio)

    print("✅ Recording completed!")

    return filename