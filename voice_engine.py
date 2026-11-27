import os
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel


class VoiceEngine:

    def __init__(self):

        print("[Voice] Loading Whisper model...")

        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

        print("[Voice] Whisper loaded successfully.")

        self.sample_rate = 48000
        self.record_seconds = 4


    def listen(self):

        print()
        print("🎤 [Voice] Listening...")

        audio = sd.rec(
            int(
                self.record_seconds *
                self.sample_rate
            ),
            samplerate=self.sample_rate,
            channels=2,
            dtype="int16"
        )

        sd.wait()

        temp_file = os.path.join(
            tempfile.gettempdir(),
            "synapse_voice.wav"
        )

        write(
            temp_file,
            self.sample_rate,
            audio
        )

        print("🧠 [Voice] Recognizing...")

        segments, info = self.model.transcribe(
            temp_file,
            language="en",
            beam_size=5,
            temperature=0,
            condition_on_previous_text=False,
            vad_filter=True
        )

        words = []

        for segment in segments:

            text = segment.text.strip()

            if text:
                words.append(text)


        text = " ".join(words)

        text = text.strip()


        if not text:

            print("[Voice] No speech detected.")

            return ""


        # Remove accidental repeated phrases
        parts = text.split()

        cleaned = []

        for word in parts:

            if not cleaned or word.lower() != cleaned[-1].lower():

                cleaned.append(word)


        text = " ".join(cleaned)


        print(
            "[Voice] You said:",
            text
        )

        return text.lower()