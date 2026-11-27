from command_engine import CommandEngine


print()
print("========================================")
print("       SYNAPSEOS COMMAND TEST")
print("========================================")
print()


engine = CommandEngine()


while True:

    command = input(
        "\nEnter command: "
    )

    if not engine.execute(command):
        break