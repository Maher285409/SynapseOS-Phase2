
import pyaudio
import audioop
import time

MIC_INDEX = 1

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=MIC_INDEX,
    frames_per_buffer=CHUNK
)

print("========================================")
print("       SYNAPSEOS MICROPHONE LEVEL")
print("========================================")
print()
print("Speak normally for 10 seconds.")
print("Watch the numbers below.")
print()

for i in range(100):

    data = stream.read(
        CHUNK,
        exception_on_overflow=False
    )

    level = audioop.rms(
        data,
        2
    )

    print(
        f"Mic level: {level:5d}"
    )

    time.sleep(0.1)


stream.stop_stream()
stream.close()

audio.terminate()

print()
print("Microphone test finished.")

