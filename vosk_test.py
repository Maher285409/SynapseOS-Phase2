
import json
import os
import audioop
import pyaudio
from vosk import Model, KaldiRecognizer


# =========================================================
# SYNAPSEOS VOSK VOICE TEST
# =========================================================

MODEL_PATH = "vosk-model-small-en-us-0.15"

MIC_INDEX = 5

MIC_RATE = 44100

VOSK_RATE = 16000

CHANNELS = 1

CHUNK = 4096


# =========================================================
# LOAD MODEL
# =========================================================

print()
print("========================================")
print("       SYNAPSEOS VOSK VOICE TEST")
print("========================================")
print()

if not os.path.exists(MODEL_PATH):

    print("ERROR: Vosk model not found.")
    print("Expected folder:")
    print(MODEL_PATH)
    exit()


print("Loading offline speech model...")

model = Model(MODEL_PATH)

recognizer = KaldiRecognizer(
    model,
    VOSK_RATE
)

print("Vosk model loaded successfully.")
print()


# =========================================================
# AUDIO DEVICE
# =========================================================

audio = pyaudio.PyAudio()

device = audio.get_device_info_by_index(
    MIC_INDEX
)

print("Using microphone:")
print(device["name"])

print()

print("Microphone sample rate:")
print(device["defaultSampleRate"])

print()


# =========================================================
# OPEN MICROPHONE
# =========================================================

stream = audio.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=MIC_RATE,
    input=True,
    input_device_index=MIC_INDEX,
    frames_per_buffer=CHUNK
)

stream.start_stream()


# =========================================================
# RESAMPLER
# =========================================================

resample_state = None


# =========================================================
# START
# =========================================================

print("========================================")
print("🎤 LISTENING")
print("========================================")
print()

print("Speak clearly.")
print()

print("Try:")
print("  Hello SynapseOS")
print("  Open Chrome")
print("  Increase volume")
print()

print("Press Ctrl+C to stop.")
print()


# =========================================================
# RECOGNITION LOOP
# =========================================================

try:

    while True:

        data = stream.read(
            CHUNK,
            exception_on_overflow=False
        )


        # -------------------------------------------------
        # Convert 44.1 kHz → 16 kHz
        # -------------------------------------------------

        converted_audio, resample_state = audioop.ratecv(
            data,
            2,
            CHANNELS,
            MIC_RATE,
            VOSK_RATE,
            resample_state
        )


        # -------------------------------------------------
        # Send converted audio to Vosk
        # -------------------------------------------------

        if recognizer.AcceptWaveform(
            converted_audio
        ):

            result = json.loads(
                recognizer.Result()
            )

            text = result.get(
                "text",
                ""
            ).strip()


            if text:

                print()
                print(
                    "YOU:",
                    text
                )
                print()


        else:

            partial = json.loads(
                recognizer.PartialResult()
            ).get(
                "partial",
                ""
            ).strip()


            if partial:

                print(
                    "Listening:",
                    partial,
                    end="\r"
                )


except KeyboardInterrupt:

    print()
    print()
    print("Stopping voice test...")


finally:

    stream.stop_stream()
    stream.close()

    audio.terminate()


print("Voice test closed.")

