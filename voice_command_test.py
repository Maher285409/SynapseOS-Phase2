from voice_engine import VoiceEngine
from command_engine import CommandEngine


print()
print("========================================")
print("      SYNAPSEOS VOICE COMMAND TEST")
print("========================================")
print()


voice = VoiceEngine()
commands = CommandEngine()


print()
print("Voice command system ready.")
print()
print("Try saying:")
print("  Open Chrome")
print("  Open YouTube")
print("  Increase volume")
print("  Decrease volume")
print("  Mute volume")
print("  What time is it")
print()
print("Say 'exit' to stop.")
print()


while True:

    text = voice.listen()

    if not text:
        continue

    print()
    print("[Voice Command]", text)

    running = commands.execute(text)

    if not running:
        break


print()
print("Voice command system closed.")