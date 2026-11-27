
import os
import wave
from faster_whisper import WhisperModel


# =========================================================
# SYNAPSEOS WHISPER TEST
# =========================================================

AUDIO_FILE = "voice_test.wav"

MODEL_SIZE = "base"


print()
print("========================================")
print("       SYNAPSEOS WHISPER TEST")
print("========================================")
print()


# =========================================================
# CHECK AUDIO
# =========================================================

if not os.path.exists(AUDIO_FILE):

    print("ERROR: voice_test.wav not found.")
    print()
    print("Run record_voice.py first.")
    exit()


# =========================================================
# LOAD WHISPER
# =========================================================

print("Loading Whisper model...")
print("This may take a little while the first time.")
print()

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded successfully.")
print()


# =========================================================
# TRANSCRIBE
# =========================================================

print("Transcribing:")
print(AUDIO_FILE)
print()

segments, info = model.transcribe(
    AUDIO_FILE,
    beam_size=5,
    language="en"
)


text = ""

for segment in segments:

    text += segment.text


text = text.strip()


# =========================================================
# RESULT
# =========================================================

print("========================================")

if text:

    print("WHISPER HEARD:")
    print(text)

else:

    print("Whisper could not detect speech.")


print("========================================")
print()

print("Detected language:", info.language)
print("Probability:", info.language_probability)

print()

