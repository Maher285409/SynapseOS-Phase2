from voice_engine import VoiceEngine


print()
print("========================================")
print("       SYNAPSEOS VOICE ENGINE")
print("========================================")
print()

voice = VoiceEngine()

print()
print("Say:")
print("  Hello SynapseOS")
print()

text = voice.listen()

print()
print("Final result:")
print(text)