
import speech_recognition as sr
import pyttsx3
import time


# =========================================================
# SETTINGS
# =========================================================

MIC_INDEX = 1

# =========================================================
# TEXT TO SPEECH
# =========================================================

engine = pyttsx3.init()

engine.setProperty("rate", 165)
engine.setProperty("volume", 1.0)


def speak(text):

    print("SynapseOS:", text)

    engine.say(text)
    engine.runAndWait()


# =========================================================
# SPEECH RECOGNIZER
# =========================================================

recognizer = sr.Recognizer()

# Don't make the recognizer too aggressive
recognizer.energy_threshold = 60

recognizer.dynamic_energy_threshold = True

recognizer.pause_threshold = 0.8

recognizer.phrase_threshold = 0.2

recognizer.non_speaking_duration = 0.5


# =========================================================
# MICROPHONE
# =========================================================

microphone = sr.Microphone(
    device_index=MIC_INDEX
)


print()
print("========================================")
print("       SYNAPSEOS VOICE TEST")
print("========================================")
print()

print(
    "Microphone:",
    sr.Microphone.list_microphone_names()[MIC_INDEX]
)

print()

speak(
    "Hello. SynapseOS voice assistant is ready."
)

print(
    "Say something clearly."
)

print(
    "Say exit to stop."
)

print()


# =========================================================
# CALIBRATE
# =========================================================

with microphone as source:

    print(
        "Calibrating microphone..."
    )

    recognizer.adjust_for_ambient_noise(
        source,
        duration=1
    )

    print(
        "Energy threshold:",
        recognizer.energy_threshold
    )

    print()


# =========================================================
# LISTENING LOOP
# =========================================================

while True:

    try:

        with microphone as source:

            print("🎤 Listening...")

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=6
            )


        print(
            "Audio captured."
        )

        print(
            "🧠 Recognizing..."
        )


        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )


        text = text.lower().strip()


        print()
        print(
            "YOU:",
            text
        )
        print()


        # =================================================
        # EXIT
        # =================================================

        if text in (
            "exit",
            "quit",
            "stop",
            "close"
        ):

            speak(
                "Goodbye."
            )

            break


        # =================================================
        # RESPONSE
        # =================================================

        speak(
            f"I heard you say {text}"
        )


    except sr.WaitTimeoutError:

        print(
            "⏱️ Nothing detected."
        )


    except sr.UnknownValueError:

        print(
            "❌ I heard audio, "
            "but couldn't understand the speech."
        )

        speak(
            "I couldn't understand that."
        )


    except sr.RequestError as e:

        print(
            "❌ Speech service error:",
            e
        )

        speak(
            "The speech recognition service is unavailable."
        )

        time.sleep(2)


    except KeyboardInterrupt:

        print(
            "\nVoice test stopped."
        )

        break


    except Exception as e:

        print(
            "❌ Unexpected error:",
            e
        )

        break

