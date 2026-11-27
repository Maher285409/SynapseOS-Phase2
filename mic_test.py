
import speech_recognition as sr

recognizer = sr.Recognizer()

MIC_INDEX = 1

print("========================================")
print("       SYNAPSEOS MICROPHONE TEST")
print("========================================")
print()
print("Using microphone:")
print(
    sr.Microphone.list_microphone_names()[MIC_INDEX]
)
print()
print("Speak clearly for a few seconds.")
print()


with sr.Microphone(device_index=MIC_INDEX) as source:

    print("Adjusting microphone for background noise...")

    recognizer.adjust_for_ambient_noise(
        source,
        duration=1
    )

    print(
        "Energy threshold:",
        recognizer.energy_threshold
    )

    print()
    print("🎤 LISTENING — SAY SOMETHING NOW!")

    audio = recognizer.listen(
        source,
        timeout=10,
        phrase_time_limit=6
    )


print()
print("Audio captured!")
print("Trying to recognize your speech...")
print()


try:

    text = recognizer.recognize_google(
        audio
    )

    print()
    print("========================================")
    print("YOU SAID:")
    print(text)
    print("========================================")


except sr.UnknownValueError:

    print()
    print("❌ Microphone captured audio,")
    print("but speech could not be understood.")


except sr.RequestError as e:

    print()
    print("❌ Google speech service error:")
    print(e)


except Exception as e:

    print()
    print("❌ Error:")
    print(e)

