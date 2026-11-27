import sounddevice as sd
from scipy.io.wavfile import write


# =========================================================
# SYNAPSEOS AUDIO RECORDING TEST
# =========================================================

SAMPLE_RATE = 48000
CHANNELS = 2
SECONDS = 30

OUTPUT_FILE = "voice_test.wav"


print()
print("========================================")
print("       SYNAPSEOS AUDIO RECORDING")
print("========================================")
print()

print("Microphone recording")
print("Sample rate:", SAMPLE_RATE)
print("Channels:", CHANNELS)
print("Duration:", SECONDS, "seconds")
print()

print("You can speak normally.")
print("You do NOT need to speak continuously.")
print()

input("Press ENTER when you are ready to start...")

print()
print("🎤 RECORDING NOW...")
print("Speak normally!")
print()


try:

    audio = sd.rec(
        int(SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    print()
    print("Recording finished.")
    print("Saving...")


    write(
        OUTPUT_FILE,
        SAMPLE_RATE,
        audio
    )


    print()
    print("========================================")
    print("Recording saved successfully!")
    print("File:", OUTPUT_FILE)
    print("========================================")


except Exception as e:

    print()
    print("========================================")
    print("RECORDING ERROR")
    print("========================================")
    print()
    print(type(e).__name__)
    print(e)